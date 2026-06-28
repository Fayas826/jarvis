import os
import shutil
import ast
import subprocess

# 🩺 HORCRUX_SURGEON_MODULE
# Chapter 10: Advanced Self-Healing & Neural Suturing

class HorcruxSurgeon:
    def __init__(self):
        self.core_dir = r"c:\jarvis AI\jarvis\backend"
        self.backup_dir = os.path.join(os.environ["LOCALAPPDATA"], "JARVIS_GOLDEN_STATE")
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_golden_backup(self):
        """Saves a 100% stable version of all JARVIS modules."""
        print("[HORCRUX] Manifesting Golden State Backup...")
        for file in os.listdir(self.core_dir):
            if file.endswith(".py"):
                src = os.path.join(self.core_dir, file)
                # Only backup if the current file is syntactically correct
                if self.verify_integrity(src):
                    shutil.copy2(src, os.path.join(self.backup_dir, file))

    def verify_integrity(self, file_path):
        """Performs a deep syntax check on a module."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                ast.parse(f.read())
            return True
        except (SyntaxError, UnicodeDecodeError):
            return False

    def perform_surgery(self):
        """Scans all modules and repairs those that are 'bleeding' (Broken Syntax)."""
        for file in os.listdir(self.core_dir):
            if file.endswith(".py"):
                path = os.path.join(self.core_dir, file)
                if not self.verify_integrity(path):
                    print(f"[HORCRUX] CRITICAL: '{file}' is corrupted. Initiating Neural Suture...")
                    backup = os.path.join(self.backup_dir, file)
                    if os.path.exists(backup):
                        shutil.copy2(backup, path)
                        print(f"[HORCRUX] Surgery Successful. '{file}' restored to Golden State.")
                    else:
                        print(f"[HORCRUX] FAILED: No Golden Backup for '{file}'. Manual intervention required.")

# Initialized as a global guardian
surgeon = HorcruxSurgeon()
