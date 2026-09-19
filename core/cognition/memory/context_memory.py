"""
Phase 34.4 — Context Memory Layer
Adds short-term conversational context, task memory, grounding pattern cache,
and confidence-weighted expiry.

SAFETY NOTE: This layer is advisory only.
- Memory NEVER overrides current screen state.
- Memory NEVER overrides safety policy.
- Memory NEVER bypasses confirmation gates.
"""

import time
import threading
from typing import List, Dict, Any, Optional
from collections import deque


class ConversationalContext:
    """Sliding window of recent conversation turns for pronoun/reference resolution."""

    def __init__(self, max_turns: int = 20):
        self._lock = threading.Lock()
        self._turns: deque = deque(maxlen=max_turns)

    def add_turn(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a conversation turn. role: 'user' | 'assistant'"""
        with self._lock:
            self._turns.append({
                "role": role,
                "content": content,
                "timestamp": time.time(),
                "metadata": metadata or {}
            })

    def get_recent(self, n: int = 5) -> List[Dict[str, Any]]:
        """Return the last n turns."""
        with self._lock:
            turns = list(self._turns)
            return turns[-n:] if len(turns) >= n else turns

    def get_context_string(self, n: int = 5) -> str:
        """Return a formatted context string for LLM injection."""
        turns = self.get_recent(n)
        lines = []
        for t in turns:
            prefix = "User" if t["role"] == "user" else "JARVIS"
            lines.append(f"{prefix}: {t['content']}")
        return "\n".join(lines)

    def clear(self):
        with self._lock:
            self._turns.clear()

    def __len__(self):
        return len(self._turns)


class TaskMemory:
    """Stores per-task execution state, inputs, outputs, and progress with TTL expiry."""

    TASK_TTL_SECONDS = 1800  # 30 minutes

    def __init__(self):
        self._lock = threading.Lock()
        self._tasks: Dict[str, Dict] = {}

    def record_task(self, task_id: str, objective: str, plan: List[Dict],
                    risk_level: str = "LOW"):
        """Register a new task into working memory."""
        with self._lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "objective": objective,
                "plan": plan,
                "risk_level": risk_level,
                "steps_completed": [],
                "steps_failed": [],
                "outputs": {},
                "status": "IN_PROGRESS",
                "confidence": 1.0,
                "created_at": time.time(),
                "updated_at": time.time(),
            }
            print(f"[TASK_MEMORY] Registered task: {task_id} — '{objective[:60]}'")

    def record_step_result(self, task_id: str, step_id: str, success: bool,
                           output: Any = None, failure_reason: str = ""):
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task["updated_at"] = time.time()
            if success:
                task["steps_completed"].append({
                    "step_id": step_id,
                    "output": output,
                    "timestamp": time.time()
                })
            else:
                task["steps_failed"].append({
                    "step_id": step_id,
                    "reason": failure_reason,
                    "timestamp": time.time()
                })
                # Decay confidence on failure
                task["confidence"] = max(0.1, task["confidence"] - 0.15)

    def record_output(self, task_id: str, key: str, value: Any):
        """Store a named output value for later steps to use."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task["outputs"][key] = value
                task["updated_at"] = time.time()

    def get_task(self, task_id: str) -> Optional[Dict]:
        with self._lock:
            self._expire()
            return self._tasks.get(task_id)

    def complete_task(self, task_id: str, status: str = "COMPLETED"):
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task["status"] = status
                task["updated_at"] = time.time()
                print(f"[TASK_MEMORY] Task {task_id} marked: {status}")

    def _expire(self):
        now = time.time()
        expired = [k for k, v in self._tasks.items()
                   if now - v["created_at"] > self.TASK_TTL_SECONDS]
        for k in expired:
            del self._tasks[k]
            print(f"[TASK_MEMORY] Expired task: {k}")

    def active_count(self) -> int:
        with self._lock:
            self._expire()
            return len(self._tasks)


class GroundingPatternCache:
    """Caches successful element grounding patterns per application context.

    ADVISORY ONLY — never execute an old coordinate without re-validating.
    """

    CACHE_TTL_SECONDS = 300  # 5 minutes — coordinates stale quickly

    def __init__(self):
        self._lock = threading.Lock()
        self._cache: Dict[str, Dict] = {}  # key: "{app}::{instruction}"

    def _make_key(self, app_title: str, instruction: str) -> str:
        return f"{app_title.lower().strip()}::{instruction.lower().strip()}"

    def record(self, app_title: str, instruction: str, element_source: str,
               confidence: float, bbox: List[int], center: List[int]):
        """Record a successful grounding result."""
        if confidence < 0.60:
            return  # Don't cache weak matches
        key = self._make_key(app_title, instruction)
        with self._lock:
            self._cache[key] = {
                "app_title": app_title,
                "instruction": instruction,
                "element_source": element_source,
                "confidence": confidence,
                "bbox": bbox,
                "center": center,
                "recorded_at": time.time(),
                "hit_count": self._cache.get(key, {}).get("hit_count", 0) + 1
            }

    def lookup(self, app_title: str, instruction: str) -> Optional[Dict]:
        """Look up a cached grounding result. Returns None if expired."""
        key = self._make_key(app_title, instruction)
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            age = time.time() - entry["recorded_at"]
            if age > self.CACHE_TTL_SECONDS:
                del self._cache[key]
                print(f"[GROUNDING_CACHE] Expired entry for: '{instruction}' in '{app_title}'")
                return None
            print(f"[GROUNDING_CACHE] Cache hit: '{instruction}' in '{app_title}' "
                  f"(source: {entry['element_source']}, age: {age:.0f}s)")
            return entry

    def invalidate(self, app_title: str):
        """Invalidate all cached entries for a given application (e.g. on navigation)."""
        prefix = app_title.lower().strip()
        with self._lock:
            stale = [k for k in self._cache if k.startswith(prefix)]
            for k in stale:
                del self._cache[k]
            if stale:
                print(f"[GROUNDING_CACHE] Invalidated {len(stale)} entries for app: '{app_title}'")

    def cache_size(self) -> int:
        with self._lock:
            return len(self._cache)


# ---------------------------------------------------------------------------
# Phase 35.4 — AppActionMemory
# ---------------------------------------------------------------------------

class AppActionMemory:
    """
    Per-app, per-action, per-tool outcome history for adaptive routing.

    Records whether a given tool (dom/uia/ocr/vlm/pyautogui) succeeded or
    failed for a specific action type in a specific application, so the
    ToolRouter can bias future candidate scoring based on real history.

    ADVISORY ONLY — never overrides current evidence or safety policy.
    Thread-safe.
    """

    MIN_OBSERVATIONS = 3      # need at least this many before trusting preference
    MAX_HISTORY_PER_KEY = 50  # cap per (app, action, tool) ring buffer

    def __init__(self):
        self._lock = threading.Lock()
        # key: (app_name_lower, action_type_upper, tool_lower)
        # value: {"success": int, "fail": int, "total": int, "last_latency_ms": float}
        self._records: Dict[tuple, Dict] = {}

    def record(
        self,
        app_name: str,
        action_type: str,
        tool: str,
        success: bool,
        latency_ms: float = 0.0,
    ):
        """Record one execution outcome."""
        key = (app_name.lower().strip(), action_type.upper().strip(), tool.lower().strip())
        with self._lock:
            if key not in self._records:
                self._records[key] = {"success": 0, "fail": 0, "total": 0, "last_latency_ms": 0.0}
            rec = self._records[key]
            if success:
                rec["success"] += 1
            else:
                rec["fail"] += 1
            rec["total"] = min(rec["success"] + rec["fail"], self.MAX_HISTORY_PER_KEY)
            rec["last_latency_ms"] = latency_ms
        print(
            f"[APP_ACTION_MEM] {app_name}/{action_type}/{tool} "
            f"-> success={self._records[key]['success']} "
            f"fail={self._records[key]['fail']}"
        )

    def get_success_rate(self, app_name: str, action_type: str, tool: str) -> Optional[float]:
        """Returns success rate (0.0–1.0) or None if insufficient observations."""
        key = (app_name.lower().strip(), action_type.upper().strip(), tool.lower().strip())
        with self._lock:
            rec = self._records.get(key)
            if not rec or rec["total"] < self.MIN_OBSERVATIONS:
                return None
            total = rec["success"] + rec["fail"]
            return rec["success"] / total if total > 0 else None

    def get_preferred_tool(self, app_name: str, action_type: str) -> Optional[str]:
        """Returns the tool with the highest success rate for this app+action combo."""
        app_l = app_name.lower().strip()
        act_u = action_type.upper().strip()
        with self._lock:
            candidates = {
                key[2]: self._records[key]
                for key in self._records
                if key[0] == app_l and key[1] == act_u
            }
        if not candidates:
            return None
        # Filter to keys with sufficient observations
        qualified = {
            tool: rec for tool, rec in candidates.items()
            if (rec["success"] + rec["fail"]) >= self.MIN_OBSERVATIONS
        }
        if not qualified:
            return None
        best = max(
            qualified.items(),
            key=lambda kv: kv[1]["success"] / max(kv[1]["success"] + kv[1]["fail"], 1)
        )
        return best[0]

    def get_app_profile(self, app_name: str) -> Dict[str, Any]:
        """Returns the full tool preference map for an app."""
        app_l = app_name.lower().strip()
        profile: Dict[str, Any] = {}
        with self._lock:
            for key, rec in self._records.items():
                if key[0] != app_l:
                    continue
                action = key[1]
                tool = key[2]
                total = rec["success"] + rec["fail"]
                rate = rec["success"] / total if total > 0 else 0.0
                if action not in profile:
                    profile[action] = {}
                profile[action][tool] = {
                    "success_rate": round(rate, 3),
                    "observations": total,
                    "last_latency_ms": rec["last_latency_ms"],
                }
        return profile

    def observation_count(self, app_name: str, action_type: str, tool: str) -> int:
        key = (app_name.lower().strip(), action_type.upper().strip(), tool.lower().strip())
        with self._lock:
            rec = self._records.get(key)
            if not rec:
                return 0
            return rec["success"] + rec["fail"]


# Module-level singletons — imported by orchestration layer
conversational_context = ConversationalContext(max_turns=20)
task_memory = TaskMemory()
grounding_cache = GroundingPatternCache()
app_action_memory = AppActionMemory()
