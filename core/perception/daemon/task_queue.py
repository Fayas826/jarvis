import queue
import time
import threading
import logging
from datetime import datetime

from .adb_client import phone_tap, phone_swipe, adb_shell, phone_type, phone_home, phone_back, phone_scroll_down, phone_scroll_up
from .vision_engine import screenshot_to_text, analyse_screen_content
from .youtube_engine import deep_youtube_play_and_analyse
from .voice_output import speak

log = logging.getLogger("jarvis_daemon")

class TaskQueue:
    def __init__(self):
        self.q = queue.Queue()
        self.running = True
        self.current_task = None
        self.history = []

    def add(self, task_type, params=None, priority=5):
        self.q.put({"type": task_type, "params": params or {}, "priority": priority, "queued_at": datetime.now().isoformat()})
        log.info(f"[QUEUE] Task added: {task_type} | params={params}")

    def worker(self):
        while self.running:
            try:
                task = self.q.get(timeout=2)
                self.current_task = task
                log.info(f"[QUEUE] Executing: {task['type']}")
                result = self._execute(task)
                task["result"] = result
                task["completed_at"] = datetime.now().isoformat()
                self.history.append(task)
                if len(self.history) > 50: self.history.pop(0)
                self.current_task = None
                self.q.task_done()
            except queue.Empty: pass
            except Exception as e:
                log.error(f"[QUEUE] Task error: {e}")
                self.current_task = None

    def _execute(self, task):
        t = task["type"]
        p = task["params"]
        if t == "youtube_deep": return deep_youtube_play_and_analyse(p.get("query", "trending"))
        elif t == "tap": phone_tap(p.get("x", 540), p.get("y", 960)); return "TAPPED"
        elif t == "swipe": phone_swipe(p.get("x1",540), p.get("y1",1400), p.get("x2",540), p.get("y2",600)); return "SWIPED"
        elif t == "screenshot_analyse": text = screenshot_to_text(); return analyse_screen_content(text, p.get("context", "general"))
        elif t == "speak": speak(p.get("text", "")); return "SPOKEN"
        elif t == "adb_shell": out, _ = adb_shell(*p.get("cmd", ["echo", "hello"])); return out
        elif t == "open_app": app = p.get("app", ""); adb_shell("am", "start", "-n", app); return f"OPENED {app}"
        elif t == "type_text": phone_type(p.get("text", "")); return "TYPED"
        elif t == "home": phone_home(); return "HOME"
        elif t == "back": phone_back(); return "BACK"
        elif t == "scroll_down": phone_scroll_down(); return "SCROLLED_DOWN"
        elif t == "scroll_up": phone_scroll_up(); return "SCROLLED_UP"
        elif t == "wait": time.sleep(p.get("seconds", 1)); return "WAITED"
        else: return f"Unknown task: {t}"

    def start(self):
        t = threading.Thread(target=self.worker, daemon=True)
        t.start()
        return t

    def status(self):
        return {"queue_size": self.q.qsize(), "current_task": self.current_task, "history_count": len(self.history), "last_3": self.history[-3:] if self.history else []}
