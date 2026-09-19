import os
import json
from typing import Dict, Any, Optional
from core.orchestration.task_state import task_state_controller

class TaskRecoveryController:
    """Restores plan queues and rollback execution checkpoints on loop errors."""

    def attempt_recovery(self) -> Optional[Dict[str, Any]]:
        """Checks for interrupted tasks and attempts to restore from the last checkpoint."""
        state = task_state_controller.get_state()
        if state.get("status") in ["RUNNING", "PLANNING"] and state.get("active_task_id"):
            task_id = state.get("active_task_id")
            print(f"[RECOVERY] Interrupted execution detected for task: {task_id}")
            
            # Retrieve active plan items to restore progress
            plan = task_state_controller.load_active_plan()
            for task in plan:
                if task.get("task_id") == task_id:
                    task["status"] = "PENDING"
                    task_state_controller.save_active_plan(plan)
                    task_state_controller.update_state({"status": "PLANNING", "active_task_id": None})
                    print(f"[RECOVERY] Reset task {task_id} back to PENDING status.")
                    return task
        return None

    def rollback_files(self, files_changed: list):
        """Rolls back files if backups exist during checkpoints."""
        # Checkpoint files rollback hooks
        for filepath in files_changed:
            backup_path = filepath + ".bak"
            if os.path.exists(backup_path):
                try:
                    os.replace(backup_path, filepath)
                    print(f"[ROLLBACK] Reverted file: {filepath}")
                except Exception as e:
                    print(f"[ROLLBACK] Failed reverting {filepath}: {e}")

task_recovery_controller = TaskRecoveryController()
