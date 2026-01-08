
import os
import sys

log_file = "training.log"
if os.path.exists(log_file):
    print(f"--- Tailing {log_file} ---")
    os.system(f"tail -n 50 {log_file}")
    
    # Also check if process is running
    print("\n--- Process Status ---")
    os.system("ps -ef | grep train_all.py | grep -v grep")
else:
    print(f"Log file {log_file} not found.")
