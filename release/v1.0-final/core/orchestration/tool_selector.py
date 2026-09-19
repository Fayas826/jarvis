"""
Phase 36.5A — Adaptive Tool Selector
=====================================

Learns which tool (dom, uia, ocr, cv, vlm, pyautogui, powershell, python)
works best for each (app_name, action_type) combination by tracking outcomes.

Design:
- Success/failure counts persisted to disk (atomic writes)
- Confidence score = successes / (successes + failures + 1)
- Never overrides Safety Kernel decisions
- Never allows learned memory to reduce risk_level

VRAM: 0 GB added (stdlib only)
"""

import os
import json
import time
import threading
import tempfile
from typing import Dict, Any, List, Optional, Tuple

_TOOL_DB_PATH = os.path.join("project_memory", "tool_learning.json")
_LOCK = threading.Lock()

_TOOL_PRIORITY_DEFAULTS = {
    "browser": ["dom", "ocr", "cv", "vlm"],
    "desktop": ["uia", "ocr", "cv", "vlm"],
    "file":    ["python", "powershell"],
    "terminal":["powershell", "python"],
    "unknown": ["uia", "ocr", "dom", "cv", "vlm"],
}


def _atomic_write(path: str, data: Any):
    dir_ = os.path.dirname(path) or "."
    os.makedirs(dir_, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'tool_selector', f'Unhandled exception: {e}')
        try:
            os.unlink(tmp)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'tool_selector', f'Unhandled exception: {e}')
            pass
        raise


def _safe_load(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'tool_selector', f'Unhandled exception: {e}')
        return default


class AdaptiveToolSelector:
    """
    Selects and ranks tools for a given (context_type, action_type) based on
    historical success rates learned from execution outcomes.
    """

    def __init__(self):
        self._db: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        self._db = _safe_load(_TOOL_DB_PATH, {})

    def _persist(self):
        _atomic_write(_TOOL_DB_PATH, self._db)

    def _key(self, app_context: str, action_type: str) -> str:
        return f"{app_context.lower()}::{action_type.lower()}"

    def record_outcome(self, app_context: str, action_type: str, tool: str, success: bool):
        """Record a tool outcome to update learned success rates."""
        with _LOCK:
            key = self._key(app_context, action_type)
            entry = self._db.setdefault(key, {})
            tool_stats = entry.setdefault(tool, {"successes": 0, "failures": 0, "last_used": 0})
            if success:
                tool_stats["successes"] += 1
            else:
                tool_stats["failures"] += 1
            tool_stats["last_used"] = time.time()
            self._persist()

    def get_success_rate(self, app_context: str, action_type: str, tool: str) -> Optional[float]:
        key = self._key(app_context, action_type)
        tool_stats = self._db.get(key, {}).get(tool)
        if not tool_stats:
            return None
        total = tool_stats["successes"] + tool_stats["failures"]
        if total == 0:
            return None
        return tool_stats["successes"] / total

    def rank_tools(self, app_context: str, action_type: str, context_type: str = "unknown") -> List[str]:
        """
        Returns tools ranked by learned success rate.
        Falls back to default priority order if no history.
        """
        defaults = _TOOL_PRIORITY_DEFAULTS.get(context_type, _TOOL_PRIORITY_DEFAULTS["unknown"])
        key = self._key(app_context, action_type)
        stats = self._db.get(key, {})

        if not stats:
            return defaults

        scored = []
        for tool in defaults:
            ts = stats.get(tool, {})
            successes = ts.get("successes", 0)
            failures = ts.get("failures", 0)
            total = successes + failures
            rate = successes / (total + 1e-6)
            scored.append((rate, tool))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored]

    def best_tool(self, app_context: str, action_type: str, context_type: str = "unknown") -> str:
        """Returns the single best tool for this context."""
        ranked = self.rank_tools(app_context, action_type, context_type)
        return ranked[0] if ranked else "uia"


adaptive_tool_selector = AdaptiveToolSelector()
