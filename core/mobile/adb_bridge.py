import subprocess
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ADB_BRIDGE] %(message)s")

ADB_PATH = r"C:\AMD\platform-tools\adb.exe"

def run_adb(args, timeout=10):
    if not os.path.exists(ADB_PATH):
        return None, "ADB binary not found at C:\\AMD\\platform-tools\\adb.exe"
    cmd = [ADB_PATH] + args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return None, str(e)

def get_devices():
    stdout, stderr = run_adb(["devices"])
    if not stdout:
        return []
    devices = []
    lines = stdout.splitlines()[1:]
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == 'device':
            devices.append(parts[0])
    return devices

def make_call(phone_number):
    logging.info(f"Initiating direct phone call via USB ADB to {phone_number}...")
    stdout, stderr = run_adb(["shell", "am", "start", "-a", "android.intent.action.CALL", "-d", f"tel:{phone_number}"])
    return stdout

def unlock_phone(password=None):
    logging.info("Attempting automated phone unlock sequence via USB ADB...")
    # 1. Wake screen
    run_adb(["shell", "input", "keyevent", "224"])
    time.sleep(0.5)
    # 2. Swipe up to reveal PIN/Password keypad
    run_adb(["shell", "input", "swipe", "500", "1500", "500", "500", "200"])
    time.sleep(0.5)
    if password:
        # 3. Enter password/PIN
        run_adb(["shell", "input", "text", str(password)])
        time.sleep(0.3)
        # 4. Press Enter
        run_adb(["shell", "input", "keyevent", "66"])
    return "UNLOCK_SEQUENCE_DISPATCHED"

def tap_screen(x, y):
    stdout, stderr = run_adb(["shell", "input", "tap", str(x), str(y)])
    return stdout

def swipe_screen(x1, y1, x2, y2, duration=300):
    stdout, stderr = run_adb(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])
    return stdout

def type_text(text):
    stdout, stderr = run_adb(["shell", "input", "text", text])
    return stdout

def capture_screen_bytes():
    if not os.path.exists(ADB_PATH):
        return None
    try:
        res = subprocess.run([ADB_PATH, "exec-out", "screencap", "-p"], capture_output=True, timeout=5)
        if res.returncode == 0:
            return res.stdout
    except Exception as e:
        logging.error(f"Failed to capture screen: {e}")
    return None

if __name__ == "__main__":
    devs = get_devices()
    print(f"Connected ADB Devices: {devs}")
