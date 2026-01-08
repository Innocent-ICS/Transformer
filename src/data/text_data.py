import torch
from torch.utils.data import Dataset, DataLoader
from collections import Counter
import os
from typing import List, Tuple, Dict
import re

class Tokenizer:
    def __init__(self, min_freq: int = 2):
        self.min_freq = min_freq
        self.vocab = {"<pad>": 0, "<unk>": 1, "<sos>": 2, "<eos>": 3}
        self.reverse_vocab = {0: "<pad>", 1: "<unk>", 2: "<sos>", 3: "<eos>"}
        self.pad_token_id = 0
        self.unk_token_id = 1
        self.sos_token_id = 2
        self.eos_token_id = 3

    def build_vocab(self, texts: List[str]):
        counter = Counter()
        for text in texts:
            tokens = self._tokenize(text)
            counter.update(tokens)
        
        idx = 4
        for token, freq in counter.items():
            if freq >= self.min_freq:
                self.vocab[token] = idx
                self.reverse_vocab[idx] = token
                idx += 1
    
    def _tokenize(self, text: str) -> List[str]:
        # Simple tokenization: lowercase and split by non-alphanumeric
        # Keeping it simple for this assignment, but could be improved
        text = text.lower().strip()
        # Add spaces around punctuation to treat them as tokens
        text = re.sub(r"([?.!,])", r" \1 ", text)
        text = re.sub(r'[" "]+', " ", text)
        return text.split()

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        tokens = self._tokenize(text)
        ids = [self.vocab.get(token, self.unk_token_id) for token in tokens]
        if add_special_tokens:
            ids = [self.sos_token_id] + ids + [self.eos_token_id]
        return ids

    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        tokens = []
        for i in ids:
            token = self.reverse_vocab.get(i, "<unk>")
            if skip_special_tokens and i in [self.pad_token_id, self.sos_token_id, self.eos_token_id]:
                continue
            tokens.append(token)
        return " ".join(tokens)

    def __len__(self):
        return len(self.vocab)

class TranslationDataset(Dataset):
    def __init__(self, src_path: str, trg_path: str, src_tokenizer: Tokenizer, trg_tokenizer: Tokenizer):
        self.src_data = self._read_file(src_path)
        self.trg_data = self._read_file(trg_path)
        assert len(self.src_data) == len(self.trg_data), "Source and target files must have same number of lines"
        
        self.src_tokenizer = src_tokenizer
        self.trg_tokenizer = trg_tokenizer

    def _read_file(self, path: str) -> List[str]:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    def __len__(self):
        return len(self.src_data)

    def __getitem__(self, idx):
        src_text = self.src_data[idx]
        trg_text = self.trg_data[idx]
        
        src_ids = self.src_tokenizer.encode(src_text)
        trg_ids = self.trg_tokenizer.encode(trg_text)
        
        return torch.tensor(src_ids), torch.tensor(trg_ids)

class GenerationDataset(Dataset):
    def __init__(self, path: str, tokenizer: Tokenizer, max_len: int = 128):
        self.data = self._read_file(path)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def _read_file(self, path: str) -> List[str]:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text = self.data[idx]
        ids = self.tokenizer.encode(text)
        # For generation, input is ids[:-1], target is ids[1:]
        # But here we just return the full sequence, slicing happens in training loop or collate
        return torch.tensor(ids)

def collate_fn_translation(batch, pad_idx):
    src_batch, trg_batch = zip(*batch)
    
    src_padded = torch.nn.utils.rnn.pad_sequence(src_batch, padding_value=pad_idx, batch_first=True)
    trg_padded = torch.nn.utils.rnn.pad_sequence(trg_batch, padding_value=pad_idx, batch_first=True)
    
    return src_padded, trg_padded

def collate_fn_generation(batch, pad_idx):
    batch_padded = torch.nn.utils.rnn.pad_sequence(batch, padding_value=pad_idx, batch_first=True)
    return batch_padded

def get_dataloaders(
    train_src: str, train_trg: str, 
    test_src: str, test_trg: str,
    batch_size: int,
    min_freq: int = 2
):
    # Build tokenizers
    src_tokenizer = Tokenizer(min_freq=min_freq)
    trg_tokenizer = Tokenizer(min_freq=min_freq)
    
    with open(train_src, 'r') as f: src_texts = f.readlines()
    with open(train_trg, 'r') as f: trg_texts = f.readlines()
    
    src_tokenizer.build_vocab(src_texts)
    trg_tokenizer.build_vocab(trg_texts)
    
    # Create datasets
    full_dataset = TranslationDataset(train_src, train_trg, src_tokenizer, trg_tokenizer)
    
    # Split train/val (20% val)
    val_size = int(0.2 * len(full_dataset))
    train_size = len(full_dataset) - val_size
    train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])
    
    test_dataset = TranslationDataset(test_src, test_trg, src_tokenizer, trg_tokenizer)
    
    # Create loaders
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, 
        collate_fn=lambda x: collate_fn_translation(x, src_tokenizer.pad_token_id)
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, 
        collate_fn=lambda x: collate_fn_translation(x, src_tokenizer.pad_token_id)
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, 
        collate_fn=lambda x: collate_fn_translation(x, src_tokenizer.pad_token_id)
    )
    
    return train_loader, val_loader, test_loader, src_tokenizer, trg_tokenizer

def get_generation_dataloaders(
    train_path: str, 
    dev_path: str = None,
    test_path: str = None, 
    batch_size: int = 16,
    min_freq: int = 2,
    use_validation_split: bool = True
):
    """
    Get dataloaders for generation task.
    
    Args:
        train_path: Path to training data
        dev_path: Optional path to dev data (if None, uses validation_split from train)
        test_path: Optional path to test data
        batch_size: Batch size
        min_freq: Minimum frequency for vocabulary
        use_validation_split: If True and dev_path is None, split train data 80/20
    """
    tokenizer = Tokenizer(min_freq=min_freq)
    
    with open(train_path, 'r') as f: texts = f.readlines()
    tokenizer.build_vocab(texts)
    
    full_dataset = GenerationDataset(train_path, tokenizer)
    
    # Handle dev set
    if dev_path is not None:
        # Use provided dev set
        train_dataset = full_dataset
        val_dataset = GenerationDataset(dev_path, tokenizer)
    elif use_validation_split:
        # Split train data
        val_size = int(0.2 * len(full_dataset))
        train_size = len(full_dataset) - val_size
        train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])
    else:
        # No validation
        train_dataset = full_dataset
        val_dataset = None
    
    # Handle test set
    if test_path is not None:
        test_dataset = GenerationDataset(test_path, tokenizer)
    else:
        test_dataset = None
    
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, 
        collate_fn=lambda x: collate_fn_generation(x, tokenizer.pad_token_id)
    )
    
    val_loader = None
    if val_dataset is not None:
        val_loader = DataLoader(
            val_dataset, batch_size=batch_size, shuffle=False, 
            collate_fn=lambda x: collate_fn_generation(x, tokenizer.pad_token_id)
        )
    
    test_loader = None
    if test_dataset is not None:
        test_loader = DataLoader(
            test_dataset, batch_size=batch_size, shuffle=False, 
            collate_fn=lambda x: collate_fn_generation(x, tokenizer.pad_token_id)
        )
    
    return train_loader, val_loader, test_loader, tokenizer

