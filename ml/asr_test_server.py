"""
Standalone ASR test server for speech-to-text testing
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import soundfile as sf
import io
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from peft import PeftModel, PeftConfig
import torchaudio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ASR Test Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global ASR service
asr_model = None
asr_processor = None
asr_base_model_name = None

def load_asr_model(model_dir="./whisper-small-asr-shona-lora"):
    """Load Whisper ASR model"""
    global asr_model, asr_processor, asr_base_model_name
    
    try:
        # Load config and base model
        config = PeftConfig.from_pretrained(model_dir)
        asr_base_model_name = config.base_model_name_or_path
        
        # Load processor
        asr_processor = WhisperProcessor.from_pretrained(
            asr_base_model_name,
            language="English",
            task="transcribe"
        )
        
        # Load model with adapters
        base_model = WhisperForConditionalGeneration.from_pretrained(asr_base_model_name)
        asr_model = PeftModel.from_pretrained(base_model, model_dir)
        asr_model.eval()
        asr_model.to("cpu")
        
        logger.info(f"✅ ASR model loaded: {asr_base_model_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load ASR model: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_asr_model()

@app.get("/")
async def root():
    return {
        "message": "ASR Test Server",
        "status": "running" if asr_model else "model_not_loaded",
        "model": asr_base_model_name
    }

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio to text"""
    if not asr_model:
        raise HTTPException(status_code=503, detail="ASR model not loaded")
    
    try:
        # Read audio
        audio_bytes = await audio.read()
        audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
        
        # Preprocess
        audio_tensor = torch.from_numpy(audio_data).float()
        
        # Handle stereo
        if len(audio_tensor.shape) > 1:
            audio_tensor = torch.mean(audio_tensor, dim=-1)
            
        # Resample
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            audio_tensor = resampler(audio_tensor)
            
        # Get features
        input_features = asr_processor(
            audio_tensor.numpy(),
            sampling_rate=16000,
            return_tensors="pt"
        ).input_features
        
        # Transcribe
        with torch.no_grad():
            predicted_ids = asr_model.generate(input_features)
            
        transcription = asr_processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        
        logger.info(f"Transcription: {transcription}")
        
        return {
            "transcription": transcription,
            "sample_rate": sample_rate,
            "model_used": asr_base_model_name
        }
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("asr_test_server:app", host="0.0.0.0", port=8000, reload=False)
