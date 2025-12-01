"""
Whisper ASR Service for Shona-accented English
"""
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from peft import PeftModel, PeftConfig
import torchaudio
import numpy as np
from pathlib import Path


class WhisperASRService:
    """Service for speech-to-text using trained Whisper model"""
    
    def __init__(self, model_dir: str = "./whisper-small-asr-shona-lora", device: str = "cpu"):
        """
        Initialize the ASR service with a trained Whisper model
        
        Args:
            model_dir: Path to the LoRA model directory
            device: Device to run inference on ('cpu', 'cuda', 'mps')
        """
        self.device = device
        self.model_dir = Path(model_dir)
        
        # Check current and parent directories
        if not self.model_dir.exists():
            # Try parent directory
            parent_dir = Path("..") / self.model_dir
            if parent_dir.exists():
                self.model_dir = parent_dir
            else:
                # Fallback to tiny model
                alt_dir = Path("./whisper-asr-shona-lora")
                if not alt_dir.exists():
                    alt_dir = Path("../whisper-asr-shona-lora")
                
                if alt_dir.exists():
                    self.model_dir = alt_dir
                else:
                    raise ValueError(f"Model directory not found: {model_dir}")
        
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model with LoRA adapters"""
        # Load config and base model
        config = PeftConfig.from_pretrained(str(self.model_dir))
        self.base_model_name = config.base_model_name_or_path
        
        # Load processor
        self.processor = WhisperProcessor.from_pretrained(
            self.base_model_name,
            language="English",
            task="transcribe"
        )
        
        # Load model with adapters
        base_model = WhisperForConditionalGeneration.from_pretrained(self.base_model_name)
        self.model = PeftModel.from_pretrained(base_model, str(self.model_dir))
        self.model.eval()
        self.model.to(self.device)
        
    def preprocess_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Preprocess audio data for Whisper
        
        Args:
            audio_data: Audio array (can be stereo or mono)
            sample_rate: Sample rate of the audio
            
        Returns:
            Preprocessed mono 16kHz audio
        """
        # Convert to tensor
        audio_tensor = torch.from_numpy(audio_data).float()
        
        # Handle stereo (convert to mono)
        if len(audio_tensor.shape) > 1:
            audio_tensor = torch.mean(audio_tensor, dim=-1)  # Average channels
            
        # Resample to 16kHz if needed
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            audio_tensor = resampler(audio_tensor)
            
        return audio_tensor.numpy()
    
    def transcribe(self, audio_path: str=None, audio_data: np.ndarray=None, sample_rate: int=16000) -> str:
        """
        Transcribe audio to text
        
        Args:
            audio_path: Path to audio file (optional)
            audio_data: Audio numpy array (optional)
            sample_rate: Sample rate if providing audio_data
            
        Returns:
            Transcribed text
        """
        if audio_path:
            # Load from file
            import soundfile as sf
            audio_data, sample_rate = sf.read(audio_path)
        elif audio_data is None:
            raise ValueError("Must provide either audio_path or audio_data")
        
        # Preprocess
        audio = self.preprocess_audio(audio_data, sample_rate)
        
        # Get input features
        input_features = self.processor(
            audio,
            sampling_rate=16000,
            return_tensors="pt"
        ).input_features.to(self.device)
        
        # Generate transcription
        with torch.no_grad():
            predicted_ids = self.model.generate(input_features)
            
        # Decode
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        
        return transcription
