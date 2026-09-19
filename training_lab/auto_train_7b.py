import subprocess
import time
import sys

MODEL_NAME = "unsloth/Qwen2.5-Coder-1.5B-bnb-4bit"

def download_model():
    print(f"\n[*] Starting automated resilient download for {MODEL_NAME}...")
    attempt = 1
    while True:
        print(f"[*] Download Attempt {attempt}...")
        result = subprocess.run(
            ["hf", "download", MODEL_NAME],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[+] Download COMPLETED successfully!")
            break
        else:
            print(f"[!] Download interrupted (Network Error). Resuming in 5 seconds... (Attempt {attempt})")
            time.sleep(5)
            attempt += 1

def start_training():
    print("\n[*] Launching Full 1.5B Expert Training Protocol...")
    result = subprocess.run([sys.executable, "training_lab/train_all_experts_7b.py"])
    if result.returncode == 0:
        print("[+] ALL TRAINING COMPLETED SUCCESSFULLY!")
    else:
        print("[!] Training crashed or was interrupted. Check logs.")

if __name__ == "__main__":
    print("==================================================")
    print(" JARVIS AUTONOMOUS TRAINING MANAGER")
    print("==================================================")
    download_model()
    start_training()
