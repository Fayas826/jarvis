import os
import time
import base64
import pyautogui
from PIL import Image
from io import BytesIO

# 🧿 J.A.R.V.I.S. O.M.E.G.A. — VISION_SENTINEL_V1
# This node gives JARVIS the ability to 'See' the Architect's workspace.

from infrastructure.config.settings import VISION_DIR

class VisionSentinel:
    def __init__(self, storage_dir=str(VISION_DIR)):
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def capture_vision(self):
        """Takes a neural snapshot of the current screen state."""
        try:
            screenshot = pyautogui.screenshot()
            # Compress for high-speed neural transfer
            buffered = BytesIO()
            screenshot.save(buffered, format="JPEG", quality=50)
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            print(f"[VISION_ERROR] Screen capture failed: {e}")
            return None

    def capture_intruder(self):
        """Tier 18: SENTINEL_EYE. Captures the physical face in front of the laptop."""
        try:
            import cv2
            cam = cv2.VideoCapture(0)
            ret, frame = cam.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                img_str = base64.b64encode(buffer).decode()
                cam.release()
                return img_str
            cam.release()
        except Exception as e:
            print(f"[VISION_ERROR] Webcam capture failed: {e}")
        return None

vision_sentinel = VisionSentinel()
