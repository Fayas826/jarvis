
import os
import sys
import time
import json
import requests
from typing import Dict

class JarvisHUD:
    """🖥️ O.M.E.G.A. DASHBOARD: Visibility & Control."""
    
    def __init__(self):
        self.api_url = "http://localhost:5001/api"
        self.colors = {
            "header": "\033[95m",
            "blue": "\033[94m",
            "green": "\033[92m",
            "warning": "\033[93m",
            "fail": "\033[91m",
            "end": "\033[0m",
            "bold": "\033[1m"
        }

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        self.clear()
        print(f"{self.colors['header']}=== JARVIS O.M.E.G.A. ZENITH_HUD ==={self.colors['end']}")
        
        try:
            # 1. System Health
            health = requests.get(f"{self.api_url}/health").json()
            status = health.get("status", "UNKNOWN")
            print(f"Status: {self.colors['green'] if status == 'HEALTHY' else self.colors['fail']}{status}{self.colors['end']}")
            
            # 2. Context
            context = requests.get(f"{self.api_url}/system/status").json() # Assuming this endpoint exists or similar
            state = context.get("state", "IDLE")
            print(f"Intelligence State: {self.colors['blue']}{state}{self.colors['end']}")
            print(f"CPU: {context.get('cpu_percent', 0)}% | MEM: {context.get('memory_percent', 0)}%")
            
            # 3. Recent Tasks
            print(f"\n{self.colors['bold']}Recent Tasks:{self.colors['end']}")
            # Mocking recent tasks or fetching from a log
            print("- [SUCCESS] Start Work (09:00)")
            print("- [SUCCESS] Cleanup System (12:30)")
            
            print(f"\n{self.colors['warning']}Commands: start_work, cleanup_system, prepare_meeting, shutdown_all{self.colors['end']}")
            
        except Exception as e:
            print(f"{self.colors['fail']}❌ HUD_DISCONNECTED: Backend unreachable.{self.colors['end']}")

if __name__ == "__main__":
    hud = JarvisHUD()
    while True:
        hud.render()
        time.sleep(5)
