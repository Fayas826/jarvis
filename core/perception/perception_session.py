import time
import uuid
from typing import Any, Dict

from core.perception.screen_capture import screen_capturer
from core.perception.visual_segmentation import visual_segmenter


class PerceptionSession:
    """Manages start/stop state for screen capture session."""

    def __init__(self):
        self.session_id: str | None = None
        self.active: bool = False
        self.last_frame_ts: float = 0.0

    def start(self) -> Dict[str, Any]:
        if not self.active:
            self.session_id = f"psess-{uuid.uuid4().hex[:8]}"
            self.active = True
        return {"status": "ACTIVE", "session_id": self.session_id}

    def stop(self) -> Dict[str, Any]:
        self.active = False
        self.session_id = None
        return {"status": "STOPPED"}

    def analyze_frame(self) -> Dict[str, Any]:
        if not self.active:
            return {"status": "INACTIVE"}
        
        try:
            frame = screen_capturer.capture_frame()
            elements = visual_segmenter.segment_elements(frame.image_b64)
            self.last_frame_ts = time.time()
            return {
                "status": "SUCCESS",
                "session_id": self.session_id,
                "frame": {
                    "width": frame.width,
                    "height": frame.height,
                    "active_window": frame.active_window,
                },
                "elements_count": len(elements),
                "insight": f"Visual field updated. {len(elements)} elements detected."
            }
        except Exception as e:
            # Graceful degradation if vision libs aren't fully functional in this env
            return {
                "status": "DEGRADED",
                "session_id": self.session_id,
                "mode": "SIMULATED",
                "insight": "Visual stream degraded or simulated.",
                "errors": [str(e)]
            }


perception_session = PerceptionSession()
