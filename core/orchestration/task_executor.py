import time
import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from core.orchestration.task_state import task_state_controller
from core.orchestration.task_recovery import task_recovery_controller
from core.orchestration.computer_use_agent import computer_use_agent
from core.context.checkpoint_manager import checkpoint_manager
from core.context.context_manager import context_manager

# Meta-Architect is imported lazily to avoid circular import issues
_meta_architect = None
def _get_meta_architect():
    global _meta_architect
    if _meta_architect is None:
        try:
            from core.orchestration.meta_architect_agent import meta_architect
            _meta_architect = meta_architect
        except Exception as e:
            print(f"[EXECUTOR] Meta-Architect unavailable: {e}")
    return _meta_architect

# ---------------------------------------------------------------------------
# Tier Thresholds
# ---------------------------------------------------------------------------
TIER_1_MAX_RETRIES = 3   # Self-healing error injection
TIER_2_MAX_RETRIES = 6   # Cryogenic Swarm specialist
TIER_3_MAX_RETRIES = 9   # Meta-Architect source surgery
# Beyond Tier 3 → Human notification only

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
            
            objective = task.get("description", "")
            if task.get("previous_error"):
                objective += (
                    f"\n\n[SELF-HEALING REQUIRED: Your previous attempt crashed with the following error. "
                    f"Analyze the stack trace, find the bug, and rewrite the code to fix it.]\n"
                    f"Error Log:\n{task['previous_error']}"
                )
                
            # 3. Dispatch to worker
            result = await self.worker.run_task(
                task_id=task_id,
                objective=objective,
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
                task.pop("previous_error", None) # Clear error on success
                task_state_controller.save_active_plan(plan)
                task_state_controller.register_completed_task(task)
                
                # Create recovery checkpoint
                checkpoint_manager.create_checkpoint(task_id, files_changed=task.get("relevant_files", []))
                print(f"[EXECUTOR] Task step {task_id} COMPLETED successfully.")
            else:
                task["status"] = "FAILED"
                error_msg = result.get("error", "Execution failed.")
                task["error"] = error_msg
                task["previous_error"] = error_msg # Feed into next iteration
                task_state_controller.save_active_plan(plan)
                task_state_controller.register_failed_task(task)
                
                print(f"[EXECUTOR] Task step {task_id} FAILED: {error_msg}. Initiating recovery.")
                task_recovery_controller.rollback_files(task.get("relevant_files", []))
                
                # ── 4-TIER ESCALATION ──────────────────────────────────────
                retries = task.get("retry_count", 0) + 1
                task["retry_count"] = retries

                if retries <= TIER_1_MAX_RETRIES:
                    # Tier 1: Self-healing error injection (handled via objective above)
                    task["status"] = "PENDING"
                    task_state_controller.save_active_plan(plan)
                    print(f"[EXECUTOR] ⚡ TIER 1 — Self-heal retry {retries}/{TIER_1_MAX_RETRIES} for: {task_id}")

                elif retries <= TIER_2_MAX_RETRIES:
                    # Tier 2: Wake a Cryogenic Swarm specialist agent
                    task["status"] = "PENDING"
                    task_state_controller.save_active_plan(plan)
                    print(f"[EXECUTOR] ❄️  TIER 2 — Cryogenic Swarm dispatched for: {task_id}")
                    ma = _get_meta_architect()
                    if ma:
                        asyncio.get_event_loop().run_in_executor(
                            None, ma._dispatch_swarm_specialist,
                            {"task_id": task_id, "error": error_msg, "retries": retries,
                             "description": task.get("description", "")},
                            None
                        )

                elif retries <= TIER_3_MAX_RETRIES:
                    # Tier 3: Meta-Architect performs autonomous source code surgery
                    task["status"] = "PENDING"
                    task_state_controller.save_active_plan(plan)
                    print(f"[EXECUTOR] 🔧 TIER 3 — Meta-Architect SOURCE SURGERY for: {task_id}")
                    ma = _get_meta_architect()
                    if ma:
                        asyncio.get_event_loop().run_in_executor(
                            None, ma.run_analysis_cycle
                        )

                else:
                    # Final Tier: All automated recovery exhausted — notify human
                    task["status"] = "BLOCKED"
                    task_state_controller.save_active_plan(plan)
                    task_state_controller.update_state({"status": "BLOCKED"})
                    print(
                        f"[EXECUTOR] 🚨 FINAL TIER — All {retries} escalation attempts failed for task '{task_id}'.\n"
                        f"           Human intervention required. Error: {error_msg}"
                    )
                    self.is_running = False
                    break
                    
        self.is_running = False
        state = task_state_controller.get_state()
        return {"status": "SUCCESS" if state.get("status") != "BLOCKED" else "BLOCKED"}

    def stop(self):
        self.is_running = False

task_executor = TaskExecutor()
