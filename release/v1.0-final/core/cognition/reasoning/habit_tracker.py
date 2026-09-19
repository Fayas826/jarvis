
import os
import json
import time
from datetime import datetime
from typing import Dict, List

class UserHabitTracker:
    """👤 O.M.E.G.A. HABIT_TRACKER: You-Aware Personalization."""
    
    def __init__(self):
        self.history_path = "data/memory/user_habits.json"
        os.makedirs("data/memory", exist_ok=True)
        self.current_session = {
            "apps": {},
            "start_time": time.time()
        }
        self._load_history()

    def _load_history(self):
        try:
            if os.path.exists(self.history_path):
                with open(self.history_path, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = {"patterns": {}, "daily_stats": {}}
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'habit_tracker', f'Unhandled exception: {e}')
            self.history = {"patterns": {}, "daily_stats": {}}

    def track_app_usage(self, app_name: str):
        """Called by Vision Sentinel or Process Monitor."""
        hour = datetime.now().hour
        day = datetime.now().strftime("%A")
        
        # Track Frequency by Hour
        key = f"{day}_{hour}"
        if key not in self.history["patterns"]:
            self.history["patterns"][key] = {}
        
        self.history["patterns"][key][app_name] = self.history["patterns"][key].get(app_name, 0) + 1
        self._save_history()

    def get_likely_apps(self) -> List[str]:
        """Predicts what apps you usually open now."""
        hour = datetime.now().hour
        day = datetime.now().strftime("%A")
        key = f"{day}_{hour}"
        
        patterns = self.history["patterns"].get(key, {})
        # Sort by frequency
        sorted_apps = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        return [app for app, count in sorted_apps if count > 5] # Threshold for habit

    def _save_history(self):
        try:
            with open(self.history_path, 'w') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'habit_tracker', f'Unhandled exception: {e}')
            pass

habit_tracker = UserHabitTracker()
