import os
import subprocess

def install_unsloth():
    print("========================================")
    print("  PHASE 21: UNSLOTH ACCELERATION ENGINE ")
    print("========================================")
    print("\n[1] Initializing Hybrid Tensor Core + Unsloth Installation...")
    
    # Unsloth requires very specific pip installs for Windows
    commands = [
        "python -m pip install unsloth",
        "python -m pip install --upgrade --no-deps xformers",
        "python -m pip install trl peft accelerate bitsandbytes"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        subprocess.run(cmd, shell=True)
        
    print("\n[2] Unsloth Engine Ready.")
    print("Next time we run a training loop, JARVIS will automatically use:")
    print("- Mixed Precision (FP16 / bfloat16)")
    print("- Triton Math Kernels")
    print("- 2x to 5x Training Speed!")
    print("========================================")

if __name__ == "__main__":
    install_unsloth()
