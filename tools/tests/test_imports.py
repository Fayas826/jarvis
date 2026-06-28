import sys
print("Starting import test...")

try:
    import fastapi
    print("[OK] fastapi")
except ImportError as e:
    print(f"[FAIL] fastapi: {e}")

try:
    from openai import OpenAI
    print("[OK] openai")
except ImportError as e:
    print(f"[FAIL] openai: {e}")

try:
    from memory import memory
    print("[OK] memory")
except ImportError as e:
    print(f"[FAIL] memory: {e}")

try:
    from sonic_engine_v2 import sonic_engine
    print("[OK] sonic_engine_v2")
except ImportError as e:
    print(f"[FAIL] sonic_engine_v2: {e}")

try:
    from vision_core import vision_core
    print("[OK] vision_core")
except ImportError as e:
    print(f"[FAIL] vision_core: {e}")

try:
    from zenith_core import zenith_core
    print("[OK] zenith_core")
except ImportError as e:
    print(f"[FAIL] zenith_core: {e}")

try:
    from omega_mesh import omega_mesh
    print("[OK] omega_mesh")
except ImportError as e:
    print(f"[FAIL] omega_mesh: {e}")

print("Import test complete.")
