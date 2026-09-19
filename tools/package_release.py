import os
import shutil

def package_release():
    print("==================================================")
    print("JARVIS PRODUCTION RELEASE PACKAGER")
    print("==================================================")
    
    src_dir = r"c:\jarvis AI\jarvis"
    dest_dir = os.path.join(src_dir, "release", "v1.0-final")
    
    # Clean old final release if exists
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)
    
    # Directories to copy
    dirs_to_copy = ["core", "infrastructure", "backend", "action"]
    
    for d in dirs_to_copy:
        src_path = os.path.join(src_dir, d)
        dest_path = os.path.join(dest_dir, d)
        if os.path.exists(src_path):
            shutil.copytree(src_path, dest_path, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.tmp"))
            print(f"Copied directory: {d} -> release/v1.0-final/{d}")
            
    # Copy root manifest and starter scripts
    files_to_copy = [
        "api_starter.py",
        "jarvis_sentinel_v2.py",
        "PHASE_38_BASELINE_MANIFEST.json",
        "PHASE_38_FINAL_VERDICT.md"
    ]
    
    for f in files_to_copy:
        src_file = os.path.join(src_dir, f)
        dest_file = os.path.join(dest_dir, f)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_file)
            print(f"Copied file: {f} -> release/v1.0-final/{f}")
            
    print("==================================================")
    print("RELEASE PACKAGING COMPLETED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    package_release()
