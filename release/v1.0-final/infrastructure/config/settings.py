
import os
from pathlib import Path

# 🧱 BASE_PATHS
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

# 📊 DATA_PATHS
LOG_DIR = DATA_DIR / "logs"
MEMORY_DIR = DATA_DIR / "memory"
VISION_DIR = DATA_DIR / "vision"
CACHE_DIR = DATA_DIR / "cache"

# 🛡️ ENSURE_DIRECTORIES
for d in [LOG_DIR, MEMORY_DIR, VISION_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ⚙️ CONFIG
JARVIS_PIN = os.getenv("JARVIS_PIN", "4422")
JWT_SECRET = os.getenv("JWT_SECRET", "09af8242d5f81e3a628a50438a2e1d6e5a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# 🧠 NEURAL_PATHS
USER_MEMORY_PATH = MEMORY_DIR / "user_memory.json"
SOUL_LATTICE_PATH = MEMORY_DIR / "soul_lattice.json"
GLOBAL_STATE_PATH = CACHE_DIR / "global_state.json"
SENTIENT_VECTOR_DIR = MEMORY_DIR / "sentient_vector_store"
LONG_TERM_VECTOR_DIR = MEMORY_DIR / "long_term_vector_store"
SENTIENT_FALLBACK_PATH = MEMORY_DIR / "sentient_fallback.json"
LONG_TERM_FALLBACK_PATH = MEMORY_DIR / "long_term_fallback.json"
TASK_HISTORY_PATH = DATA_DIR / "tasks" / "task_history.json"
TEMP_WORKSPACE_DIR = DATA_DIR / "temp"
