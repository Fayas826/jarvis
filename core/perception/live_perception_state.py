import time
from typing import Any, Dict, List

from core.orchestration.world_state_engine import world_state_engine


class LivePerceptionState:
    """Contracts for browser/mobile/audio/video perception telemetry."""

    def __init__(self):
        self.audio_events: List[Dict[str, Any]] = []
        self.video_events: List[Dict[str, Any]] = []
        self.last_state: Dict[str, Any] = {
            "audio": "UNKNOWN",
            "video": "UNKNOWN",
            "last_update": None,
            "attention": "STANDBY",
            "confidence": 0,
        }

    def ingest(self, stream: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        stream = stream.lower()
        event = {
            "ts": time.time(),
            "stream": stream,
            "payload": payload,
            "confidence": self._confidence(stream, payload),
        }
        if stream == "audio":
            self.audio_events.append(event)
            self.audio_events = self.audio_events[-60:]
            self.last_state["audio"] = "LIVE"
        elif stream == "video":
            self.video_events.append(event)
            self.video_events = self.video_events[-60:]
            self.last_state["video"] = "LIVE"
        else:
            self.last_state[stream] = "LIVE"
        self.last_state["last_update"] = event["ts"]
        self.last_state["confidence"] = event["confidence"]
        self.last_state["attention"] = self._attention_label()
        world_state_engine.record_event("PERCEPTION_EVENT", event, "perception")
        return event

    def snapshot(self) -> Dict[str, Any]:
        stale_after = 15
        now = time.time()
        last_update = self.last_state.get("last_update")
        state = dict(self.last_state)
        if not last_update or now - last_update > stale_after:
            if state["audio"] == "LIVE":
                state["audio"] = "STALE"
            if state["video"] == "LIVE":
                state["video"] = "STALE"
        state["audio_events"] = self.audio_events[-5:]
        state["video_events"] = self.video_events[-5:]
        return state

    def _confidence(self, stream: str, payload: Dict[str, Any]) -> int:
        if stream == "audio":
            rms = float(payload.get("rms", payload.get("level", 0)) or 0)
            return max(20, min(96, int(45 + rms)))
        if stream == "video":
            faces = int(payload.get("faces", 0) or 0)
            motion = float(payload.get("motion", 0) or 0)
            return max(30, min(96, int(55 + faces * 12 + motion * 10)))
        return 50

    def _attention_label(self) -> str:
        recent_audio = self.audio_events[-1:] and time.time() - self.audio_events[-1]["ts"] < 8
        recent_video = self.video_events[-1:] and time.time() - self.video_events[-1]["ts"] < 8
        if recent_audio and recent_video:
            return "MULTIMODAL_LOCK"
        if recent_audio:
            return "AUDIO_FOCUS"
        if recent_video:
            return "VISION_FOCUS"
        return "STANDBY"


live_perception_state = LivePerceptionState()
