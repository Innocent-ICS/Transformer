from datasets import load_dataset

# Try to understand dataset structure
print("Loading dataset metadata...")
dataset = load_dataset("tobiolatunji/afrispeech-200", "all", split="train", streaming=True, trust_remote_code=True)

print("\nChecking first sample structure...")
first_sample = next(iter(dataset))
print("Keys:", first_sample.keys())
print("Accent:", first_sample.get('accent'))
print("Transcript:", first_sample.get('transcript'))
print("Audio keys:", first_sample.get('audio', {}).keys() if isinstance(first_sample.get('audio'), dict) else type(first_sample.get('audio')))
print("\nSearching for Shona samples...")
count = 0
shona_count = 0
for i, sample in enumerate(dataset):
    if 'shona' in sample.get('accent', '').lower() or 'sn' in sample.get('accent', '').lower():
        print(f"Found Shona sample {shona_count + 1}: accent={sample['accent']}, transcript={sample['transcript'][:50]}...")
        shona_count += 1
        if shona_count >= 5:
            break
    count += 1
    if count >= 1000:
        print(f"Checked {count} samples, found {shona_count} Shona samples")
        break

print(f"\nTotal checked: {count}, Shona samples found: {shona_count}")
