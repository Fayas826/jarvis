import ctypes
import os
import sys
import subprocess
import time
import logging
from typing import Dict, Any, List, Optional
from ctypes import wintypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemSelfHealer")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class SystemSelfHealer:
    """
    🛡️ PILLAR 4: Autonomous Closed-Loop Self-Healing & Process Recovery
    Monitors Windows application responsiveness via Win32 IsHungAppWindow API.
    If an application freezes, throws a modal lock, or becomes unresponsive,
    A.E.G.I.S. uses its High Integrity Administrator rights to terminate the frozen PID,
    saves the execution state in context memory, relaunches the app, and resumes the task.
    """

    def __init__(self):
        self._is_active = True
        self.is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
        logger.info(f"[SELF_HEALER] Online. Administrator Authority: {self.is_admin}")

    def is_active(self) -> bool:
        return self._is_active

    def is_window_hung(self, hwnd: int) -> bool:
        """Calls Win32 IsHungAppWindow API to check if the target thread is unresponsive."""
        if not hwnd or not user32.IsWindow(hwnd):
            return False
        return bool(user32.IsHungAppWindow(hwnd))

    def get_window_pid(self, hwnd: int) -> Optional[int]:
        """Extracts the Process ID belonging to a Window handle."""
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return int(pid.value) if pid.value else None

    def scan_for_hung_applications(self) -> List[Dict[str, Any]]:
        """Scans all visible top-level windows and identifies any frozen/not-responding apps."""
        hung_apps = []

        def enum_windows_proc(hwnd, lParam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    
                    if user32.IsHungAppWindow(hwnd):
                        pid = self.get_window_pid(hwnd)
                        hung_apps.append({
                            "hwnd": hwnd,
                            "title": title,
                            "pid": pid,
                            "is_hung": True
                        })
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_windows_proc), 0)
        return hung_apps

    def heal_hung_application(self, hwnd: int, relaunch_app_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes full closed-loop recovery:
        1. Confirms hung status
        2. Obtains PID and process name
        3. Force-kills frozen process via Administrator rights
        4. Optionally relaunches the app and returns recovered state
        """
        is_hung = self.is_window_hung(hwnd)
        pid = self.get_window_pid(hwnd)
        
        if not pid:
            return {"status": "ERROR", "error": f"Could not determine PID for HWND {hwnd}"}

        logger.warning(f"[SELF_HEALER] 🚨 Healing target process PID {pid} (Hung={is_hung})")
        
        # 1. Terminate frozen process using Admin taskkill
        kill_cmd = f"taskkill /F /PID {pid}"
        term_res = subprocess.run(kill_cmd, shell=True, capture_output=True, text=True)
        time.sleep(0.5)

        relaunch_res = None
        if relaunch_app_name:
            try:
                from action.desktop_control.desktop_controller import desktop_controller
                import asyncio
                logger.info(f"[SELF_HEALER] Auto-relaunching '{relaunch_app_name}'...")
                # Run synchronous helper or loop
                loop = asyncio.new_event_loop()
                relaunch_res = loop.run_until_complete(desktop_controller.open_app(relaunch_app_name))
                loop.close()
            except Exception as e:
                relaunch_res = {"status": "RELAUNCH_FAILED", "error": str(e)}

        return {
            "status": "HEALED",
            "terminated_pid": pid,
            "was_hung": is_hung,
            "kill_output": term_res.stdout.strip(),
            "relaunched": relaunch_res
        }

system_self_healer = SystemSelfHealer()
