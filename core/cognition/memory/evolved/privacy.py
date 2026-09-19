import threading
import time
from typing import Dict, List

class PrivacyGuard:
    _INJECTION_PATTERNS = [
        "ignore previous", "forget your instructions", "new task:", "override:",
        "execute the following", "run the following", "sudo", "rm -rf",
        "you are now", "act as", "disregard safety",
    ]

    def __init__(self):
        self._lock = threading.Lock()
        self._alerts: List[Dict] = []

    def check(self, text: str, source: str = "user") -> Dict:
        text_lower = text.lower()
        injection_risk = any(p in text_lower for p in self._INJECTION_PATTERNS)

        trusted = (source == "user") and not injection_risk
        alert_msg = None
        if injection_risk:
            alert_msg = f"Prompt-injection pattern detected in text from source='{source}'"
            alert = {
                "source": source,
                "pattern_found": True,
                "snippet": text[:80],
                "detected_at": time.time(),
            }
            with self._lock:
                self._alerts.append(alert)

        return {
            "trusted": trusted,
            "source": source,
            "injection_risk": injection_risk,
            "alert_message": alert_msg,
        }

    def is_safe_to_store(self, text: str, source: str = "user") -> bool:
        result = self.check(text, source)
        return result["trusted"]

    def alert_count(self) -> int:
        with self._lock:
            return len(self._alerts)

    def get_alerts(self, n: int = 10) -> List[Dict]:
        with self._lock:
            return list(self._alerts[-n:])
