import threading
import time
import uuid
from typing import Any, Dict, List, Optional

class SessionMemory:
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
        if len(str(value)) > self.MAX_VALUE_BYTES:
            value = str(value)[:self.MAX_VALUE_BYTES] + "...[TRUNCATED]"
        with self._lock:
            if len(self._store) >= self.MAX_KEYS:
                evict_key = next(iter(self._store))
                del self._store[evict_key]
            self._store[key] = {
                "value": value,
                "trusted": trusted,
                "written_at": time.time(),
            }

    def get(self, key: str, trusted_only: bool = False) -> Optional[Any]:
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
        with self._lock:
            self._store.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._store)
