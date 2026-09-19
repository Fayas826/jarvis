import os
import sys
import time
import subprocess
import threading
import ctypes
from ctypes import wintypes
import socket
import numpy as np
import requests
import json
import psutil
import queue
import random
from collections import deque
from datetime import datetime
from colorama import init, Fore, Back, Style
from infrastructure.watchdog.system_guardian import system_guardian

# Initialize Colorama
init(autoreset=True)

# ----------------------- ADVANCED IMPORTS -----------------------
try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import openwakeword
    from openwakeword.model import Model
    OWW_AVAILABLE = True
except ImportError:
    OWW_AVAILABLE = False
    Model = None

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

# ----------------------- ENFORCER -----------------------
_original_popen = subprocess.Popen
class HiddenPopen(_original_popen):
    def __init__(self, *args, **kwargs):
        creationflags = kwargs.get('creationflags', 0)
        # 0x08000000 = CREATE_NO_WINDOW
        kwargs['creationflags'] = creationflags | 0x08000000
        super().__init__(*args, **kwargs)

subprocess.Popen = HiddenPopen

# ----------------------- CONFIG -----------------------
BASE_DIR = r"c:\jarvis AI\jarvis"
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
API_URL = "http://127.0.0.1:5001"
DIAG_LOG = os.path.join(BASE_DIR, "wake_diagnostics.log")

# Trigger State
WAKE_TEST_MODE = True
IS_LISTENING = False
ACTIVE_STATE = False      # State Machine Core
PASSIVE_STANDBY = True    # Standby Flag
SERVICES_READY = False
BOOTING = False
CALIBRATION_PASSED = True 

# Audio Parameters
BEST_MIC_INDEX = None
BEST_MIC_RATE = 16000
BEST_MIC_CHANNELS = 1
BEST_MIC_DTYPE = 'float32'
BEST_MIC_GAIN = 1.0
SILENCE_BASELINE = 0.0
VOICE_THRESHOLD = 0.35 
CLAP_THRESHOLD = 0.5

# Queues & Events
AUDIO_QUEUE = queue.Queue(maxsize=100)
VOICE_TRIGGER_EVENT = threading.Event()
LAST_SENTINEL_HEARTBEAT = time.time()
_WAKE_GATE = threading.Lock()

# CLAP_TRUTH State
CLAP_ENERGY_HISTORY = deque([0.001] * 20, maxlen=20)
CLAP_BACKOFF = 0
LAST_BLOCK_PEAK = 0.0
LAST_BLOCK_CREST = 0.0
CLAP_CONSEC_HIGH = 0

# TTS Initialization
LOCAL_TTS_ACTIVE = False
LOCAL_ENGINE = None
if pyttsx3:
    try:
        LOCAL_ENGINE = pyttsx3.init()
        voices = LOCAL_ENGINE.getProperty('voices')
        for voice in voices:
            v_name = voice.name.lower()
            if "male" in v_name or "david" in v_name or "george" in v_name:
                LOCAL_ENGINE.setProperty('voice', voice.id)
                break
        LOCAL_ENGINE.setProperty('rate', 180)
        LOCAL_TTS_ACTIVE = True
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'jarvis_sentinel_v2', f'Unhandled exception: {e}')
        LOCAL_TTS_ACTIVE = False

# ----------------------- LOGGING -----------------------
def log_wake_diagnostic(trigger_type, success, wakeword=None, latency_ms=0, confidence=0.0, rms=0.0):
    if not WAKE_TEST_MODE:
        return
    try:
        diag = {
            "timestamp": datetime.now().isoformat(),
            "trigger": trigger_type,
            "success": success,
            "wakeword": wakeword,
            "latency_ms": int(latency_ms),
            "confidence": round(float(confidence), 2),
            "rms": round(float(rms), 1)
        }
        with open(DIAG_LOG, "a") as f:
            f.write(json.dumps(diag) + "\n")
        print(Fore.BLACK + Back.CYAN + f"[DIAGNOSTIC] {trigger_type} event logged (Success={success})")
    except Exception as e:
        print(f"[DIAG_FAIL] {e}")

# ----------------------- SINGLETON -----------------------
def verify_singleton():
    lock_file = os.path.join(os.getcwd(), "sentinel.lock")
    try:
        if os.path.exists(lock_file):
            with open(lock_file, "r") as f:
                try:
                    content = f.read().strip()
                    if content:
                        old_pid = int(content)
                        if psutil.pid_exists(old_pid):
                            print(Fore.RED + f"[CRITICAL] Sentinel already running with PID {old_pid}")
                            sys.exit(1)
                except (ValueError, Exception):
                    pass
            try:
                os.remove(lock_file)
            except Exception as e:
                from core.reliability.system_logger import system_logger
                system_logger.log('ERROR', 'jarvis_sentinel_v2', f'Unhandled exception: {e}')
                pass
        
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))
        return lock_file
    except Exception as e:
        print(Fore.YELLOW + f"[WARN] Lock check failed: {e}. Proceeding cautiously.")
        return None

def cleanup_lock(lock_file):
    if lock_file and os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            print(Fore.CYAN + "[CLEANUP] Neural lock released.")
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'jarvis_sentinel_v2', f'Unhandled exception: {e}')
            pass

# ----------------------- HARDWARE -----------------------
def select_best_microphone():
    global BEST_MIC_INDEX, BEST_MIC_RATE, BEST_MIC_CHANNELS
    if not sd:
        print(Fore.RED + "[HARDWARE_ERR] sounddevice module missing.")
        return False
    try:
        devices = sd.query_devices()
        print(Fore.CYAN + "\n" + "="*60)
        print(Fore.CYAN + "PHASE 1: MICROPHONE TRUTH AUDIT")
        print("="*60)
        print(f"{'Idx':<4} {'Name':<35} {'Ch':<4} {'SR':<8} {'Latency'}")
        print("-" * 65)
        
        candidates = []
        rejected_names = []
        reject_kws = ["mapper", "stereo mix", "loopback", "virtual", "speaker", "output"]
        prefer_kws = ["realtek microphone array", "realtek microphone", "built-in physical microphone", "microphone array"]

        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                name = d['name']
                sr = int(d['default_samplerate'])
                ch = d['max_input_channels']
                lat = f"{d['default_low_input_latency']:.3f}/{d['default_high_input_latency']:.3f}"
                
                print(f"{i:<4} {name[:33]:<35} {ch:<4} {sr:<8} {lat}")
                
                if any(kw in name.lower() for kw in reject_kws):
                    rejected_names.append(name)
                    continue
                candidates.append((i, d))

        if rejected_names:
            print(Fore.YELLOW + f"\nPHASE 2: PERMANENT DEVICE REJECTION")
            for r in rejected_names[:5]:
                print(f" - [REJECTED] {r}")

        best_idx = None
        best_name = ""
        for kw in prefer_kws:
            for idx, d in candidates:
                if kw in d['name'].lower():
                    best_idx = idx
                    best_name = d['name']
                    break
            if best_idx is not None:
                break
            
        if best_idx is None and candidates:
            best_idx = candidates[0][0]
            best_name = candidates[0][1]['name']
            
        if best_idx is not None:
            BEST_MIC_INDEX = best_idx
            BEST_MIC_RATE = 16000
            BEST_MIC_CHANNELS = 1
            dev = devices[best_idx]
            print(Fore.GREEN + f"\n[MIC_LOCK] {best_name}")
            print(
                Fore.CYAN
                + f"[AUDIO_PIPELINE] device_index={best_idx} channels={BEST_MIC_CHANNELS} "
                f"sample_rate={BEST_MIC_RATE} dtype={BEST_MIC_DTYPE} "
                f"latency_low={dev['default_low_input_latency']:.4f}s "
                f"latency_high={dev['default_high_input_latency']:.4f}s"
            )
            return True
        return False
    except Exception as e:
        print(Fore.RED + f"[HARDWARE_ERR] {e}")
        return False

def calibrate_threshold():
    global SILENCE_BASELINE, CLAP_THRESHOLD
    if not sd:
        return False
    print(Fore.CYAN + "[CALIBRATION] Profiling room acoustics (3s)...")
    try:
        samples_rms = []
        def callback(indata, frames, t, status):
            samples_rms.append(np.linalg.norm(indata) / np.sqrt(len(indata)))
        with sd.InputStream(
            callback=callback,
            samplerate=BEST_MIC_RATE,
            channels=1,
            device=BEST_MIC_INDEX,
            dtype=np.float32,
        ):
            time.sleep(3)
        if samples_rms:
            SILENCE_BASELINE = float(np.mean(samples_rms)) * 1000
            CLAP_THRESHOLD = SILENCE_BASELINE * 2.5
            print(Fore.GREEN + f"[CALIBRATION] Baseline: {SILENCE_BASELINE:.1f} | Threshold: {CLAP_THRESHOLD:.1f}")
            return True
        return False
    except Exception as e:
        print(Fore.RED + f"[CALIBRATION_ERR] {e}")
        return False

# ----------------------- SERVICES -----------------------
def start_services():
    global SERVICES_READY, BOOTING
    if BOOTING:
        return
    BOOTING = True
    print(Fore.YELLOW + "[SENTINEL] Igniting Backend Services...")
    try:
        python_exe = r"C:\Users\Asus\AppData\Local\Programs\Python\Python311\pythonw.exe"
        if not os.path.exists(python_exe):
            python_exe = "pythonw"
        
        is_running = False
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmd = " ".join(proc.info.get('cmdline') or [])
                if "api.py" in cmd:
                    is_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not is_running:
            subprocess.Popen([python_exe, "api.py"], cwd=BACKEND_DIR)
        
        for _ in range(30):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', 5001)) == 0:
                    SERVICES_READY = True
                    print(Fore.GREEN + "[SENTINEL] Neural Core MOORED.")
                    return
            time.sleep(1)
    finally:
        BOOTING = False

def speak_via_api(text):
    if not SERVICES_READY:
        return
    try:
        requests.post(f"{API_URL}/jarvis", json={"message": f"SAY {text}"}, timeout=5)
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'jarvis_sentinel_v2', f'Unhandled exception: {e}')
        pass

# ----------------------- CORE TRIGGER LOGIC -----------------------
def _oww_best_score(probs):
    if not isinstance(probs, dict) or not probs:
        return 0.0, ""
    for name in ("hey_jarvis_v0.1", "hey_jarvis"):
        if name in probs:
            return float(probs[name]), name
    for k, v in probs.items():
        if "jarvis" in k.lower():
            return float(v), k
    k0 = next(iter(probs))
    return float(probs[k0]), k0


def _safe_format_float(val, prec=4):
    if isinstance(val, (int, float, np.floating)):
        return f"{float(val):.{prec}f}"
    if isinstance(val, str):
        try:
            return f"{float(val):.{prec}f}"
        except ValueError:
            return val
    try:
        return f"{float(val):.{prec}f}"
    except (TypeError, ValueError):
        return str(val)


def is_clap_fingerprint(samples, rms, peak, crest, zcr):
    """Clap Truth Validation: transient spike, peak vs baseline, short duration."""
    global CLAP_ENERGY_HISTORY, CLAP_BACKOFF, LAST_BLOCK_PEAK, LAST_BLOCK_CREST, CLAP_CONSEC_HIGH

    baseline = np.mean(list(CLAP_ENERGY_HISTORY)) if CLAP_ENERGY_HISTORY else max(SILENCE_BASELINE / 1000.0, 1e-6)
    raw_rms = rms / 1000.0
    CLAP_ENERGY_HISTORY.append(raw_rms)

    if CLAP_BACKOFF > 0:
        CLAP_BACKOFF -= 1
        LAST_BLOCK_PEAK = peak
        LAST_BLOCK_CREST = crest
        return False

    frame_sec = len(samples) / float(BEST_MIC_RATE) if BEST_MIC_RATE else 0.08
    impulse_like = peak > (baseline * 2.0) and crest >= 6.0
    if impulse_like:
        CLAP_CONSEC_HIGH += 1
    else:
        CLAP_CONSEC_HIGH = 0
    if CLAP_CONSEC_HIGH > 3:
        print(Fore.RED + f"[CLAP_REJECTED] sustained impulse >{int(3 * frame_sec * 1000)}ms (not a clap transient)")
        CLAP_CONSEC_HIGH = 0
        LAST_BLOCK_PEAK = peak
        LAST_BLOCK_CREST = crest
        return False

    quiet_prev = LAST_BLOCK_CREST < 6.0 and LAST_BLOCK_PEAK < (baseline * 2.0)
    sharp_onset = quiet_prev or LAST_BLOCK_PEAK < (baseline * 1.5)

    is_sharp_rise = raw_rms > (baseline * 3.5)
    is_peak_spike = peak > max(baseline * 2.0, 0.012)
    is_impulsive = crest > 8.5
    is_clap_spectrum = 0.12 < zcr < 0.38

    if crest < 6.0:
        LAST_BLOCK_PEAK = peak
        LAST_BLOCK_CREST = crest
        return False
    if zcr > 0.45:
        LAST_BLOCK_PEAK = peak
        LAST_BLOCK_CREST = crest
        return False
    if zcr < 0.08:
        LAST_BLOCK_PEAK = peak
        LAST_BLOCK_CREST = crest
        return False

    if not (sharp_onset and is_sharp_rise and is_peak_spike and is_impulsive and is_clap_spectrum):
        LAST_BLOCK_PEAK = peak
        LAST_BLOCK_CREST = crest
        return False

    CLAP_BACKOFF = 10
    CLAP_CONSEC_HIGH = 0
    LAST_BLOCK_PEAK = peak
    LAST_BLOCK_CREST = crest
    return True

def audio_callback(indata, frames, t, status):
    global IS_LISTENING, BEST_MIC_GAIN
    amplified_data = indata * BEST_MIC_GAIN
    samples = np.clip(amplified_data.flatten(), -1.0, 1.0)
    
    # PHASE 1: Live Signal Audit
    raw_rms = float(np.sqrt(np.mean(samples**2)))
    rms = raw_rms * 1000
    peak = float(np.max(np.abs(samples)))
    crest = peak / raw_rms if raw_rms > 0.0001 else 0
    zcr = float(np.mean(np.abs(np.diff(np.sign(samples))) > 0))
    
    if WAKE_TEST_MODE and not IS_LISTENING:
        print(f"{Fore.BLACK}{Style.BRIGHT}[RMS_TRACE] RMS: {rms:7.3f} | Peak: {peak:.4f} | Crest: {crest:5.2f} | ZCR: {zcr:.4f}")
    
    if not IS_LISTENING:
        try:
            oww_chunk = (samples * 32767).astype(np.int16)
            AUDIO_QUEUE.put_nowait(oww_chunk)
        except queue.Full:
            pass
            
    if IS_LISTENING:
        return
        
    if is_clap_fingerprint(samples, rms, peak, crest, zcr):
        print(Fore.MAGENTA + Style.BRIGHT + "\n[EVENT_FIRE] Clap Truth Validated")
        VOICE_TRIGGER_EVENT.set()
        log_wake_diagnostic("CLAP", True, confidence=1.0, rms=rms)
        threading.Thread(target=process_voice_command, args=("CLAP",), daemon=True).start()
    elif crest >= 6.0 and (peak > max((SILENCE_BASELINE / 1000.0) * 2.0, 0.01) or raw_rms > (SILENCE_BASELINE / 1000.0) * 2.5):
        print(Fore.RED + "[CLAP_REJECTED] impulse-like signal failed clap profile (noise shield / onset / duration)")

def process_voice_command(trigger_source):
    global IS_LISTENING, ACTIVE_STATE, PASSIVE_STANDBY
    with _WAKE_GATE:
        if IS_LISTENING:
            return
        IS_LISTENING = True
        ACTIVE_STATE = True
        PASSIVE_STANDBY = False

    print(Fore.YELLOW + f"\n[STATE_AUDIT] Current State: ACTIVE")
    print(Fore.YELLOW + f"[STATE_AUDIT] Trigger Source: {trigger_source}")
    print(Fore.YELLOW + f"[STATE_AUDIT] Last Activation: {datetime.now().strftime('%H:%M:%S')}")
    print(Fore.CYAN + Back.BLACK + f"--- [TRANSITION] JARVIS ACTIVE ({trigger_source}) ---")

    start_time = time.time()
    deadline = start_time + 10.0
    try:
        if LOCAL_TTS_ACTIVE and LOCAL_ENGINE:
            LOCAL_ENGINE.say("Yes, Sir?")
            LOCAL_ENGINE.runAndWait()

        while time.time() < deadline:
            time.sleep(0.1)

    except Exception as e:
        print(Fore.RED + f"[PROCESS_ERR] {e}")
    finally:
        VOICE_TRIGGER_EVENT.clear()
        IS_LISTENING = False
        ACTIVE_STATE = False
        PASSIVE_STANDBY = True
        print(Fore.YELLOW + "[STATE_RESET] Returning to standby (Timeout Recovery)\n")

def whisper_fallback_validation(audio_chunk):
    if not WhisperModel:
        return
    try:
        fallback_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        audio_float = audio_chunk.astype(np.float32) / 32767.0
        segments, _ = fallback_model.transcribe(audio_float, beam_size=1)
        for segment in segments:
            if "jarvis" in segment.text.lower():
                print(Fore.YELLOW + f"[WHISPER] Detected: '{segment.text}'")
                VOICE_TRIGGER_EVENT.set()
                log_wake_diagnostic("VOICE", True, confidence=0.99)
                threading.Thread(target=process_voice_command, args=("WHISPER_FALLBACK",), daemon=True).start()
                return
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'jarvis_sentinel_v2', f'Unhandled exception: {e}')
        pass

# ----------------------- THREADS -----------------------
def voice_monitor():
    print(Fore.CYAN + "[THREAD_START] Voice")
    if not OWW_AVAILABLE or not Model:
        print(Fore.RED + "[VOICE_FAILURE] openwakeword not available.")
        return

    try:
        package_models = os.path.join(os.path.dirname(openwakeword.__file__), "resources", "models")
        wake_model_path = os.path.join(package_models, "hey_jarvis_v0.1.onnx")
        
        if not os.path.exists(wake_model_path):
            print(Fore.RED + f"[CRITICAL] Wake model missing: {wake_model_path}")
            return

        oww_model = Model(wakeword_models=[wake_model_path], inference_framework='onnx')
        probe = np.zeros(1280, dtype=np.int16)
        probe_probs = oww_model.predict(probe)
        probe_score, probe_label = _oww_best_score(probe_probs)
        print(Fore.GREEN + f"[VOICE] Neural Engine Ignited. Model: FP32 High Fidelity")
        print(
            Fore.CYAN
            + f"[OWW_AUDIT] path={wake_model_path} onnx_active=yes label={probe_label!r} "
            f"idle_score={_safe_format_float(probe_score, 4)}"
        )
    except Exception as e:
        print(Fore.RED + f"[VOICE_FAILURE] Neural path obstructed: {e}")
        return

    while True:
        try:
            chunk = AUDIO_QUEUE.get(timeout=1.0)
            if IS_LISTENING:
                continue
            t_infer = time.perf_counter()
            probs = oww_model.predict(chunk)
            infer_ms = (time.perf_counter() - t_infer) * 1000.0
            score, label = _oww_best_score(probs)

            if WAKE_TEST_MODE:
                lbl = label if isinstance(label, str) else str(label)
                print(
                    f"{Fore.BLACK}{Style.BRIGHT}[VOICE_TRACE] label={lbl or 'none'} "
                    f"confidence={_safe_format_float(score, 4)} latency_ms={_safe_format_float(infer_ms, 2)}"
                )

            if score > VOICE_THRESHOLD:
                print(Fore.GREEN + f"[EVENT_FIRE] Voice ({_safe_format_float(score, 2)})")
                VOICE_TRIGGER_EVENT.set()
                log_wake_diagnostic("VOICE", True, confidence=float(score), latency_ms=infer_ms)
                threading.Thread(target=process_voice_command, args=("VOICE",), daemon=True).start()
            elif score > 0.15:
                threading.Thread(target=whisper_fallback_validation, args=(chunk,), daemon=True).start()
        except queue.Empty:
            continue
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'jarvis_sentinel_v2', f'Unhandled exception: {e}')
            continue

def hotkey_monitor():
    print(Fore.CYAN + "[THREAD_START] Hotkey")
    user32 = ctypes.windll.user32
    # Register CTRL + SPACE (0x0002 | 0x20)
    if user32.RegisterHotKey(None, 1, 0x0002, 0x20):
        try:
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312: # WM_HOTKEY
                    print(Fore.MAGENTA + "[EVENT_FIRE] Hotkey")
                    log_wake_diagnostic("HOTKEY", True, confidence=1.0)
                    threading.Thread(target=process_voice_command, args=("HOTKEY",), daemon=True).start()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)

def health_check_loop():
    global LAST_SENTINEL_HEARTBEAT
    print(Fore.CYAN + "[THREAD_START] Watchdog")
    while True:
        if time.time() - LAST_SENTINEL_HEARTBEAT > 10:
            print(Fore.BLACK + Back.WHITE + "[HEARTBEAT] Sentinel Alive")
            LAST_SENTINEL_HEARTBEAT = time.time()
        time.sleep(5)

# ----------------------- ENTRY -----------------------
def main_boot_sequence():
    print(Fore.CYAN + "[BOOT] JARVIS Sentinel O.M.E.G.A. Initializing...")
    lock_file = verify_singleton()
    try:
        start_services()
        if select_best_microphone():
            calibrate_threshold()
            threading.Thread(target=health_check_loop, daemon=True).start()
            threading.Thread(target=voice_monitor, daemon=True).start()
            threading.Thread(target=hotkey_monitor, daemon=True).start()
            
            # 🛡️ O.M.E.G.A. TIER_11: Start Sentinel Intelligence Watchdog
            print(Fore.CYAN + "[THREAD_START] Intelligence Watchdog (Self-Heal)")
            system_guardian.start()
            
            if not sd:
                return
            try:
                with sd.InputStream(
                    callback=audio_callback,
                    channels=BEST_MIC_CHANNELS,
                    samplerate=BEST_MIC_RATE,
                    device=BEST_MIC_INDEX,
                    blocksize=1280,
                    dtype=np.float32,
                ):
                    print(Fore.GREEN + "[SENTINEL] O.M.E.G.A. Systems ACTIVE. Listening...")
                    while True:
                        time.sleep(1)
            except Exception as e:
                print(Fore.RED + f"[CRITICAL_STREAM_FAIL] {e}")
        else:
            print(Fore.RED + "[BOOT_FAIL] No acoustic sensors detected.")
    finally:
        cleanup_lock(lock_file)

if __name__ == "__main__":
    try:
        main_boot_sequence()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[SENTINEL] Shutdown requested.")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n[SENTINEL_CRASH] {e}")
        sys.exit(1)
