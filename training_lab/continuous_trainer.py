import subprocess
import time
import os

print("[*] JARVIS Continuous Trainer Supervisor Online")
script_path = os.path.join(os.path.dirname(__file__), "train_game_dev_unsloth.py")

while True:
    print("\n[*] Spinning up fresh PyTorch process for next chunk...")
    result = subprocess.run(["python", script_path])
    
    if result.returncode != 0:
        print("[!] Training process exited with an error. Retrying in 10 seconds...")
        time.sleep(10)
    else:
        # If it returns 0, it means it completed the chunk successfully. 
        # It will loop and start the next chunk freshly.
        time.sleep(2)
