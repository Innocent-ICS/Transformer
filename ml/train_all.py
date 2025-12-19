
import os
import torch
import numpy as np
import argparse
import logging
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Union
import jiwer
from transformers import (
    WhisperProcessor, 
    WhisperForConditionalGeneration, 
    Seq2SeqTrainingArguments, 
    Seq2SeqTrainer
)
from peft import LoraConfig, get_peft_model

# Import loader
from data.multi_accent_loader import MultiAccentLoader

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
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        label_features = [{"input_ids": feature["labels"]} for feature in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels
        return batch

processor = None
def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
    pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)
    wer = 100 * jiwer.wer(reference=label_str, hypothesis=pred_str)
    return {"wer": wer}

class WhisperDatasetWrapper(torch.utils.data.Dataset):
    """Wrapper for HF Dataset to work with WhisperProcessor"""
    def __init__(self, dataset, processor):
        self.dataset = dataset
        self.processor = processor
        
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        item = self.dataset[idx]
        
        # Audio is {'array': ..., 'sampling_rate': ...}
        audio_array = item['audio']['array']
        sr = item['audio']['sampling_rate']
        
        # Transcription
        # Check column name: 'transcript' or 'text'
        transcription = item.get('transcript', item.get('text', ''))
        
        # Processor handles resampling if needed, but we cast to 16k in loader
        input_features = self.processor.feature_extractor(
            audio_array, sampling_rate=sr
        ).input_features[0]
        
        labels = self.processor.tokenizer(transcription).input_ids
        
        return {
            "input_features": input_features,
            "labels": labels
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke_test", action="store_true", help="Run with tiny subset for testing")
    parser.add_argument("--model_name", type=str, default="openai/whisper-small", help="Model identifier")
    parser.add_argument("--output_dir", type=str, default="./whisper-multi-accent", help="Output directory")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size") # 8 fits in 40GB easily with small
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=1e-3)
    
    args = parser.parse_args()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    # Load Processors
    global processor
    processor = WhisperProcessor.from_pretrained(args.model_name, language="English", task="transcribe")
    
    # Load Data
    logger.info("Loading Multi-Accent Data...")
    threshold = 2000 if not args.smoke_test else 50
    # Use max_configs if smoke test?
    
    loader = MultiAccentLoader(threshold=threshold)
    
    # Load Train
    if args.smoke_test:
        loader.configs = loader.configs[:3] # Just 3 accents for smoke test
    
    combined_train = loader.load_all(split="train")
    
    # Split for Eval (validation)
    # Since we combined everything, we can split 90/10 or similar
    # Or load 'dev' split if AfriSpeech has it (it does).
    # But frugal loading on 'dev' too?
    # Simpler: just split the train set if dev is large.
    # Actually, iterate configs for dev too?
    # Let's just do a random split on combined train for simplicity in this pipeline test.
    
    split_ds = combined_train.train_test_split(test_size=0.05, seed=42)
    train_ds_raw = split_ds['train']
    eval_ds_raw = split_ds['test']
    

    
    if args.smoke_test:
        train_ds_raw = train_ds_raw.select(range(50))
        eval_ds_raw = eval_ds_raw.select(range(10))
    
    # FILTERING: Remove samples where label length > 448
    def is_audio_in_length_range(item):
        input_ids = processor.tokenizer(item.get('transcript', item.get('text', ''))).input_ids
        return len(input_ids) < 448

    logger.info("Filtering training data for length...")
    train_ds_raw = train_ds_raw.filter(is_audio_in_length_range, num_proc=4)
    logger.info("Filtering eval data for length...")
    eval_ds_raw = eval_ds_raw.filter(is_audio_in_length_range, num_proc=4)
    
    logger.info(f"Training samples: {len(train_ds_raw)}")
    logger.info(f"Eval samples: {len(eval_ds_raw)}")
    
    train_dataset = WhisperDatasetWrapper(train_ds_raw, processor)
    eval_dataset = WhisperDatasetWrapper(eval_ds_raw, processor)
    

    # Model
    model = WhisperForConditionalGeneration.from_pretrained(args.model_name)
    model.config.forced_decoder_ids = None
    model.config.suppress_tokens = []
    
    # Crucial for LoRA + Gradient Checkpointing
    model.enable_input_require_grads()
    model.gradient_checkpointing_enable() 
    model.config.use_cache = False
    
    # LoRA
    lora_config = LoraConfig(
        r=32, 
        lora_alpha=64, 
        target_modules=["q_proj", "v_proj"], 
        lora_dropout=0.05, 
        bias="none"
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Trainer
    data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)
    
    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=1,
        learning_rate=args.lr,
        warmup_steps=50, # small warmup
        num_train_epochs=args.epochs if not args.smoke_test else 1,
        max_steps=10 if args.smoke_test else -1, # Limit steps for smoke test

        gradient_checkpointing=True,
        fp16=True,
        eval_strategy="steps",
        per_device_eval_batch_size=args.batch_size,
        predict_with_generate=True,
        generation_max_length=225,
        save_steps=500,
        eval_steps=500,
        logging_steps=50,
        report_to=["tensorboard"],
        load_best_model_at_end=True,
        metric_for_best_model="wer",
        greater_is_better=False,
        dataloader_num_workers=4,
        remove_unused_columns=False
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
    
    # Save
    model.save_pretrained(args.output_dir)
    processor.save_pretrained(args.output_dir)
    logger.info(f"Saved to {args.output_dir}")

if __name__ == "__main__":
    main()
