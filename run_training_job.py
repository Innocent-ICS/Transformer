
import subprocess
import sys
import os

# Use the specific python environment found earlier
PYTHON_EXEC = "/home/compute.ashesi.lan/ptinibu/python-env/bin/python"
SCRIPT = "ml/train_all.py"

print(f"Running {SCRIPT} using {PYTHON_EXEC}...")


cmd = f"nohup {PYTHON_EXEC} {SCRIPT} > training.log 2>&1 &"
print(f"Command: {cmd}")

os.system(cmd)
print("Training started in background. Tailing log for 10 seconds...")
import time
time.sleep(5)
os.system("tail -n 20 training.log")

# If smoke test passes, maybe run full training?
# User said "Test the full dataloading pipeline...". 
# The smoke test uses frugal loading too (but small limit).
# I should probably just run the smoke test to prove it works.
# Or ask user? User said "First test the full capabilities... select best suited... Plan effectively then implement".
# If I run smoke test and it works, I have fulfilled "Test dataloading pipeline".
# Actual training might take hours.
# I'll stick to running the smoke test to confirm pipeline, then tell the user I trained a small version and ready for full.
