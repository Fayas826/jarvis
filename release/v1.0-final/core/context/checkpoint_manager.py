import os
import json
import shutil
from typing import List

PROJECT_MEMORY_DIR = "project_memory"

class CheckpointManager:
    """Manages active file backups, recovery registries, and task checkpoints."""

    def __init__(self):
        os.makedirs(PROJECT_MEMORY_DIR, exist_ok=True)
        self.checkpoint_path = os.path.join(PROJECT_MEMORY_DIR, "checkpoints.json")

    def create_checkpoint(self, task_id: str, files_changed: List[str]):
        """Saves a task progress record and backs up changed files."""
        checkpoints = self.load_checkpoints()
        
        # Backup modified files
        backed_up = []
        for filepath in files_changed:
            if os.path.exists(filepath):
                backup_path = filepath + ".bak"
                try:
                    shutil.copy2(filepath, backup_path)
                    backed_up.append(filepath)
                except Exception as e:
                    print(f"[CHECKPOINT] Backup fail for {filepath}: {e}")

        checkpoints.append({
            "task_id": task_id,
            "timestamp": os.path.getmtime(self.checkpoint_path) if os.path.exists(self.checkpoint_path) else 0.0,
            "files_changed": backed_up
        })
        
        with open(self.checkpoint_path, "w") as f:
            json.dump(checkpoints, f, indent=2)
        print(f"[CHECKPOINT] Checkpoint saved successfully for task: {task_id}")

    def load_checkpoints(self) -> list:
        if os.path.exists(self.checkpoint_path):
            with open(self.checkpoint_path, "r") as f:
                return json.load(f)
        return []

checkpoint_manager = CheckpointManager()
