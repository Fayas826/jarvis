
import os
import re

MAPPINGS = {
    # COGNITION: REASONING (From Monolithic & v1 Sovereign)
    r"from onnx_engine import": "from core.cognition.reasoning.onnx_engine import",
    r"from core.intelligence.onnx_engine import": "from core.cognition.reasoning.onnx_engine import",
    
    r"from brain import": "from core.cognition.reasoning.brain import",
    r"from core.intelligence.brain import": "from core.cognition.reasoning.brain import",
    
    r"from neural_core import": "from core.cognition.reasoning.neural_core import",
    r"from core.intelligence.neural_core import": "from core.cognition.reasoning.neural_core import",
    
    r"from evolution_engine import": "from core.cognition.reasoning.evolution_engine import",
    r"from core.intelligence.evolution_engine import": "from core.cognition.reasoning.evolution_engine import",
    
    r"from shared_state import": "from core.cognition.reasoning.shared_state import",
    r"from core.intelligence.shared_state import": "from core.cognition.reasoning.shared_state import",
    
    r"from sentience import": "from core.cognition.reasoning.sentience import",
    r"from core.intelligence.sentience import": "from core.cognition.reasoning.sentience import",
    
    r"from omega_mesh import": "from core.cognition.reasoning.omega_mesh import",
    r"from services.ai.omega_mesh import": "from core.cognition.reasoning.omega_mesh import",

    # COGNITION: MEMORY
    r"from memory import": "from core.cognition.memory.memory import",
    r"from core.memory.memory import": "from core.cognition.memory.memory import",
    
    r"from sentient_memory import": "from core.cognition.memory.sentient_memory import",
    r"from core.memory.sentient_memory import": "from core.cognition.memory.sentient_memory import",
    
    # PERCEPTION
    r"from vision_cortex import": "from perception.vision.vision_cortex import",
    r"from services.vision.vision_cortex import": "from perception.vision.vision_cortex import",
    
    r"from sonic_engine_v2 import": "from perception.voice.sonic_engine_v2 import",
    r"from services.voice.sonic_engine_v2 import": "from perception.voice.sonic_engine_v2 import",
    
    # COGNITION: EMOTION & CACHE
    r"from emotion_engine import": "from core.cognition.reasoning.emotion_engine import",
    r"from core.intelligence.emotion_engine import": "from core.cognition.reasoning.emotion_engine import",
    
    r"from cache_manager import": "from core.reliability.cache_manager import",
    r"from core.memory.cache_manager import": "from core.reliability.cache_manager import",
    
    # INFRASTRUCTURE: WATCHDOG & SAFETY
    r"from safety_layer import": "from infrastructure.watchdog.safety_layer import",
    r"from system.watchdog.safety_layer import": "from infrastructure.watchdog.safety_layer import",
    
    r"from controller import": "from infrastructure.system.controller import",
    r"from services.system.controller import": "from infrastructure.system.controller import",
    
    # CONFIG
    r"from config import settings": "from infrastructure.config import settings",
    r"import config.settings": "import infrastructure.config.settings",
    r"from config.settings import": "from infrastructure.config.settings import",
    
    # AGENT & SUB-CORTEX
    r"from agent import": "from core.orchestration.agent import",
    
    # SERVICES: AI (Special Cases)
    r"from services.ai.minimax_provider import": "from core.cognition.reasoning.minimax_provider import",
}

def repair_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original = content
        for pattern, replacement in MAPPINGS.items():
            # Avoid double-wrapping if already repaired
            if replacement in content:
                continue
            content = re.sub(pattern, replacement, content)

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[REPAIRED] {filepath}")
    except Exception as e:
        print(f"[ERROR] Failed to repair {filepath}: {e}")

def main():
    target_dirs = ["core", "perception", "infrastructure", "api", "backend", "action"]
    for d in target_dirs:
        if not os.path.exists(d): continue
        for root, dirs, files in os.walk(d):
            for file in files:
                if file.endswith(".py"):
                    repair_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
