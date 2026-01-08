# Runyoro: Shona Language AI Platform

## Abstract

Runyoro is a comprehensive AI platform designed to bridge the digital divide for the Shona language. This project implements state-of-the-art Natural Language Processing (NLP) techniques, including Transformer-based Neural Machine Translation (NMT), Autoregressive Text Generation, and Automatic Speech Recognition (ASR). The system features a modern web interface that allows users to translate text between Shona and English, generate creative Shona text, and transcribe spoken Shona-accented English.

## Table of Contents

1. [Installation](#installation)
2. [Project Structure](#project-structure)
3. [Usage](#usage)
4. [Methodology and Results](#methodology-and-results)

---

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Supabase Account (for authentication and database)

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd web_app/backend
    ```

2.  Activate the project environment:
    ```bash
    conda activate transformer
    ```

    *If you haven't set up the environment yet, refer to [ENVIRONMENT.md](ENVIRONMENT.md).*

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd web_app/frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

---

## Project Structure

The project has been organized to ensure distinct separation of concerns between source code, data, models, and the web application.

```
.
├── src/                     # Core Source Code
│   ├── data/                # Data loaders (AfriSpeech, Text)
│   ├── models/              # Model definitions (Transformer, etc.)
│   ├── training/            # Training scripts for all modalities
│   ├── inference/           # Inference scripts for generation/translation
│   ├── evaluation/          # Evaluation metrics and tools
│   └── utils/               # Common utilities (seed, checkpoints)
├── data/                    # Dataset storage
│   ├── Train/               # Training Datasets
│   │   ├── AfriSpeech/      # ASR Data (Shona)
│   │   └── Flores-200/      # Translation/Gen Data (Shona/English)
│   ├── Test/                # Test Datasets
│   │   ├── AfriSpeech/      # ASR Data (Shona)
│   │   └── Flores-200/      # Translation/Gen Data (Shona/English)
├── saved_models/            # Trained model artifacts and checkpoints
│   ├── checkpoints/         # Training checkpoints
│   └── whisper-*/           # Fine-tuned Whisper models
├── scripts/                 # Utility and Runner Scripts
│   ├── train/               # Scripts to launch training jobs
│   ├── evaluation/          # Scripts to generate deliverables
│   └── utils/               # Log checkers and maintenance scripts
├── web_app/                 # Full Stack Web Application
│   ├── backend/             # FastAPI Backend
│   └── frontend/            # Next.js Frontend
├── results/                 # Evaluation outputs (PDFs, TSVs)
└── legacy/                  # Archived previous versions and grading files
```

---

## Usage

### Training Models

All training scripts are located in `src/training/` and should be executed from the project root.

**1. Neural Machine Translation (NMT)**
```bash
python src/training/train_nmt.py --epochs 10 --batch_size 16
```

**2. Text Generation (Shona)**
```bash
python src/training/train_gen.py --epochs 10 --batch_size 16
```

**3. Automatic Speech Recognition (ASR - Whisper)**
```bash
python src/training/train_asr.py --use_lora
```
Or use the runner script for background execution:
```bash
python scripts/train/run_training_job.py
```

### Evaluation

To generate the final deliverables (PDF report, Transcriptions TSV, Ground Truth TXT):

```bash
python scripts/evaluation/generate_deliverables.py
```
Outputs will be saved in the project root or specified output directory.

### Inference

**Generate Text:**
```bash
python src/inference/generate_samples.py --checkpoint saved_models/checkpoints/gen-run-1_best.pth.tar
```

---

## Methodology and Results

### Neural Machine Translation
We trained a Transformer model from scratch for Shona-English translation.
-   **Architecture**: Transformer (d_model=256, n_layers=3, heads=4)
-   **Performance**: BLEU Score: 32.82%, WER: 0.697

### Text Generation
Autoregressive models trained for Shona text generation.
-   **Large Model**: Trained on 100,000 sentences.
-   **Result**: Coherent Shona text generation with low validation loss.

### Automatic Speech Recognition
Fine-tuned OpenAI's Whisper models using LoRA on the AfriSpeech-200 Shona dataset.
-   **Performance**: WER: 33.13% (Significant improvement over baseline).
