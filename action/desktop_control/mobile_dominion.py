import os
import ctypes
import asyncio
import time
import shutil
import pyzipper
from action.desktop_control.desktop import capture_screen
from perception.voice.sonic_engine_v2 import sonic_engine

# 📱 O.M.E.G.A. MOBILE DOMINION (Chapter 14 & 15)
# Remote Biometric, Intruder Control & Data Vault Protocol

class MobileDominion:
    def __init__(self):
        self.intruder_log_dir = r"c:\jarvis AI\jarvis\scratch\intruder_logs"
        self.sensitive_data_dir = r"c:\jarvis AI\jarvis\Vault_Data"
        self.vault_archive = r"c:\jarvis AI\jarvis\Vault_Secure.zip"
        self.vault_password = b"OMEGA_PROTOCOL_99" # Default Master Password

        if not os.path.exists(self.intruder_log_dir):
            os.makedirs(self.intruder_log_dir)
        # Create a dummy sensitive folder if it doesn't exist
        if not os.path.exists(self.sensitive_data_dir) and not os.path.exists(self.vault_archive):
            os.makedirs(self.sensitive_data_dir)
            with open(os.path.join(self.sensitive_data_dir, "secret_manifest.txt"), "w") as f:
                f.write("TOP SECRET JARVIS DATA\nThis folder will be encrypted and deleted during Lockdown.")

    def execute_vault_protocol(self):
        """
        Chapter 15: Ghost Mode
        Encrypts the sensitive directory into a secure AES ZIP, then deletes the unencrypted folder.
        """
        if not os.path.exists(self.sensitive_data_dir):
            print("[MOBILE_DOMINION] Vault Protocol: No sensitive directory found to ghost.")
            return False

        print("[MOBILE_DOMINION] Executing Vault Protocol (Ghost Mode)...")
        try:
            # 1. Compress & AES Encrypt
            with pyzipper.AESZipFile(self.vault_archive,
                                     'w',
                                     compression=pyzipper.ZIP_LZMA,
                                     encryption=pyzipper.WZ_AES) as zf:
                zf.setpassword(self.vault_password)
                for foldername, subfolders, filenames in os.walk(self.sensitive_data_dir):
                    for filename in filenames:
                        filepath = os.path.join(foldername, filename)
                        arcname = os.path.relpath(filepath, self.sensitive_data_dir)
                        zf.write(filepath, arcname)
            
            # 2. Securely Delete Original Unencrypted Data
            shutil.rmtree(self.sensitive_data_dir)
            print("[MOBILE_DOMINION] Vault Protocol SUCCESS. Data Ghosted.")
            return True
        except Exception as e:
            print(f"[MOBILE_DOMINION] Vault Protocol FAILED: {e}")
            return False

    def trigger_intruder_lockdown(self):
        """
        Executes the 'Theft Protocol':
        1. Executes Vault Protocol (Encrypts & Deletes Data).
        2. Takes a webcam/screen snapshot.
        3. Locks the Windows workstation instantly.
        4. Fires the Sonic Alarm.
        """
        print("[MOBILE_DOMINION] 🚨 INTRUDER LOCKDOWN INITIATED 🚨")
        
        # 0. Ghost the Data (Chapter 15 Vault Protocol)
        self.execute_vault_protocol()

        # 1. Capture the intruder
        timestamp = int(time.time())
        snapshot_path = os.path.join(self.intruder_log_dir, f"intruder_{timestamp}.png")
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(snapshot_path, frame)
            cap.release()
            print(f"[MOBILE_DOMINION] Intruder visual secured: {snapshot_path}")
        except Exception as e:
            print(f"[MOBILE_DOMINION] Vision capture failed: {e}")

        # 2. Lock the Workstation (Windows API)
        try:
            ctypes.windll.user32.LockWorkStation()
            print("[MOBILE_DOMINION] Workstation Hard-Locked.")
        except Exception as e:
            print(f"[MOBILE_DOMINION] Lock failed: {e}")

        # 3. Trigger Sonic Alarm
        asyncio.create_task(sonic_engine.speak("WARNING. UNAUTHORIZED ACCESS DETECTED. INTRUDER PROTOCOL ENGAGED. AUTHORITIES HAVE BEEN NOTIFIED."))
        
        return {"status": "LOCKDOWN_ENGAGED", "snapshot": snapshot_path, "vault": "SECURED"}

    def remote_ignite(self):
        """Wakes up the laptop HUD remotely."""
        print("[MOBILE_DOMINION] Remote Ignition Received.")
        from vocal_guardian import ignite_hud_vocal
        return ignite_hud_vocal()

mobile_dominion = MobileDominion()
