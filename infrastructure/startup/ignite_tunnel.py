import subprocess
import time
import json
import os
import shutil
import signal
import sys

# 🛰️ J.A.R.V.I.S. O.M.E.G.A. — TUNNEL_IGNITION_V17 (Localtunnel)
# This script ensures the mobile app always has a stable endpoint.
# Optimized to prevent process leaks and recursive spawns.

from system_logger import system_logger

def ignite():
    # 🛡️ O.M.E.G.A. PROCESS_GUARD: Prevent duplicate tunnels
    import psutil
    for proc in psutil.process_iter(['name', 'cmdline']):
        if proc.info['cmdline'] and 'localtunnel' in " ".join(proc.info['cmdline']):
             if "--subdomain jarvis-zenith-omega-v10" in " ".join(proc.info['cmdline']):
                 system_logger.log("INFO", "TUNNEL", "REDUNDANT_PROCESS_DETECTED", {"action": "TERMINATING"})
                 proc.terminate()

    system_logger.log("INFO", "TUNNEL", "IGNITION_STARTING", {"subdomain": "jarvis-zenith-omega-v10"})
    
    subdomain = "jarvis-zenith-omega-v10"
    port = "5001" 
    
    npx_path = shutil.which("npx") or r"C:\Program Files\nodejs\npx.cmd"
    lt_args = [npx_path, "localtunnel", "--port", port, "--subdomain", subdomain]
    
    while True:
        try:
            # 🧬 O.M.E.G.A. SILENT_IGNITION: shell=False + CREATE_NO_WINDOW
            proc = subprocess.Popen(
                lt_args, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                creationflags=0x08000000 # CREATE_NO_WINDOW
            )
            
            manifest = {
                "backend": f"https://{subdomain}.loca.lt",
                "timestamp": time.time(),
                "protocol": "LOCALTUNNEL_V17"
            }
            
            with open("tunnel_manifest.json", "w") as f:
                json.dump(manifest, f)
            
            system_logger.log("SUCCESS", "TUNNEL", "RESONANCE_ESTABLISHED", {"url": manifest["backend"]})
            
            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    system_logger.log("WARNING", "TUNNEL", "CONNECTION_LOST", {"action": "RECONNECTING"})
                    break
                time.sleep(1)
            
            try: proc.terminate()
            except: pass
            time.sleep(10)
            
        except Exception as e:
            system_logger.log("ERROR", "TUNNEL", "CRITICAL_FAIL", {"error": str(e)})
            time.sleep(15)

if __name__ == "__main__":
    try:
        ignite()
    except KeyboardInterrupt:
        system_logger.log("INFO", "TUNNEL", "SHUTDOWN", {"reason": "USER_INTERRUPT"})
        sys.exit(0)
