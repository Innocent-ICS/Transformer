import torch
import argparse
from model import Transformer
from text_data import Tokenizer

def translate_sentence(model, sentence, src_tokenizer, trg_tokenizer, max_length=100, device='cpu'):
    """Translate a sentence using the trained model."""
    model.eval()
    
    # Tokenize source
    src_tokens = src_tokenizer.encode(sentence)
    src_tensor = torch.tensor([src_tokens], dtype=torch.long).to(device)
    
    # Create source mask
    src_mask = (src_tensor != 0).unsqueeze(1).unsqueeze(2)
    
    # Encode source
    with torch.no_grad():
        memory = model.encode(src_tensor, src_mask)
    
    # Start with <sos> token
    trg_tokens = [trg_tokenizer.sos_token_id]
    
    for _ in range(max_length):
        trg_tensor = torch.tensor([trg_tokens], dtype=torch.long).to(device)
        
        # Create target mask (causal)
        size = trg_tensor.size(1)
        trg_mask = (torch.triu(torch.ones(size, size, device=device), diagonal=1) == 0).unsqueeze(0).unsqueeze(0)
        
        with torch.no_grad():
            output = model.decode(trg_tensor, memory, src_mask, trg_mask)
        
        # Get next token (greedy)
        next_token = output.argmax(dim=-1)[0, -1].item()
        
        if next_token == trg_tokenizer.eos_token_id:
            break
        
        trg_tokens.append(next_token)
    
    return trg_tokenizer.decode(trg_tokens)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--direction', type=str, choices=['en2sn', 'sn2en'], default='en2sn',
                       help='Translation direction: en2sn (English to Shona) or sn2en (Shona to English)')
    parser.add_argument('--src_file', type=str, default='Train/english.txt')
    parser.add_argument('--trg_file', type=str, default='Train/shona.txt')
    parser.add_argument('--d_model', type=int, default=256)
    parser.add_argument('--n_layers', type=int, default=3)
    parser.add_argument('--heads', type=int, default=4)
    parser.add_argument('--dropout', type=float, default=0.3)
    args = parser.parse_args()
    
    # Device
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    print(f"Translation direction: {args.direction}\n")
    
    # Load tokenizers
    print("Loading tokenizers...")
    src_tokenizer = Tokenizer(min_freq=2)
    trg_tokenizer = Tokenizer(min_freq=2)
    
    # Determine which is source and which is target based on direction
    if args.direction == 'en2sn':
        # English to Shona (as trained)
        src_file = args.src_file
        trg_file = args.trg_file
    else:
        # Shona to English (reverse)
        src_file = args.trg_file
        trg_file = args.src_file
    
    with open(src_file, 'r') as f:
        src_texts = f.readlines()
    with open(trg_file, 'r') as f:
        trg_texts = f.readlines()
    
    src_tokenizer.build_vocab(src_texts)
    trg_tokenizer.build_vocab(trg_texts)
    
    print(f"Source vocab size: {len(src_tokenizer.vocab)}")
    print(f"Target vocab size: {len(trg_tokenizer.vocab)}")
    
    # Load model
    print("Loading model...")
    from model import make_model
    
    model = make_model(
        len(src_tokenizer.vocab),
        len(trg_tokenizer.vocab),
        N=args.n_layers,
        d_model=args.d_model,
        h=args.heads,
        dropout=args.dropout
    ).to(device)
    
    checkpoint = torch.load(args.checkpoint, map_location=device)
    model.load_state_dict(checkpoint['state_dict'])
    print(f"Loaded checkpoint from epoch {checkpoint['epoch']}\n")
    
    # Test sentences
    if args.direction == 'en2sn':
        test_sentences = [
            "Hello, how are you?",
            "I am going to school.",
            "The weather is nice today.",
            "Thank you very much.",
            "I love my family."
        ]
    else:
        test_sentences = [
            "Mhoro, makadini?",
            "Ndiri kuenda kuchikoro.",
            "Mamiriro ekunze akanaka nhasi.",
            "Ndatenda chaizvo.",
            "Ndinoda mhuri yangu."
        ]
    
    print("="*80)
    print("TRANSLATION EXAMPLES")
    print("="*80)
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n[Example {i}]")
        print(f"Input:  {sentence}")
        
        translation = translate_sentence(
            model, sentence, src_tokenizer, trg_tokenizer,
            max_length=100, device=device
        )
        
        print(f"Output: {translation}")
        print("-" * 80)

if __name__ == "__main__":
    main()
