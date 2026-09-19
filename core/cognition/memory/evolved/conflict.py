import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

_MEM_DIR = Path("project_memory") / "evolved"
_MEM_DIR.mkdir(parents=True, exist_ok=True)
_CONFLICT_PATH = _MEM_DIR / "memory_conflicts.json"

class ConflictResolution:
    LATEST_WINS = "LATEST_WINS"
    TRUSTED_WINS = "TRUSTED_WINS"
    BOTH_KEPT = "BOTH_KEPT"
    USER_WINS = "USER_WINS"

class MemoryConflictResolver:
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
            system_logger.log('ERROR', 'conflict', f'Unhandled exception: {e}')
            self._log = []

    def _save_log(self):
        try:
            with open(_CONFLICT_PATH, "w", encoding="utf-8") as f:
                json.dump(self._log[-self.MAX_LOG:], f, indent=2)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'conflict', f'Unhandled exception: {e}')
            pass

    def resolve(self, key: str, existing_value: Any, existing_trusted: bool, new_value: Any, new_trusted: bool, is_user_correction: bool = False) -> Tuple[Any, str]:
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

        return winner, resolution

    def conflict_count(self) -> int:
        with self._lock:
            return len(self._log)

    def get_recent_conflicts(self, n: int = 10) -> List[Dict]:
        with self._lock:
            return list(self._log[-n:])
