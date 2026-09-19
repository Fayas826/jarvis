import time
from typing import Dict, Any, List, Optional

class TaskLifecycleRecord:
    """Represents the persistent lifecycle state of a single task execution session."""

    def __init__(self, plan_id: str, objective: str, intent: Dict[str, Any]):
        self.plan_id = plan_id
        self.objective = objective
        self.intent = intent  # Contains risk_level, forbidden_actions, confidence_requirement
        self.created_at = time.time()
        self.updated_at = time.time()
        self.status = "PENDING"      # Top-level session status
        self.active_node_id: Optional[str] = None
        self.nodes: Dict[str, Dict[str, Any]] = {}   # node_id → node lifecycle record
        self.tool_history: List[Dict[str, Any]] = []
        self.error_history: List[Dict[str, Any]] = []
        self.recovery_history: List[Dict[str, Any]] = []
        self.variables: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "objective": self.objective,
            "intent": self.intent,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "active_node_id": self.active_node_id,
            "nodes": self.nodes,
            "tool_history": self.tool_history,
            "error_history": self.error_history,
            "recovery_history": self.recovery_history,
            "variables": self.variables,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "TaskLifecycleRecord":
        r = TaskLifecycleRecord(
            plan_id=d.get("plan_id", ""),
            objective=d.get("objective", ""),
            intent=d.get("intent", {}),
        )
        r.created_at = d.get("created_at", time.time())
        r.updated_at = d.get("updated_at", time.time())
        r.status = d.get("status", "PENDING")
        r.active_node_id = d.get("active_node_id")
        r.nodes = d.get("nodes", {})
        r.tool_history = d.get("tool_history", [])
        r.error_history = d.get("error_history", [])
        r.recovery_history = d.get("recovery_history", [])
        r.variables = d.get("variables", {})
        return r
