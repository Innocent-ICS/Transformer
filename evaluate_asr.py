import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from peft import PeftModel, PeftConfig
from data.afrispeech_loader import AfriSpeechShona
import jiwer
import numpy as np
from tqdm import tqdm
import logging
import sys

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def evaluate_model(model_dir):
    logger.info(f"Loading model from {model_dir}...")
    # Load base model
    config = PeftConfig.from_pretrained(model_dir)
    model = WhisperForConditionalGeneration.from_pretrained(config.base_model_name_or_path)
    processor = WhisperProcessor.from_pretrained(config.base_model_name_or_path, language="English", task="transcribe")
    
    # Load adapters
    model = PeftModel.from_pretrained(model, model_dir)
    model.eval()
    
    device = "cpu" # Force CPU for Mac
    model.to(device)
    
    logger.info("Loading test dataset...")
    test_dataset = AfriSpeechShona(data_dir="./data/afrispeech_shona", split="test")
    logger.info(f"Test samples: {len(test_dataset)}")
    
    predictions = []
    references = []
    
    logger.info("Starting evaluation...")
    for i in tqdm(range(len(test_dataset))):
        sample = test_dataset[i]
        audio = sample['audio']
        transcription = sample['transcription']
        sample_rate = sample['sample_rate']
        
        # Preprocess audio (mono + resample)
        audio_tensor = torch.from_numpy(audio).float()
        if len(audio_tensor.shape) > 1:
            audio_tensor = torch.mean(audio_tensor, dim=1)
            
        if sample_rate != 16000:
            import torchaudio
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            audio_tensor = resampler(audio_tensor)
            
        input_features = processor(audio_tensor.numpy(), sampling_rate=16000, return_tensors="pt").input_features.to(device)
        
        # Generate
        with torch.no_grad():
            predicted_ids = model.generate(input_features)
            
        transcription_pred = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        
        predictions.append(transcription_pred)
        references.append(transcription)
        
        logger.info(f"\nSample {i+1}:")
        logger.info(f"Ref:  {transcription}")
        logger.info(f"Pred: {transcription_pred}")
        
    # Compute WER
    wer = jiwer.wer(reference=references, hypothesis=predictions)
    logger.info(f"\n{'='*60}")
    logger.info(f"Model: {model_dir}")
    logger.info(f"Final Test WER: {wer * 100:.2f}%")
    logger.info(f"{'='*60}")
    
    return wer * 100

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", type=str, default="./whisper-small-asr-shona-lora", help="Model directory")
    args = parser.parse_args()
    
    evaluate_model(args.model_dir)
