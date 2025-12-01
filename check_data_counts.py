from data.afrispeech_loader import AfriSpeechShona

def check_counts():
    print("Checking dataset counts...")
    
    splits = ['train', 'dev', 'test']
    total = 0
    
    for split in splits:
        try:
            dataset = AfriSpeechShona(data_dir="./data/afrispeech_shona", split=split)
            count = len(dataset)
            print(f"{split}: {count} samples")
            total += count
        except Exception as e:
            print(f"{split}: Error loading - {e}")
            
    print(f"Total samples: {total}")

if __name__ == "__main__":
    check_counts()
