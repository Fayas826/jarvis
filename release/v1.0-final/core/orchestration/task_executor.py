import time
import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from core.orchestration.task_state import task_state_controller
from core.orchestration.task_recovery import task_recovery_controller
from core.orchestration.computer_use_agent import computer_use_agent
from core.context.checkpoint_manager import checkpoint_manager
from core.context.context_manager import context_manager

class BaseWorker(ABC):
    """Generic worker interface for task delegation (Phase 10)."""
    
    @abstractmethod
    async def run_task(self, task_id: str, objective: str, context: Dict[str, Any], files: List[str], constraints: List[str]) -> Dict[str, Any]:
        """
        Runs the specified task and returns a results payload containing:
        - status: "SUCCESS" | "FAILED"
        - files_changed: List[str]
        - test_results: Dict[str, Any]
        - error: Optional[str]
        """
        pass

class DefaultAgentWorker(BaseWorker):
    """Default Computer Use Agent Task Worker execution wrapper."""
    
    async def run_task(self, task_id: str, objective: str, context: Dict[str, Any], files: List[str], constraints: List[str]) -> Dict[str, Any]:
        print(f"[WORKER] Executing task {task_id} with description: '{objective}'")
        try:
            # Dispatch to the ComputerUseAgent loop
            res = await computer_use_agent.execute_task(objective)
            if res.get("status") == "SUCCESS":
                return {
                    "status": "SUCCESS",
                    "files_changed": files,
                    "test_results": {"verification": "PASS"},
                    "error": None
                }
            else:
                return {
                    "status": "FAILED",
                    "files_changed": [],
                    "test_results": {"verification": "FAIL"},
                    "error": res.get("reason", "Step execution failure.")
                }
        except Exception as e:
            return {
                "status": "FAILED",
                "files_changed": [],
                "test_results": {"verification": "CRASH"},
                "error": str(e)
            }

class TaskExecutor:
    """Orchestrates plan execution by coordinating worker dispatches and task validations."""

    def __init__(self, worker: Optional[BaseWorker] = None):
        self.is_running = False
        self.worker = worker or DefaultAgentWorker()

    def set_worker(self, worker: BaseWorker):
        self.worker = worker

    async def execute_plan(self) -> Dict[str, Any]:
        self.is_running = True
        plan = task_state_controller.load_active_plan()
        
        print(f"[EXECUTOR] Resuming task execution queue containing {len(plan)} items.")
        
        for task in plan:
            if not self.is_running:
                break
                
            if task.get("status") in ["COMPLETED", "SKIPPED"]:
                continue
                
            task_id = task.get("task_id")
            print(f"[EXECUTOR] Launching task step: {task_id} - '{task.get('objective')}'")
            
            # 1. Update active task state (VERIFYING, RUNNING)
            task["status"] = "RUNNING"
            task["started_at"] = time.time()
            task_state_controller.save_active_plan(plan)
            task_state_controller.update_state({"status": "RUNNING", "active_task_id": task_id})
            
            # 2. Retrieve focused context for the task
            relevant_context = context_manager.assemble_active_context(task_id)
            
            # 3. Dispatch to worker
            result = await self.worker.run_task(
                task_id=task_id,
                objective=task.get("description", ""),
                context=relevant_context,
                files=task.get("relevant_files", []),
                constraints=task.get("constraints", [])
            )
            
            task["ended_at"] = time.time()
            success = result.get("status") == "SUCCESS"
            
            # 4. Verification Check
            task["result"] = result
            task["files_changed"] = result.get("files_changed", [])
            
            if success:
                task["status"] = "COMPLETED"
                task_state_controller.save_active_plan(plan)
                task_state_controller.register_completed_task(task)
                
                # Create recovery checkpoint
                checkpoint_manager.create_checkpoint(task_id, files_changed=task.get("relevant_files", []))
                print(f"[EXECUTOR] Task step {task_id} COMPLETED successfully.")
            else:
                task["status"] = "FAILED"
                task["error"] = result.get("error", "Execution failed.")
                task_state_controller.save_active_plan(plan)
                task_state_controller.register_failed_task(task)
                
                print(f"[EXECUTOR] Task step {task_id} FAILED: {task['error']}. Initiating recovery.")
                task_recovery_controller.rollback_files(task.get("relevant_files", []))
                
                # Check for retry limit bounds
                retries = task.get("retry_count", 0)
                if retries < 2:
                    task["retry_count"] = retries + 1
                    task["status"] = "PENDING"
                    task_state_controller.save_active_plan(plan)
                    print(f"[EXECUTOR] Scheduled retry attempt {retries + 1} for task: {task_id}")
                else:
                    task["status"] = "BLOCKED"
                    task_state_controller.save_active_plan(plan)
                    task_state_controller.update_state({"status": "BLOCKED"})
                    print(f"[EXECUTOR] Task {task_id} BLOCKED. Halting orchestrator execution.")
                    self.is_running = False
                    break
                    
        self.is_running = False
        state = task_state_controller.get_state()
        return {"status": "SUCCESS" if state.get("status") != "BLOCKED" else "BLOCKED"}

    def stop(self):
        self.is_running = False

task_executor = TaskExecutor()
