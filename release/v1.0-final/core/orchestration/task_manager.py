import datetime
import threading
import time
import json
import os

# 🛡️ O.M.E.G.A. TIER_15: TASK_TEMPORAL_MONITOR
# Manages Alarms, Reminders, and Scheduled Mission Nodes.

REMINDERS_FILE = os.path.join(os.path.dirname(__file__), "reminders.json")

class TaskManager:
    def __init__(self):
        self.reminders = self._load()
        self.active = False
        self.callback = None

    def _load(self):
        if os.path.exists(REMINDERS_FILE):
            try:
                with open(REMINDERS_FILE, "r") as f:
                    return json.load(f)
            except: return []
        return []

    def _save(self):
        with open(REMINDERS_FILE, "w") as f:
            json.dump(self.reminders, f, indent=4)

    def add_reminder(self, text, delta_minutes=0, time_str=None):
        """Adds a reminder. Use delta_minutes or time_str (HH:MM)."""
        target_time = None
        if delta_minutes:
            target_time = datetime.datetime.now() + datetime.timedelta(minutes=delta_minutes)
        elif time_str:
            try:
                h, m = map(int, time_str.split(":"))
                target_time = datetime.datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
                if target_time < datetime.datetime.now():
                    target_time += datetime.timedelta(days=1)
            except: return "INVALID_TIME_FORMAT"

        if target_time:
            reminder = {
                "id": int(time.time()),
                "text": text,
                "time": target_time.isoformat(),
                "status": "PENDING"
            }
            self.reminders.append(reminder)
            self._save()
            return f"Reminder set for {target_time.strftime('%H:%M')}."
        return "FAILED_TO_SET_REMINDER"

    def start_monitor(self, alert_callback):
        """Starts the background watchdog to trigger reminders."""
        self.callback = alert_callback
        self.active = True
        threading.Thread(target=self._watchdog_loop, daemon=True).start()
        print("[TASK_MANAGER] Temporal Monitor: ONLINE")

    def _watchdog_loop(self):
        while self.active:
            now = datetime.datetime.now()
            for r in self.reminders:
                if r["status"] == "PENDING":
                    target = datetime.datetime.fromisoformat(r["time"])
                    if now >= target:
                        print(f"[TASK_MANAGER] Triggering reminder: {r['text']}")
                        if self.callback:
                            self.callback(r["text"])
                        r["status"] = "TRIGGERED"
                        self._save()
            time.sleep(30)

    def get_pending(self):
        return [r for r in self.reminders if r["status"] == "PENDING"]

task_manager = TaskManager()
