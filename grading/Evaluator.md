# Evaluator Guide to Core Files

This directory contains the essential implementation files for the project, separated into "From Scratch" implementations and "Fine-tuning" scripts.

## 1. Transformer from Scratch (NMT & Text Generation)

These files implement the Transformer architecture and training loops without using high-level trainer abstractions or pre-built model libraries like standard Hugging Face components (except for tokenization utilities).

*   **`model.py`**
    *   **Description**: The core file containing the **Transformer architecture implemented from scratch** using PyTorch.
    *   **Key Components**:
        *   `MultiHeadAttention`: Manual implementation of Scaled Dot-Product Attention.
        *   `EncoderLayer` / `DecoderLayer`: The building blocks of the Transformer.
        *   `Transformer`: The full Encoder-Decoder model used for Machine Translation.
        *   `LanguageModel`: A Decoder-only adaptation used for Text Generation.
        *   `PositionalEncoding`: Sinusoidal positional embeddings.

*   **`train_nmt.py`** (Original: `ml/train.py`)
    *   **Description**: The training script for the **Neural Machine Translation (NMT)** task.
    *   **Functionality**: It initializes the `Transformer` from `model.py` and trains it on the parallel Shona-English dataset. It implements the training loop, loss calculation (`CrossEntropyLoss`), and evaluation logic explicitly.

*   **`train_text_gen.py`** (Original: `ml/train_gen.py`)
    *   **Description**: The training script for the **Autoregressive Text Generation** task.
    *   **Functionality**: It uses the `LanguageModel` (decoder-only Transformer) from `model.py`. It trains the model to predict the next token in a Shona sentence, implementing a causal mask to prevent peeking at future tokens.

*   **`text_data.py`**
    *   **Description**: Data preprocessing utilities for the scratch models.
    *   **Functionality**: Handles tokenization, vocabulary building, and batching for both NMT and Text Generation tasks.

## 2. Fine-Tuning (Automatic Speech Recognition)

These files leverage Transfer Learning by fine-tuning a pre-trained state-of-the-art model.

*   **`train_asr_finetune.py`** (Original: `ml/train_asr.py`)
    *   **Description**: The script for fine-tuning **OpenAI's Whisper** model for Shona ASR.
    *   **Methodology**: Uses **LoRA (Low-Rank Adaptation)** via the `peft` library to efficiently fine-tune the model parameters on a small dataset. It utilizes Hugging Face's `Seq2SeqTrainer` for the training loop.

*   **`afrispeech_loader.py`**
    *   **Description**: Custom data loader.
    *   **Functionality**: Loads and processes the AfriSpeech audio dataset, handling audio resampling and text normalization for the ASR task.
