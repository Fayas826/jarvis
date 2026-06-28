import os
import subprocess
import webbrowser
import pyautogui
import platform
import asyncio
from typing import Dict, Any

# Local Imports
from core.cognition.memory.memory import memory

class SystemController:
    """🛡️ TIER_4: PHYSICAL_DOMINION_CONTROLLER"""
    
    def __init__(self):
        self.is_windows = platform.system() == "Windows"

    def execute_action(self, intent: str, payload: Any) -> Dict[str, Any]:
        """Routes higher-level intents to physical OS commands."""
        try:
            if intent == "open_app":
                return self.open_app(str(payload))
            elif intent == "search":
                return self.search_web(str(payload))
            elif intent == "set_volume":
                return self.set_volume(int(payload))
            elif intent == "system_power":
                return self.system_power(str(payload))
            elif intent == "type_text":
                return self.type_text(str(payload))
            
            return {"status": "ERROR", "message": f"Intent {intent} not mapped to physical node."}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    def open_app(self, app_name: str) -> Dict[str, Any]:
        # Use existing desktop logic but centralized here
        from action.desktop_control.desktop import open_app as desktop_open
        res = desktop_open(app_name)
        memory.add_mission_log("LAUNCH_SUCCESS", f"Ignited system node: {app_name}")
        return {"status": "SUCCESS", "response": res}

    def search_web(self, query: str) -> Dict[str, Any]:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        memory.add_mission_log("INTEL_SCAN", f"Crawling global node: {query}")
        return {"status": "SUCCESS", "response": "Web search sequence initiated."}

    def set_volume(self, level: int) -> Dict[str, Any]:
        from action.desktop_control.desktop import set_volume as desktop_vol
        res = desktop_vol(level)
        memory.add_mission_log("AUDIO_GAIN", f"Levels: {level}%")
        return {"status": "SUCCESS", "response": res}

    def system_power(self, mode: str) -> Dict[str, Any]:
        from action.desktop_control.desktop import system_power as desktop_pwr
        res = desktop_pwr(mode)
        memory.add_mission_log("POWER_PULSE", f"Sequence: {mode}")
        return {"status": "SUCCESS", "response": res}

    def type_text(self, text: str) -> Dict[str, Any]:
        pyautogui.write(text, interval=0.05)
        memory.add_mission_log("NEURAL_INPUT", f"Data typed: {text}")
        return {"status": "SUCCESS", "response": "Typing sequence successful."}

    def get_running_tasks(self):
        from action.desktop_control.desktop import get_running_tasks as desktop_tasks
        return desktop_tasks()

    def kill_process(self, name: str):
        from action.desktop_control.desktop import kill_process as desktop_kill
        return desktop_kill(name)

    def capture_screen(self):
        from action.desktop_control.desktop import capture_screen as desktop_capture
        return desktop_capture()

# Global Instance
controller = SystemController()
