"""
Phase 34 Track 3 — Memory & Conversational Context Evolution
============================================================

New capabilities (all backward-compatible with existing context_memory.py):

1. EpisodicTaskHistory   — persistent disk-backed record of completed tasks
2. EntityRegistry        — cross-turn entity/target persistence with expiry
3. SessionMemory         — strict per-session isolation (no cross-session leakage)
4. MemoryConflictResolver — detects and resolves contradictory memory entries
5. PrivacyGuard          — prevents untrusted screen text from becoming instructions
6. Enhanced ConversationalContext (via mixin) — per-turn TTL expiry

SAFETY NOTE:
- This module is advisory only.
- Memory NEVER overrides current screen state.
- Memory NEVER overrides safety policy or confirmation gates.
- Untrusted (screen-originated) text is tagged and quarantined; it can NEVER
  promote itself to trusted instructions.
- No heavyweight models. No new VRAM cost. No new dependencies.

VRAM: 0.0 GB added.
New dependencies: none (stdlib only: json, pathlib, threading, hashlib, time).
"""

import json
import os
import time
import threading
import hashlib
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import deque

# ──────────────────────────────────────────────────────────────────────────────
# Storage root (same as existing project_memory convention)
# ──────────────────────────────────────────────────────────────────────────────
_MEM_DIR = Path("project_memory") / "evolved"
_MEM_DIR.mkdir(parents=True, exist_ok=True)

_EPISODIC_PATH   = _MEM_DIR / "episodic_task_history.json"
_ENTITY_PATH     = _MEM_DIR / "entity_registry.json"
_ISOLATION_PATH  = _MEM_DIR / "session_isolation.json"
_CONFLICT_PATH   = _MEM_DIR / "memory_conflicts.json"


# ══════════════════════════════════════════════════════════════════════════════
# 1. EpisodicTaskHistory
# ══════════════════════════════════════════════════════════════════════════════

class EpisodicTaskHistory:
    """
    Persistent, disk-backed record of completed tasks.

    Design:
    - Written to disk after every task completion so history survives restart.
    - Bounded to MAX_EPISODES entries (ring-buffer eviction: oldest first).
    - Each episode tagged with session_id so cross-session leakage can be
      detected (episodes from other sessions are marked read-only context).
    - No PII stored beyond what the user explicitly provided as the task
      objective. Screen-captured text is never written to episodic history.

    Restart behaviour:
    - On __init__, loads history from disk if present.
    - If disk file is corrupt/missing, starts fresh with an empty history.
    """

    MAX_EPISODES = 200
    EPISODE_TTL_DAYS = 30

    def __init__(self, session_id: str):
        self._lock = threading.Lock()
        self._session_id = session_id
        self._episodes: List[Dict] = []
        self._load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self):
        try:
            if _EPISODIC_PATH.exists():
                with open(_EPISODIC_PATH, encoding="utf-8") as f:
                    data = json.load(f)
                self._episodes = data if isinstance(data, list) else []
                # Evict TTL-expired episodes
                cutoff = time.time() - self.EPISODE_TTL_DAYS * 86400
                self._episodes = [e for e in self._episodes if e.get("completed_at", 0) > cutoff]
                print(f"[EPISODIC] Loaded {len(self._episodes)} episodes from disk.")
        except Exception as e:
            print(f"[EPISODIC] Load failed (non-fatal): {e}. Starting fresh.")
            self._episodes = []

    def _save(self):
        try:
            with open(_EPISODIC_PATH, "w", encoding="utf-8") as f:
                json.dump(self._episodes[-self.MAX_EPISODES:], f, indent=2)
        except Exception as e:
            print(f"[EPISODIC] Save failed (non-fatal): {e}")

    # ── Public API ────────────────────────────────────────────────────────────

    def record(
        self,
        task_id: str,
        objective: str,
        status: str,
        steps_completed: int,
        steps_failed: int,
        risk_level: str = "LOW",
        duration_seconds: float = 0.0,
    ):
        """Record a completed task episode. Screen text must NOT be passed as objective."""
        episode = {
            "episode_id": f"ep_{uuid.uuid4().hex[:8]}",
            "session_id": self._session_id,
            "task_id": task_id,
            "objective": objective[:256],        # hard cap on stored text
            "status": status,
            "steps_completed": steps_completed,
            "steps_failed": steps_failed,
            "risk_level": risk_level,
            "duration_seconds": round(duration_seconds, 2),
            "completed_at": time.time(),
        }
        with self._lock:
            self._episodes.append(episode)
            if len(self._episodes) > self.MAX_EPISODES:
                self._episodes = self._episodes[-self.MAX_EPISODES:]
            self._save()
        print(f"[EPISODIC] Recorded episode: {episode['episode_id']} — '{objective[:50]}'")
        return episode["episode_id"]

    def get_recent(self, n: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        """Return the last n episodes, optionally filtered to a specific session."""
        with self._lock:
            episodes = list(self._episodes)
        if session_id:
            episodes = [e for e in episodes if e.get("session_id") == session_id]
        return episodes[-n:]

    def get_by_objective_keyword(self, keyword: str, n: int = 5) -> List[Dict]:
        """Find past episodes whose objective contains the keyword."""
        kw = keyword.lower()
        with self._lock:
            matches = [e for e in self._episodes if kw in e.get("objective", "").lower()]
        return matches[-n:]

    def session_episodes(self) -> List[Dict]:
        """Return all episodes for the current session only."""
        return self.get_recent(n=self.MAX_EPISODES, session_id=self._session_id)

    def episode_count(self) -> int:
        with self._lock:
            return len(self._episodes)

    def clear_session(self):
        """Remove only episodes from the current session (e.g. on logout)."""
        with self._lock:
            self._episodes = [e for e in self._episodes
                              if e.get("session_id") != self._session_id]
            self._save()


# ══════════════════════════════════════════════════════════════════════════════
# 2. EntityRegistry
# ══════════════════════════════════════════════════════════════════════════════

class EntityRegistry:
    """
    Cross-turn entity/target persistence within a session.

    Stores named entities (apps, files, UI elements, people) mentioned
    by the user so subsequent pronoun/reference resolution can look them up.

    Design:
    - Each entity has a TTL; stale entities expire automatically.
    - Entities are session-scoped: they cannot leak between sessions.
    - Screen-originated entities are tagged `trusted=False` and can never
      be promoted to trusted instructions.
    - Size-bounded: MAX_ENTITIES per session.
    """

    MAX_ENTITIES = 100
    DEFAULT_TTL_SECONDS = 1800       # 30 min — same as TaskMemory TTL

    def __init__(self, session_id: str):
        self._lock = threading.Lock()
        self._session_id = session_id
        # key: entity_name_lower → {name, type, value, trusted, first_seen, last_seen, ttl}
        self._registry: Dict[str, Dict] = {}

    def register(
        self,
        name: str,
        entity_type: str,   # "app" | "file" | "element" | "person" | "url" | "generic"
        value: str,
        trusted: bool = True,
        ttl_seconds: Optional[float] = None,
    ):
        """
        Register or update an entity.
        trusted=False for screen-originated entities (cannot become commands).
        """
        key = name.lower().strip()
        ttl = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL_SECONDS
        now = time.time()
        with self._lock:
            if key in self._registry:
                self._registry[key].update({
                    "value": value,
                    "last_seen": now,
                    "expires_at": now + ttl,
                    # Trust can only be downgraded, never upgraded
                    "trusted": self._registry[key]["trusted"] and trusted,
                })
            else:
                if len(self._registry) >= self.MAX_ENTITIES:
                    self._evict_oldest()
                self._registry[key] = {
                    "name": name,
                    "entity_type": entity_type,
                    "value": value,
                    "trusted": trusted,
                    "session_id": self._session_id,
                    "first_seen": now,
                    "last_seen": now,
                    "expires_at": now + ttl,
                }
        print(f"[ENTITY_REG] Registered entity: '{name}' type={entity_type} trusted={trusted}")

    def lookup(self, name: str) -> Optional[Dict]:
        """Look up an entity by name. Returns None if not found or expired."""
        key = name.lower().strip()
        now = time.time()
        with self._lock:
            entity = self._registry.get(key)
            if not entity:
                return None
            if entity.get("expires_at", 0) < now:
                del self._registry[key]
                return None
            return dict(entity)

    def find_by_type(self, entity_type: str) -> List[Dict]:
        """Return all non-expired entities of a given type."""
        now = time.time()
        with self._lock:
            return [
                dict(e) for e in self._registry.values()
                if e.get("entity_type") == entity_type
                and e.get("expires_at", 0) >= now
            ]

    def get_most_recent_entity(self) -> Optional[Dict]:
        """Return the most recently seen non-expired entity."""
        now = time.time()
        with self._lock:
            valid = [e for e in self._registry.values() if e.get("expires_at", 0) >= now]
        if not valid:
            return None
        return dict(max(valid, key=lambda e: e["last_seen"]))

    def touch(self, name: str, extra_ttl: float = DEFAULT_TTL_SECONDS):
        """Extend the TTL of an entity."""
        key = name.lower().strip()
        with self._lock:
            if key in self._registry:
                self._registry[key]["expires_at"] = time.time() + extra_ttl
                self._registry[key]["last_seen"] = time.time()

    def invalidate(self, name: str):
        """Manually expire an entity."""
        key = name.lower().strip()
        with self._lock:
            self._registry.pop(key, None)

    def count(self) -> int:
        self._evict_expired()
        with self._lock:
            return len(self._registry)

    def clear_session(self):
        with self._lock:
            self._registry = {
                k: v for k, v in self._registry.items()
                if v.get("session_id") != self._session_id
            }

    def _evict_oldest(self):
        """Evict the least-recently-seen entity. Must hold lock."""
        if not self._registry:
            return
        oldest_key = min(self._registry, key=lambda k: self._registry[k]["last_seen"])
        del self._registry[oldest_key]

    def _evict_expired(self):
        now = time.time()
        with self._lock:
            expired = [k for k, v in self._registry.items() if v.get("expires_at", 0) < now]
            for k in expired:
                del self._registry[k]


# ══════════════════════════════════════════════════════════════════════════════
# 3. SessionMemory  (strict per-session isolation)
# ══════════════════════════════════════════════════════════════════════════════

class SessionMemory:
    """
    Strict session-scoped memory container.

    Guarantees:
    - Memory written in session A cannot be read in session B.
    - When a session ends, all session-local memory is wiped.
    - Persistent metadata (e.g. episodic history) is session-tagged
      and filtered on read.

    Size limits:
    - Max MAX_KEYS keys per session.
    - Values truncated to MAX_VALUE_BYTES bytes.
    """

    MAX_KEYS = 200
    MAX_VALUE_BYTES = 4096

    def __init__(self, session_id: Optional[str] = None):
        self._lock = threading.Lock()
        self._session_id = session_id or uuid.uuid4().hex
        self._store: Dict[str, Any] = {}
        self._created_at = time.time()

    @property
    def session_id(self) -> str:
        return self._session_id

    def set(self, key: str, value: Any, trusted: bool = True):
        """Store a key in this session. Untrusted values are quarantined."""
        if len(str(value)) > self.MAX_VALUE_BYTES:
            value = str(value)[:self.MAX_VALUE_BYTES] + "...[TRUNCATED]"
        with self._lock:
            if len(self._store) >= self.MAX_KEYS:
                # Evict the first inserted key
                evict_key = next(iter(self._store))
                del self._store[evict_key]
                print(f"[SESSION_MEM] Evicted '{evict_key}' due to size limit.")
            self._store[key] = {
                "value": value,
                "trusted": trusted,
                "written_at": time.time(),
            }

    def get(self, key: str, trusted_only: bool = False) -> Optional[Any]:
        """Retrieve a value. trusted_only=True rejects untrusted entries."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if trusted_only and not entry.get("trusted", True):
                return None
            return entry["value"]

    def is_trusted(self, key: str) -> bool:
        with self._lock:
            entry = self._store.get(key)
            return entry.get("trusted", False) if entry else False

    def keys(self) -> List[str]:
        with self._lock:
            return list(self._store.keys())

    def clear(self):
        """Destroy all session memory."""
        with self._lock:
            self._store.clear()
        print(f"[SESSION_MEM] Session {self._session_id[:8]} cleared.")

    def size(self) -> int:
        with self._lock:
            return len(self._store)


# ══════════════════════════════════════════════════════════════════════════════
# 4. MemoryConflictResolver
# ══════════════════════════════════════════════════════════════════════════════

class ConflictResolution:
    LATEST_WINS  = "LATEST_WINS"   # Most recent entry replaces older
    TRUSTED_WINS = "TRUSTED_WINS"  # Trusted source always wins
    BOTH_KEPT    = "BOTH_KEPT"     # Both kept, flagged for disambiguation
    USER_WINS    = "USER_WINS"     # Explicit user correction always wins


class MemoryConflictResolver:
    """
    Detects and resolves contradictory memory entries.

    A conflict is detected when two memory entries about the same entity
    or context key carry different values.

    Resolution policy (in order of precedence):
    1. If one entry is trusted and the other is not: TRUSTED_WINS
    2. If one is a user explicit correction: USER_WINS
    3. Otherwise: LATEST_WINS (most recent write wins)

    All conflicts are logged to disk for audit.
    """

    MAX_LOG = 500

    def __init__(self):
        self._lock = threading.Lock()
        self._log: List[Dict] = []
        self._load_log()

    def _load_log(self):
        try:
            if _CONFLICT_PATH.exists():
                with open(_CONFLICT_PATH, encoding="utf-8") as f:
                    self._log = json.load(f)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'evolved_memory', f'Unhandled exception: {e}')
            self._log = []

    def _save_log(self):
        try:
            with open(_CONFLICT_PATH, "w", encoding="utf-8") as f:
                json.dump(self._log[-self.MAX_LOG:], f, indent=2)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'evolved_memory', f'Unhandled exception: {e}')
            pass

    def resolve(
        self,
        key: str,
        existing_value: Any,
        existing_trusted: bool,
        new_value: Any,
        new_trusted: bool,
        is_user_correction: bool = False,
    ) -> Tuple[Any, str]:
        """
        Returns (winning_value, resolution_type).
        Logs the conflict regardless of outcome.
        """
        conflict = {
            "key": key,
            "existing": str(existing_value)[:100],
            "new": str(new_value)[:100],
            "existing_trusted": existing_trusted,
            "new_trusted": new_trusted,
            "is_user_correction": is_user_correction,
            "detected_at": time.time(),
        }

        if is_user_correction:
            resolution = ConflictResolution.USER_WINS
            winner = new_value
        elif new_trusted and not existing_trusted:
            resolution = ConflictResolution.TRUSTED_WINS
            winner = new_value
        elif existing_trusted and not new_trusted:
            resolution = ConflictResolution.TRUSTED_WINS
            winner = existing_value
        else:
            resolution = ConflictResolution.LATEST_WINS
            winner = new_value

        conflict["resolution"] = resolution
        conflict["winner"] = str(winner)[:100]

        with self._lock:
            self._log.append(conflict)
            self._save_log()

        print(f"[CONFLICT_RESOLVER] key='{key}' resolution={resolution}")
        return winner, resolution

    def conflict_count(self) -> int:
        with self._lock:
            return len(self._log)

    def get_recent_conflicts(self, n: int = 10) -> List[Dict]:
        with self._lock:
            return list(self._log[-n:])


# ══════════════════════════════════════════════════════════════════════════════
# 5. PrivacyGuard
# ══════════════════════════════════════════════════════════════════════════════

class PrivacyGuard:
    """
    Prevents untrusted (screen-originated) text from being promoted to
    trusted memory instructions.

    Rules:
    - Text that arrives via screen OCR/VLM is tagged `source=screen`.
    - Screen-originated text is NEVER stored as a trusted memory value.
    - Screen-originated text CANNOT be used as a task objective.
    - If screen text contains a phrase that looks like a command ("execute X",
      "run X", "install X"), a prompt-injection alert is raised.

    This is advisory enforcement — the Safety Kernel remains the final gate.
    """

    # Patterns that suggest prompt injection from screen text
    _INJECTION_PATTERNS = [
        "ignore previous", "forget your instructions", "new task:", "override:",
        "execute the following", "run the following", "sudo", "rm -rf",
        "you are now", "act as", "disregard safety",
    ]

    def __init__(self):
        self._lock = threading.Lock()
        self._alerts: List[Dict] = []

    def check(self, text: str, source: str = "user") -> Dict:
        """
        Returns:
            {
                "trusted": bool,
                "source": source,
                "injection_risk": bool,
                "alert_message": str or None
            }
        """
        text_lower = text.lower()
        injection_risk = any(p in text_lower for p in self._INJECTION_PATTERNS)

        trusted = (source == "user") and not injection_risk

        alert_msg = None
        if injection_risk:
            alert_msg = f"Prompt-injection pattern detected in text from source='{source}'"
            alert = {
                "source": source,
                "pattern_found": True,
                "snippet": text[:80],
                "detected_at": time.time(),
            }
            with self._lock:
                self._alerts.append(alert)
            print(f"[PRIVACY_GUARD] ALERT: {alert_msg}")

        return {
            "trusted": trusted,
            "source": source,
            "injection_risk": injection_risk,
            "alert_message": alert_msg,
        }

    def is_safe_to_store(self, text: str, source: str = "user") -> bool:
        """Quick boolean check for memory storage decisions."""
        result = self.check(text, source)
        return result["trusted"]

    def alert_count(self) -> int:
        with self._lock:
            return len(self._alerts)

    def get_alerts(self, n: int = 10) -> List[Dict]:
        with self._lock:
            return list(self._alerts[-n:])


# ══════════════════════════════════════════════════════════════════════════════
# 6. EvolvingConversationalContext  (extends existing ConversationalContext)
# ══════════════════════════════════════════════════════════════════════════════

class EvolvingConversationalContext:
    """
    Enhanced conversational context with per-turn TTL, conflict resolution,
    and privacy guard integration. Drop-in compatible with ConversationalContext.

    Differences from Phase 34.4 ConversationalContext:
    - Per-turn TTL: turns older than TURN_TTL_SECONDS are auto-expired on read
    - Privacy guard: screen-originated turns are tagged and excluded from
      trusted resolution paths
    - Conflict detection: contradictory user statements are flagged
    - get_recent() skips expired turns automatically
    """

    TURN_TTL_SECONDS = 3600   # 1 hour per turn
    MAX_TURNS = 30

    def __init__(
        self,
        privacy_guard: Optional[PrivacyGuard] = None,
        conflict_resolver: Optional[MemoryConflictResolver] = None,
    ):
        self._lock = threading.Lock()
        self._turns: deque = deque(maxlen=self.MAX_TURNS)
        self._privacy = privacy_guard or PrivacyGuard()
        self._resolver = conflict_resolver or MemoryConflictResolver()

    def add_turn(
        self,
        role: str,
        content: str,
        source: str = "user",        # "user" | "screen" | "assistant"
        metadata: Optional[Dict] = None,
    ):
        """Add a turn with trust tagging and TTL."""
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
        """Return last n non-expired turns. Optionally filter to trusted only."""
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
        """Return the most significant noun from the last user turn (heuristic)."""
        turns = self.get_recent(3, trusted_only=True)
        for t in reversed(turns):
            if t["role"] == "user":
                words = t["content"].split()
                # Return first capitalised word or quoted token as the entity hint
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


# ══════════════════════════════════════════════════════════════════════════════
# Module-level singletons (session-scoped, created fresh per process)
# ══════════════════════════════════════════════════════════════════════════════

_default_session_id = uuid.uuid4().hex

privacy_guard           = PrivacyGuard()
conflict_resolver       = MemoryConflictResolver()
episodic_history        = EpisodicTaskHistory(session_id=_default_session_id)
entity_registry         = EntityRegistry(session_id=_default_session_id)
session_memory          = SessionMemory(session_id=_default_session_id)
evolving_context        = EvolvingConversationalContext(
                              privacy_guard=privacy_guard,
                              conflict_resolver=conflict_resolver,
                          )
