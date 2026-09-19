import time
import random
import threading

# 🧿 O.M.E.G.A. SPECTRE_LAB_V1.0
# Simulated "Vulnerable IoT Drone" for Practical Learning

class VulnerableDrone:
    def __init__(self):
        self.is_hijacked = False
        self.control_owner = "ORIGINAL_OS"
        self.status = "PATROLLING"
        self.buffer = []

    def run_simulation(self):
        print(f"[DRONE] Initializing Original OS... System: {self.control_owner}")
        while True:
            if self.is_hijacked:
                print(f"[DRONE] !!! ALERT !!! CONTROL_OVERWRITTEN BY: {self.control_owner}")
                self.status = "STARK_CONTROL_ACTIVE"
            else:
                print(f"[DRONE] Status: {self.status} | Owner: {self.control_owner}")
            time.sleep(5)

    def inject_packet(self, packet_type, payload):
        """Simulates a vulnerability to buffer overflow or protocol hijacking."""
        if "PRIORITY_OVERRIDE" in payload and "STARK" in payload:
            print("[DRONE] !!! CRITICAL BUFFER OVERFLOW DETECTED !!!")
            print("[DRONE] Recalibrating Handshake...")
            time.sleep(2)
            self.is_hijacked = True
            self.control_owner = "MASTER_FAYAS"
            self.status = "TOTAL_TAKEOVER_COMPLETE"
            return True
        return False

# Global Lab Instance
lab_drone = VulnerableDrone()

def start_lab():
    t = threading.Thread(target=lab_drone.run_simulation)
    t.daemon = True
    t.start()
    print("[LAB] Simulated 'Villain Drone' is now active on localhost.")
    print("[LAB] Target Vulnerability: 'Priority_Override' Buffer Overflow.")

if __name__ == "__main__":
    start_lab()
    while True:
        time.sleep(1)
