import os
import glob
import json
import time

def generate_dashboard():
    model_dir = r"c:\jarvis AI\jarvis\training_lab\jarvis_5million_game_dev_model"
    print("="*60)
    print(" JARVIS UNIVERSAL TRAINING DASHBOARD - ARCHITECT TIER")
    print("="*60)
    
    total_rows = 5_000_000
    rows_per_chunk = 500  # As configured in max_steps
    
    completed_chunks = []
    
    if not os.path.exists(model_dir):
        print("[!] Model directory not found. Training has not started.")
        return
        
    for i in range(1, 51):
        chunk_path = os.path.join(model_dir, f"chunk_{i:02d}")
        if os.path.exists(chunk_path):
            # Check if it has an adapter or a completed checkpoint
            adapters = glob.glob(os.path.join(chunk_path, "adapter_model.*"))
            checkpoints = glob.glob(os.path.join(chunk_path, "checkpoint-*"))
            if adapters or (checkpoints and len(checkpoints) > 0):
                completed_chunks.append(i)
                
    active_chunk = max(completed_chunks) if completed_chunks else 1
    # Check if the root has the adapter saved for chunk 13
    if os.path.exists(os.path.join(model_dir, "adapter_config.json")):
        # The latest chunk might have saved to root
        pass
        
    total_completed = active_chunk * rows_per_chunk
    percent_complete = (total_completed / total_rows) * 100
    
    print(f"Data Source:      5-Million Row Game Dev Dataset")
    print(f"Current Chunk:    {active_chunk} / 10000")
    print(f"Rows Processed:   {total_completed:,} / {total_rows:,}")
    print(f"Completion Limit: {percent_complete:.6f}%")
    print("-" * 60)
    
    # Progress Bar
    bar_length = 40
    filled = min(bar_length, int((active_chunk / 20) * bar_length)) # Scaling for visual
    bar = '#' * filled + '-' * (bar_length - filled)
    print(f"Progress Phase 1: [{bar}]")
    
    # NEW: Fetch live step progress from recent background task logs
    try:
        log_dir = r"C:\Users\Asus\.gemini\antigravity-ide\brain\7b743d62-ee01-421f-9811-857d037f759c\.system_generated\tasks"
        if os.path.exists(log_dir):
            list_of_logs = glob.glob(os.path.join(log_dir, '*.log'))
            if list_of_logs:
                latest_log = max(list_of_logs, key=os.path.getctime)
                with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    # Find the last line that looks like a tqdm progress bar
                    progress_line = ""
                    for line in reversed(lines[-50:]):
                        if "%|" in line and "/" in line:
                            progress_line = line.strip()
                            break
                    if progress_line:
                        print(f"Live Iteration:   {progress_line}")
                    else:
                        print(f"Live Iteration:   [Waiting for Training Daemon to start next Chunk...]")
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'universal_progress_dashboard', f'Unhandled exception: {e}')
        pass

    print("-" * 60)
    
    try:
        import psutil
        vram_free = "Unknown"
        # Try pynvml or nvidia-smi
        import subprocess
        res = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,nounits,noheader"], capture_output=True, text=True)
        if res.returncode == 0:
            vram_free = f"{res.stdout.strip()} MB"
            
        mem = psutil.virtual_memory()
        print(f"Hardware Status:  VRAM Free: {vram_free} | Sys RAM Free: {mem.available / (1024**2):.1f} MB")
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'universal_progress_dashboard', f'Unhandled exception: {e}')
        pass
        
    print("="*60)
    print("To start the next chunk autonomously, JARVIS Orchestrator will trigger:")
    print(f"python train_game_dev_unsloth.py (Chunk {active_chunk + 1})")
    print("="*60)

def run_live_dashboard():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        generate_dashboard()
        print("\n[Live Refreshing every 5 seconds... Press Ctrl+C to exit]")
        time.sleep(5)

if __name__ == "__main__":
    try:
        run_live_dashboard()
    except KeyboardInterrupt:
        print("\nExiting Live Dashboard.")
