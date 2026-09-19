import ctypes
from typing import List, Tuple

class CoordinateMapper:
    """Handles DPI scale factor normalization and monitor coordinate offsets."""
    
    def __init__(self):
        self.dpi_scale = self._detect_dpi_scale()
        print(f"[COORDS] Active Windows DPI Scaling detected: {self.dpi_scale * 100}%")

    def _detect_dpi_scale(self) -> float:
        """Calls Windows windll shcore GetScaleFactorForDevice to fetch scaling factor."""
        try:
            # SHCORE is available on Windows 8.1 and higher
            shcore = ctypes.windll.shcore
            # 0 is the primary monitor index
            scale = shcore.GetScaleFactorForDevice(0)
            return scale / 100.0
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'coordinate_mapper', f'Unhandled exception: {e}')
            try:
                # Fallback to user32 GetDpiForSystem
                user32 = ctypes.windll.user32
                dpi = user32.GetDpiForSystem()
                return dpi / 96.0
            except Exception as e:
                from core.reliability.system_logger import system_logger
                system_logger.log('ERROR', 'coordinate_mapper', f'Unhandled exception: {e}')
                return 1.0

    def screenshot_to_physical(self, x: int, y: int, frame_w: int, frame_h: int) -> Tuple[int, int]:
        """Maps coordinates from screenshot frame dimensions to physical system pixels."""
        # Frame dimensions are usually smaller or identical to screen dimensions
        # Map proportionally
        try:
            user32 = ctypes.windll.user32
            screen_w = user32.GetSystemMetrics(0) # SM_CXSCREEN
            screen_h = user32.GetSystemMetrics(1) # SM_CYSCREEN
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'coordinate_mapper', f'Unhandled exception: {e}')
            screen_w, screen_h = frame_w, frame_h
            
        ratio_x = screen_w / frame_w
        ratio_y = screen_h / frame_h
        
        physical_x = int(x * ratio_x)
        physical_y = int(y * ratio_y)
        
        return physical_x, physical_y

    def physical_to_pyautogui(self, x: int, y: int) -> Tuple[int, int]:
        """
        Converts physical screen pixels into PyAutoGUI system mouse coordinates.
        PyAutoGUI matches virtual screen pixels which are divided by the DPI scale.
        """
        pyautogui_x = int(x / self.dpi_scale)
        pyautogui_y = int(y / self.dpi_scale)
        return pyautogui_x, pyautogui_y

    def map_coords(self, x: int, y: int, frame_w: int, frame_h: int) -> Tuple[int, int]:
        """Full pipeline conversion: Screenshot -> Physical -> PyAutoGUI virtual cursor."""
        phys_x, phys_y = self.screenshot_to_physical(x, y, frame_w, frame_h)
        return self.physical_to_pyautogui(phys_x, phys_y)

coordinate_mapper = CoordinateMapper()
