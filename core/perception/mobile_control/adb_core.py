import os
import subprocess

ADB_PATH = r"C:\AMD\platform-tools\adb.exe"

def adb(*args, timeout=12):
    if not os.path.exists(ADB_PATH):
        return None, "ADB not found at " + ADB_PATH
    try:
        r = subprocess.run([ADB_PATH] + list(args), capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return None, str(e)

def adb_shell(*args, timeout=12):
    return adb("shell", *args, timeout=timeout)

def adb_raw_bytes(*args, timeout=10):
    try:
        r = subprocess.run([ADB_PATH] + list(args), capture_output=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else None
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'adb_core', f'Unhandled exception: {e}')
        return None
