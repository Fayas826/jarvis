"""
Phase 36.6B — Autonomous Recovery Manager
==========================================

Implements the full Phase 36 recovery hierarchy:

  Failure
    → Retry (same action, same tool)
    → Re-ground (fresh perception, same tool)
    → Parameter Adjustment (modify target/payload)
    → Tool Substitution (switch to alternative tool)
    → Subtask Repair (insert prerequisite node)
    → Plan Rebuild (rebuild downstream branch)
    → Ask User (surface for guidance)
    → Stop

CRITICAL SAFETY RULE:
- SAFETY_BLOCK immediately routes to STOP. No retries. No reruns. No workarounds.
- Risk level from task_node is NEVER reduced by recovery decisions.
- Forbidden actions from intent remain forbidden regardless of recovery state.
"""

import time
from typing import Dict, Any, List, Optional


class RecoveryAction:
    RETRY              = "RETRY"
    REGROUND           = "REGROUND"
    ADJUST_PARAMETERS  = "ADJUST_PARAMETERS"
    SUBSTITUTE_TOOL    = "SUBSTITUTE_TOOL"
    REPAIR_SUBTASK     = "REPAIR_SUBTASK"
    REBUILD_PLAN       = "REBUILD_PLAN"
    ASK_USER           = "ASK_USER"
    STOP               = "STOP"


class AutonomousRecoveryManager:
    """
    Stateful recovery manager that escalates through the recovery hierarchy
    per node, tracking attempt counts to prevent infinite loops.
    """

    def __init__(self, max_retries: int = 2, max_regrounds: int = 2, max_total_escalations: int = 6):
        self._max_retries = max_retries
        self._max_regrounds = max_regrounds
        self._max_total = max_total_escalations
        # Per node_id tracking: {node_id: {action: count, total: int}}
        self._history: Dict[str, Dict[str, Any]] = {}

    def decide_recovery(
        self,
        node_id: str,
        verification_status: str,
        task_node: Dict[str, Any],
        exec_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Given a failed node and verification result, return the next recovery action.
        """
        # ── Safety gate — always terminal ──────────────────────────────────────
        if verification_status == "SAFETY_BLOCK":
            return self._decision(RecoveryAction.STOP, node_id,
                                  "Safety block is terminal. Cannot recover.")

        # ── Escalation budget ──────────────────────────────────────────────────
        hist = self._history.setdefault(node_id, {
            "retry": 0, "reground": 0, "param_adjust": 0,
            "tool_sub": 0, "subtask_repair": 0, "plan_rebuild": 0, "total": 0
        })

        if hist["total"] >= self._max_total:
            return self._decision(RecoveryAction.ASK_USER, node_id,
                                  "Maximum recovery escalations reached.")

        # ── Hierarchy ──────────────────────────────────────────────────────────

        # 1. Retry (for transient failures)
        if verification_status in ("RECOVERABLE_FAILURE", "UNKNOWN"):
            if hist["retry"] < self._max_retries:
                hist["retry"] += 1
                hist["total"] += 1
                return self._decision(RecoveryAction.RETRY, node_id,
                                      f"Retry attempt {hist['retry']}/{self._max_retries}.")

        # 2. Re-ground (stale perception)
        if verification_status in ("RECOVERABLE_FAILURE", "ENVIRONMENT_CHANGE", "UNKNOWN"):
            if hist["reground"] < self._max_regrounds:
                hist["reground"] += 1
                hist["total"] += 1
                return self._decision(RecoveryAction.REGROUND, node_id,
                                      f"Re-ground attempt {hist['reground']}/{self._max_regrounds}.")

        # 3. Parameter Adjustment
        if hist["param_adjust"] < 1:
            hist["param_adjust"] += 1
            hist["total"] += 1
            return self._decision(RecoveryAction.ADJUST_PARAMETERS, node_id,
                                  "Adjusting action parameters.")

        # 4. Tool Substitution
        if hist["tool_sub"] < 1:
            hist["tool_sub"] += 1
            hist["total"] += 1
            return self._decision(RecoveryAction.SUBSTITUTE_TOOL, node_id,
                                  "Substituting alternate tool.")

        # 5. Subtask Repair
        if verification_status == "PARTIAL_SUCCESS" and hist["subtask_repair"] < 1:
            hist["subtask_repair"] += 1
            hist["total"] += 1
            return self._decision(RecoveryAction.REPAIR_SUBTASK, node_id,
                                  "Inserting prerequisite subtask.")

        # 6. Plan Rebuild
        if hist["plan_rebuild"] < 1:
            hist["plan_rebuild"] += 1
            hist["total"] += 1
            return self._decision(RecoveryAction.REBUILD_PLAN, node_id,
                                  "Rebuilding downstream plan branch.")

        # 7. Ask User
        return self._decision(RecoveryAction.ASK_USER, node_id,
                              "All automated recovery options exhausted.")

    def reset_node(self, node_id: str):
        """Reset recovery history for a node (e.g., after successful repair)."""
        self._history.pop(node_id, None)

    def get_history(self, node_id: str) -> Dict[str, Any]:
        return self._history.get(node_id, {})

    def _decision(self, action: str, node_id: str, reason: str) -> Dict[str, Any]:
        print(f"[RECOVERY_MANAGER] Node={node_id} -> {action}: {reason}")
        return {
            "action": action,
            "node_id": node_id,
            "reason": reason,
            "is_terminal": action in (RecoveryAction.STOP, RecoveryAction.ASK_USER),
        }


autonomous_recovery_manager = AutonomousRecoveryManager()
