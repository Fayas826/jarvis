import time
import os
import sys
import ctypes
import logging
import threading
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [INTRUSION_DETECTOR] %(message)s")

INTRUDER_LOG_DIR = r"c:\jarvis AI\jarvis\vault_traps\intruder_logs"
os.makedirs(INTRUDER_LOG_DIR, exist_ok=True)

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', ctypes.c_uint),
        ('dwTime', ctypes.c_uint),
    ]

def get_idle_time_seconds() -> float:
    """Queries Windows Kernel User32 API for exact mouse/keyboard idle time."""
    if sys.platform != "win32":
        return 0.0
    try:
        li = LASTINPUTINFO()
        li.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li)):
            millis = ctypes.windll.kernel32.GetTickCount() - li.dwTime
            return millis / 1000.0
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'unauthorized_intrusion_detector', f'Unhandled exception: {e}')
        pass
    return 0.0

class UnauthorizedIntrusionDetector:
    """
    Real Unauthorized Laptop Touch & Intrusion Security Sentinel.
    - Monitors Windows User32 LastInputInfo API.
    - When laptop is touched during owner absence:
      1. Operates SILENTLY (No voice spoken, No audio chime).
      2. Snaps silent evidence photo of intruder to vault_traps/intruder_logs/.
      3. Silently locks Windows Workstation (LockWorkStation API).
    """

    def __init__(self, idle_threshold_sec: float = 120.0):
        self.idle_threshold_sec = idle_threshold_sec
        self.running = False
        self.was_idle = False

    def start_sentinel(self):
        self.running = True
        t = threading.Thread(target=self._sentinel_loop, daemon=True)
        t.start()

    def _sentinel_loop(self):
        logging.info(f"Intrusion Sentinel Active. Idle Threshold: {self.idle_threshold_sec}s.")
        while self.running:
            try:
                idle_sec = get_idle_time_seconds()
                if idle_sec >= self.idle_threshold_sec:
                    self.was_idle = True
                elif self.was_idle and idle_sec < 2.0:
                    # Laptop mouse/keyboard touched after being idle!
                    logging.warning("UNAUTHORIZED TOUCH DETECTED! Executing Silent Intrusion Protocol...")
                    self.was_idle = False
                    self._execute_silent_intrusion_protocol()
            except Exception as e:
                logging.error(f"Intrusion sentinel error: {e}")
            time.sleep(1.0)

    def _execute_silent_intrusion_protocol(self):
        """Snaps silent photo and locks Windows workstation without making any sound."""
        # 1. Snap Silent Photo
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                time.sleep(0.3)
                ret, frame = cap.read()
                cap.release()
                if ret:
                    ts = time.strftime("%Y%m%d_%H%M%S")
                    img_path = os.path.join(INTRUDER_LOG_DIR, f"intruder_{ts}.jpg")
                    cv2.imwrite(img_path, frame)
                    logging.info(f"SILENT EVIDENCE CAPTURED: {img_path}")
        except Exception as e:
            logging.error(f"Evidence capture exception: {e}")

        # 2. Silently Lock Windows Workstation
        try:
            if sys.platform == "win32":
                ctypes.windll.user32.LockWorkStation()
                logging.info("Windows Workstation SILENTLY LOCKED.")
        except Exception as e:
            logging.error(f"LockWorkStation error: {e}")

if __name__ == "__main__":
    detector = UnauthorizedIntrusionDetector(idle_threshold_sec=10.0)
    detector.start_sentinel()
    print("Intrusion detector test started. Idle for 10s then touch mouse to test silent lock...")
    time.sleep(15)
