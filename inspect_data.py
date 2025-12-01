from datasets import load_dataset
import collections

try:
    print("Loading AfriSpeech dataset (streaming)...")
    dataset = load_dataset("tobiolatunji/afrispeech-200", "all", split="train", streaming=True, trust_remote_code=True)
    
    accents = collections.Counter()
    domains = collections.Counter()
    
    print("Inspecting first 5000 samples...")
    for i, sample in enumerate(dataset):
        accents[sample.get('accent', 'unknown')] += 1
        domains[sample.get('domain', 'unknown')] += 1
        if i >= 5000:
            break
            
    print("\nAccents found:")
    for acc, count in accents.most_common():
        print(f"{acc}: {count}")
        
    print("\nDomains found:")
    for dom, count in domains.most_common():
        print(f"{dom}: {count}")

except Exception as e:
    print(f"Error: {e}")
