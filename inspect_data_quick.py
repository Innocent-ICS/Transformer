from datasets import load_dataset

try:
    dataset = load_dataset("tobiolatunji/afrispeech-200", "all", split="train", streaming=True, trust_remote_code=True)
    
    print("Checking first 200 samples for accents...")
    accents = set()
    for i, sample in enumerate(dataset):
        accents.add(sample.get('accent', 'unknown'))
        if i >= 200:
            break
            
    print("Accents found:", accents)

except Exception as e:
    print(f"Error: {e}")
