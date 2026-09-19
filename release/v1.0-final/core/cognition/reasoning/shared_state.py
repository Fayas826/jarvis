import threading

# 🛡️ O.M.E.G.A. STATE_LOCKS
NEURAL_LOCK = threading.Lock()
INTEL_LOCK = threading.Lock()
SPEECH_LOCK = threading.Lock()
CACHE_LOCK = threading.Lock()
QUEUE_LOCK = threading.Lock()

NEURAL_INSIGHT_CACHE = {
    "visual": "Scanning tactical focal plane...",
    "audio": "Sonic resonance nominal.",
    "threat_level": "NOMINAL",
    "timestamp": 0
}

INTEL_CACHE = {
    "news": [],
    "threat_level": "NOMINAL",
    "timestamp": 0
}

# 🎙️ SOVEREIGN_VOICE_LINK
SPEECH_QUEUE = []
