import re
from collections import Counter
import unicodedata

def analyze_dataset(file_path, num_lines=100000):
    """Analyze character patterns in the dataset."""
    
    # Counters for analysis
    special_chars = Counter()
    line_start_patterns = Counter()
    unicode_categories = Counter()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx >= num_lines:
                break
            
            # Analyze first few characters (potential line numbers)
            first_word = line.split()[0] if line.strip() else ""
            if first_word.isdigit():
                line_start_patterns['LINE_NUMBER'] += 1
            elif first_word.startswith('◆'):
                line_start_patterns['BULLET'] += 1
            elif first_word.startswith('"'):
                line_start_patterns['QUOTE_START'] += 1
            
            # Find all special/non-alphabetic characters
            for char in line:
                # Skip basic alphanumeric and common punctuation
                if not (char.isalnum() or char in ' .,!?;:\n'):
                    special_chars[char] += 1
                    # Get unicode category
                    cat = unicodedata.category(char)
                    unicode_categories[cat] += 1
    
    return special_chars, line_start_patterns, unicode_categories

if __name__ == "__main__":
    file_path = "Train/shona_100K.txt"
    
    print("Analyzing dataset...")
    special_chars, line_starts, unicode_cats = analyze_dataset(file_path)
    
    print("\n" + "="*60)
    print("LINE START PATTERNS")
    print("="*60)
    for pattern, count in line_starts.most_common(10):
        print(f"{pattern:20s}: {count:6d} ({count/1000:.1f}%)")
    
    print("\n" + "="*60)
    print("TOP 30 SPECIAL CHARACTERS")
    print("="*60)
    for char, count in special_chars.most_common(30):
        print(f"'{char}' (U+{ord(char):04X}): {count:6d} - {unicodedata.name(char, 'UNKNOWN')}")
    
    print("\n" + "="*60)
    print("UNICODE CATEGORIES")
    print("="*60)
    for cat, count in unicode_cats.most_common():
        print(f"{cat}: {count:6d}")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    if line_starts.get('LINE_NUMBER', 0) > 50000:
        print("✓ Remove line numbers at start of lines")
    if special_chars.get('◆', 0) > 100:
        print("✓ Handle bullet points (◆)")
    if special_chars.get('"', 0) + special_chars.get('"', 0) + special_chars.get('"', 0) > 1000:
        print("✓ Normalize smart quotes to regular quotes")
    if special_chars.get('—', 0) + special_chars.get('–', 0) > 1000:
        print("✓ Normalize em-dashes and en-dashes to hyphens")
