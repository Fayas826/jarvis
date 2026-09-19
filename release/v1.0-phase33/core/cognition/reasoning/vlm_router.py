import os
from typing import Dict, Any

class VLMRouter:
    """Model-independent VLM routing layer selecting local or cloud models (Phase 9)."""

    def __init__(self):
        self.local_vram_limit_gb = 4.0
        self.gemini_active = bool(os.getenv("GEMINI_API_KEY"))
        self.mistral_active = bool(os.getenv("MISTRAL_API_KEY"))

    def decide_route(self, task_type: str, privacy_required: bool = False, network_available: bool = True) -> str:
        """Determines model routing (LOCAL vs CLOUD) based on criteria constraints."""
        # Privacy constraints dictate strictly local
        if privacy_required:
            return "LOCAL"

        # Hardware VRAM constraints restrict heavy local vision pipelines
        if self.local_vram_limit_gb <= 4.0:
            if network_available and (self.gemini_active or self.mistral_active):
                return "CLOUD"
            return "LOCAL"

        return "LOCAL"

vlm_router = VLMRouter()
