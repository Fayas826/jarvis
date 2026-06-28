
import psutil
import time
import os
import json
from typing import Dict

class ContextEngine:
    """🌍 O.M.E.G.A. CONTEXTUAL_INTELLIGENCE: State-Driven Behavior Enforcement."""
    
    def __init__(self):
        self.state = "IDLE" 
        self.last_input_time = time.time()
        self.behavior_map = {
            "IDLE": "OPTIMIZE: Perform cleanup and background learning.",
            "FOCUSED": "SILENT: Minimize interference, suppress non-critical alerts.",
            "HIGH_LOAD": "BALANCE: Throttle non-essential background tasks.",
            "CRITICAL": "REPAIR: Aggressive self-healing and resource recovery."
        }
        
    def get_context(self) -> Dict:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        
        # Determine State
        if cpu > 95 or mem > 95:
            self.state = "CRITICAL"
        elif cpu > 75:
            self.state = "HIGH_LOAD"
        elif time.time() - self.last_input_time < 300: # 5 mins
            self.state = "FOCUSED"
        else:
            self.state = "IDLE"
            
        return {
            "state": self.state,
            "behavior": self.behavior_map[self.state],
            "cpu_percent": cpu,
            "memory_percent": mem,
            "timestamp": time.time(),
            "os": "Windows"
        }

    def update_activity(self):
        """Called by Sentinel when user activity (mouse/key) is detected."""
        self.last_input_time = time.time()
        if self.state == "IDLE":
            self.state = "FOCUSED"

    async def enforce_behavior(self, task_engine):
        """Triggers background tasks based on context."""
        context = self.get_context()
        if context["state"] == "IDLE":
            # Example: Trigger System Clean Skill
            print("🌍 [CONTEXT] System IDLE. Initiating optimizations...")
            # await task_engine.execute_task(...) # Placeholder for autonomous tasks
        elif context["state"] == "CRITICAL":
            print("🚨 [CONTEXT] System CRITICAL. Freeing resources...")
            # Logic to kill high-memory non-essential processes

context_engine = ContextEngine()
