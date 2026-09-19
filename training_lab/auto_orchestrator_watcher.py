import os
import time
import subprocess
import sys

TRAINING_LAB = r"c:\jarvis AI\jarvis\training_lab"
PROGRESS_FILE = os.path.join(TRAINING_LAB, "jarvis_1million_FULL_model", "chunk_progress.txt")

def log(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [AUTO-WATCHER] {msg}", flush=True)

def wait_for_1m_foundation():
    log("Waiting for 1 Million Foundation Training to complete (chunk 10)...")
    while True:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, "r") as f:
                try:
                    chunk = int(f.read().strip())
                    if chunk >= 10:
                        log("1 Million Foundation Training is COMPLETE!")
                        return
                except Exception as e:
                    from core.reliability.system_logger import system_logger
                    system_logger.log('ERROR', 'auto_orchestrator_watcher', f'Unhandled exception: {e}')
                    pass
        time.sleep(30) # Check every 30 seconds

def run_script(script_name):
    script_path = os.path.join(TRAINING_LAB, script_name)
    log(f"Starting {script_name}...")
    try:
        subprocess.run([sys.executable, script_path], check=True)
        log(f"{script_name} finished successfully.")
    except Exception as e:
        log(f"ERROR running {script_name}: {e}")

if __name__ == "__main__":
    # 1. Wait for foundation to finish
    wait_for_1m_foundation()
    
    # 2. Run the balance trainer (6 original models)
    run_script("train_swarm_balance.py")
    
    # 3. Run the master orchestrator (18 queued models)
    run_script("master_swarm_orchestrator.py")
    
    log("ALL AUTOMATED TRAINING QUEUES FINISHED!")
