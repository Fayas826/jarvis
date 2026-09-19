"""
Phase 36.7A — Human-in-the-Loop (HiTL) Risk Manager
======================================================

Implements the risk confirmation gate required by the Phase 36 spec:

    LOW      → fully automatic
    MEDIUM   → automatic + post-action verification
    HIGH     → requires user confirmation before execution
    CRITICAL → explicit confirmation + safety gate check

SAFETY:
- This module does NOT bypass safety_layer.py — safety gate checks happen independently.
- A CRITICAL action blocked here CANNOT be re-attempted without fresh user confirmation.
- Confirmation decisions are NOT persisted across sessions (must re-confirm each session).
"""

import time
from typing import Dict, Any, Optional


class RiskLevel:
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"

    # Ordered scale for comparison
    _ORDER = {LOW: 0, MEDIUM: 1, HIGH: 2, CRITICAL: 3}

    @classmethod
    def is_at_least(cls, level: str, minimum: str) -> bool:
        return cls._ORDER.get(level, 0) >= cls._ORDER.get(minimum, 0)


class HumanInTheLoopManager:
    """
    Gate that intercepts HIGH and CRITICAL actions for confirmation.
    In autonomous mode (headless), HIGH actions are auto-approved with a warning.
    CRITICAL actions are blocked unless explicitly pre-authorized.
    """

    def __init__(self, autonomous_mode: bool = True):
        self._autonomous_mode = autonomous_mode
        # Pre-authorized actions for this session (plan_id → set of node_ids)
        self._authorized: Dict[str, set] = {}

    def pre_authorize(self, plan_id: str, node_id: str):
        """Explicitly pre-authorize a HIGH/CRITICAL node for execution."""
        self._authorized.setdefault(plan_id, set()).add(node_id)

    def check_authorization(
        self,
        task_node: Dict[str, Any],
        plan_id: str = "",
        intent: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Returns authorization result for this task node.
        Raises no exceptions — callers check result["approved"].
        """
        risk_level = task_node.get("risk_level", RiskLevel.LOW)
        node_id    = task_node.get("task_id", "unknown")
        intent     = intent or {}
        forbidden  = intent.get("forbidden_actions", [])

        # Check forbidden actions
        action_type = task_node.get("action_type", "")
        if action_type in forbidden:
            return {
                "approved": False,
                "risk_level": risk_level,
                "reason": f"Action '{action_type}' is forbidden by intent constraints.",
                "requires_user": True,
            }

        # LOW — always approved
        if risk_level == RiskLevel.LOW:
            return {"approved": True, "risk_level": risk_level, "reason": "LOW risk — automatic."}

        # MEDIUM — approved with verification note
        if risk_level == RiskLevel.MEDIUM:
            return {
                "approved": True,
                "risk_level": risk_level,
                "reason": "MEDIUM risk — auto-approved with post-action verification.",
                "requires_verification": True,
            }

        # HIGH — requires user confirmation per Phase 36 spec.
        # In fully-autonomous headless mode we block and surface to user
        # rather than silently approve a potentially destructive action.
        # Callers that have explicitly pre-authorized this node may bypass.
        if risk_level == RiskLevel.HIGH:
            if node_id in self._authorized.get(plan_id, set()):
                return {"approved": True, "risk_level": risk_level,
                        "reason": "HIGH risk — pre-authorized by user."}
            # Not pre-authorized: block and require explicit confirmation
            return {
                "approved": False,
                "risk_level": risk_level,
                "reason": (
                    "HIGH risk — user confirmation required before execution. "
                    "Call hitl_manager.pre_authorize(plan_id, node_id) to allow."
                ),
                "requires_user": True,
            }

        # CRITICAL — requires explicit pre-authorization regardless of mode
        if node_id in self._authorized.get(plan_id, set()):
            return {"approved": True, "risk_level": risk_level, "reason": "CRITICAL — pre-authorized by user."}

        return {
            "approved": False,
            "risk_level": risk_level,
            "reason": "CRITICAL risk — explicit confirmation + safety gate required.",
            "requires_user": True,
            "safety_gate_required": True,
        }


hitl_manager = HumanInTheLoopManager(autonomous_mode=True)
