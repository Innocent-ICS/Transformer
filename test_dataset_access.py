from datasets import load_dataset
import torch

try:
    print("Loading AfriSpeech dataset...")
    # Load streaming to avoid downloading everything if it works
    dataset = load_dataset("tobiolatunji/afrispeech-200", "all", split="train", streaming=True, trust_remote_code=True)
    print("Dataset loaded successfully.")
    print(next(iter(dataset)))
except Exception as e:
    print(f"Error loading dataset: {e}")
