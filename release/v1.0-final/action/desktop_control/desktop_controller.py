
import os
import subprocess
import asyncio
import psutil
from typing import Dict

try:
    import pyautogui
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'desktop_controller', f'Unhandled exception: {e}')
    pyautogui = None

try:
    import pygetwindow as gw
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'desktop_controller', f'Unhandled exception: {e}')
    gw = None

class DesktopController:
    """🖥️ O.M.E.G.A. DESKTOP_DOMINANCE: Advanced OS Control Layer."""
    
    def __init__(self):
        self.pyautogui = pyautogui
        if self.pyautogui is not None:
            self.pyautogui.FAILSAFE = True
        self.app_registry = {
            "chrome": "chrome.exe",
            "vscode": "code",
            "spotify": "spotify.exe",
            "notepad": "notepad.exe",
            "terminal": "wt.exe"
        }

    async def execute(self, action_type: str, payload: Dict) -> Dict:
        """Main entry point for advanced OS control."""
        print(f"[DESKTOP_DOMINANCE] Executing: {action_type} | {payload}")
        
        try:
            if action_type == "APP_OPEN":
                return await self.open_app(payload.get("app_name"))
            elif action_type == "WINDOW_CONTROL":
                return await self.control_window(payload)
            elif action_type == "UI_AUTOMATION":
                return await self.automate_ui(payload)
            elif action_type == "OS_COMMAND":
                return await self.run_command(payload.get("command"))
            elif action_type == "FILE_OP":
                return await self.file_operation(payload)
            elif action_type == "READ_SCREEN":
                return await self.read_screen_context()
            else:
                return {"status": "ERROR", "error": f"Unknown action type: {action_type}"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def open_app(self, app_name: str) -> Dict:
        app_name = app_name.lower()
        executable = self.app_registry.get(app_name, app_name)
        try:
            subprocess.Popen(executable, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # Give it a moment to launch
            await asyncio.sleep(1)
            return {"status": "SUCCESS", "detail": f"Launched {app_name}"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def control_window(self, payload: Dict) -> Dict:
        """focus, minimize, maximize, close, switch."""
        title = payload.get("title")
        action = payload.get("action", "focus").lower()
        if gw is None:
            return {"status": "ERROR", "error": "WINDOW_CONTROL_UNAVAILABLE"}
        
        try:
            windows = gw.getWindowsWithTitle(title)
            if not windows:
                return {"status": "ERROR", "error": f"No window found with title: {title}"}
            
            win = windows[0]
            if action == "focus":
                win.activate()
            elif action == "minimize":
                win.minimize()
            elif action == "maximize":
                win.maximize()
            elif action == "close":
                win.close()
            elif action == "restore":
                win.restore()
                
            return {"status": "SUCCESS", "detail": f"Window '{title}' {action}ed."}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def automate_ui(self, payload: Dict) -> Dict:
        """type, click, hotkey."""
        action = payload.get("action").lower()
        text = payload.get("text")
        key = payload.get("key")
        coords = payload.get("coords") # [x, y]
        if self.pyautogui is None:
            return {"status": "ERROR", "error": "UI_AUTOMATION_UNAVAILABLE"}
        
        try:
            if action == "type":
                self.pyautogui.write(text, interval=0.05)
            elif action == "click":
                if coords:
                    self.pyautogui.click(x=coords[0], y=coords[1])
                else:
                    self.pyautogui.click()
            elif action == "hotkey":
                keys = key.split('+')
                self.pyautogui.hotkey(*keys)
            elif action == "press":
                self.pyautogui.press(key)
                
            return {"status": "SUCCESS", "detail": f"UI action {action} completed."}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def run_command(self, command: str) -> Dict:
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return {"status": "SUCCESS", "output": stdout.decode().strip()}
            else:
                return {"status": "ERROR", "error": stderr.decode().strip()}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def file_operation(self, payload: Dict) -> Dict:
        op = payload.get("operation")
        path = os.path.abspath(payload.get("path"))
        try:
            if op == "create":
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(payload.get("content", ""))
            elif op == "delete":
                if os.path.isfile(path): os.remove(path)
                elif os.path.isdir(path): import shutil; shutil.rmtree(path)
            elif op == "move":
                dest = os.path.abspath(payload.get("destination"))
                os.rename(path, dest)
            return {"status": "SUCCESS", "detail": f"File op {op} on {path} completed."}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def read_screen_context(self) -> Dict:
        """Takes a screenshot and returns metadata (for now, just status)."""
        # In a real scenario, this would use OCR or Vision Sentinel
        if self.pyautogui is None:
            return {"status": "ERROR", "error": "SCREEN_CAPTURE_UNAVAILABLE"}
        try:
            # We'll save a temp screenshot for the Vision Sentinel to analyze if needed
            path = "data/temp/screen_capture.png"
            os.makedirs("data/temp", exist_ok=True)
            self.pyautogui.screenshot(path)
            return {"status": "SUCCESS", "screenshot_path": path}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

desktop_controller = DesktopController()
