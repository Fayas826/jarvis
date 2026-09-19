import os
import sys
import time
import asyncio
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 🛡️ O.M.E.G.A. TIER_11: SOVEREIGN_WATCHDOG_V1.0

class SovereignWatchdog(FileSystemEventHandler):
    def __init__(self, architect_callback):
        self.architect = architect_callback
        self.error_registry = {} # file_path: attempt_count
        self.MAX_ATTEMPTS = 3

    def on_modified(self, event):
        if event.is_directory: return
        if event.src_path.endswith((".py", ".jsx", ".js")):
            self.verify_integrity(event.src_path)

    def verify_integrity(self, file_path):
        """Scans for structural instabilities or syntax crashes."""
        try:
            if file_path.endswith(".py"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    compile(content, file_path, "exec")
            # Clear error registry on successful compile
            if file_path in self.error_registry:
                del self.error_registry[file_path]
        except SyntaxError as e:
            error_context = {
                "message": e.msg,
                "lineno": e.lineno,
                "offset": e.offset,
                "text": e.text,
                "type": type(e).__name__
            }
            self.handle_instability(file_path, error_context)

    def handle_instability(self, file_path, error_context):
        attempts = self.error_registry.get(file_path, 0) + 1
        self.error_registry[file_path] = attempts
        
        error_msg = error_context["message"]
        if attempts <= self.MAX_ATTEMPTS:
            print(f"[WATCHDOG] Instability detected in {os.path.basename(file_path)} (Line {error_context.get('lineno')}): {error_msg}. Attempting Self-Heal ({attempts}/{self.MAX_ATTEMPTS})...")
            # Trigger the Architect Core to rewrite the broken logic
            asyncio.run(self.architect(file_path, error_context))
        else:
            print(f"[CRITICAL] Self-Heal Failed for {os.path.basename(file_path)}. Generating Agentic Beacon for Antigravity.")
            self.ignite_beacon(file_path, error_msg)

    def ignite_beacon(self, file_path, error_msg):
        """Manifests a beacon log that the Antigravity Agent monitors."""
        beacon_path = file_path + ".RES_FAIL"
        with open(beacon_path, "w") as f:
            f.write(f"TIMESTAMP: {time.ctime()}\n")
            f.write(f"ERROR: {error_msg}\n")
            f.write(f"STATUS: JARVIS_SURRENDERED_CONTROL\n")
            f.write("ACTION_REQUIRED: Antigravity Agent Intervention Needed.")

from core.cognition.reasoning.architect_core import architect_core

# Singleton Watchdog interface
async def architect_repair_logic(file_path, error_context):
    """
    This is where JARVIS uses his local reasoning to fix his own code.
    """
    success = await architect_core.repair(file_path, error_context)
    if not success:
        # If internal repair fails, we can log it for Antigravity (the LLM)
        # In a real scenario, this might trigger a webhook or a specific log format.
        pass
    return success

class GuardianSystem:
    def __init__(self):
        self.observer = Observer()
        self.handler = SovereignWatchdog(architect_repair_logic)

    def start(self):
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.observer.schedule(self.handler, path=root_path, recursive=True)
        self.observer.start()
        print("[WATCHDOG] Sentinel Intelligence Monitoring: ACTIVE")

    def stop(self):
        self.observer.stop()
        self.observer.join()

system_guardian = GuardianSystem()
