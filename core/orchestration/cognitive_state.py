"""
Phase 37.1 — Cognitive State Manager
====================================

Manages persistent task state:
- active subgoals
- completed work
- pending work
- failures
- assumptions
- confidence
- context compression policy
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from core.orchestration.task_state import _atomic_write, _safe_load

class CognitiveStateManager:
    """Manages long-horizon cognitive state, subgoal tracking, and task assumptions."""
    
    def __init__(self, state_file: str = r"c:\jarvis AI\jarvis\scratch\cognitive_state.json"):
        self.state_file = state_file
        self.state = {
            "current_objective": "",
            "active_subgoal_id": None,
            "completed_subgoals": [],
            "pending_subgoals": [],
            "failed_attempts": {},  # subgoal_id -> count
            "assumptions": {},      # key -> value
            "confidence_score": 1.0,
            "history": [],          # list of state transitions
            "last_updated": time.time()
        }
        self.load()

    def load(self):
        self.state = _safe_load(self.state_file, self.state)

    def save(self):
        self.state["last_updated"] = time.time()
        _atomic_write(self.state_file, self.state)

    def initialize_goal(self, objective: str, subgoals: List[Dict[str, Any]]):
        self.state["current_objective"] = objective
        self.state["pending_subgoals"] = subgoals
        self.state["completed_subgoals"] = []
        self.state["active_subgoal_id"] = None
        self.state["failed_attempts"] = {}
        self.state["assumptions"] = {}
        self.state["confidence_score"] = 1.0
        self.state["history"] = [f"Goal initialized: {objective}"]
        self.save()

    def set_active_subgoal(self, subgoal_id: str):
        self.state["active_subgoal_id"] = subgoal_id
        self.state["history"].append(f"Active subgoal set to: {subgoal_id}")
        self.save()

    def mark_subgoal_complete(self, subgoal_id: str):
        # Move from pending to completed
        subgoal = None
        pending = []
        for sg in self.state["pending_subgoals"]:
            if sg.get("id") == subgoal_id:
                subgoal = sg
            else:
                pending.append(sg)
        
        self.state["pending_subgoals"] = pending
        if subgoal:
            subgoal["status"] = "COMPLETED"
            subgoal["completed_at"] = time.time()
            self.state["completed_subgoals"].append(subgoal)
        
        if self.state["active_subgoal_id"] == subgoal_id:
            self.state["active_subgoal_id"] = None

        self.state["history"].append(f"Subgoal completed: {subgoal_id}")
        self.save()

    def record_subgoal_failure(self, subgoal_id: str, reason: str):
        count = self.state["failed_attempts"].get(subgoal_id, 0) + 1
        self.state["failed_attempts"][subgoal_id] = count
        self.state["confidence_score"] = max(0.1, self.state["confidence_score"] - 0.15)
        self.state["history"].append(f"Subgoal failure: {subgoal_id} (Attempt {count}): {reason}")
        self.save()

    def set_assumption(self, key: str, value: Any):
        self.state["assumptions"][key] = value
        self.save()

    def get_assumption(self, key: str, default: Any = None) -> Any:
        return self.state["assumptions"].get(key, default)

    def get_context_compression_prompt(self) -> str:
        """Generates a compressed state prompt for LLM consumption to save token context."""
        summary = {
            "objective": self.state["current_objective"],
            "completed": [s.get("id") for s in self.state["completed_subgoals"]],
            "active": self.state["active_subgoal_id"],
            "failed_counts": self.state["failed_attempts"],
            "assumptions": self.state["assumptions"]
        }
        return json.dumps(summary)

cognitive_state_manager = CognitiveStateManager()
