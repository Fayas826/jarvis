import os
import shutil
from datetime import datetime

def create_system_restore():
    print("========================================")
    print("  SYSTEM RESTORE POINT INITIATED        ")
    print("========================================")
    
    source_dir = r"c:\jarvis AI\jarvis"
    backup_dir = rf"c:\jarvis AI\JARVIS_RESTORE_POINTS\backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"[1] Creating full system image of: {source_dir}")
    print(f"[2] Saving restore point to: {backup_dir}")
    
    # We ignore the heavy VENV and HuggingFace cache to keep the backup fast
    try:
        shutil.copytree(source_dir, backup_dir, ignore=shutil.ignore_patterns('venv', '.git', '*.safetensors', '__pycache__'))
        print("[3] SUCCESS: JARVIS System Restore Point created.")
        
        # Auto-cleanup: Keep only the latest 5 restore points
        print("[4] Executing Windows-style Auto-Cleanup...")
        all_backups = sorted([os.path.join(r"c:\jarvis AI\JARVIS_RESTORE_POINTS", d) 
                              for d in os.listdir(r"c:\jarvis AI\JARVIS_RESTORE_POINTS") 
                              if d.startswith("backup_")])
        
        if len(all_backups) > 5:
            oldest_backups = all_backups[:-5] # Get all backups except the 5 newest
            for old_backup in oldest_backups:
                shutil.rmtree(old_backup)
                print(f"    - Deleted old restore point to save space: {os.path.basename(old_backup)}")
                
        print("\nIf a fatal error ever corrupts the project, you can instantly revert to this backup.")
    except Exception as e:
        print(f"[ERROR] Failed to create restore point: {e}")
        
    print("========================================")

if __name__ == "__main__":
    create_system_restore()
