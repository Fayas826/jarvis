"""
Phase 36.7B — Continuous Goal Monitor
======================================

Monitors progress toward the active session goal by tracking:
- Completed vs total nodes
- Time since last progress
- Stall detection (no progress in N seconds)
- Circular execution detection (same node attempted repeatedly)

This is an OBSERVATION layer only. It does NOT execute actions or modify the DAG.
"""

import time
from typing import Dict, Any, List, Optional


class GoalProgressStatus:
    ON_TRACK   = "ON_TRACK"
    STALLED    = "STALLED"
    REGRESSING = "REGRESSING"
    COMPLETE   = "COMPLETE"
    FAILED     = "FAILED"


class ContinuousGoalMonitor:
    """
    Tracks session goal progress and emits status signals.
    """

    def __init__(self, stall_timeout_seconds: float = 120.0, max_node_repeats: int = 3):
        self._stall_timeout = stall_timeout_seconds
        self._max_node_repeats = max_node_repeats
        self._last_progress_ts = time.time()
        self._node_attempt_counts: Dict[str, int] = {}
        self._completed_node_ids: set = set()
        self._total_nodes: int = 0

    def initialize(self, plan: List[Dict[str, Any]]):
        """Initialize monitor with the active plan."""
        self._total_nodes = len(plan)
        self._completed_node_ids = {
            t["task_id"] for t in plan if t.get("status") == "COMPLETED"
        }
        self._last_progress_ts = time.time()
        self._node_attempt_counts = {}

    def record_node_start(self, node_id: str):
        count = self._node_attempt_counts.get(node_id, 0) + 1
        self._node_attempt_counts[node_id] = count
        if count > self._max_node_repeats:
            print(f"[GOAL_MONITOR] WARNING: Node {node_id} attempted {count} times — possible loop.")

    def record_node_completed(self, node_id: str):
        self._completed_node_ids.add(node_id)
        self._last_progress_ts = time.time()

    def get_status(self) -> Dict[str, Any]:
        now = time.time()
        completed = len(self._completed_node_ids)
        total = self._total_nodes

        # Check completion
        if total > 0 and completed >= total:
            return self._status(GoalProgressStatus.COMPLETE, completed, total,
                                "All nodes completed.")

        # Check for stall
        time_since_progress = now - self._last_progress_ts
        if time_since_progress > self._stall_timeout:
            return self._status(GoalProgressStatus.STALLED, completed, total,
                                f"No progress for {time_since_progress:.0f}s.")

        # Check for circular execution
        repeat_nodes = [nid for nid, count in self._node_attempt_counts.items()
                       if count > self._max_node_repeats]
        if repeat_nodes:
            return self._status(GoalProgressStatus.REGRESSING, completed, total,
                                f"Repeated nodes detected: {repeat_nodes}")

        return self._status(GoalProgressStatus.ON_TRACK, completed, total,
                            f"Progress: {completed}/{total} nodes.")

    def _status(self, state: str, completed: int, total: int, detail: str) -> Dict[str, Any]:
        progress_pct = (completed / max(total, 1)) * 100
        return {
            "status": state,
            "completed_nodes": completed,
            "total_nodes": total,
            "progress_pct": round(progress_pct, 1),
            "detail": detail,
            "last_progress_ts": self._last_progress_ts,
        }

    def should_escalate(self) -> bool:
        """Returns True if the monitor recommends escalation (stall or regression)."""
        status = self.get_status()
        return status["status"] in (GoalProgressStatus.STALLED, GoalProgressStatus.REGRESSING)


goal_monitor = ContinuousGoalMonitor()
