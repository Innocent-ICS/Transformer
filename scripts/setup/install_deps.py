
import subprocess
import sys

pkgs = ["peft", "transformers", "datasets", "jiwer", "evaluate", "accelerate", "soundfile", "tensorboard"]
print(f"Installing {pkgs}...")
subprocess.run([sys.executable, "-m", "pip", "install"] + pkgs, check=True)
print("Done installing.")
