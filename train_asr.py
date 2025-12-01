import os
import torch
import numpy as np
from datasets import Audio
from transformers import (
    WhisperProcessor, 
    WhisperForConditionalGeneration, 
    Seq2SeqTrainingArguments, 
    Seq2SeqTrainer
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import evaluate
from dataclasses import dataclass
from typing import Any, Dict, List, Union
import argparse
import logging
import sys

# Import the Prosit2 data loader
from data.afrispeech_loader import AfriSpeechShona

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lengths and need different padding methods
        # first treat the audio inputs by simply returning torch tensors
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        # get the tokenized label sequences
        label_features = [{"input_ids": feature["labels"]} for feature in features]
        # pad the labels to max length
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        # if bos token is appended in previous tokenization step,
        # cut bos token here as it's append later anyways
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels

        return batch

import jiwer

# Global processor for metrics
processor = None

def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids

    # replace -100 with the pad_token_id
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id

    # we do not want to group tokens when computing the metrics
    pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    wer = 100 * jiwer.wer(reference=label_str, hypothesis=pred_str)

    return {"wer": wer}

class WhisperDataset(torch.utils.data.Dataset):
    """Wrapper around AfriSpeechShona for Whisper preprocessing"""
    
    def __init__(self, afrispeech_dataset, processor):
        self.dataset = afrispeech_dataset
        self.processor = processor
        
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        sample = self.dataset[idx]
        
        # Get audio and transcription
        audio = sample['audio']
        transcription = sample['transcription']
        sample_rate = sample['sample_rate']
        
        # Convert to tensor
        audio_tensor = torch.from_numpy(audio).float()
        
        # Handle stereo (convert to mono)
        if len(audio_tensor.shape) > 1:
            # sf.read returns (samples, channels), we want (samples,)
            audio_tensor = torch.mean(audio_tensor, dim=1)
        
        # Resample if needed
        if sample_rate != 16000:
            import torchaudio
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            audio_tensor = resampler(audio_tensor)
            sample_rate = 16000
        
        # Convert back to numpy for processor
        audio = audio_tensor.numpy()
        
        # Process audio
        input_features = self.processor.feature_extractor(
            audio, sampling_rate=sample_rate
        ).input_features[0]
        
        # Process transcription
        labels = self.processor.tokenizer(transcription).input_ids
        
        return {
            "input_features": input_features,
            "labels": labels
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke_test", action="store_true", help="Run a quick smoke test with few samples")
    parser.add_argument("--model_name", type=str, default="openai/whisper-tiny", help="Model identifier")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size per device")
    parser.add_argument("--grad_accum", type=int, default=4, help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=1e-3, help="Learning rate (higher for LoRA)")
    parser.add_argument("--epochs", type=int, default=8, help="Number of training epochs")
    parser.add_argument("--output_dir", type=str, default="./whisper-asr-shona-lora", help="Output directory")
    parser.add_argument("--data_dir", type=str, default="./data/afrispeech_shona", help="Data directory")
    parser.add_argument("--use_lora", action="store_true", default=True, help="Use LoRA for training")
    parser.add_argument("--lora_rank", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=32, help="LoRA alpha")
    args = parser.parse_args()

    device = "cpu"  # Force CPU for Mac stability
    logger.info(f"Using device: {device} (forced for Mac stability)")

    # Load datasets using Prosit2's data loader
    logger.info("Loading Shona dataset...")
    if args.smoke_test:
        logger.info("SMOKE TEST MODE: Using subset of 20 samples")
        train_afri = AfriSpeechShona(data_dir=args.data_dir, split="train", subset_size=20)
        eval_afri = AfriSpeechShona(data_dir=args.data_dir, split="dev", subset_size=10)
    else:
        train_afri = AfriSpeechShona(data_dir=args.data_dir, split="train")
        eval_afri = AfriSpeechShona(data_dir=args.data_dir, split="dev")
    
    # Processor
    global processor
    processor = WhisperProcessor.from_pretrained(args.model_name, language="English", task="transcribe")
    
    # Wrap datasets for Whisper preprocessing
    train_dataset = WhisperDataset(train_afri, processor)
    eval_dataset = WhisperDataset(eval_afri, processor)
    
    logger.info(f"Train samples: {len(train_dataset)}, Eval samples: {len(eval_dataset)}")

    # Model
    logger.info(f"Loading model: {args.model_name}")
    model = WhisperForConditionalGeneration.from_pretrained(args.model_name)
    model.config.forced_decoder_ids = None
    model.config.suppress_tokens = []
    
    # Apply LoRA for memory efficiency
    if args.use_lora:
        logger.info("Applying LoRA configuration for parameter-efficient fine-tuning...")
        logger.info(f"LoRA config: rank={args.lora_rank}, alpha={args.lora_alpha}")
        
        # Configure LoRA
        lora_config = LoraConfig(
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            target_modules=["q_proj", "v_proj"],  # Attention layers
            lora_dropout=0.1,
            bias="none",
        )
        
        # Apply LoRA
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
    
    # Data Collator
    data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

    # Training Args
    if args.smoke_test:
        epochs = 1
        eval_steps = 2
        save_steps = 2  # Must be multiple of eval_steps
        logging_steps = 1
    else:
        epochs = args.epochs
        eval_steps = 500
        save_steps = 500
        logging_steps = 25

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        warmup_steps=50,
        num_train_epochs=epochs,
        gradient_checkpointing=False,  # Not needed with LoRA
        fp16=False,  # Disabled for CPU
        eval_strategy="steps",
        per_device_eval_batch_size=args.batch_size,
        predict_with_generate=True,
        generation_max_length=225,
        save_steps=save_steps,
        eval_steps=eval_steps,
        logging_steps=logging_steps,
        report_to=["wandb"],
        load_best_model_at_end=True,
        metric_for_best_model="wer",
        greater_is_better=False,
        push_to_hub=False,
        remove_unused_columns=False,
        dataloader_num_workers=0,  # Disable multiprocessing for Mac stability
        dataloader_pin_memory=False, # Disable pinned memory for Mac stability
    )

    trainer = Seq2SeqTrainer(
        args=training_args,
        model=model,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        tokenizer=processor.feature_extractor,
    )

    logger.info("Starting training...")
    trainer.train()
    
    logger.info("Evaluating...")
    metrics = trainer.evaluate()
    logger.info(f"Eval metrics: {metrics}")
    
    # Save the model and adapter
    if args.use_lora:
        logger.info(f"Saving LoRA adapters to {args.output_dir}")
        model.save_pretrained(args.output_dir)
    else:
        trainer.save_model()
    
    processor.save_pretrained(args.output_dir)
    
    logger.info(f"Model and processor saved to {args.output_dir}")

if __name__ == "__main__":
    main()
