"""
Phase 37.6 — Multi-Step Task Scheduler
======================================

Manages a priority execution queue of task nodes based on DAG dependencies.
Handles:
- priority queues
- task execution status tracking (PENDING, RUNNING, COMPLETED, FAILED)
- dependency resolution
- pause / resume
"""

import time
from typing import Dict, Any, List, Optional

class TaskScheduler:
    """Manages queue, dependencies, and state transitions of tasks during a session."""

    def __init__(self):
        self.queue: List[Dict[str, Any]] = []
        self.active_tasks: List[str] = []
        self.paused = False

    def load_plan(self, plan: List[Dict[str, Any]]):
        self.queue = list(plan)
        self.active_tasks.clear()
        self.paused = False

    def get_next_runnable_task(self) -> Optional[Dict[str, Any]]:
        if self.paused:
            return None

        from core.orchestration.task_state import task_state_controller
        active_plan = task_state_controller.load_active_plan() or self.queue

        # Map task IDs to their actual record status
        completed_ids = set()
        status_map = {}
        if task_state_controller._record:
            for tid, node_record in task_state_controller._record.nodes.items():
                stat = node_record.get("status", "PENDING")
                status_map[tid] = stat
                if stat == "COMPLETED":
                    completed_ids.add(tid)
        else:
            for t in active_plan:
                stat = t.get("status", "PENDING")
                status_map[t["task_id"]] = stat
                if stat == "COMPLETED":
                    completed_ids.add(t["task_id"])

        for task in active_plan:
            tid = task["task_id"]
            stat = status_map.get(tid, "PENDING")
            if stat in ("PENDING", "FAILED"):
                # Check dependencies
                deps = task.get("dependencies", [])
                if all(d in completed_ids for d in deps):
                    return task
        return None

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def get_progress(self) -> Dict[str, Any]:
        from core.orchestration.task_state import task_state_controller
        active_plan = task_state_controller.load_active_plan() or self.queue
        total = len(active_plan)
        completed = len([t for t in active_plan if t.get("status") == "COMPLETED"])
        failed = len([t for t in active_plan if t.get("status") == "FAILED"])
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "progress_percent": int((completed / total) * 100) if total > 0 else 0
        }

task_scheduler = TaskScheduler()
