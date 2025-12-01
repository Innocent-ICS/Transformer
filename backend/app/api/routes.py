"""
API routes for the Transformer model server.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.api.schemas import (
    TranslationRequest, TranslationResponse,
    GenerationRequest, GenerationResponse,
    ModelListResponse, ModelDetailResponse, ModelInfo,
    HealthResponse, ErrorResponse
)
from typing import Dict, Any
import soundfile as sf
import io
import numpy as np


router = APIRouter()

# These will be injected by main.py
registry = None
translation_service = None
generation_service = None
asr_service = None


def set_services(reg, trans, gen, asr=None):
    """Set service instances"""
    global registry, translation_service, generation_service, asr_service
    registry = reg
    translation_service = trans
    generation_service = gen
    asr_service = asr


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "device": str(registry.device),
        "loaded_models": len(registry.loaded_models)
    }


@router.get("/models", response_model=ModelListResponse)
async def list_models():
    """List all available models"""
    models_dict = registry.list_models()
    models = [ModelInfo(**model_data) for model_data in models_dict.values()]
    return {"models": models}


@router.get("/models/{model_id}", response_model=ModelDetailResponse)
async def get_model_info(model_id: str):
    """Get detailed information about a specific model"""
    try:
        model_info = registry.get_model_info(model_id)
        return model_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/models/load")
async def load_model(model_id: str):
    """Load a specific model"""
    try:
        registry.load_model(model_id)
        return {"message": f"Model {model_id} loaded successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")


@router.post("/models/unload")
async def unload_model(model_id: str):
    """Unload a specific model to free memory"""
    try:
        registry.unload_model(model_id)
        return {"message": f"Model {model_id} unloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unloading model: {str(e)}")


@router.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """Translate text using the specified model"""
    try:
        result = translation_service.translate(
            text=request.text,
            model_id=request.model_id,
            max_length=request.max_length
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")


@router.post("/generate", response_model=GenerationResponse)
async def generate(request: GenerationRequest):
    """Generate text using the specified model"""
    try:
        result = generation_service.generate(
            prompt=request.prompt,
            model_id=request.model_id,
            max_length=request.max_length,
            temperature=request.temperature
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio to text using Whisper ASR
    
    Args:
        audio: Audio file (supports various formats via soundfile)
        
    Returns:
        JSON with transcription
    """
    if not asr_service:
        raise HTTPException(status_code=503, detail="ASR service not available")
    
    try:
        # Read audio file
        audio_bytes = await audio.read()
        audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
        
        # Transcribe
        transcription = asr_service.transcribe(audio_data=audio_data, sample_rate=sample_rate)
        
        return {
            "transcription": transcription,
            "sample_rate": sample_rate,
            "duration_seconds": len(audio_data) / sample_rate if len(audio_data.shape) == 1 else len(audio_data) / sample_rate,
            "model_used": asr_service.base_model_name
        }
    except Exception as e:
        # Try converting with ffmpeg if direct read fails
        try:
            import subprocess
            print("Direct read failed, trying ffmpeg conversion...")
            
            process = subprocess.Popen(
                ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', '-ac', '1', '-ar', '16000', 'pipe:1'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            wav_bytes, err = process.communicate(input=audio_bytes)
            
            if process.returncode != 0:
                print(f"FFmpeg error: {err.decode()}")
                raise e
            
            audio_data, sample_rate = sf.read(io.BytesIO(wav_bytes))
            
            # Transcribe
            transcription = asr_service.transcribe(audio_data=audio_data, sample_rate=sample_rate)
            
            return {
                "transcription": transcription,
                "sample_rate": sample_rate,
                "duration_seconds": len(audio_data) / sample_rate,
                "model_used": asr_service.base_model_name
            }
        except Exception as ffmpeg_error:
            import traceback
            traceback.print_exc()
            print(f"Error processing audio: {str(e)}")
            print(f"FFmpeg fallback failed: {str(ffmpeg_error)}")
            raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}. FFmpeg required for WebM audio.")
