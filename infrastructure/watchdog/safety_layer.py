import os
import json
from typing import Dict, Any, List

# 🛡️ O.M.E.G.A. SAFETY_LAYER_V1
# Implements permission gates, sandboxing logic, and destructive action verification.

class SafetyLayer:
    def __init__(self):
        self.dangerous_intents = [
            "system_power", 
            "delete_file", 
            "registry_edit", 
            "terminate_process",
            "format_drive",
            "execute_risky_script"
        ]
        self.pending_actions = {} # ID -> Action

    def check_safety(self, intent: str, payload: Any) -> Dict[str, Any]:
        """
        🧬 THE_PERIMETER_GATE
        Returns status: "ALLOWED" or "PENDING_CONFIRMATION"
        """
        if intent in self.dangerous_intents:
            action_id = f"act_{os.urandom(4).hex()}"
            self.pending_actions[action_id] = {"intent": intent, "payload": payload}
            
            return {
                "status": "PENDING_CONFIRMATION",
                "action_id": action_id,
                "message": f"Sir, I require confirmation for the following destructive action: {intent.upper()}"
            }
        
        return {"status": "ALLOWED"}

    def confirm_action(self, action_id: str) -> Dict[str, Any]:
        if action_id in self.pending_actions:
            action = self.pending_actions.pop(action_id)
            return {"status": "ALLOWED", "action": action}
        return {"status": "ERROR", "message": "Invalid or expired Action ID."}

    def sandbox_validate(self, script_path: str) -> bool:
        """Simple static analysis for risky keywords in scripts."""
        risky_keywords = ["rm -rf", "del /s", "format ", "reg delete", "os.system"]
        try:
            with open(script_path, 'r') as f:
                content = f.read()
                for kw in risky_keywords:
                    if kw in content:
                        return False
            return True
        except:
            return False

safety_gate = SafetyLayer()
