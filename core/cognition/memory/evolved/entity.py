import threading
import time
from typing import Dict, List, Optional

class EntityRegistry:
    MAX_ENTITIES = 100
    DEFAULT_TTL_SECONDS = 1800

    def __init__(self, session_id: str):
        self._lock = threading.Lock()
        self._session_id = session_id
        self._registry: Dict[str, Dict] = {}

    def register(self, name: str, entity_type: str, value: str, trusted: bool = True, ttl_seconds: Optional[float] = None):
        key = name.lower().strip()
        ttl = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL_SECONDS
        now = time.time()
        with self._lock:
            if key in self._registry:
                self._registry[key].update({
                    "value": value,
                    "last_seen": now,
                    "expires_at": now + ttl,
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

    def lookup(self, name: str) -> Optional[Dict]:
        key = name.lower().strip()
        now = time.time()
        with self._lock:
            entity = self._registry.get(key)
            if not entity: return None
            if entity.get("expires_at", 0) < now:
                del self._registry[key]
                return None
            return dict(entity)

    def find_by_type(self, entity_type: str) -> List[Dict]:
        now = time.time()
        with self._lock:
            return [dict(e) for e in self._registry.values() if e.get("entity_type") == entity_type and e.get("expires_at", 0) >= now]

    def get_most_recent_entity(self) -> Optional[Dict]:
        now = time.time()
        with self._lock:
            valid = [e for e in self._registry.values() if e.get("expires_at", 0) >= now]
        if not valid: return None
        return dict(max(valid, key=lambda e: e["last_seen"]))

    def touch(self, name: str, extra_ttl: float = DEFAULT_TTL_SECONDS):
        key = name.lower().strip()
        with self._lock:
            if key in self._registry:
                self._registry[key]["expires_at"] = time.time() + extra_ttl
                self._registry[key]["last_seen"] = time.time()

    def invalidate(self, name: str):
        key = name.lower().strip()
        with self._lock:
            self._registry.pop(key, None)

    def count(self) -> int:
        self._evict_expired()
        with self._lock:
            return len(self._registry)

    def clear_session(self):
        with self._lock:
            self._registry = {k: v for k, v in self._registry.items() if v.get("session_id") != self._session_id}

    def _evict_oldest(self):
        if not self._registry: return
        oldest_key = min(self._registry, key=lambda k: self._registry[k]["last_seen"])
        del self._registry[oldest_key]

    def _evict_expired(self):
        now = time.time()
        with self._lock:
            expired = [k for k, v in self._registry.items() if v.get("expires_at", 0) < now]
            for k in expired: del self._registry[k]
