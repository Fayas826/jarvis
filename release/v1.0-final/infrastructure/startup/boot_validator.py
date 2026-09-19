
import os
import sys
import importlib

from dotenv import load_dotenv

# Add project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Load environment variables from root .env
load_dotenv(os.path.join(ROOT_DIR, ".env"))

print(f"[BOOT] O.M.E.G.A. BOOT_VALIDATOR [ROOT: {ROOT_DIR}]")

CORE_MODULES = [
    "core.cognition.reasoning.brain",
    "core.cognition.reasoning.neural_core",
    "core.cognition.reasoning.onnx_engine",
    "core.cognition.memory.memory",
    "core.orchestration.agent",
    "core.reliability.reliability_engine",
    "infrastructure.system.controller",
    "perception.vision.vision_cortex",
    "infrastructure.watchdog.system_guardian",
]

def validate():
    success_count = 0
    fail_count = 0
    
    print("-" * 50)
    for mod in CORE_MODULES:
        try:
            importlib.import_module(mod)
            print(f"[OK] {mod}")
            success_count += 1
        except Exception as e:
            print(f"[FAIL] {mod}: {e}")
            fail_count += 1
    
    print("-" * 50)
    print(f"SUMMARY: {success_count} Passed, {fail_count} Failed")
    
    if fail_count == 0:
        print("[SUCCESS] SYSTEM ARCHITECTURE IS STABLE.")
    else:
        print("[CRITICAL] ARCHITECTURE INSTABILITY DETECTED.")
        sys.exit(1)

if __name__ == "__main__":
    validate()
