import os
from typing import Dict, Any, List
from core.orchestration.task_state import task_state_controller

class ContextManager:
    """Dynamically compiles relevant context parameters for active task steps."""

    def assemble_active_context(self, task_id: str) -> Dict[str, Any]:
        """Gathers only the current task metrics and the content of targeted files."""
        plan = task_state_controller.load_active_plan()
        state = task_state_controller.get_state()
        
        active_task = None
        for t in plan:
            if t.get("task_id") == task_id:
                active_task = t
                break
                
        if not active_task:
            return {"error": f"Task {task_id} not found in active plan."}

        # Retrieve target files source contents
        files_context = {}
        for filepath in active_task.get("relevant_files", []):
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        # Limit large files read size
                        files_context[filepath] = f.read(2000)
                except Exception as e:
                    files_context[filepath] = f"Error reading file: {e}"

        return {
            "current_objective": state.get("current_objective"),
            "task_id": task_id,
            "objective": active_task.get("objective"),
            "description": active_task.get("description"),
            "acceptance_criteria": active_task.get("acceptance_criteria"),
            "files_context": files_context
        }

context_manager = ContextManager()
