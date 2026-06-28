
import time
import psutil
import threading

class GovernanceEngine:
    def __init__(self):
        # ⚖️ DOMAIN_6: PRIORITY_ARBITRATION
        self.priority_map = {
            "USER_VOICE": 100,
            "SYSTEM_HALT": 95,
            "THERMAL_CRITICAL": 90,
            "MISSION_AGENT": 80,
            "USER_CLAP": 70,
            "THERMAL_WARNING": 60,
            "VISION_ALERT": 50,
            "BACKGROUND_SCAN": 10
        }
        
        self.event_queue = []
        self.active_lock = threading.Lock()
        self.current_execution = None
        self.interrupt_flag = False

    def request_execution(self, event_type, payload):
        """Domain 6: Arbitrates event priority and decides execution order."""
        priority = self.priority_map.get(event_type, 0)
        
        with self.active_lock:
            if self.current_execution:
                current_prio = self.priority_map.get(self.current_execution["type"], 0)
                if priority > current_prio:
                    print(f"⚖️ GOVERNANCE: Interrupting {self.current_execution['type']} for {event_type}")
                    self.interrupt_flag = True
                    return self.execute(event_type, payload)
                else:
                    print(f"⚖️ GOVERNANCE: Queuing {event_type} (Priority: {priority} < {current_prio})")
                    self.event_queue.append({"type": event_type, "prio": priority, "payload": payload})
                    return {"status": "QUEUED", "priority": priority}
            else:
                return self.execute(event_type, payload)

    def execute(self, event_type, payload):
        self.interrupt_flag = False
        self.current_execution = {"type": event_type, "payload": payload}
        # Simulation of execution logic
        return {"status": "EXECUTING", "type": event_type}

    def yield_execution(self):
        """Instant interrupt policy."""
        print("⚖️ GOVERNANCE: Global Interrupt - Yielding immediately.")
        self.interrupt_flag = True
        self.current_execution = None
        return {"status": "YIELDED"}

    # 🛡️ DOMAIN_6: PERMISSION_CONTROL
    def verify_action(self, intent, confidence):
        """Checks safety, reversibility, and auth before critical actions."""
        critical_intents = ["delete", "format", "shutdown", "override"]
        safety_score = confidence * 1.0 # Simple simulation
        
        is_critical = any(kw in intent.lower() for kw in critical_intents)
        if is_critical and safety_score < 0.95:
            return {"authorized": False, "reason": "Insufficient safety score for critical action."}
        
        return {"authorized": True, "safety_score": safety_score}

    # 🔋 DOMAIN_6: RESOURCE_ETHICS
    def get_resource_policy(self):
        """Monitors hardware load and dictates sacrifice priorities."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        policy = {
            "hud_particles": 1.0,
            "vision_frequency": 1.0,
            "background_scans": True,
            "mode": "PERFORMANCE"
        }

        if cpu > 80 or ram > 85:
            policy["hud_particles"] = 0.2
            policy["vision_frequency"] = 0.1
            policy["background_scans"] = False
            policy["mode"] = "POWER_SAVE"
        elif cpu > 60:
            policy["hud_particles"] = 0.5
            policy["vision_frequency"] = 0.5
            policy["mode"] = "BALANCED"

        return policy

governance = GovernanceEngine()
