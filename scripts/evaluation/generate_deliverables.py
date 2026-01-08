import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from peft import PeftModel, PeftConfig
from src.data.afrispeech_loader import AfriSpeechShona
import jiwer
import numpy as np
from tqdm import tqdm
import logging
import sys
import argparse
from fpdf import FPDF
import os

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def generate_pdf_report(wer, output_path="results/report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="ASR Model Evaluation Report", ln=1, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Model: Whisper Small + LoRA (Shona)", ln=1)
    pdf.cell(200, 10, txt=f"Test Set: AfriSpeech-200 (Shona)", ln=1)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt=f"Final WER: {wer:.2f}%", ln=1)
    
    pdf.output(output_path)
    logger.info(f"PDF report saved to {output_path}")

def main(model_dir):
    logger.info(f"Loading model from {model_dir}...")
    # Load base model
    config = PeftConfig.from_pretrained(model_dir)
    model = WhisperForConditionalGeneration.from_pretrained(config.base_model_name_or_path)
    processor = WhisperProcessor.from_pretrained(config.base_model_name_or_path, language="English", task="transcribe")
    
    # Load adapters
    model = PeftModel.from_pretrained(model, model_dir)
    model.eval()
    
    device = "cpu" # Force CPU for Mac
    # if torch.cuda.is_available():
    #     device = "cuda"
    # elif torch.backends.mps.is_available():
    #     device = "mps"
        
    model.to(device)
    logger.info(f"Using device: {device}")
    
    logger.info("Loading test dataset...")
    test_dataset = AfriSpeechShona(data_dir="data/Test/AfriSpeech/Shona", split="test")
    logger.info(f"Test samples: {len(test_dataset)}")
    
    predictions = []
    references = []
    filenames = []
    
    # Files to write to
    os.makedirs("results", exist_ok=True)
    txt_file = open("results/ground_truth.txt", "w", encoding="utf-8")
    tsv_file = open("results/transcriptions.tsv", "w", encoding="utf-8")
    
    logger.info("Starting evaluation...")
    for i in tqdm(range(len(test_dataset))):
        sample = test_dataset[i]
        audio = sample['audio']
        transcription = sample['transcription']
        sample_rate = sample['sample_rate']
        filename = sample['filename']
        
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
        filenames.append(filename)
        
        # Write to TXT
        txt_file.write(f"{transcription.strip()}\n{transcription_pred.strip()}\n")
        
        # Write to TSV
        tsv_file.write(f"{filename}\t{transcription_pred.strip()}\n")
        
    txt_file.close()
    tsv_file.close()
    
    # Compute WER
    wer = jiwer.wer(reference=references, hypothesis=predictions) * 100
    logger.info(f"\n{'='*60}")
    logger.info(f"Final Test WER: {wer:.2f}%")
    logger.info(f"{'='*60}")
    
    # Generate PDF
    generate_pdf_report(wer)
    
    logger.info("All deliverables generated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", type=str, default="saved_models/whisper-small-asr-shona-lora", help="Model directory")
    args = parser.parse_args()
    
    main(args.model_dir)
