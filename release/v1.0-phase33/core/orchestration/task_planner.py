import uuid
import time
from typing import List, Dict, Any
from core.cognition.reasoning.brain import brain
from core.orchestration.task_state import task_state_controller

class TaskPlanner:
    """Decomposes complex objectives into a sequence of trackable sub-tasks."""

    async def create_plan(self, master_objective: str) -> List[Dict[str, Any]]:
        print(f"[PLANNER] Generating execution plan for objective: '{master_objective}'")
        
        prompt = (
            f"You are JARVIS Master Task Planner. Objective: '{master_objective}'\n"
            "Decompose this goal into small, sequential, trackable sub-tasks.\n"
            "Return ONLY a JSON list matching this format:\n"
            "[\n"
            "  {\n"
            "    \"task_id\": \"T-001\",\n"
            "    \"objective\": \"Step title\",\n"
            "    \"description\": \"Detailed description of what to do\",\n"
            "    \"relevant_files\": [\"list_of_relative_files_to_edit\"],\n"
            "    \"acceptance_criteria\": \"What needs to verify pass\",\n"
            "    \"status\": \"PENDING\"\n"
            "  }\n"
            "]"
        )
        
        try:
            res = await brain.get_ai_response(prompt)
            tasks = res.get("response") or res.get("payload")
            if isinstance(tasks, list) and len(tasks) > 0:
                # Add default structural keys if missing (Phase 10 Alignment)
                for idx, t in enumerate(tasks):
                    t.setdefault("id", f"TASK-{idx+1:03d}")
                    t.setdefault("goal", t.get("objective") or "Execute task node")
                    t.setdefault("dependencies", [])
                    t.setdefault("inputs", {})
                    t.setdefault("expected_state", t.get("acceptance_criteria") or "SUCCESS")
                    t.setdefault("risk_level", "LOW")
                    t.setdefault("timeout", 30.0)
                    t.setdefault("retry_limit", 3)
                    t.setdefault("verification_strategy", "title_check")
                    t.setdefault("rollback_strategy", "retry")
                    t.setdefault("status", "PENDING")
                
                task_state_controller.save_active_plan(tasks)
                task_state_controller.update_state({
                    "current_objective": master_objective,
                    "status": "PLANNING",
                    "active_task_id": None
                })
                print(f"[PLANNER] Decomposed objective into {len(tasks)} tasks.")
                return tasks
        except Exception as e:
            print(f"[PLANNER] Decomposition failed: {e}")
            
        # Basic offline mock plan for calculator testing
        mock_tasks = [
            {
                "task_id": "TASK-001",
                "objective": "Verify screen capture active state",
                "description": "Initialize screen captures and verify active application displays",
                "relevant_files": [],
                "status": "PENDING",
                "dependencies": []
            },
            {
                "task_id": "TASK-002",
                "objective": "Launch sandbox Calculator application",
                "description": "Trigger calculator launches and verify title change state",
                "relevant_files": [],
                "status": "PENDING",
                "dependencies": ["TASK-001"]
            }
        ]
        task_state_controller.save_active_plan(mock_tasks)
        task_state_controller.update_state({
            "current_objective": master_objective,
            "status": "PLANNING"
        })
        return mock_tasks

task_planner = TaskPlanner()
