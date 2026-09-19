import os
import psutil
from colorama import Fore

def select_best_microphone(sd):
    if not sd:
        print(Fore.RED + "[HARDWARE_ERR] sounddevice module missing.")
        return None, 16000, 1
    try:
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                name = d['name'].lower()
                if "realtek" in name or "microphone" in name:
                    return i, int(d['default_samplerate']), d['max_input_channels']
        return sd.default.device[0], 16000, 1
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'audio_hardware', f'Unhandled exception: {e}')
        return None, 16000, 1

def verify_singleton():
    lock_file = os.path.join(os.getcwd(), "sentinel.lock")
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                content = f.read().strip()
                if content:
                    old_pid = int(content)
                    if psutil.pid_exists(old_pid):
                        print(Fore.RED + f"[CRITICAL] Sentinel already running with PID {old_pid}")
                        return None
        except Exception: pass
        try:
            os.remove(lock_file)
        except Exception: pass
    
    with open(lock_file, "w") as f:
        f.write(str(os.getpid()))
    return lock_file

def cleanup_lock(lock_file):
    if lock_file and os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            print(Fore.CYAN + "[CLEANUP] Neural lock released.")
        except Exception: pass
