import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
import sacrebleu
import jiwer
from model import make_model
from text_data import get_dataloaders
from utils import load_checkpoint
import argparse
import os

def calculate_metrics(hypotheses, references):
    # BLEU
    bleu = sacrebleu.corpus_bleu(hypotheses, [references])
    
    # WER & CER
    wer = jiwer.wer(references, hypotheses)
    cer = jiwer.cer(references, hypotheses)
    
    return {
        "BLEU": bleu.score,
        "WER": wer,
        "CER": cer
    }

def generate_translation(model, src, src_mask, max_len=50, start_symbol=2, end_symbol=3, device='cpu'):
    memory = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type_as(src.data).long()
    
    for i in range(max_len-1):
        out = model.decode(memory, src_mask, ys, 
                           torch.triu(torch.ones(1, ys.size(1), ys.size(1), device=device), diagonal=1) == 0)
        # print(f"DEBUG: out shape: {out.shape}")
        # out shape should be (batch, seq_len, d_model)
        # prob = model.generator(out[:, -1]) # This was the original error line if out is (1, seq_len, d_model)
        # If out is (1, seq_len, d_model), out[:, -1] is (1, d_model)
        # model.generator expects (batch, d_model) -> (batch, vocab)
        
        # Wait, the error says: input and weight.T shapes cannot be multiplied (1x2249 and 512x2249)
        # 2249 is vocab size? 512 is d_model.
        # So input is (1, 2249)? That means out[:, -1] is ALREADY projected?
        # Let's check model.decode.
        # In model.py:
        # def decode(self, memory, src_mask, tgt, tgt_mask):
        #    return self.generator(self.decoder(self.tgt_embed(tgt), memory, src_mask, tgt_mask))
        # Ah! model.decode ALREADY calls self.generator!
        # So out IS the logits (batch, seq_len, vocab_size).
        
        prob = out[:, -1]
        _, next_word = torch.max(prob, dim=1)

        next_word = next_word.data[0]
        ys = torch.cat([ys, torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=1)
        if next_word == end_symbol:
            break
            
    return ys

def evaluate_test_set(model, loader, src_tokenizer, trg_tokenizer, device):
    model.eval()
    hypotheses = []
    references = []
    
    with torch.no_grad():
        for i, (src, trg) in enumerate(tqdm(loader, desc="Testing")):
            src = src.to(device)
            trg = trg.to(device)
            
            # Greedy decoding for each sentence in batch
            # Note: This is slow for large batches, beam search would be better but this is simple
            for j in range(src.size(0)):
                src_seq = src[j].unsqueeze(0)
                src_mask = (src_seq != 0).unsqueeze(1).unsqueeze(2)
                
                out_seq = generate_translation(
                    model, src_seq, src_mask, 
                    max_len=50, 
                    start_symbol=trg_tokenizer.sos_token_id, 
                    end_symbol=trg_tokenizer.eos_token_id,
                    device=device
                )
                
                pred_text = trg_tokenizer.decode(out_seq[0].tolist(), skip_special_tokens=True)
                ref_text = trg_tokenizer.decode(trg[j].tolist(), skip_special_tokens=True)
                
                hypotheses.append(pred_text)
                references.append(ref_text)
    
    if not hypotheses:
        print("WARNING: No hypotheses generated!")
        return {"BLEU": 0, "WER": 0, "CER": 0}

    metrics = calculate_metrics(hypotheses, references)
    
    print("\nSample Predictions:")
    print("-" * 50)
    for i in range(min(5, len(hypotheses))):
        print(f"Ref:  {references[i]}")
        print(f"Pred: {hypotheses[i]}")
        print("-" * 50)
        
    return metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--batch_size', type=int, default=1) # Batch size 1 for generation simplicity
    parser.add_argument('--d_model', type=int, default=512)
    parser.add_argument('--n_layers', type=int, default=6)
    parser.add_argument('--heads', type=int, default=8)
    parser.add_argument('--dropout', type=float, default=0.1)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
    
    # Data
    _, _, test_loader, src_tokenizer, trg_tokenizer = get_dataloaders(
        'Train/shona.txt', 'Train/english.txt',
        'Test/shona_test.txt', 'Test/english_test.txt',
        args.batch_size
    )
    
    if args.debug:
        from itertools import islice
        test_loader = list(islice(test_loader, 10))

    
    src_vocab_size = len(src_tokenizer)
    trg_vocab_size = len(trg_tokenizer)
    
    # Model
    model = make_model(
        src_vocab_size, trg_vocab_size, 
        N=args.n_layers, d_model=args.d_model, h=args.heads, dropout=args.dropout
    ).to(device)
    
    checkpoint = torch.load(args.checkpoint, map_location=device)
    load_checkpoint(checkpoint, model)
    
    metrics = evaluate_test_set(model, test_loader, src_tokenizer, trg_tokenizer, device)
    
    print("Test Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
