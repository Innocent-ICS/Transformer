import torch
import torch.nn as nn
import torch.optim as optim
import wandb
import argparse
import os
from tqdm import tqdm
from model import make_lm_model
from text_data import get_generation_dataloaders
from utils import set_seed, save_checkpoint
from itertools import islice

def train_epoch(model, loader, optimizer, criterion, device, clip=1.0):
    model.train()
    epoch_loss = 0
    
    for i, batch in enumerate(tqdm(loader, desc="Training")):
        batch = batch.to(device)
        
        # Input: <sos> ... <last_token>
        # Target: <first_token> ... <eos>
        
        input_seq = batch[:, :-1]
        target_seq = batch[:, 1:]
        
        # Causal mask
        size = input_seq.size(1)
        mask = torch.triu(torch.ones(size, size), diagonal=1).type_as(input_seq).unsqueeze(0).unsqueeze(0) == 0
        # Also pad mask?
        # Standard mask in Transformer handles both causal and padding if we combine them
        # But here we just use causal mask for simplicity as padding is handled by loss ignore_index
        # Actually we should mask padding positions too to avoid attention to pads
        pad_mask = (input_seq != 0).unsqueeze(1).unsqueeze(2)
        mask = mask & pad_mask
        
        optimizer.zero_grad()
        
        output = model(input_seq, mask)
        
        output_dim = output.shape[-1]
        output = output.contiguous().view(-1, output_dim)
        target_seq = target_seq.contiguous().view(-1)
        
        loss = criterion(output, target_seq)
        loss.backward()
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
        optimizer.step()
        
        epoch_loss += loss.item()
        
    return epoch_loss / len(loader)

def evaluate(model, loader, criterion, device):
    model.eval()
    epoch_loss = 0
    
    with torch.no_grad():
        for i, batch in enumerate(tqdm(loader, desc="Evaluating")):
            batch = batch.to(device)
            
            input_seq = batch[:, :-1]
            target_seq = batch[:, 1:]
            
            size = input_seq.size(1)
            mask = torch.triu(torch.ones(size, size), diagonal=1).type_as(input_seq).unsqueeze(0).unsqueeze(0) == 0
            pad_mask = (input_seq != 0).unsqueeze(1).unsqueeze(2)
            mask = mask & pad_mask
            
            output = model(input_seq, mask)
            
            output_dim = output.shape[-1]
            output = output.contiguous().view(-1, output_dim)
            target_seq = target_seq.contiguous().view(-1)
            
            loss = criterion(output, target_seq)
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
    parser.add_argument('--train_path', type=str, default='Train/shona.txt')
    parser.add_argument('--dev_path', type=str, default=None)
    parser.add_argument('--test_path', type=str, default='Test/shona_test.txt')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--project_name', type=str, default="transformer-shona-generation")
    parser.add_argument('--run_name', type=str, default="gen-run-1")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    set_seed(args.seed)
    
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    
    wandb.init(project=args.project_name, name=args.run_name, config=args)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Data
    train_loader, val_loader, test_loader, tokenizer = get_generation_dataloaders(
        args.train_path, 
        dev_path=args.dev_path,
        test_path=args.test_path,
        batch_size=args.batch_size,
        use_validation_split=(args.dev_path is None)
    )
    
    if args.debug:
        print("Debug mode: using small subset of data")
        args.epochs = 2
        train_loader = list(islice(train_loader, 2))
        val_loader = list(islice(val_loader, 2))
    
    vocab_size = len(tokenizer)
    print(f"Vocab Size: {vocab_size}")
    
    # Model
    model = make_lm_model(
        vocab_size, 
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
