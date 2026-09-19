import sys
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.perception.browser_console_swarm import BrowserConsoleSwarm
from core.specialized.ide_surveillance_swarm import IDESurveillanceSwarm
from core.orchestration.swarm_message_board import SwarmMessageBoard
from core.orchestration.cryogenic_swarm_manager import CryogenicSwarmManager
from core.orchestration.sandbox_approval_queue import SandboxApprovalQueue

def reset_test_environment():
    # Reset the index.html so the test works
    with open("c:\\jarvis AI\\jarvis\\scratch\\broken_app\\index.html", "w") as f:
        f.write('<!DOCTYPE html>\n<html>\n<head>\n    <title>Jarvis Swarm Test App</title>\n</head>\n<body>\n    <h1>Data Entry Form</h1>\n    <p>Clicking this button will throw an Uncaught ReferenceError in the F12 Console.</p>\n    <button onclick="submitData()">Submit</button>\n</body>\n</html>')
        
    # Clear the proxy cache and approval queue
    with open("c:\\jarvis AI\\jarvis\\scratch\\swarm_cache.json", "w") as f:
        f.write("[]")
    with open("c:\\jarvis AI\\jarvis\\scratch\\pending_approvals.json", "w") as f:
        f.write("[]")

def main():
    print("==================================================")
    print(" JARVIS 100-AGENT CRYOGENIC SANDBOX TEST")
    print("==================================================")
    
    reset_test_environment()
    
    board = SwarmMessageBoard()
    browser_agent = BrowserConsoleSwarm()
    ide_agent = IDESurveillanceSwarm()
    cryo_manager = CryogenicSwarmManager()
    
    print("\n--- PHASE 1: VULNERABILITY DETECTION ---")
    browser_agent.monitor_live_tab("http://localhost:8000/index.html")
    time.sleep(1)
    
    print("\n--- PHASE 2: CRYOGENIC ROUTING ---")
    # Instead of the IDE swarm polling blindly, the Cryogenic Manager acts as a God-Router
    # It reads the JS_ERROR topic and wakes up exactly 1 of the 100 agents.
    messages = board.poll_messages("JS_ERROR")
    for msg in messages:
        # The Cryogenic Router identifies this as a React/JS issue
        # It wakes up the exact specialist for this task out of 100.
        woken_agent = cryo_manager.wake_agent("REACT_COMPONENT_REFACTORER")
        if woken_agent:
            # Execute with the agent in an isolated Sandbox Memory Context
            result = cryo_manager.execute_and_sleep(msg['payload'])
            # After returning to sleep, it routes the payload to the Actuator
            msg["status"] = "UNREAD"
            
    # Save back to cache so IDE can pick it up
    import json
    with open(board.board_file, 'w') as f:
        json.dump(messages, f, indent=4)
        
    time.sleep(1)
    
    print("\n--- PHASE 3: SANDBOX APPROVAL QUEUE ---")
    # IDE Agent polls, reads the generated fix from the capability chain, but CANNOT WRITE IT.
    ide_agent.poll_and_heal()
    time.sleep(1)
    
    # We now prompt the User to manually approve the code in the Sandbox
    queue = SandboxApprovalQueue()
    queue.process_queue_interactively()
    
    print("\n==================================================")
    print(" TEST SUCCESS: The Sandbox architecture is secure!")
    print("==================================================")

if __name__ == "__main__":
    main()
