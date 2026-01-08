import torch
import argparse
from model import make_model
from text_data import Tokenizer

def translate_sentence_simple(model, sentence, src_tokenizer, trg_tokenizer, max_length=100, device='cpu'):
    """Translate using same approach as evaluate.py"""
    model.eval()
    
    # Tokenize
    src_ids = torch.LongTensor([src_tokenizer.encode(sentence)]).to(device)
    
    # Source mask
    src_mask = (src_ids != 0).unsqueeze(1).unsqueeze(2)
    
    # Encode
    with torch.no_grad():
        memory = model.encode(src_ids, src_mask)
    
    # Start with <sos>
    ys = torch.ones(1, 1).fill_(trg_tokenizer.sos_token_id).type_as(src_ids)
    
    for _ in range(max_length):
        # Decode with causal mask (exact same as evaluate.py)
        with torch.no_grad():
            out = model.decode(memory, src_mask, ys,
                              torch.triu(torch.ones(1, ys.size(1), ys.size(1), device=device), diagonal=1) == 0)
        
        prob = out[:, -1]
        _, next_word = torch.max(prob, dim=1)
        next_word = next_word.data[0]
        
        if next_word == trg_tokenizer.eos_token_id:
            break
            
        ys = torch.cat([ys, torch.ones(1, 1).type_as(src_ids).fill_(next_word)], dim=1)
    
    return trg_tokenizer.decode(ys[0].tolist())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--src_file', type=str, default='Train/shona.txt')
    parser.add_argument('--trg_file', type=str, default='Train/english.txt')
    parser.add_argument('--d_model', type=int, default=256)
    parser.add_argument('--n_layers', type=int, default=3)
    parser.add_argument('--heads', type=int, default=4)
    parser.add_argument('--dropout', type=float, default=0.3)
    args = parser.parse_args()
    
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}\n")
    
    # Load tokenizers (Shona = source, English = target)
    print("Loading tokenizers...")
    src_tokenizer = Tokenizer(min_freq=2)
    trg_tokenizer = Tokenizer(min_freq=2)
    
    with open(args.src_file, 'r') as f:
        src_texts = f.readlines()
    with open(args.trg_file, 'r') as f:
        trg_texts = f.readlines()
    
    src_tokenizer.build_vocab(src_texts)
    trg_tokenizer.build_vocab(trg_texts)
    
    print(f"Shona vocab: {len(src_tokenizer.vocab)}")
    print(f"English vocab: {len(trg_tokenizer.vocab)}\n")
    
    # Load model
    print("Loading model...")
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
    print(f"Loaded from epoch {checkpoint['epoch']}\n")
    
    # Test translations (Shona → English)
    test_sentences = [
        "Ndiri kuenda kuchikoro.",
        "Mamiriro ekunze akanaka nhasi.",
        "Ndinoda mhuri yangu.",
        "Mhoro, makadini?",
        "Ndatenda chaizvo."
    ]
    
    print("="*80)
    print("SHONA → ENGLISH TRANSLATION")
    print("="*80)
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n[Example {i}]")
        print(f"Shona:   {sentence}")
        
        translation = translate_sentence_simple(
            model, sentence, src_tokenizer, trg_tokenizer,
            max_length=100, device=device
        )
        
        print(f"English: {translation}")
        print("-" * 80)

if __name__ == "__main__":
    main()
