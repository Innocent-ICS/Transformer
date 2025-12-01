import torch
from transformers import WhisperProcessor
from data.afrispeech_loader import AfriSpeechShona
import numpy as np
import os

# Import WhisperDataset from train_asr (copying class definition to avoid importing whole script)
class WhisperDataset(torch.utils.data.Dataset):
    def __init__(self, afrispeech_dataset, processor):
        self.dataset = afrispeech_dataset
        self.processor = processor
        
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        print(f"    [DEBUG] Getting item {idx}")
        sample = self.dataset[idx]
        print(f"    [DEBUG] Loaded sample from dataset")
        
        audio = sample['audio']
        transcription = sample['transcription']
        sample_rate = sample['sample_rate']
        # Convert to tensor
        audio_tensor = torch.from_numpy(audio).float()
        
        # Handle stereo (convert to mono)
        if len(audio_tensor.shape) > 1:
            print(f"    [DEBUG] Converting stereo {audio_tensor.shape} to mono")
            # sf.read returns (samples, channels), we want (samples,)
            audio_tensor = torch.mean(audio_tensor, dim=1)
            print(f"    [DEBUG] Mono shape: {audio_tensor.shape}")
        
        if sample_rate != 16000:
            print(f"    [DEBUG] Resampling from {sample_rate} to 16000")
            import torchaudio
            # torchaudio resample expects (channels, time) or (time,) depending on version/func
            # transforms.Resample expects (..., time)
            # Our tensor is (time,). Let's make it (1, time) for safety or just (time,)
            
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            audio_tensor = resampler(audio_tensor)
            sample_rate = 16000
            print(f"    [DEBUG] Resampled shape: {audio_tensor.shape}")
            
        # Convert back to numpy for processor
        audio = audio_tensor.numpy()
        
        print(f"    [DEBUG] Running processor...")
        input_features = self.processor.feature_extractor(
            audio, sampling_rate=sample_rate
        ).input_features[0]
        print(f"    [DEBUG] Processor done")
        
        labels = self.processor.tokenizer(transcription).input_ids
        
        return {
            "input_features": input_features,
            "labels": labels
        }

def test_data():
    print("Loading processor...")
    processor = WhisperProcessor.from_pretrained("openai/whisper-tiny", language="English", task="transcribe")
    
    print("Loading dataset (subset)...")
    dataset = AfriSpeechShona(data_dir="./data/afrispeech_shona", split="train", subset_size=20)
    print(f"Loaded {len(dataset)} samples")
    
    print("Wrapping dataset...")
    whisper_dataset = WhisperDataset(dataset, processor)
    
    print("Testing __getitem__ for first 5 samples...")
    for i in range(5):
        print(f"Processing sample {i}...")
        item = whisper_dataset[i]
        print(f"  Input features shape: {np.array(item['input_features']).shape}")
        print(f"  Labels length: {len(item['labels'])}")
    
    print("Success!")

if __name__ == "__main__":
    test_data()
