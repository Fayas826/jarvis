import json
import os
import threading
import time
from core.cognition.reasoning.shared_state import INTEL_CACHE

# 🛰️ O.M.E.G.A. TIER_7: OMNI_LINK
# Global Mesh & Multi-Device State Synchronization

class OmniLink:
    def __init__(self):
        self.sync_active = False
        self.nodes = ["PC_SENTINEL", "MOBILE_CENTRAL", "SATELLITE_ALPHA"]
        self.state_file = "c:\\jarvis AI\\jarvis\\backend\\global_state.json"
        self._lock = threading.Lock()

    def start(self):
        """Ignites the global mesh sync."""
        if self.sync_active: return
        self.sync_active = True
        threading.Thread(target=self._sync_loop, daemon=True).start()
        print("[OMNI] Global Mesh: ONLINE")

    def _sync_loop(self):
        """Continuously broadcasts local state to the global mesh."""
        while self.sync_active:
            try:
                # 🧬 Gather current tactical state
                state = {
                    "vitals": INTEL_CACHE.get("vitals", {}),
                    "vision": INTEL_CACHE.get("vision_insight", ""),
                    "mode": INTEL_CACHE.get("mode", "default"),
                    "timestamp": time.time()
                }
                
                with self._lock:
                    with open(self.state_file, "w") as f:
                        json.dump(state, f)
                
            except Exception as e:
                print(f"[OMNI] Sync Error: {e}")
            
            time.sleep(5) # Sync interval

    def get_global_state(self):
        """Retrieves the state from the mesh."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, "r") as f:
                    return json.load(f)
        except: pass
        return {}

# Global Instance
omni_link = OmniLink()
