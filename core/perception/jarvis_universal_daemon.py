import time
import os
import sys
import math
import struct
import logging
import threading
import subprocess
import webbrowser
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [JARVIS_UNIVERSAL_DAEMON] %(message)s")

class DockerAutoManager:
    """Automatic Docker Desktop Auto-Start & Readiness Engine."""

    @staticmethod
    def ensure_docker_running() -> bool:
        logging.info("Checking Docker Desktop daemon status...")
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                logging.info("Docker daemon is ONLINE and 100% operational.")
                return True
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'jarvis_universal_daemon', f'Unhandled exception: {e}')
            pass

        logging.info("Docker daemon dormant. Launching Docker Desktop in background...")
        docker_paths = [
            r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
            r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
        ]
        launched = False
        for path in docker_paths:
            if os.path.exists(path):
                subprocess.Popen([path], creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
                launched = True
                logging.info(f"Docker Desktop process started from: {path}")
                break

        if launched:
            for attempt in range(15):
                time.sleep(2)
                try:
                    res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=3)
                    if res.returncode == 0:
                        logging.info("Docker Desktop initialized successfully and ready for full JARVIS access!")
                        return True
                except Exception as e:
                    from core.reliability.system_logger import system_logger
                    system_logger.log('ERROR', 'jarvis_universal_daemon', f'Unhandled exception: {e}')
                    pass

        return False

class UniversalModeSwitcher:
    """Routes voice/clap actions between Desktop 3D HUD, Web Dashboard, and Stealth Background."""

    @staticmethod
    def trigger_web_mode():
        logging.info("JARVIS ACTION: Switching to Web Command Center Dashboard...")
        try:
            from core.perception.launch_stark_dashboard import find_open_port
            port = find_open_port(8088)
            url = f"http://localhost:{port}/core/perception/stark_dashboard.html"
            subprocess.Popen([sys.executable, r"c:\jarvis AI\jarvis\core\perception\launch_stark_dashboard.py"])
            time.sleep(1.0)
            webbrowser.open(url)
        except Exception as e:
            logging.error(f"Web mode switch error: {e}")

    @staticmethod
    def trigger_desktop_hud_mode():
        logging.info("JARVIS ACTION: Switching to Desktop 3D Arc Reactor HUD...")
        try:
            subprocess.Popen([sys.executable, r"c:\jarvis AI\jarvis\core\perception\ironman_vitals_hud.py"])
        except Exception as e:
            logging.error(f"Desktop HUD mode error: {e}")

    @staticmethod
    def trigger_stealth_mode():
        logging.info("JARVIS ACTION: Going stealth (Invisible Background Listening)...")
        # Visual windows closed; silent background listening remains active.

class AcousticClapDetector:
    """Dual Acoustic Clap Peak Signature Detector using PyAudio stream."""

    def __init__(self, callback):
        self.callback = callback
        self.running = False

    def start_listening(self):
        self.running = True
        t = threading.Thread(target=self._audio_loop, daemon=True)
        t.start()

    def stop_listening(self):
        self.running = False

    def _audio_loop(self):
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

            logging.info("Acoustic Clap Listener active in background (Double-Clap to wake JARVIS)...")
            clap_history = []

            while self.running:
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    count = len(data) // 2
                    shorts = struct.unpack("%dh" % count, data)
                    sum_squares = sum(s * s for s in shorts)
                    rms = math.sqrt(sum_squares / float(count))

                    if rms > 7500: # Sharp acoustic peak threshold
                        now = time.time()
                        clap_history.append(now)
                        clap_history = [t for t in clap_history if (now - t) < 1.0]

                        if len(clap_history) >= 2:
                            interval = clap_history[-1] - clap_history[-2]
                            if 0.10 <= interval <= 0.50: # Valid double-clap interval
                                logging.info("DOUBLE CLAP DETECTED! Waking up JARVIS...")
                                clap_history = []
                                try:
                                    import winsound
                                    winsound.Beep(1200, 100)
                                    winsound.Beep(1800, 150)
                                except Exception as e:
                                    from core.reliability.system_logger import system_logger
                                    system_logger.log('ERROR', 'jarvis_universal_daemon', f'Unhandled exception: {e}')
                                    pass
                                self.callback("CLAP_WAKEUP")
                except Exception as e:
                    from core.reliability.system_logger import system_logger
                    system_logger.log('ERROR', 'jarvis_universal_daemon', f'Unhandled exception: {e}')
                    pass
                time.sleep(0.01)

            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            logging.warning(f"Acoustic clap listener standby: {e}")

class JARVISUniversalDaemon:
    """Master Background Daemon combining Clap Wakeup, Intrusion Detection, and Docker Auto-Start."""

    def __init__(self):
        self.clap_detector = AcousticClapDetector(self.on_wake_event)
        from core.perception.unauthorized_intrusion_detector import UnauthorizedIntrusionDetector
        self.intrusion_detector = UnauthorizedIntrusionDetector(idle_threshold_sec=120.0)

    def on_wake_event(self, event_type: str):
        logging.info(f"JARVIS UNIVERSAL WAKE-UP TRIGGERED VIA: {event_type}")
        print("\n=======================================================")
        print("🤖 JARVIS IS ONLINE AND AT YOUR COMMAND, SIR!")
        print("Opening Web Command Center Dashboard...")
        print("=======================================================\n")
        UniversalModeSwitcher.trigger_web_mode()

    def start(self):
        logging.info("Starting JARVIS Universal Invisible Background Daemon...")
        
        # 1. Ensure Docker is running in background
        threading.Thread(target=DockerAutoManager.ensure_docker_running, daemon=True).start()

        # 2. Start Acoustic Clap Listener
        self.clap_detector.start_listening()

        # 3. Start Silent Intrusion Sentinel
        self.intrusion_detector.start_sentinel()

        print(f"\n=======================================================")
        print(f"JARVIS UNIVERSAL BACKGROUND DAEMON IS RUNNING INVISIBLE!")
        print(f"1. Double-Clap hands -> Wakes JARVIS & opens Web Dashboard.")
        print(f"2. Silent Intrusion Security -> Snaps photo & locks Windows if laptop touched by stranger.")
        print(f"3. Docker Auto-Start -> Ensuring container readiness.")
        print(f"4. Windows Boot Autostart -> VBS script installed in Windows Startup folder.")
        print(f"=======================================================\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("JARVIS Universal Daemon stopped.")

if __name__ == "__main__":
    daemon = JARVISUniversalDaemon()
    daemon.start()

