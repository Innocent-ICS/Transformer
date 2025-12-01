# Speech-to-Text Integration Guide

## Overview
Speech-to-text functionality has been integrated into the Runyoro frontend using the trained Whisper-Small model (33.13% WER on Shona-accented English).

## Components

### Frontend
1. **SpeechToTextButton** (`frontend/components/SpeechToTextButton.tsx`)
   - Records audio using browser Media Recorder API
   - Sends audio to backend for transcription
   - Displays recording status and errors
   - Integrated into ChatInterface input area

### Backend
1. **WhisperASRService** (`backend/app/models/asr.py`)
   - Loads the trained Whisper model with LoRA adapters
   - Preprocessing: stereo→mono conversion, resampling to 16kHz
   - Transcription using `whisper-small-asr-shona-lora`

2. **API Endpoint** (`/api/transcribe`)
   - Accepts audio files via FormData
   - Returns JSON with transcription and metadata

## Usage

### From Frontend
1. Click the microphone icon in the chat input area
2. Allow microphone access when prompted
3. Speak your message
4. Click the icon again to stop recording
5. The transcription appears in the text input

### API Testing
```bash
# Test endpoint with audio file
curl -X POST http://localhost:8000/api/transcribe \
  -F "audio=@recording.webm" \
  | jq .
```

## Requirements

### Backend Dependencies
Add to `backend/requirements.txt`:
```
transformers>=4.30.0
torch>=2.0.0
torchaudio>=2.0.0
peft>=0.4. 0
soundfile>=0.12.0
```

### Model Files
Required model directory:
- `/whisper-small-asr-shona-lora/` (or fallback to `-tiny-`)

## Running the System

### 1. Backend Server
```bash
cd backend
python -m app.main
```

### 2. Frontend
```bash
cd frontend
npm run dev
```

### 3. Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Configuration

### Audio Settings
The system supports:
- Various audio formats (webm, wav, mp3, etc.)
- Automatic sample rate conversion (to 16kHz)
- Stereo→mono conversion
- Variable audio lengths

### Model Selection
To change the ASR model:
1. Edit `backend/app/main.py`
2. Modify `WhisperASRService(model_dir="path/to/model")`

## Troubleshooting

### Microphone Access Denied
Browser settings → Camera & Microphone → Allow for localhost

### ASR Service Not Available
1. Check model exists: `ls whisper-small-asr-shona-lora/`
2. Check backend logs for initialization errors
3. Verify dependencies installed

### Poor Transcription Quality
Current model trained on medical/technical domain with small dataset
- Expected WER: ~33% on Shona-accented English
- Best performance on medical terminology
- Less accurate on conversational language

## Future Improvements
1. Train on larger, more diverse dataset
2. Use Whisper-Base or Whisper-Medium for better accuracy
3. Add language detection for auto-switching
4. Implement real-time streaming transcription
5. Fine-tune on conversational Shona data
