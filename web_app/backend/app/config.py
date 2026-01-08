"""
Model configurations for the application.
"""

MODEL_CONFIGS = [
    {
        "model_id": "translation-final",
        "type": "translation",
        "checkpoint_path": "../../../saved_models/checkpoints/translation-final_best.pth.tar",
        "config": {
            "src_vocab_size": 1950,
            "trg_vocab_size": 2249,
            "d_model": 256,
            "n_layers": 3,
            "heads": 4,
            "dropout": 0.3
        },
        "tokenizer_config": {
            "src_vocab_file": "../../../data/Train/Flores-200/Shona/shona.txt",
            "trg_vocab_file": "../../../data/Train/Flores-200/Shona/english.txt",
            "min_freq": 2
        },
        "metadata": {
            "name": "Shona-English Translation",
            "description": "Translation model trained on 997 sentence pairs",
            "bleu_score": 32.82,
            "direction": "Shona → English",
            "trained_on": "997 samples"
        }
    },
    {
        "model_id": "shona-100K-final",
        "type": "generation",
        "checkpoint_path": "../../../saved_models/checkpoints/shona-100K-final_best.pth.tar",
        "config": {
            "vocab_size": 58227,
            "d_model": 256,
            "n_layers": 3,
            "heads": 4,
            "dropout": 0.3
        },
        "tokenizer_config": {
            "vocab_file": "../../../data/Train/Flores-200/Shona/shona_100K_train.txt",
            "min_freq": 2
        },
        "metadata": {
            "name": "Shona Text Generation (100K)",
            "description": "Autoregressive model trained on 100K Shona sentences",
            "val_loss": 6.347,
            "trained_on": "100K samples",
            "vocabulary_size": "~58K tokens"
        }
    },
    {
        "model_id": "shona-gen-small",
        "type": "generation",
        "checkpoint_path": "../../../saved_models/checkpoints/generation-final_best.pth.tar",
        "config": {
            "vocab_size": 1950,
            "d_model": 256,
            "n_layers": 3,
            "heads": 4,
            "dropout": 0.3
        },
        "tokenizer_config": {
            "vocab_file": "../../../data/Train/Flores-200/Shona/shona.txt",
            "min_freq": 2
        },
        "metadata": {
            "name": "Shona Text Generation (Small)",
            "description": "Autoregressive model trained on 997 Shona sentences",
            "val_loss": 5.115,
            "trained_on": "997 samples",
            "vocabulary_size": "~2K tokens"
        }
    }
]
