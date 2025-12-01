import torch
import argparse
from model import LanguageModel
from text_data import Tokenizer

def generate_text(model, tokenizer, prompt, max_length=100, temperature=1.0, device='cpu'):
    """Generate text from a prompt using the language model."""
    model.eval()
    
    # Tokenize prompt
    tokens = tokenizer.encode(prompt)
    input_ids = torch.tensor([tokens], dtype=torch.long).to(device)
    
    generated = tokens.copy()
    
    with torch.no_grad():
        for _ in range(max_length):
            # Create causal mask
            size = input_ids.size(1)
            mask = torch.triu(torch.ones(size, size), diagonal=1).type_as(input_ids).float().unsqueeze(0).unsqueeze(0) == 0
            pad_mask = (input_ids != 0).unsqueeze(1).unsqueeze(2)
            mask = mask & pad_mask
            
            # Get predictions
            output = model(input_ids, mask)
            
            # Get next token probabilities (last position)
            logits = output[:, -1, :] / temperature
            probs = torch.softmax(logits, dim=-1)
            
            # Sample from distribution
            next_token = torch.multinomial(probs, num_samples=1).item()
            
            # Stop if we hit EOS
            if next_token == tokenizer.eos_token_id:
                break
            
            generated.append(next_token)
            
            # Update input (use sliding window if too long)
            if len(generated) > 512:
                input_ids = torch.tensor([generated[-512:]], dtype=torch.long).to(device)
            else:
                input_ids = torch.tensor([generated], dtype=torch.long).to(device)
    
    return tokenizer.decode(generated)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--vocab_file', type=str, default='Train/shona_100K_train.txt')
    parser.add_argument('--d_model', type=int, default=256)
    parser.add_argument('--n_layers', type=int, default=3)
    parser.add_argument('--heads', type=int, default=4)
    parser.add_argument('--dropout', type=float, default=0.3)
    parser.add_argument('--max_length', type=int, default=100)
    parser.add_argument('--temperature', type=float, default=0.8)
    parser.add_argument('--num_samples', type=int, default=5)
    args = parser.parse_args()
    
    # Device
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load tokenizer
    print("Loading tokenizer...")
    tokenizer = Tokenizer(min_freq=2)
    with open(args.vocab_file, 'r') as f:
        texts = f.readlines()
    tokenizer.build_vocab(texts)
    print(f"Vocabulary size: {len(tokenizer.vocab)}")
    
    # Load model
    print("Loading model...")
    from model import make_lm_model
    
    model = make_lm_model(
        len(tokenizer.vocab),
        N=args.n_layers,
        d_model=args.d_model,
        h=args.heads,
        dropout=args.dropout
    ).to(device)
    
    checkpoint = torch.load(args.checkpoint, map_location=device)
    model.load_state_dict(checkpoint['state_dict'])
    print(f"Loaded checkpoint from epoch {checkpoint['epoch']}")
    
    # Generate samples with different prompts
    prompts = [
        "Musi",
        "Ndiri",
        "Zvino",
        "Amai",
        "Munhu"
    ]
    
    print("\n" + "="*80)
    print("GENERATED TEXT SAMPLES")
    print("="*80)
    
    for i, prompt in enumerate(prompts[:args.num_samples], 1):
        print(f"\n[Sample {i}]")
        print(f"Prompt: '{prompt}'")
        print("-" * 80)
        
        generated = generate_text(
            model, tokenizer, prompt, 
            max_length=args.max_length,
            temperature=args.temperature,
            device=device
        )
        
        print(f"Generated: {generated}")
        print("-" * 80)

if __name__ == "__main__":
    main()
