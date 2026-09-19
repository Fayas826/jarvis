"""
Phase 37.3 — Persistent Working Memory
======================================

Short-term execution state blackboard holding session-specific values:
- temporary execution variables (extracted parameters)
- current working directory
- clipboard cache
- session context memories queried from action_memory.py
"""

import os
import json
from typing import Dict, Any, Optional
from core.orchestration.task_state import _atomic_write, _safe_load

class WorkingMemory:
    """Session-specific working blackboard memory."""
    
    def __init__(self, memory_file: str = r"c:\jarvis AI\jarvis\scratch\working_memory.json"):
        self.memory_file = memory_file
        self.data = {
            "variables": {},
            "environment_state": {},
            "active_recipe": None,
            "session_context": {}
        }
        self.load()

    def load(self):
        self.data = _safe_load(self.memory_file, self.data)

    def save(self):
        _atomic_write(self.memory_file, self.data)

    def set_variable(self, name: str, value: Any):
        self.data["variables"][name] = value
        self.save()

    def get_variable(self, name: str, default: Any = None) -> Any:
        return self.data["variables"].get(name, default)

    def clear(self):
        self.data = {
            "variables": {},
            "environment_state": {},
            "active_recipe": None,
            "session_context": {}
        }
        self.save()

working_memory = WorkingMemory()
