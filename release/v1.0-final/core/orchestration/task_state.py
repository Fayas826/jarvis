"""
Phase 36.4 — Persistent Task State & Episodic Execution Memory
===============================================================

Replaces the Phase 35 task_state.py stub with a full lifecycle controller:

- Atomic writes (write-to-tmp + os.replace) so partial writes never corrupt state
- Full task lifecycle tracking: PENDING → RUNNING → COMPLETED/FAILED/CANCELLED/RETRYING
- Plan ID, task IDs, intent, risk level all persisted
- Timestamps on every state transition
- Tool execution history per node
- Error history per node
- Recovery information per node
- Episodic execution memory connected to EpisodicTaskHistory
- Restart recovery: interrupted RUNNING tasks reset to PENDING with context preserved
- Variable injection ({{var}}) for dynamic payload substitution
- Corruption-safe: any JSON decode error falls back to clean state

SAFETY:
- Safety metadata (risk_level, forbidden_actions) is NEVER downgraded during recovery
- A restored task cannot have its risk_level reduced below the original intent value
- This module has NO dependency on safety_layer.py (it is advisory state only)
"""

import os
import json
import time
import uuid
import threading
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path

PROJECT_MEMORY_DIR = "project_memory"
_LIFECYCLE_DIR = os.path.join(PROJECT_MEMORY_DIR, "lifecycle")

# Valid task node state transitions
_VALID_TRANSITIONS = {
    "PENDING":    {"RUNNING", "CANCELLED"},
    "RUNNING":    {"COMPLETED", "FAILED", "CANCELLED", "RETRYING"},
    "RETRYING":   {"RUNNING", "FAILED", "CANCELLED"},
    "COMPLETED":  set(),   # Terminal
    "FAILED":     {"RETRYING", "CANCELLED"},
    "CANCELLED":  set(),   # Terminal
}

_LOCK = threading.Lock()


def _atomic_write(path: str, data: Any):
    """Write JSON atomically using a temp file + os.replace with Windows backoff retries."""
    dir_ = os.path.dirname(path) or "."
    os.makedirs(dir_, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w") as f:
            json.dump(data, f, indent=2)
        
        # Retry loop for Windows file-locking race conditions
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                os.replace(tmp_path, path)
                break
            except PermissionError as pe:
                if attempt == max_attempts - 1:
                    raise pe
                time.sleep(0.05 * (attempt + 1))
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'task_state', f'Unhandled exception: {e}')
        try:
            os.unlink(tmp_path)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'task_state', f'Unhandled exception: {e}')
            pass
        raise


def _safe_load(path: str, default: Any) -> Any:
    """Load JSON, falling back to default on any error."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'task_state', f'Unhandled exception: {e}')
        return default


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


class TaskStateController:
    """
    Phase 36.4 — Full Persistent Task Lifecycle Controller.

    Manages:
    - Active task session (atomic JSON persistence)
    - DAG plan node states
    - Episodic execution memory (connected to EpisodicTaskHistory)
    - Restart recovery
    - Variable injection
    """

    def __init__(self):
        os.makedirs(PROJECT_MEMORY_DIR, exist_ok=True)
        os.makedirs(_LIFECYCLE_DIR, exist_ok=True)

        self._session_path = os.path.join(PROJECT_MEMORY_DIR, "active_session.json")
        self._plan_path    = os.path.join(PROJECT_MEMORY_DIR, "active_plan.json")
        self._state_path   = os.path.join(PROJECT_MEMORY_DIR, "project_state.json")   # legacy compat
        self._completed_path = os.path.join(PROJECT_MEMORY_DIR, "completed_tasks.json")
        self._failed_path    = os.path.join(PROJECT_MEMORY_DIR, "failed_tasks.json")
        self._episodic_path  = os.path.join(PROJECT_MEMORY_DIR, "episodic_memory.json")

        self._record: Optional[TaskLifecycleRecord] = None
        self._lock = _LOCK

        # Attempt to load an existing interrupted session on startup
        self._load_session()

    # ──────────────────────────────────────────────────────────────────────────
    # Session lifecycle
    # ──────────────────────────────────────────────────────────────────────────

    def _load_session(self):
        data = _safe_load(self._session_path, None)
        if data:
            self._record = TaskLifecycleRecord.from_dict(data)
            if self._record.status == "RUNNING":
                # Mark interrupted session for recovery
                self._record.status = "INTERRUPTED"
                self._record.updated_at = time.time()
                self._persist_session()
                print(f"[TASK_STATE] Interrupted session detected: {self._record.plan_id}")

    def _persist_session(self):
        if self._record:
            _atomic_write(self._session_path, self._record.to_dict())

    def begin_session(self, objective: str, intent: Dict[str, Any]) -> str:
        """Create and persist a new task session. Returns plan_id."""
        with self._lock:
            plan_id = str(uuid.uuid4())
            self._record = TaskLifecycleRecord(plan_id=plan_id, objective=objective, intent=intent)
            self._record.status = "PLANNING"
            self._record.updated_at = time.time()
            self._persist_session()
            # Also update legacy state for backward compat
            self._legacy_update({"current_objective": objective, "status": "PLANNING", "active_task_id": None})
            print(f"[TASK_STATE] Session started: {plan_id}")
            return plan_id

    def get_interrupted_session(self) -> Optional[TaskLifecycleRecord]:
        """Returns interrupted session record if one exists, else None."""
        with self._lock:
            if self._record and self._record.status == "INTERRUPTED":
                return self._record
            return None

    def recover_session(self) -> Optional[Dict[str, Any]]:
        """
        Phase 36.4 recovery: resets interrupted RUNNING nodes to PENDING,
        preserves completed nodes, preserves safety metadata.
        Returns the first recoverable node or None.
        """
        with self._lock:
            if not self._record or self._record.status != "INTERRUPTED":
                return None

            # Safety: never downgrade risk_level
            original_risk = self._record.intent.get("risk_level", "LOW")

            recovered_node = None
            plan = _safe_load(self._plan_path, {}).get("tasks", [])
            for task in plan:
                node_id = task.get("task_id")
                node_state = self._record.nodes.get(node_id, {})
                node_status = node_state.get("status", task.get("status", "PENDING"))

                if node_status == "RUNNING":
                    # Reset to PENDING for retry
                    task["status"] = "PENDING"
                    node_state["status"] = "PENDING"
                    node_state["recovery_ts"] = time.time()
                    node_state["recovered"] = True
                    self._record.nodes[node_id] = node_state
                    # Ensure risk not downgraded
                    if task.get("risk_level", "LOW") != original_risk:
                        task["risk_level"] = original_risk
                    recovered_node = task
                    break
                elif node_status == "COMPLETED":
                    task["status"] = "COMPLETED"  # Preserve completed state

            _atomic_write(self._plan_path, {"tasks": plan})
            self._record.status = "RECOVERING"
            self._record.active_node_id = None
            self._record.updated_at = time.time()
            self._persist_session()

            print(f"[TASK_STATE] Recovery complete. Resumed at node: {recovered_node.get('task_id') if recovered_node else 'None'}")
            return recovered_node

    # ──────────────────────────────────────────────────────────────────────────
    # Node lifecycle
    # ──────────────────────────────────────────────────────────────────────────

    def mark_node_running(self, node_id: str):
        with self._lock:
            if self._record:
                self._record.active_node_id = node_id
                self._record.status = "RUNNING"
                node = self._record.nodes.setdefault(node_id, {})
                node["status"] = "RUNNING"
                node["started_at"] = time.time()
                self._record.updated_at = time.time()
                self._persist_session()
                self._legacy_update({"status": "RUNNING", "active_task_id": node_id})

    def mark_node_completed(self, node_id: str, result: Dict[str, Any] = None):
        with self._lock:
            if self._record:
                node = self._record.nodes.setdefault(node_id, {})
                if not self._is_valid_transition(node.get("status", "RUNNING"), "COMPLETED"):
                    print(f"[TASK_STATE] Invalid transition {node.get('status')} → COMPLETED for {node_id}")
                    return
                node["status"] = "COMPLETED"
                node["completed_at"] = time.time()
                node["result"] = result or {}
                if self._record.active_node_id == node_id:
                    self._record.active_node_id = None
                self._record.updated_at = time.time()
                self._persist_session()

    def mark_node_failed(self, node_id: str, error: str, error_type: str = "UNKNOWN"):
        with self._lock:
            if self._record:
                node = self._record.nodes.setdefault(node_id, {})
                node["status"] = "FAILED"
                node["failed_at"] = time.time()
                node["last_error"] = error
                node["error_type"] = error_type
                self._record.error_history.append({
                    "node_id": node_id,
                    "error": error,
                    "error_type": error_type,
                    "ts": time.time()
                })
                self._record.updated_at = time.time()
                self._persist_session()

    def mark_node_retrying(self, node_id: str, retry_count: int):
        with self._lock:
            if self._record:
                node = self._record.nodes.setdefault(node_id, {})
                node["status"] = "RETRYING"
                node["retry_count"] = retry_count
                node["retry_at"] = time.time()
                self._record.updated_at = time.time()
                self._persist_session()

    def record_tool_use(self, node_id: str, tool: str, result: str, latency_ms: float):
        with self._lock:
            if self._record:
                self._record.tool_history.append({
                    "node_id": node_id,
                    "tool": tool,
                    "result": result,
                    "latency_ms": latency_ms,
                    "ts": time.time()
                })
                self._record.updated_at = time.time()
                self._persist_session()

    def record_recovery(self, node_id: str, strategy: str, outcome: str):
        with self._lock:
            if self._record:
                self._record.recovery_history.append({
                    "node_id": node_id,
                    "strategy": strategy,
                    "outcome": outcome,
                    "ts": time.time()
                })
                self._record.updated_at = time.time()
                self._persist_session()

    def _is_valid_transition(self, from_status: str, to_status: str) -> bool:
        allowed = _VALID_TRANSITIONS.get(from_status, set())
        return to_status in allowed

    def complete_session(self, final_result: str = "SUCCESS"):
        """Mark the entire session as complete and write episodic memory."""
        with self._lock:
            if self._record:
                self._record.status = final_result
                self._record.updated_at = time.time()
                self._persist_session()
                self._write_episodic_memory()
                self._legacy_update({"status": "STANDBY", "active_task_id": None})
                print(f"[TASK_STATE] Session {self._record.plan_id} completed: {final_result}")

    # ──────────────────────────────────────────────────────────────────────────
    # Episodic memory
    # ──────────────────────────────────────────────────────────────────────────

    def _write_episodic_memory(self):
        """Append a summary episode to the persistent episodic memory store."""
        if not self._record:
            return
        episodes = _safe_load(self._episodic_path, [])
        # Deduplicate by plan_id
        episodes = [e for e in episodes if e.get("plan_id") != self._record.plan_id]
        episode = {
            "plan_id": self._record.plan_id,
            "objective": self._record.objective,
            "intent": self._record.intent,
            "final_status": self._record.status,
            "node_count": len(self._record.nodes),
            "completed_nodes": sum(1 for n in self._record.nodes.values() if n.get("status") == "COMPLETED"),
            "failed_nodes": sum(1 for n in self._record.nodes.values() if n.get("status") == "FAILED"),
            "tool_history_count": len(self._record.tool_history),
            "error_count": len(self._record.error_history),
            "recovery_count": len(self._record.recovery_history),
            "created_at": self._record.created_at,
            "completed_at": time.time(),
        }
        episodes.append(episode)
        # Keep last 200 episodes
        if len(episodes) > 200:
            episodes = episodes[-200:]
        _atomic_write(self._episodic_path, episodes)
        print(f"[EPISODIC_MEMORY] Episode recorded: {self._record.plan_id}")

    def retrieve_episodic_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve most recent episodes for use in future planning/routing."""
        episodes = _safe_load(self._episodic_path, [])
        return episodes[-limit:]

    def find_similar_episodes(self, objective: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Find past episodes with similar objectives (simple keyword match)."""
        episodes = _safe_load(self._episodic_path, [])
        keywords = set(objective.lower().split())
        scored = []
        for ep in episodes:
            ep_words = set(ep.get("objective", "").lower().split())
            overlap = len(keywords & ep_words)
            if overlap > 0:
                scored.append((overlap, ep))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored[:limit]]

    # ──────────────────────────────────────────────────────────────────────────
    # Plan management (backward compat)
    # ──────────────────────────────────────────────────────────────────────────

    def save_active_plan(self, tasks: List[Dict[str, Any]]):
        _atomic_write(self._plan_path, {"tasks": tasks})

    def load_active_plan(self) -> List[Dict[str, Any]]:
        return _safe_load(self._plan_path, {}).get("tasks", [])

    def register_completed_task(self, task: Dict[str, Any]):
        completed = _safe_load(self._completed_path, [])
        completed.append({**task, "registered_at": time.time()})
        _atomic_write(self._completed_path, completed)

    def register_failed_task(self, task: Dict[str, Any]):
        failed = _safe_load(self._failed_path, [])
        failed.append({**task, "registered_at": time.time()})
        _atomic_write(self._failed_path, failed)

    # ──────────────────────────────────────────────────────────────────────────
    # Legacy state (backward compat with computer_use_agent.py)
    # ──────────────────────────────────────────────────────────────────────────

    def get_state(self) -> Dict[str, Any]:
        data = _safe_load(self._state_path, {
            "current_objective": "None", "status": "STANDBY", "active_task_id": None
        })
        if self._record:
            data["variables"] = self._record.variables
        return data

    def update_state(self, updates: Dict[str, Any]):
        self._legacy_update(updates)

    def _legacy_update(self, updates: Dict[str, Any]):
        state = _safe_load(self._state_path, {"current_objective": "None", "status": "STANDBY"})
        state.update(updates)
        _atomic_write(self._state_path, state)

    # ──────────────────────────────────────────────────────────────────────────
    # Variable injection (Phase 36.2 — preserved)
    # ──────────────────────────────────────────────────────────────────────────

    def set_variable(self, name: str, value: Any):
        with self._lock:
            if self._record:
                self._record.variables[name] = value
                self._persist_session()
            # Also persist in legacy state for compat
            state = self.get_state()
            state.setdefault("variables", {})[name] = value
            _atomic_write(self._state_path, state)

    def substitute_variables(self, task_node: Dict[str, Any]) -> Dict[str, Any]:
        variables = {}
        if self._record:
            variables = self._record.variables
        else:
            variables = self.get_state().get("variables", {})

        def replace_val(v):
            if isinstance(v, str):
                for name, val in variables.items():
                    placeholder = "{{" + name + "}}"
                    if placeholder in v:
                        v = v.replace(placeholder, str(val))
            elif isinstance(v, dict):
                return {k: replace_val(val) for k, val in v.items()}
            elif isinstance(v, list):
                return [replace_val(item) for item in v]
            return v

        return replace_val(task_node)


# Module singleton
task_state_controller = TaskStateController()
