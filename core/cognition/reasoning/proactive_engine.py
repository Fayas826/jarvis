import asyncio
import time
import psutil
from datetime import datetime
from typing import List, Dict

class ProactiveEngine:
    def __init__(self):
        self.insights = []
        self.last_check = 0
        self.CHECK_INTERVAL = 300 # 5 minutes
        self.running = False

    async def start_loop(self):
        self.running = True
        print("[PROACTIVE_ENGINE] Neural Background Monitor ACTIVE.")
        while self.running:
            try:
                await self.run_diagnostics()
            except Exception as e:
                print(f"[PROACTIVE_ENGINE_ERR] {e}")
            await asyncio.sleep(self.CHECK_INTERVAL)

    async def run_diagnostics(self):
        new_insights = []
        now = datetime.now()
        
        # 1. Temporal Context
        if now.hour >= 23 or now.hour <= 4:
            new_insights.append({
                "id": "PRO_TEMPORAL",
                "title": "Circadian Alert",
                "text": "Sir, it's well past midnight. Cognitive performance declines after 18 hours of wakefulness. Tactical rest is advised.",
                "severity": "LOW",
                "action": "GO_TO_SLEEP"
            })

        # 2. Hardware Vitals
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 90:
            new_insights.append({
                "id": "PRO_CPU",
                "title": "Thermal Redline",
                "text": f"CPU load is at {cpu_usage}%. Core temperatures are rising. Shall I purge non-essential background processes?",
                "severity": "HIGH",
                "action": "PURGE_PROCESSES"
            })
            
        # 3. Project Context (Detect if user is working on a specific file)
        # This could be expanded by checking active window or recent files
        
        # 4. Proactive Task: "I see you're working on X, shall I do Y?"
        # Placeholder for more complex logic
        
        self.insights = new_insights
        if self.insights:
            print(f"[PROACTIVE_ENGINE] Generated {len(self.insights)} new insights.")

    def get_latest_insights(self) -> List[Dict]:
        return self.insights

proactive_engine = ProactiveEngine()
