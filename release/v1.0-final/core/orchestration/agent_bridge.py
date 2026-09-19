import os
import json
import time
from typing import Dict, Any, List, Optional

PROJECT_MEMORY_DIR = "project_memory"

class AgentBridge:
    """Task Orchestration bridge providing task packets communication to external coders."""

    def __init__(self):
        os.makedirs(PROJECT_MEMORY_DIR, exist_ok=True)
        self.bridge_path = os.path.join(PROJECT_MEMORY_DIR, "agent_bridge.json")
        self._init_bridge()

    def _init_bridge(self):
        if not os.path.exists(self.bridge_path):
            self.save_bridge_data({
                "active_task": None,
                "completed_tasks": [],
                "failed_tasks": [],
                "task_queue": [],
                "last_update": time.time()
            })

    def load_bridge_data(self) -> Dict[str, Any]:
        try:
            with open(self.bridge_path, "r") as f:
                return json.load(f)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'agent_bridge', f'Unhandled exception: {e}')
            return {"active_task": None, "completed_tasks": [], "failed_tasks": [], "task_queue": []}

    def save_bridge_data(self, data: Dict[str, Any]):
        with open(self.bridge_path, "w") as f:
            json.dump(data, f, indent=2)

    def send_task(self, task_id: str, objective: str, files: List[str], expected_output: str):
        """Sends and registers a new task packet on the queue."""
        data = self.load_bridge_data()
        packet = {
            "task_id": task_id,
            "objective": objective,
            "files": files,
            "expected_output": expected_output,
            "status": "QUEUED",
            "timestamp": time.time()
        }
        data["task_queue"].append(packet)
        self.save_bridge_data(data)
        print(f"[BRIDGE] Enqueued task packet: {task_id}")

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Retrieves and flags the next queued task as active."""
        data = self.load_bridge_data()
        if data["task_queue"]:
            next_task = data["task_queue"].pop(0)
            next_task["status"] = "ACTIVE"
            data["active_task"] = next_task
            self.save_bridge_data(data)
            return next_task
        return None

    def report_progress(self, progress_details: str):
        data = self.load_bridge_data()
        if data["active_task"]:
            data["active_task"]["progress"] = progress_details
            data["last_update"] = time.time()
            self.save_bridge_data(data)

    def report_failure(self, error_message: str):
        data = self.load_bridge_data()
        if data["active_task"]:
            task = data["active_task"]
            task["status"] = "FAILED"
            task["error"] = error_message
            data["failed_tasks"].append(task)
            data["active_task"] = None
            self.save_bridge_data(data)

    def mark_complete(self):
        data = self.load_bridge_data()
        if data["active_task"]:
            task = data["active_task"]
            task["status"] = "COMPLETED"
            data["completed_tasks"].append(task)
            data["active_task"] = None
            self.save_bridge_data(data)

agent_bridge = AgentBridge()
