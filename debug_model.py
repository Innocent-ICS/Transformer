import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from peft import LoraConfig, get_peft_model
import numpy as np
import os

# Disable W&B
os.environ["WANDB_DISABLED"] = "true"

def test_model():
    print("Loading processor...")
    processor = WhisperProcessor.from_pretrained("openai/whisper-tiny", language="English", task="transcribe")
    
    print("Loading model...")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
    
    print("Applying LoRA...")
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    print("Creating dummy input...")
    # Dummy audio: 1 second of silence at 16kHz
    dummy_audio = np.zeros(16000)
    input_features = processor(dummy_audio, sampling_rate=16000, return_tensors="pt").input_features
    
    # Dummy labels
    dummy_labels = torch.tensor([[50258, 50259, 50359]]) # <|startoftranscript|><|en|><|transcribe|>
    
    print("Running forward pass...")
    outputs = model(input_features=input_features, labels=dummy_labels)
    print(f"Loss: {outputs.loss}")
    
    print("Success!")

if __name__ == "__main__":
    test_model()
