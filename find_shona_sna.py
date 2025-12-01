from datasets import load_dataset
import collections

print("Loading AfriSpeech dataset...")
dataset = load_dataset("tobiolatunji/afrispeech-200", "all", split="train", streaming=True, trust_remote_code=True)

print("\nSearching for 'sna' accent (Shona ISO code)...")
count = 0
sna_count = 0
accents_found = set()

for i, sample in enumerate(dataset):
    accent = sample.get('accent', '').lower()
    accents_found.add(accent)
    
    # Check for sna, shona, or any variant
    if 'sna' in accent or 'shona' in accent:
        print(f"Found Shona/sna sample {sna_count + 1}:")
        print(f"  Accent: {sample['accent']}")
        print(f"  Transcript: {sample['transcript'][:80]}...")
        print(f"  Country: {sample.get('country', 'N/A')}")
        sna_count += 1
        if sna_count >= 5:
            break
    
    count += 1
    if count >= 5000:  # Check first 5000 samples
        break

print(f"\nChecked {count} samples, found {sna_count} Shona/sna samples")
print(f"\nAll unique accents found in first {count} samples:")
for acc in sorted(accents_found):
    print(f"  - {acc}")
