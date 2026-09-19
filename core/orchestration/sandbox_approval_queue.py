import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class SandboxApprovalQueue:
    """
    The Safety Sandbox Gateway.
    Agents can generate code, but they are physically locked out of writing to the C:\ Drive.
    They must submit their Capability Payloads here for human 'Y/N' approval.
    """
    def __init__(self, queue_file="c:\\jarvis AI\\jarvis\\scratch\\pending_approvals.json"):
        self.queue_file = queue_file
        if not os.path.exists(self.queue_file):
            with open(self.queue_file, 'w') as f:
                json.dump([], f)
                
    def submit_for_approval(self, agent_name: str, target_file: str, proposed_content: str):
        """Agents submit their proposed file changes to the Sandbox Queue."""
        try:
            with open(self.queue_file, 'r') as f:
                queue = json.load(f)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'sandbox_approval_queue', f'Unhandled exception: {e}')
            queue = []
            
        request_id = f"REQ-{len(queue)+1}"
        payload = {
            "id": request_id,
            "agent": agent_name,
            "target": target_file,
            "content": proposed_content,
            "status": "PENDING"
        }
        queue.append(payload)
        
        with open(self.queue_file, 'w') as f:
            json.dump(queue, f, indent=4)
            
        logging.info(f"🛡️ [Sandbox Queue] Request {request_id} submitted by {agent_name} for {target_file}. Awaiting human approval.")
        return request_id
        
    def process_queue_interactively(self):
        """The User CLI to review and approve/deny pending changes in the Sandbox."""
        try:
            with open(self.queue_file, 'r') as f:
                queue = json.load(f)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'sandbox_approval_queue', f'Unhandled exception: {e}')
            return
            
        pending = [q for q in queue if q["status"] == "PENDING"]
        if not pending:
            print("[Sandbox Queue] No pending capabilities in the Sandbox.")
            return
            
        for req in pending:
            print("\n==================================================")
            print(f" [!] PENDING SANDBOX APPROVAL: {req['id']}")
            print("==================================================")
            print(f"Agent Requesting Access: {req['agent']}")
            print(f"Target File: {req['target']}")
            print(f"Proposed Code Injection:\n{req['content'][:200]}...") # truncate for display
            print("==================================================")
            
            # Interactive prompt
            ans = input("Allow Agent to execute this capability? (Y/N): ").strip().upper()
            if ans == 'Y':
                print(f"[+] Executing Sandbox Request {req['id']}...")
                req['status'] = "APPROVED"
                
                # The Sandbox Actuator actually writes the file
                target = req['target']
                if os.path.exists(target):
                    with open(target, 'w') as f:
                        f.write(req['content'])
                    print(f"[+] Successfully wrote to {target}")
                else:
                    print(f"[-] File {target} not found.")
            else:
                print(f"[-] Request {req['id']} DENIED and destroyed in Sandbox.")
                req['status'] = "DENIED"
                
        # Save state
        with open(self.queue_file, 'w') as f:
            json.dump(queue, f, indent=4)

if __name__ == "__main__":
    queue = SandboxApprovalQueue()
    queue.process_queue_interactively()
