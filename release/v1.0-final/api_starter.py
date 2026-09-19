import subprocess
import os
import time
import psutil
import sys

# 🚀 O.M.E.G.A. API_STARTER [STABILIZATION_EDITION]
# DEBUG_MODE = True: Backend/Sentinel terminals visible
# DEBUG_MODE = False: All silent
DEBUG_MODE = False  # False = silent background (no CMD windows). True = visible terminals for debugging.

BASE_DIR = r"c:\jarvis AI\jarvis"
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

# FIX: Ensure backend is always importable regardless of Task Scheduler cwd
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

def purge_zombie_sentinels():
    """Kill any orphaned jarvis_sentinel.py (v1) processes to prevent memory exhaustion."""
    current_pid = os.getpid()
    killed = []
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            cmdline = " ".join(proc.info.get('cmdline') or [])
            # Kill v1 sentinel (old name) — NOT v2
            if 'jarvis_sentinel.py' in cmdline and 'jarvis_sentinel_v2' not in cmdline:
                proc.kill()
                killed.append(proc.info['pid'])
                log_event(f"ZOMBIE_PURGED: PID={proc.info['pid']} CMD={cmdline[:60]}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if killed:
        log_event(f"PURGED {len(killed)} zombie sentinel(s)")

def is_process_running(script_name):
    """Check if a python process with the given script name is already active."""
    current_pid = os.getpid()
    for proc in psutil.process_iter(['cmdline', 'pid']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            cmdline = proc.info.get('cmdline')
            if cmdline:
                for arg in cmdline:
                    if script_name in arg:
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def log_event(message):
    log_file = os.path.join(r"C:\Users\Asus", "ignition.log")
    try:
        with open(log_file, "a") as f:
            f.write(f"[{time.ctime()}] {message}\n")
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'api_starter', f'Unhandled exception: {e}')
        pass

def ignite():
    # Use pythonw.exe for zero-window background execution
    # Fall back to python.exe if pythonw not found
    pythonw = r"C:\Users\Asus\AppData\Local\Programs\Python\Python311\pythonw.exe"
    python  = r"C:\Users\Asus\AppData\Local\Programs\Python\Python311\python.exe"
    CREATE_NO_WINDOW = 0x08000000

    api_path      = r"c:\jarvis AI\jarvis\backend\api.py"
    sentinel_path = r"c:\jarvis AI\jarvis\jarvis_sentinel_v2.py"
    log_dir       = BASE_DIR

    # Purge v1 zombie sentinels before launch
    purge_zombie_sentinels()

    try:
        # 1. Backend — always hidden, logs redirected to files
        if not is_process_running("api.py"):
            log_event(f"IGNITING_BACKEND (SILENT)")
            if DEBUG_MODE:
                # Debug: visible window using python.exe
                subprocess.Popen([python, api_path], cwd=BACKEND_DIR)
            else:
                # Production: fully hidden, output to log files
                api_stdout = open(os.path.join(log_dir, "backend", "api_stdout.log"), "a")
                api_stderr = open(os.path.join(log_dir, "backend", "api_stderr.log"), "a")
                subprocess.Popen(
                    [pythonw, api_path],
                    cwd=BACKEND_DIR,
                    stdout=api_stdout,
                    stderr=api_stderr,
                    creationflags=CREATE_NO_WINDOW
                )

        # 2. Sentinel — always hidden, logs redirected to files
        if not is_process_running("jarvis_sentinel_v2.py"):
            log_event(f"IGNITING_SENTINEL_V2 (SILENT)")
            if DEBUG_MODE:
                subprocess.Popen([python, sentinel_path], cwd=BASE_DIR)
            else:
                sen_stdout = open(os.path.join(log_dir, "sentinel_stdout.log"), "a")
                sen_stderr = open(os.path.join(log_dir, "sentinel_stderr.log"), "a")
                subprocess.Popen(
                    [python, sentinel_path],
                    cwd=BASE_DIR,
                    stdout=sen_stdout,
                    stderr=sen_stderr,
                    creationflags=CREATE_NO_WINDOW
                )

    except Exception as e:
        log_event(f"IGNITION_CRITICAL_FAIL: {str(e)}")

if __name__ == "__main__":
    ignite()
