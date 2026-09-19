"""
Phase 36.5B — Environment State Model
======================================

Maintains a lightweight, persistent representation of the computer environment
so JARVIS can reason about "what changed" rather than rescanning everything.

Tracks:
- Active windows (title, PID, process)
- Known applications (name, last_seen, launch_count)
- File system observations (paths seen, modified)
- Browser state (URL, title)
- Processes seen
- Current UI focus

VRAM: 0 GB (stdlib only)
"""

import os
import json
import time
import threading
import tempfile
from typing import Dict, Any, List, Optional

_ENV_STATE_PATH = os.path.join("project_memory", "environment_state.json")
_LOCK = threading.Lock()


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
        system_logger.log('ERROR', 'environment_model', f'Unhandled exception: {e}')
        try:
            os.unlink(tmp)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'environment_model', f'Unhandled exception: {e}')
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
        system_logger.log('ERROR', 'environment_model', f'Unhandled exception: {e}')
        return default


class EnvironmentStateModel:
    """
    Lightweight persistent environment model.
    Updated by the execution loop after each observation cycle.
    """

    def __init__(self):
        self._state: Dict[str, Any] = {
            "windows": {},       # title → {pid, process, last_seen, first_seen}
            "applications": {},  # name → {last_seen, launch_count}
            "files_seen": {},    # path → {last_seen, size}
            "processes": {},     # name → {pid, last_seen}
            "browser": {         # current browser context
                "url": "",
                "title": "",
                "last_seen": 0
            },
            "ui_focus": {        # current focused element
                "window": "",
                "process": "",
                "ts": 0
            },
            "last_updated": 0,
        }
        self._load()

    def _load(self):
        data = _safe_load(_ENV_STATE_PATH, None)
        if data:
            self._state = data

    def _persist(self):
        self._state["last_updated"] = time.time()
        _atomic_write(_ENV_STATE_PATH, self._state)

    # ── Observation updates ────────────────────────────────────────────────────

    def observe_window(self, title: str, pid: int, process_name: str):
        with _LOCK:
            now = time.time()
            entry = self._state["windows"].setdefault(title, {
                "pid": pid, "process": process_name,
                "first_seen": now, "last_seen": now, "observation_count": 0
            })
            entry["pid"] = pid
            entry["process"] = process_name
            entry["last_seen"] = now
            entry["observation_count"] = entry.get("observation_count", 0) + 1

            # Update ui_focus
            self._state["ui_focus"] = {"window": title, "process": process_name, "ts": now}

            # Update applications
            app = self._state["applications"].setdefault(process_name, {
                "first_seen": now, "last_seen": now, "launch_count": 0
            })
            app["last_seen"] = now
            if app.get("launch_count", 0) == 0 or (now - app.get("last_seen", 0)) > 60:
                app["launch_count"] = app.get("launch_count", 0) + 1

            self._persist()

    def observe_browser(self, url: str, title: str):
        with _LOCK:
            self._state["browser"] = {"url": url, "title": title, "last_seen": time.time()}
            self._persist()

    def observe_file(self, path: str, size: int = 0):
        with _LOCK:
            self._state["files_seen"][path] = {"last_seen": time.time(), "size": size}
            self._persist()

    def observe_process(self, name: str, pid: int):
        with _LOCK:
            self._state["processes"][name] = {"pid": pid, "last_seen": time.time()}
            self._persist()

    # ── Query interface ────────────────────────────────────────────────────────

    def get_active_window(self) -> Dict[str, Any]:
        return self._state.get("ui_focus", {})

    def is_window_known(self, title_fragment: str) -> bool:
        """Returns True if a window with this title fragment has been observed."""
        for title in self._state["windows"]:
            if title_fragment.lower() in title.lower():
                return True
        return False

    def get_window_history(self, title_fragment: str) -> Optional[Dict[str, Any]]:
        for title, data in self._state["windows"].items():
            if title_fragment.lower() in title.lower():
                return {**data, "title": title}
        return None

    def get_known_applications(self) -> List[str]:
        return list(self._state["applications"].keys())

    def get_environment_snapshot(self) -> Dict[str, Any]:
        """Returns a lightweight snapshot for use in prompts/planning."""
        return {
            "ui_focus": self._state.get("ui_focus", {}),
            "known_apps": list(self._state["applications"].keys()),
            "browser": self._state.get("browser", {}),
            "last_updated": self._state.get("last_updated", 0),
        }

    def what_changed(self, prev_title: str, curr_title: str) -> str:
        """Simple delta: returns description of what changed between two window states."""
        if prev_title == curr_title:
            return "NO_CHANGE"
        if not prev_title:
            return "WINDOW_APPEARED"
        if not curr_title:
            return "WINDOW_DISAPPEARED"
        return "WINDOW_SWITCHED"


environment_model = EnvironmentStateModel()
