import os
import time
import subprocess

# 🧿 J.A.R.V.I.S. O.M.E.G.A. — IMMORTAL_WATCHDOG_V1
# This process ensures JARVIS nodes are ALWAYS running.

class SentinelWatchdog:
    def __init__(self):
        self.master_key = r"c:\jarvis AI\IGNITE_ZENITH.bat"

    def monitor_heartbeat(self):
        """Checks if the master ignition is active. If not, it re-ignites."""
        while True:
            try:
                # Check if api.py is running
                import psutil
                running = False
                for proc in psutil.process_iter(['name', 'cmdline']):
                    if "api.py" in str(proc.info['cmdline']):
                        running = True
                        break
                
                if not running:
                    print("[WATCHDOG] CORE SILENCED. RE-IGNITING ZENITH...")
                    # Add a cooling period to prevent loops
                    time.sleep(5)
                    subprocess.Popen([self.master_key], shell=True)
                    time.sleep(20) # Wait for ignition to settle
            except: pass
            time.sleep(15) # 15-second heartbeat

if __name__ == "__main__":
    time.sleep(30) # Initial stabilization buffer
    guardian = SentinelWatchdog()
    guardian.monitor_heartbeat()
