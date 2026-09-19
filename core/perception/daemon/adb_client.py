import time
import subprocess
import logging

log = logging.getLogger("jarvis_daemon")
ADB_PATH = r"C:\AMD\platform-tools\adb.exe"

def adb(*args, timeout=12):
    try:
        r = subprocess.run([ADB_PATH] + list(args), capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return None, str(e)

def adb_shell(*cmd, timeout=12):
    return adb("shell", *cmd, timeout=timeout)

def adb_raw(*args, timeout=10):
    try:
        r = subprocess.run([ADB_PATH] + list(args), capture_output=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else None
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'adb_client', f'Unhandled exception: {e}')
        return None

def is_phone_connected():
    out, _ = adb("devices")
    return "uozd6pcuijqozhh6" in (out or "") or (out and "device" in out and "List" not in out.split("\n")[0])

def phone_wake():
    adb_shell("input", "keyevent", "224")
    time.sleep(0.3)

def phone_home(): adb_shell("input", "keyevent", "3")
def phone_back(): adb_shell("input", "keyevent", "4")
def phone_tap(x, y): adb_shell("input", "tap", str(x), str(y))
def phone_swipe(x1, y1, x2, y2, ms=300): adb_shell("input", "swipe", str(x1), str(y1), str(x2), str(y2), str(ms))
def phone_type(text): adb_shell("input", "text", text.replace(" ", "%s"))
def phone_scroll_down(): phone_swipe(540, 1400, 540, 600, 300)
def phone_scroll_up(): phone_swipe(540, 600, 540, 1400, 300)

def phone_screenshot_bytes():
    return adb_raw("exec-out", "screencap", "-p")

def phone_battery_level():
    out, _ = adb_shell("dumpsys", "battery")
    if out:
        for line in out.splitlines():
            if "level:" in line: return int(line.split(":")[-1].strip())
    return -1

def phone_screen_state():
    out, _ = adb_shell("dumpsys", "power")
    if out:
        for line in out.splitlines():
            if "mWakefulness=" in line: return line.split("=")[-1].strip()
    return "Unknown"
