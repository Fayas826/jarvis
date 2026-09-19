# core/orchestration/plan_repair.py
import time
from typing import List, Dict, Any, Optional

class PlanRepairController:
    """Calculates and applies dynamic remaining-DAG mutations when actions fail verification."""

    def __init__(self, max_repairs: int = 3):
        self.max_repairs = max_repairs
        self._repair_history = {} # Maps task_id -> list of applied strategies (for oscillation checks)

    def repair_plan(
        self,
        active_plan: List[Dict[str, Any]],
        failed_task_id: str,
        verification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main plan repair entry point. Mutates active plan tasks list.
        """
        # 1. Safety Block Check
        if verification_result.get("status") == "SAFETY_BLOCK":
            return {
                "status": "SAFETY_STOP",
                "repaired_plan": active_plan,
                "record": {
                    "original_node_id": failed_task_id,
                    "failure_classification": "SAFETY_BLOCK",
                    "repair_strategy": "HALT",
                    "inserted_nodes": [],
                    "removed_nodes": [],
                    "detail": "Safety gate blocked action. Plan repair forbidden."
                }
            }

        # 2. Find failed task node index
        failed_idx = -1
        for idx, t in enumerate(active_plan):
            if t.get("task_id") == failed_task_id:
                failed_idx = idx
                break

        if failed_idx == -1:
            return {
                "status": "UNREPAIRABLE",
                "repaired_plan": active_plan,
                "record": {"original_node_id": failed_task_id, "detail": "Failed task ID not found in plan."}
            }

        failed_node = active_plan[failed_idx]

        # 3. Budget & Oscillation Checks
        applied_strats = self._repair_history.setdefault(failed_task_id, [])
        if len(applied_strats) >= self.max_repairs:
            return {
                "status": "UNREPAIRABLE",
                "repaired_plan": active_plan,
                "record": {"original_node_id": failed_task_id, "detail": "Plan repair budget exhausted."}
            }

        # Select Strategy based on verification status
        v_status = verification_result.get("status", "FAILED")
        
        inserted_nodes = []
        removed_nodes = []
        strategy = "REBUILD_DOWNSTREAM"

        if v_status == "PARTIAL":
            # Strategy: Insert Prerequisite Node before the failed node to setup preconditions
            strategy = "INSERT_PREREQ"
            if "INSERT_PREREQ" in applied_strats:
                # Oscillation detected on same node strategy!
                return {
                    "status": "UNREPAIRABLE",
                    "repaired_plan": active_plan,
                    "record": {"original_node_id": failed_task_id, "detail": "Repair strategy oscillation detected."}
                }
                
            prereq_node = {
                "task_id": f"{failed_task_id}-PREREQ",
                "parent_id": failed_node.get("parent_id"),
                "objective": f"Setup precondition for {failed_node.get('objective')}",
                "description": "Dynamic recovery step inserted to resolve partial execution match.",
                "action_type": "WAIT",
                "dependencies": failed_node.get("dependencies", []),
                "status": "PENDING"
            }
            inserted_nodes.append(prereq_node)
            
            # Repoint failed node's dependencies to wait for prereq
            failed_node["dependencies"] = [prereq_node["task_id"]]
            
        elif v_status == "FAILED" or v_status == "UNEXPECTED_CHANGE":
            # Strategy: Substitute Alternative Backend or parameters on the failed node
            strategy = "SUBSTITUTE_TOOL"
            failed_node["retry_policy"] = {"max_retries": 1, "strategy": "alternate_driver"}
            failed_node["action_type"] = "OPEN_APP" if failed_node["action_type"] == "CLICK" else "CLICK"
            
        else: # NO_CHANGE / UNKNOWN
            # Strategy: Rebuild Downstream Branch (recreates downstream steps)
            strategy = "REBUILD_DOWNSTREAM"
            # Remove all tasks dependent on the failed task
            downstream_ids = [t["task_id"] for t in active_plan[failed_idx+1:]]
            removed_nodes.extend(downstream_ids)
            
            # Simulated branch reconstruction: add a fresh verify node
            recon_node = {
                "task_id": f"{failed_task_id}-RECON",
                "parent_id": failed_task_id,
                "objective": "Verify visual workspace context",
                "action_type": "WAIT",
                "dependencies": [failed_task_id],
                "status": "PENDING"
            }
            inserted_nodes.append(recon_node)

        # 4. Apply mutations to active plan
        applied_strats.append(strategy)
        new_plan = []
        
        # Keep completed tasks unmodified
        for idx, t in enumerate(active_plan):
            if idx < failed_idx:
                new_plan.append(t)
            elif idx == failed_idx:
                # Add inserted nodes before/after
                if strategy == "INSERT_PREREQ":
                    new_plan.extend(inserted_nodes)
                new_plan.append(t)
                if strategy == "REBUILD_DOWNSTREAM":
                    new_plan.extend(inserted_nodes)
            else:
                if t["task_id"] not in removed_nodes:
                    new_plan.append(t)

        # Update in state controller if available
        try:
            from core.orchestration.task_state import task_state_controller
            task_state_controller.save_active_plan(new_plan)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'plan_repair', f'Unhandled exception: {e}')
            pass

        return {
            "status": "REPAIRED",
            "repaired_plan": new_plan,
            "record": {
                "original_node_id": failed_task_id,
                "failure_classification": v_status,
                "repair_strategy": strategy,
                "inserted_nodes": inserted_nodes,
                "removed_nodes": removed_nodes,
                "repair_count": len(applied_strats),
                "detail": f"Plan repaired successfully using strategy {strategy}."
            }
        }

plan_repair_controller = PlanRepairController()
