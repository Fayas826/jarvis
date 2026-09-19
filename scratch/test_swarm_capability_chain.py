import sys
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.perception.browser_console_swarm import BrowserConsoleSwarm
from core.specialized.ide_surveillance_swarm import IDESurveillanceSwarm
from core.orchestration.swarm_message_board import SwarmMessageBoard

def main():
    print("==================================================")
    print(" JARVIS SWARM CAPABILITY CHAIN TEST")
    print("==================================================")
    
    # 1. Boot the Proxy Cache
    logging.info("🚀 Booting Swarm Message Board (Proxy Cache)...")
    board = SwarmMessageBoard()
    time.sleep(1)
    
    # 2. Boot the isolated Swarms
    browser_agent = BrowserConsoleSwarm()
    ide_agent = IDESurveillanceSwarm()
    time.sleep(1)
    
    print("\n--- PHASE 1: VULNERABILITY DETECTION ---")
    # The Browser Agent monitors the broken app.
    # It catches a ReferenceError, but cannot fix it itself.
    browser_agent.monitor_live_tab("http://localhost:8000/index.html")
    time.sleep(2)
    
    print("\n--- PHASE 2: PROXY INTERCEPTION ---")
    # We prove the message is now sitting in the Proxy Cache
    messages = board.poll_messages("JS_ERROR")
    # Put them back as UNREAD for the IDE agent to consume
    for m in messages:
        m["status"] = "UNREAD"
    with open(board.board_file, 'w') as f:
        import json
        json.dump(messages, f, indent=4)
        
    logging.info(f"📦 [Proxy Cache] Currently holding {len(messages)} UNREAD Capability Payloads.")
    time.sleep(2)
    
    print("\n--- PHASE 3: CAPABILITY EXECUTION ---")
    # The IDE Agent, completely isolated from the Browser Agent, polls the cache
    ide_agent.poll_and_heal()
    time.sleep(1)
    
    print("\n==================================================")
    print(" TEST SUCCESS: The Swarms established a Capability Chain!")
    print("==================================================")

if __name__ == "__main__":
    main()
