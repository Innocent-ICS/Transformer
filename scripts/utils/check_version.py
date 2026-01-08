
import transformers
print(f"Transformers version: {transformers.__version__}")
try:
    import whisper
    print(f"OpenAI Whisper version: {whisper.__version__}")
except ImportError:
    print("OpenAI Whisper package (openai-whisper) not installed.")
