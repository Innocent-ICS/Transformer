# Runyoro: Shona Language AI Platform

## Abstract

Runyoro is a comprehensive AI platform designed to bridge the digital divide for the Shona language. This project implements state-of-the-art Natural Language Processing (NLP) techniques, including Transformer-based Neural Machine Translation (NMT), Autoregressive Text Generation, and Automatic Speech Recognition (ASR). The system features a modern web interface that allows users to translate text between Shona and English, generate creative Shona text, and transcribe spoken Shona-accented English.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Methodology and Results](#methodology-and-results)
    - [Neural Machine Translation](#neural-machine-translation)
    - [Text Generation](#text-generation)
    - [Automatic Speech Recognition](#automatic-speech-recognition)
4. [Project Structure](#project-structure)

---

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Supabase Account (for authentication and database)

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd application/backend
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure environment variables:
    Create a `.env` file in the `application/backend` directory with the following configuration:
    ```env
    JWT_SECRET_KEY=your_secure_secret_key
    JWT_ALGORITHM=HS256
    JWT_EXPIRATION_HOURS=24
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_anon_key
    ALLOWED_ORIGINS=http://localhost:3000
    ```

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd application/frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Configure environment variables:
    Create a `.env.local` file in the `application/frontend` directory:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000/api
    ```

---

## Usage

### Running the Application

1.  **Start the Backend Server**:
    ```bash
    cd application/backend
    source venv/bin/activate
    python -m app.main
    ```
    The API will be available at `http://localhost:8000`.

2.  **Start the Frontend Application**:
    ```bash
    cd application/frontend
    npm run dev
    ```
    Access the web interface at `http://localhost:3000`.

### Features

-   **Translation**: Enter text in Shona to translate it to English. The system uses a custom-trained Transformer model.
-   **Text Generation**: Provide a prompt in Shona to generate coherent text continuations.
-   **Speech-to-Text**: Use the microphone input to transcribe spoken audio. The system utilizes a fine-tuned Whisper model optimized for Shona-accented English.

---

## Methodology and Results

### Neural Machine Translation

We trained a Transformer model from scratch for Shona-English translation.

-   **Architecture**: Transformer (d_model=256, n_layers=3, heads=4)
-   **Dataset**: 997 bilingual samples
-   **Performance**:
    -   BLEU Score: 32.82%
    -   Word Error Rate (WER): 0.697
    -   Character Error Rate (CER): 0.576

The model demonstrates the capability to learn basic translation patterns despite the limited dataset size. It is currently optimized for Shona to English translation.

### Text Generation

Two autoregressive models were trained for Shona text generation:

1.  **Small Model**: Trained on 997 samples.
2.  **Large Model**: Trained on a dataset of 100,000 Shona sentences.

**Results (Large Model)**:
-   Validation Loss: 6.347
-   The model produces grammatically correct and coherent Shona text, demonstrating successful scaling to larger datasets without overfitting.

### Automatic Speech Recognition

We fine-tuned OpenAI's Whisper models using Low-Rank Adaptation (LoRA) on the AfriSpeech-200 Shona dataset.

-   **Dataset**: 138 samples of Shona-accented English (Medical/Technical domain).
-   **Best Model**: Whisper-Small + LoRA
-   **Performance**:
    -   Word Error Rate (WER): 33.13%
    -   Improvement over baseline RNN: 66.87 percentage points

The use of transfer learning with LoRA proved highly effective for this low-resource ASR task, significantly outperforming traditional RNN approaches.

---

## Project Structure

```
.
├── ml/                      # Machine Learning workflow
│   ├── checkpoints/         # Model checkpoints
│   ├── data/                # Data loading and split scripts
│   ├── Train/               # Training data (CSV/Audio)
│   ├── Test/                # Test data
│   ├── whisper-asr-shona*/  # Fine-tuned Whisper models
│   ├── train_all.py         # Main training orchestrator
│   ├── train_asr.py         # ASR specific training script
│   ├── train_gen.py         # Text generation training script
│   └── ...                  # Other utility scripts (model.py, utils.py)
├── application/             # Full Stack Application
│   ├── backend/             # FastAPI Backend
│   │   ├── app/             # Application source code
│   │   └── requirements.txt # Python dependencies
│   └── frontend/            # Next.js React Frontend (UI)
├── generate_deliverables.py # Evaluation script: Generates WER report, TSV, and TXT
├── evaluate_asr.py          # Quick ASR Model Evaluator (WER calculation)
├── run_remote.py            # Utility to execute scripts on remote GPU servers via JupyterHub
├── check_logs.py            # Utility to tail logs of running training jobs
├── run_training_job.py      # Background job runner for long-running training tasks
└── README.md                # Project Documentation
```

## Scripts Description

-   **`generate_deliverables.py`**: Runs evaluation on the test set using the fine-tuned model and generates the project deliverables (PDF report, `transcriptions.tsv`, `ground_truth.txt`).
-   **`evaluate_asr.py`**: A standalone script to calculate WER for a given model checkpoint against the test set.
-   **`run_remote.py`**: automating remote execution. Uploads scripts to the university compute cluster, executes them, and streams input/output via WebSocket.
-   **`check_logs.py`**: Helps monitor long-running remote training jobs by tailing their log files.
-   **`run_training_job.py`**: Wraps the training script execution to run in the background (nohup) on remote servers.
