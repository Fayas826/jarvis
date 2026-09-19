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


# Module-level singletons — imported by orchestration layer
conversational_context = ConversationalContext(max_turns=20)
task_memory = TaskMemory()
grounding_cache = GroundingPatternCache()
