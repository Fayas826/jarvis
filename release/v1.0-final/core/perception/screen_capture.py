import os
import base64
import time
from PIL import Image
from io import BytesIO
from typing import Dict, Any

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

from core.perception.visual_state import ScreenFrame
from core.perception.browser_driver import browser_driver

class ScreenCapturer:
    """Perception Capture interface extracting dynamic desktop images and contexts."""
    
    def capture_frame(self) -> ScreenFrame:
        if pyautogui is None:
            raise RuntimeError("PyAutoGUI driver missing.")
            
        # 1. Capture screen image (attach thread to active default desktop if inside a custom station/agent desktop session)
        try:
            import ctypes
            h_desk = ctypes.windll.user32.OpenDesktopW('Default', 0, False, 0x01ff)
            if h_desk:
                ctypes.windll.user32.SetThreadDesktop(h_desk)
        except Exception as desk_e:
            print(f"[SCREEN_CAPTURE] Warning: Failed to attach thread to Default desktop: {desk_e}")

        screenshot = pyautogui.screenshot()
        width, height = screenshot.size
        
        # Scale for transfer compression
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        
        # 2. Identify active window name
        active_window_title = "Desktop"
        if gw is not None:
            try:
                active_win = gw.getActiveWindow()
                if active_win and active_win.title:
                    active_window_title = active_win.title
            except Exception as e:
                from core.reliability.system_logger import system_logger
                system_logger.log('ERROR', 'screen_capture', f'Unhandled exception: {e}')
                pass
                
        # 3. Compile ScreenFrame representation
        return ScreenFrame(
            image_b64=img_b64,
            width=width,
            height=height,
            active_window=active_window_title
        )

    async def capture_frame_async(self) -> ScreenFrame:
        """Asynchronous capture frame populating active DOM elements from Playwright."""
        frame = self.capture_frame()
        # Query active DOM elements if Playwright is running
        dom_elements = await browser_driver.get_active_elements()
        if dom_elements:
            frame.browser_context = {"elements": dom_elements}
        return frame

screen_capturer = ScreenCapturer()
