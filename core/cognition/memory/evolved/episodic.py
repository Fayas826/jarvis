import json
import time
import threading
import uuid
from pathlib import Path
from typing import Dict, List, Optional

_MEM_DIR = Path("project_memory") / "evolved"
_MEM_DIR.mkdir(parents=True, exist_ok=True)
_EPISODIC_PATH = _MEM_DIR / "episodic_task_history.json"

class EpisodicTaskHistory:
    MAX_EPISODES = 200
    EPISODE_TTL_DAYS = 30

    def __init__(self, session_id: str):
        self._lock = threading.Lock()
        self._session_id = session_id
        self._episodes: List[Dict] = []
        self._load()

    def _load(self):
        try:
            if _EPISODIC_PATH.exists():
                with open(_EPISODIC_PATH, encoding="utf-8") as f:
                    data = json.load(f)
                self._episodes = data if isinstance(data, list) else []
                cutoff = time.time() - self.EPISODE_TTL_DAYS * 86400
                self._episodes = [e for e in self._episodes if e.get("completed_at", 0) > cutoff]
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'episodic', f'Unhandled exception: {e}')
            self._episodes = []

    def _save(self):
        try:
            with open(_EPISODIC_PATH, "w", encoding="utf-8") as f:
                json.dump(self._episodes[-self.MAX_EPISODES:], f, indent=2)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'episodic', f'Unhandled exception: {e}')
            pass

    def record(self, task_id: str, objective: str, status: str, steps_completed: int, steps_failed: int, risk_level: str = "LOW", duration_seconds: float = 0.0):
        episode = {
            "episode_id": f"ep_{uuid.uuid4().hex[:8]}",
            "session_id": self._session_id,
            "task_id": task_id,
            "objective": objective[:256],
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
        return episode["episode_id"]

    def get_recent(self, n: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        with self._lock:
            episodes = list(self._episodes)
        if session_id:
            episodes = [e for e in episodes if e.get("session_id") == session_id]
        return episodes[-n:]

    def get_by_objective_keyword(self, keyword: str, n: int = 5) -> List[Dict]:
        kw = keyword.lower()
        with self._lock:
            matches = [e for e in self._episodes if kw in e.get("objective", "").lower()]
        return matches[-n:]

    def session_episodes(self) -> List[Dict]:
        return self.get_recent(n=self.MAX_EPISODES, session_id=self._session_id)

    def episode_count(self) -> int:
        with self._lock:
            return len(self._episodes)

    def clear_session(self):
        with self._lock:
            self._episodes = [e for e in self._episodes if e.get("session_id") != self._session_id]
            self._save()
