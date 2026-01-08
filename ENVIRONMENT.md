# Conda Environment Documentation

The 'transformer' environment is the primary environment for running all tasks in this project (ASR, NMT, Text Gen).

## Setup

To recreate this environment:
```bash
conda env create -f transformer_env.yaml
conda activate transformer
```

## Key Packages

- PyTorch 2.x
- Transformers 4.x
- Torchaudio
- PEFT (for LoRA)
- Datasets (Hugging Face)
- JiWER (ASR evaluation)
- Evaluate
- FastAPI & Uvicorn (Web App)
- Supabase (Database & Auth)
