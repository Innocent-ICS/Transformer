import evaluate
try:
    wer = evaluate.load("wer")
    print("Successfully loaded WER metric")
except Exception as e:
    print(f"Failed to load WER: {e}")

import jiwer
print(f"jiwer version: {jiwer.__version__}")
