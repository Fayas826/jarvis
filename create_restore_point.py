import os
import zipfile
import datetime
import glob

# Configuration
SOURCE_DIR = r"C:\jarvis AI\jarvis"
RESTORE_DIR = r"C:\JARVIS_RESTORE_POINTS"
MAX_BACKUPS = 5

EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
EXCLUDE_EXTS = {'.bin', '.gguf', '.pt', '.safetensors', '.onnx'}

def create_restore_point():
    if not os.path.exists(RESTORE_DIR):
        os.makedirs(RESTORE_DIR)

    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    zip_filename = os.path.join(RESTORE_DIR, f"JARVIS_RESTORE_{timestamp}.zip")
    
    print(f"[RESTORE] Creating Snapshot: {zip_filename} ...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SOURCE_DIR):
            # In-place modification to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                
                file_path = os.path.join(root, file)
                # Calculate relative path to keep zip structure clean
                arcname = os.path.relpath(file_path, SOURCE_DIR)
                try:
                    zipf.write(file_path, arcname)
                except Exception as e:
                    print(f"[RESTORE] Warning: Could not compress {arcname} ({e})")
                    
    print("[RESTORE] System Snapshot Successful!")
    cleanup_old_restore_points()
    return zip_filename

def cleanup_old_restore_points():
    backups = sorted(glob.glob(os.path.join(RESTORE_DIR, "JARVIS_RESTORE_*.zip")), key=os.path.getmtime)
    if len(backups) > MAX_BACKUPS:
        excess = len(backups) - MAX_BACKUPS
        for i in range(excess):
            try:
                os.remove(backups[i])
                print(f"[RESTORE] Cleaned up old snapshot: {os.path.basename(backups[i])}")
            except Exception as e:
                print(f"[RESTORE] Failed to delete old snapshot {backups[i]}: {e}")

if __name__ == "__main__":
    create_restore_point()
