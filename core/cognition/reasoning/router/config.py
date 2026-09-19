from typing import Dict, List

_BASE_LATENCY_MS: Dict[str, float] = {
    "native": 5.0,
    "dom":    10.0,
    "uia":    55.0,
    "ocr":    280.0,
    "vlm":    1500.0,
}

_RESOURCE_COST: Dict[str, float] = {
    "native": 0.05,
    "dom":    0.10,
    "uia":    0.20,
    "ocr":    0.50,
    "vlm":    0.95,
}

_SOURCE_RELIABILITY: Dict[str, float] = {
    "native": 0.99,
    "dom":    0.95,
    "uia":    0.88,
    "ocr":    0.72,
    "vlm":    0.85,
}

_FALLBACK_COST: Dict[str, float] = {
    "native": 0.10,
    "dom":    0.15,
    "uia":    0.30,
    "ocr":    0.60,
    "vlm":    0.90,
}

_TOOL_PRIORITY = ["native", "dom", "uia", "ocr", "vlm"]

_TARGET_TYPE_BIAS: Dict[str, Dict[str, float]] = {
    "button":     {"dom": +0.05, "uia": +0.03, "ocr": -0.05},
    "textfield":  {"dom": +0.08, "uia": +0.05, "ocr": -0.08},
    "app":        {"native": +0.10, "dom": -0.05},
    "scrollable": {"dom": +0.03, "uia": +0.02, "ocr": -0.10},
    "element":    {"uia": +0.05},
    "image":      {"vlm": +0.10, "ocr": +0.05, "dom": -0.10},
}

_MIN_OBSERVATIONS_FULL_TRUST = 5
_STALE_DECAY_FACTOR = 0.5

_VRAM_TOTAL_GB = 4.0
_VRAM_HIGH_PRESSURE_THRESHOLD = 0.85
_VRAM_CRITICAL_THRESHOLD = 0.95
