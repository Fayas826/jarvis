import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.orchestration.swarm_message_board import SwarmMessageBoard

class BrowserConsoleSwarm:
    """
    Architect Tier - Browser F12 Surveillance
    Deploys Chrome DevTools Protocol (CDP) or Playwright to hook into the F12 Inspect window.
    Reads JS/Network errors and translates them into frontend code fixes.
    """
    
    def __init__(self):
        self.sub_agents = ["Network Security Agent", "React DOM Analyzer", "Chief Console Officer"]
        self.board = SwarmMessageBoard()
        logging.info("🌐 [Browser Swarm] Hooking into Chrome DevTools Console...")

    def monitor_live_tab(self, url: str):
        """
        Connects to the active Chrome tab.
        If a red error appears in the console, the Swarm analyzes the stack trace.
        """
        logging.info(f"🌐 [Browser Swarm] Connected to F12 Console on {url}")
        
        # Simulating detecting a live Javascript error via CDP
        if "5173" in url or "3000" in url:
            error_msg = f"Uncaught SyntaxError in UI Components at {url}"
            file_hint = "App.jsx / page.tsx"
        else:
            error_msg = "Uncaught ReferenceError: submitData is not defined at HTMLButtonElement.onclick"
            file_hint = "index.html"
            
        logging.error(f"🌐 [Browser Swarm] DETECTED: {error_msg}")
        
        # The agent establishes a Capability Chain by posting it to the shared cache.
        logging.info("🌐 [Browser Swarm] No local capability to fix. Passing capability payload to Swarm Message Board.")
        self.board.post_message(
            sender="BrowserConsoleSwarm",
            topic="JS_ERROR",
            payload={
                "url": url,
                "error": error_msg,
                "file_hint": file_hint
            }
        )
        
        return {"status": "monitoring", "errors_detected": 1}

if __name__ == "__main__":
    swarm = BrowserConsoleSwarm()
    # Now monitoring the Next.js Command Center, the Vite HUD, and the legacy Python app
    target_urls = [
        "http://localhost:3000/dashboard", # Next.js
        "http://localhost:5173/",          # Vite HUD
        "http://localhost:8000/index.html" # Legacy
    ]
    
    for url in target_urls:
        swarm.monitor_live_tab(url)
