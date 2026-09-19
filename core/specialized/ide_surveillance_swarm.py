import logging
import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.orchestration.swarm_message_board import SwarmMessageBoard

class IDESurveillanceSwarm:
    """
    Architect Tier - IDE Surveillance
    Hooks into the IDE's Linter/Language Server Protocol (LSP).
    Now upgraded to poll the Swarm Message Board for Capability Chains.
    """
    
    def __init__(self):
        self.active_file = None
        self.board = SwarmMessageBoard()
        logging.info("👁️ [IDE Swarm] Booting Syntax Surveillance...")

    def poll_and_heal(self):
        """
        Polls the proxy cache for JS errors.
        """
        logging.info("👁️ [IDE Swarm] Aggressively polling Swarm Message Board for vulnerabilities...")
        messages = self.board.poll_messages("JS_ERROR")
        
        for msg in messages:
            error = msg['payload']['error']
            file_hint = msg['payload']['file_hint']
            logging.info(f"👁️ [IDE Swarm] INTERCEPTED ERROR from {msg['sender']}: {error}")
            
            # The IDE swarm autonomously writes code to heal the javascript error
            target_path = os.path.join("c:\\jarvis AI\\jarvis\\scratch\\broken_app", file_hint)
            if os.path.exists(target_path):
                with open(target_path, 'r') as f:
                    content = f.read()
                    
                if "<script>" not in content and "onclick=\"submitData()\"" in content:
                    logging.info("👁️ [IDE Swarm] Autonomously generated Javascript patch...")
                    patch = "\n<script>\nfunction submitData() {\n    alert('Data Submitted Successfully!');\n}\n</script>\n"
                    proposed_content = content.replace("</body>", patch + "</body>")
                    
                    # NEW SAFETY ARCHITECTURE: Send to Sandbox instead of writing
                    logging.warning(f"🛡️ [IDE Swarm] Safety Lock Engaged. Routing capability payload to Sandbox Approval Queue.")
                    from core.orchestration.sandbox_approval_queue import SandboxApprovalQueue
                    queue = SandboxApprovalQueue()
                    queue.submit_for_approval("IDESurveillanceSwarm", target_path, proposed_content)
                        
                logging.info(f"✅ [IDE Swarm] Capability successfully routed to Sandbox.")
            else:
                logging.error(f"👁️ [IDE Swarm] Target {target_path} not found.")

if __name__ == "__main__":
    swarm = IDESurveillanceSwarm()
    # In a real daemon, this runs in a while True loop
    swarm.poll_and_heal()
