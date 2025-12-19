
import logging
from datasets import load_dataset, get_dataset_config_names, concatenate_datasets, Audio

logger = logging.getLogger(__name__)

class MultiAccentLoader:
    """
    Loader for AfriSpeech-200 that handles multiple accents and frugal loading.
    """
    
    def __init__(self, threshold=2000, max_configs=None):
        """
        Args:
            threshold: Max samples per accent (for frugal loading).
            max_configs: Optional limit on number of accents to load (for testing).
        """
        self.threshold = threshold

        try:
            self.configs = get_dataset_config_names("intronhealth/afrispeech-200")
            # Exclude 'all' config as it duplicates others and defeats frugal loading
            if "all" in self.configs:
                self.configs.remove("all")
        except Exception as e:
            logger.error(f"Failed to fetch configs: {e}")
            self.configs = ["shona", "kiswahili", "yoruba", "hausa"] # Fallback
            
        if max_configs:
            self.configs = self.configs[:max_configs]
            
    def load_all(self, split="train", streaming=False):
        datasets_list = []
        
        for config in self.configs:
            logger.info(f"Processing accent: {config}")
            try:
                # Load dataset
                # We use streaming=False to be able to select/len, 
                # unless we want to do frugal loading differently.
                # For 24GB VRAM machine, RAM might be concern if we load ALL into memory?
                # But we are just loading metadata (Arrow).
                
                ds = load_dataset(
                    "intronhealth/afrispeech-200", 
                    config, 
                    split=split, 
                    trust_remote_code=True,
                    verification_mode="no_checks" # Speed up
                )
                
                # Frugal Loading Logic
                original_len = len(ds)
                if original_len > self.threshold:
                    logger.info(f"  -> Large dataset ({original_len}). Frugal load: capping at {self.threshold}.")
                    # Shuffle and take subset? Or just take first N?
                    # Shuffle is better but slower.
                    # ds = ds.shuffle(seed=42).select(range(self.threshold))
                    ds = ds.select(range(self.threshold))
                else:
                    logger.info(f"  -> Small dataset ({original_len}). Full load.")
                
                # Ensure audio column is Audio feature (it should be)
                # ds = ds.cast_column("audio", Audio(sampling_rate=16000))
                
                datasets_list.append(ds)
                
            except Exception as e:
                logger.warning(f"  -> Failed to load {config}: {e}")
                
        if not datasets_list:
            raise ValueError("No datasets loaded!")
            
        logger.info(f"Concatenating {len(datasets_list)} datasets...")
        combined_ds = concatenate_datasets(datasets_list)
        
        # Cast to 16kHz audio for Whisper
        combined_ds = combined_ds.cast_column("audio", Audio(sampling_rate=16000))
        
        return combined_ds
