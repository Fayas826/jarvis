import threading
import time
from collections import deque
from typing import Dict, List, Optional
from core.cognition.memory.evolved.privacy import PrivacyGuard
from core.cognition.memory.evolved.conflict import MemoryConflictResolver

class EvolvingConversationalContext:
    TURN_TTL_SECONDS = 3600
    MAX_TURNS = 30

    def __init__(self, privacy_guard: Optional[PrivacyGuard] = None, conflict_resolver: Optional[MemoryConflictResolver] = None):
        self._lock = threading.Lock()
        self._turns: deque = deque(maxlen=self.MAX_TURNS)
        self._privacy = privacy_guard or PrivacyGuard()
        self._resolver = conflict_resolver or MemoryConflictResolver()

    def add_turn(self, role: str, content: str, source: str = "user", metadata: Optional[Dict] = None):
        guard_result = self._privacy.check(content, source)
        trusted = guard_result["trusted"]
        expires_at = time.time() + self.TURN_TTL_SECONDS

        with self._lock:
            self._turns.append({
                "role": role,
                "content": content,
                "source": source,
                "trusted": trusted,
                "injection_risk": guard_result["injection_risk"],
                "timestamp": time.time(),
                "expires_at": expires_at,
                "metadata": metadata or {},
            })

    def get_recent(self, n: int = 5, trusted_only: bool = False) -> List[Dict]:
        now = time.time()
        with self._lock:
            turns = list(self._turns)
        valid = [t for t in turns if t.get("expires_at", 0) > now]
        if trusted_only:
            valid = [t for t in valid if t.get("trusted", True)]
        return valid[-n:] if len(valid) >= n else valid

    def get_context_string(self, n: int = 5, trusted_only: bool = False) -> str:
        turns = self.get_recent(n, trusted_only=trusted_only)
        lines = []
        for t in turns:
            prefix = "User" if t["role"] == "user" else "JARVIS"
            lines.append(f"{prefix}: {t['content']}")
        return "\n".join(lines)

    def get_last_user_entity(self) -> Optional[str]:
        turns = self.get_recent(3, trusted_only=True)
        for t in reversed(turns):
            if t["role"] == "user":
                words = t["content"].split()
                for w in words:
                    if w and (w[0].isupper() or w.startswith('"') or w.startswith("'")):
                        return w.strip('"\'')
        return None

    def clear(self):
        with self._lock:
            self._turns.clear()

    def __len__(self):
        now = time.time()
        with self._lock:
            return sum(1 for t in self._turns if t.get("expires_at", 0) > now)
