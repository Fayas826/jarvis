import os
import sys
import subprocess
import asyncio
import psutil
import ctypes
import winreg
import glob
from typing import Dict, Any, Optional

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'desktop_controller', f'PyAutoGUI load fail: {e}')
    pyautogui = None

try:
    import pygetwindow as gw
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'desktop_controller', f'PyGetWindow load fail: {e}')
    gw = None

from core.execution.universal_desktop_controller import desktop_controller as universal_controller
from core.perception.coordinate_mapper import CoordinateMapper

class DesktopController:
    """🖥️ O.M.E.G.A. DESKTOP_DOMINANCE: Advanced Universal OS Control Layer."""
    
    def __init__(self):
        self.pyautogui = pyautogui
        if self.pyautogui is not None:
            self.pyautogui.FAILSAFE = False
        self.coord_mapper = CoordinateMapper()
        self.user32 = ctypes.windll.user32
        
        # Standard fallback protocol aliases
        self.protocol_aliases = {
            "calc": "calc:",
            "calculator": "calc:",
            "settings": "ms-settings:",
            "store": "ms-windows-store:",
            "whatsapp": "whatsapp:",
            "spotify": "spotify:",
            "photos": "ms-photos:",
            "camera": "microsoft.windows.camera:",
            "terminal": "wt.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "edge": "msedge.exe",
            "vscode": "code",
            "code": "code",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe"
        }

    def resolve_application_path(self, app_name: str) -> Optional[str]:
        """
        Dynamically locates ANY Windows application by querying:
        1. Built-in protocol shortcuts
        2. Registry: HKLM & HKCU App Paths
        3. Start Menu Shortcuts (.lnk)
        4. PATH environment search
        """
        clean_name = app_name.strip().lower()
        if clean_name in self.protocol_aliases:
            return self.protocol_aliases[clean_name]

        # 1. Check Registry App Paths (HKLM and HKCU)
        registry_roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\App Paths")
        ]
        
        candidates = [clean_name, f"{clean_name}.exe"]
        for root, subkey in registry_roots:
            for cand in candidates:
                try:
                    with winreg.OpenKey(root, f"{subkey}\\{cand}") as key:
                        val, _ = winreg.QueryValueEx(key, "")
                        if val and os.path.exists(val):
                            return val
                except Exception:
                    continue

        # 2. Check Windows Start Menu Shortcuts
        start_menu_dirs = [
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")
        ]
        for base_dir in start_menu_dirs:
            if os.path.exists(base_dir):
                for link in glob.glob(f"{base_dir}/**/*.lnk", recursive=True):
                    base_lnk = os.path.basename(link).lower()
                    if clean_name in base_lnk:
                        return link

        # 3. Direct executable name fallback
        return f"{clean_name}.exe"

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

    async def open_app(self, app_name: str, auto_focus: bool = True) -> Dict:
        """Universally launches any installed Windows application and enforces foreground takeover."""
        resolved = self.resolve_application_path(app_name)
        print(f"[DESKTOP_DOMINANCE] Launching '{app_name}' resolved to: '{resolved}'")
        
        # 1. Minimize current foreground (e.g. IDE) so new app appears clearly on desktop
        curr_fg = self.user32.GetForegroundWindow()
        if curr_fg:
            self.user32.ShowWindow(curr_fg, 6) # SW_MINIMIZE = 6
            await asyncio.sleep(0.3)

        try:
            if resolved.endswith(":") or os.path.exists(resolved):
                os.startfile(resolved)
            else:
                subprocess.Popen(resolved, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        except Exception:
            try:
                subprocess.Popen(f"start {app_name}", shell=True)
            except Exception as e2:
                return {"status": "ERROR", "error": f"Could not launch {app_name}: {e2}"}

        # 2. Wait up to 5s for the newly opened application window to appear and bring it to top
        if auto_focus:
            target_hwnd = None
            search_terms = [app_name.lower(), resolved.lower().replace(".exe", "").split("\\")[-1]]
            for _ in range(10):
                await asyncio.sleep(0.5)
                windows = universal_controller.list_visible_windows()
                for hwnd, title in windows:
                    t_lower = title.lower()
                    if any(term in t_lower for term in search_terms if term):
                        target_hwnd = hwnd
                        break
                if target_hwnd:
                    break

            if target_hwnd:
                universal_controller.force_foreground_window(target_hwnd, minimize_current_fg=False)
                return {"status": "SUCCESS", "detail": f"Launched and brought to foreground: {app_name} (HWND {target_hwnd})"}

        return {"status": "SUCCESS", "detail": f"Universally launched {app_name} via {resolved}"}

    async def control_window(self, payload: Dict) -> Dict:
        """Universal window control with Foreground Lock Timeout bypass."""
        title = payload.get("title", "")
        action = payload.get("action", "focus").lower()
        
        # Use UniversalDesktopController
        if action in ["focus", "maximize", "foreground"]:
            hwnd = universal_controller.focus_application(title, minimize_others=payload.get("minimize_others", False))
            if hwnd:
                return {"status": "SUCCESS", "detail": f"Window '{title}' (HWND {hwnd}) brought to foreground."}
        
        # Fallback to pygetwindow
        if gw is not None:
            try:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    win = windows[0]
                    if action == "minimize": win.minimize()
                    elif action == "maximize": win.maximize()
                    elif action == "close": win.close()
                    elif action == "restore": win.restore()
                    return {"status": "SUCCESS", "detail": f"Window '{title}' {action}ed."}
            except Exception as e:
                return {"status": "ERROR", "error": str(e)}

        return {"status": "ERROR", "error": f"No window found matching title: '{title}'"}

    async def automate_ui(self, payload: Dict) -> Dict:
        """Universal DPI-aware type, click, and hotkey mechanics."""
        action = payload.get("action", "").lower()
        text = payload.get("text")
        key = payload.get("key")
        coords = payload.get("coords") # [x, y]
        
        if self.pyautogui is None:
            return {"status": "ERROR", "error": "UI_AUTOMATION_UNAVAILABLE"}
        
        try:
            if action == "type":
                if coords:
                    px, py = self.coord_mapper.physical_to_pyautogui(coords[0], coords[1])
                    self.pyautogui.click(x=px, y=py)
                    await asyncio.sleep(0.1)
                import pyperclip
                pyperclip.copy(text)
                self.pyautogui.hotkey('ctrl', 'v')
            elif action == "click":
                if coords:
                    px, py = self.coord_mapper.physical_to_pyautogui(coords[0], coords[1])
                    self.pyautogui.click(x=px, y=py)
                else:
                    self.pyautogui.click()
            elif action == "double_click":
                if coords:
                    px, py = self.coord_mapper.physical_to_pyautogui(coords[0], coords[1])
                    self.pyautogui.doubleClick(x=px, y=py)
                else:
                    self.pyautogui.doubleClick()
            elif action == "right_click":
                if coords:
                    px, py = self.coord_mapper.physical_to_pyautogui(coords[0], coords[1])
                    self.pyautogui.rightClick(x=px, y=py)
                else:
                    self.pyautogui.rightClick()
            elif action == "hotkey":
                keys = [k.strip() for k in key.split('+')]
                self.pyautogui.hotkey(*keys)
            elif action == "press":
                self.pyautogui.press(key)
            elif action == "scroll":
                clicks = payload.get("clicks", -300)
                self.pyautogui.scroll(clicks)
                
            return {"status": "SUCCESS", "detail": f"UI action {action} completed."}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def run_command(self, command: str) -> Dict:
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return {"status": "SUCCESS", "output": stdout.decode(errors='replace').strip()}
            else:
                return {"status": "ERROR", "error": stderr.decode(errors='replace').strip()}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def file_operation(self, payload: Dict) -> Dict:
        op = payload.get("operation")
        path = payload.get("path")
        try:
            if op == "read":
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    return {"status": "SUCCESS", "content": f.read()}
            elif op == "write":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(payload.get("content", ""))
                return {"status": "SUCCESS", "detail": f"Written to {path}"}
            elif op == "exists":
                return {"status": "SUCCESS", "exists": os.path.exists(path)}
            else:
                return {"status": "ERROR", "error": f"Unknown file op: {op}"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def read_screen_context(self) -> Dict:
        try:
            from core.perception.screen_capture import screen_capturer
            frame = screen_capturer.capture_frame()
            return {"status": "SUCCESS", "width": frame.width, "height": frame.height, "active_window": frame.active_window}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

desktop_controller = DesktopController()
