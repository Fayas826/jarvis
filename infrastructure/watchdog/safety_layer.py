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
            "execute_risky_script",
            "send_message",
            "purchase",
            "ticket_booking",
            "payment"
        ]
        self.pending_actions = {} # ID -> Action
        
        # Risk Classifications
        self.risk_tiers = {
            "open_app": "LOW",
            "read_screen": "LOW",
            "search": "LOW",
            "scroll": "LOW",
            "inspect_page": "LOW",
            "create_file": "MEDIUM",
            "modify_file": "MEDIUM",
            "install_package": "MEDIUM",
            "submit_form": "MEDIUM",
            "system_power": "HIGH",
            "delete_file": "HIGH",
            "registry_edit": "HIGH",
            "terminate_process": "HIGH",
            "format_drive": "HIGH",
            "execute_risky_script": "HIGH",
            "send_message": "HIGH",
            "purchase": "HIGH",
            "ticket_booking": "HIGH",
            "payment": "HIGH"
        }

    def check_safety(self, intent: str, payload: Any) -> Dict[str, Any]:
        """
        🧬 THE_PERIMETER_GATE
        Enforces safety policies: pauses destructive/high-risk actions for confirmation.
        """
        tier = self.risk_tiers.get(intent, "LOW")
        
        # Check command payload for dangerous destructive patterns
        destructive_patterns = ["rm -rf", "del /s", "del /f", "rmdir /s", "format ", "reg delete", "drop database", "shutdown"]
        is_destructive = False
        
        if isinstance(payload, dict):
            cmd_str = str(payload.get("command", "")).lower()
            script_str = str(payload.get("path", "")).lower()
            for pattern in destructive_patterns:
                if pattern in cmd_str or pattern in script_str:
                    is_destructive = True
                    break

        if tier == "HIGH" or is_destructive:
            import uuid
            action_id = f"act_{uuid.uuid4().hex[:8]}"
            self.pending_actions[action_id] = {"intent": intent, "payload": payload, "tier": tier}
            return {
                "status": "PENDING_CONFIRMATION",
                "action_id": action_id,
                "message": f"High-risk action flagged ({intent}). Awaiting explicit user confirmation."
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
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'safety_layer', f'Unhandled exception: {e}')
            return False

safety_gate = SafetyLayer()
