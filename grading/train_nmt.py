import torch
import torch.nn as nn
import torch.optim as optim
import wandb
import argparse
import os
from tqdm import tqdm
from model import make_model
from text_data import get_dataloaders
from utils import set_seed, save_checkpoint

def train_epoch(model, loader, optimizer, criterion, device, clip=1.0):
    model.train()
    epoch_loss = 0
    
    for i, (src, trg) in enumerate(tqdm(loader, desc="Training")):
        src = src.to(device)
        trg = trg.to(device)
        
        # trg input is <sos> ... <eos>
        # trg_input is <sos> ... <last_token> (exclude eos for input)
        # trg_output is <first_token> ... <eos> (exclude sos for target)
        
        trg_input = trg[:, :-1]
        trg_output = trg[:, 1:]
        
        src_mask = (src != 0).unsqueeze(1).unsqueeze(2) # (batch, 1, 1, src_len)
        trg_mask = (trg_input != 0).unsqueeze(1).unsqueeze(3) # (batch, 1, trg_len, 1)
        
        # Create causal mask for target
        size = trg_input.size(1)
        nopeak_mask = torch.triu(torch.ones(1, size, size), diagonal=1).type_as(src_mask) == 0
        trg_mask = trg_mask & nopeak_mask
        
        optimizer.zero_grad()
        
        output = model(src, trg_input, src_mask, trg_mask)
        
        # Reshape for loss
        output_dim = output.shape[-1]
        output = output.contiguous().view(-1, output_dim)
        trg_output = trg_output.contiguous().view(-1)
        
        loss = criterion(output, trg_output)
        loss.backward()
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
        optimizer.step()
        
        epoch_loss += loss.item()
        
    return epoch_loss / len(loader)

def evaluate(model, loader, criterion, device):
    model.eval()
    epoch_loss = 0
    
    with torch.no_grad():
        for i, (src, trg) in enumerate(tqdm(loader, desc="Evaluating")):
            src = src.to(device)
            trg = trg.to(device)
            
            trg_input = trg[:, :-1]
            trg_output = trg[:, 1:]
            
            src_mask = (src != 0).unsqueeze(1).unsqueeze(2)
            trg_mask = (trg_input != 0).unsqueeze(1).unsqueeze(3)
            size = trg_input.size(1)
            nopeak_mask = torch.triu(torch.ones(1, size, size), diagonal=1).type_as(src_mask) == 0
            trg_mask = trg_mask & nopeak_mask
            
            output = model(src, trg_input, src_mask, trg_mask)
            
            output_dim = output.shape[-1]
            output = output.contiguous().view(-1, output_dim)
            trg_output = trg_output.contiguous().view(-1)
            
            loss = criterion(output, trg_output)
            epoch_loss += loss.item()
            
    return epoch_loss / len(loader)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=0.0001)
    parser.add_argument('--d_model', type=int, default=256)
    parser.add_argument('--n_layers', type=int, default=3)
    parser.add_argument('--heads', type=int, default=4)
    parser.add_argument('--dropout', type=float, default=0.3)
    parser.add_argument('--label_smoothing', type=float, default=0.1)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--project_name', type=str, default="transformer-shona-english")
    parser.add_argument('--run_name', type=str, default="run-1")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    set_seed(args.seed)
    
    # Load env for wandb api key
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    
    wandb.init(project=args.project_name, name=args.run_name, config=args)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Data
    train_loader, val_loader, test_loader, src_tokenizer, trg_tokenizer = get_dataloaders(
        'Train/shona.txt', 'Train/english.txt',
        'Test/shona_test.txt', 'Test/english_test.txt',
        args.batch_size
    )

    if args.debug:
        print("Debug mode: using small subset of data")
        args.epochs = 2
        # Limit loaders to 2 batches
        from itertools import islice
        train_loader = islice(train_loader, 2)
        val_loader = islice(val_loader, 2)
        # We need to wrap them back into something that has len() if we use len(loader)
        # But our train_epoch uses len(loader) for normalization.
        # Let's just hack the len() or handle it in the loop.
        # Easier: just don't use len(loader) in train_epoch if it's an iterator.
        # But tqdm needs len.
        # Let's just create a list
        train_loader = list(islice(train_loader, 2))
        val_loader = list(islice(val_loader, 2))


    
    src_vocab_size = len(src_tokenizer)
    trg_vocab_size = len(trg_tokenizer)
    
    print(f"Src Vocab: {src_vocab_size}, Trg Vocab: {trg_vocab_size}")
    
    # Model
    model = make_model(
        src_vocab_size, trg_vocab_size, 
        N=args.n_layers, d_model=args.d_model, h=args.heads, dropout=args.dropout
    ).to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=args.lr, betas=(0.9, 0.98), eps=1e-9)
    criterion = nn.CrossEntropyLoss(ignore_index=0, label_smoothing=args.label_smoothing)
    
    best_valid_loss = float('inf')
    
    for epoch in range(args.epochs):
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device)
        valid_loss = evaluate(model, val_loader, criterion, device)
        
        wandb.log({
            "train_loss": train_loss,
            "valid_loss": valid_loss,
            "epoch": epoch
        })
        
        print(f'Epoch: {epoch+1:02} | Train Loss: {train_loss:.3f} | Val. Loss: {valid_loss:.3f}')
        
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            save_checkpoint({
                'epoch': epoch + 1,
                'state_dict': model.state_dict(),
                'optimizer': optimizer.state_dict(),
                'loss': valid_loss,
            }, filename=f"checkpoints/{args.run_name}_best.pth.tar")
            
    wandb.finish()

if __name__ == "__main__":
    if not os.path.exists("checkpoints"):
        os.makedirs("checkpoints")
    main()
