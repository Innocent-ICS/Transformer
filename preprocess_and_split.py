import re
import random

def clean_text(text):
    """Clean a single line of text."""
    # Remove line number at start (e.g., "1       ")
    text = re.sub(r'^\d+\s+', '', text)
    
    # Normalize smart quotes to regular quotes
    text = text.replace('"', '"').replace('"', '"')  # Smart double quotes
    text = text.replace(''', "'").replace(''', "'")  # Smart single quotes
    
    # Normalize dashes
    text = text.replace('—', '-')  # Em dash
    text = text.replace('–', '-')  # En dash
    
    # Normalize ellipsis
    text = text.replace('…', '...')
    
    # Remove or normalize other special characters
    text = text.replace('◆', '')  # Remove bullet diamond
    text = text.replace('•', '')  # Remove bullet
    
    # Normalize whitespace (including tabs)
    text = ' '.join(text.split())
    
    return text.strip()

def preprocess_and_split(input_file, output_dir='Train', train_ratio=0.8, dev_ratio=0.1, test_ratio=0.1, seed=42):
    """
    Preprocess dataset and split into train/dev/test.
    
    Args:
        input_file: Path to input file
        output_dir: Directory to save output files
        train_ratio: Fraction for training
        dev_ratio: Fraction for development
        test_ratio: Fraction for testing
        seed: Random seed for reproducibility
    """
    assert abs(train_ratio + dev_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
    
    random.seed(seed)
    
    # Read and clean all lines
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    # Clean lines
    print("Cleaning text...")
    cleaned_lines = []
    for idx, line in enumerate(lines):
        cleaned = clean_text(line)
        if cleaned:  # Only keep non-empty lines
            cleaned_lines.append(cleaned)
        
        if (idx + 1) % 10000 == 0:
            print(f"  Processed {idx + 1}/{len(lines)} lines...")
    
    print(f"Non-empty lines after cleaning: {len(cleaned_lines)}")
    
    # Shuffle
    print("Shuffling...")
    random.shuffle(cleaned_lines)
    
    # Split
    n_total = len(cleaned_lines)
    n_train = int(n_total * train_ratio)
    n_dev = int(n_total * dev_ratio)
    
    train_lines = cleaned_lines[:n_train]
    dev_lines = cleaned_lines[n_train:n_train + n_dev]
    test_lines = cleaned_lines[n_train + n_dev:]
    
    print(f"\nSplit sizes:")
    print(f"  Train: {len(train_lines)} ({len(train_lines)/n_total*100:.1f}%)")
    print(f"  Dev:   {len(dev_lines)} ({len(dev_lines)/n_total*100:.1f}%)")
    print(f"  Test:  {len(test_lines)} ({len(test_lines)/n_total*100:.1f}%)")
    
    # Save
    train_file = f"{output_dir}/shona_100K_train.txt"
    dev_file = f"{output_dir}/shona_100K_dev.txt"
    test_file = f"{output_dir}/shona_100K_test.txt"
    
    print(f"\nSaving files...")
    with open(train_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(train_lines))
    print(f"  Saved {train_file}")
    
    with open(dev_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(dev_lines))
    print(f"  Saved {dev_file}")
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(test_lines))
    print(f"  Saved {test_file}")
    
    # Print sample
    print("\n" + "="*60)
    print("SAMPLE FROM TRAIN SET (first 5 lines)")
    print("="*60)
    for i, line in enumerate(train_lines[:5], 1):
        print(f"{i}. {line[:100]}..." if len(line) > 100 else f"{i}. {line}")
    
    return train_file, dev_file, test_file

if __name__ == "__main__":
    input_file = "Train/shona_100K.txt"
    train_file, dev_file, test_file = preprocess_and_split(input_file)
    print("\n✅ Preprocessing and splitting complete!")
