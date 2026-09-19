import threading
import time
import os
import json
import urllib.request
import logging

from .adb_client import phone_battery_level, is_phone_connected, adb
from .voice_output import speak

log = logging.getLogger("jarvis_daemon")

class ProactiveMonitor:
    def __init__(self, task_queue, alert_url="http://localhost:8092"):
        self.tq = task_queue
        self.alert_url = alert_url
        self.running = True
        self._last_battery = -1
        self._last_adb_state = True
        self._check_interval = 30

    def _send_alert(self, message):
        log.info(f"[ALERT] {message}")
        self.tq.add("speak", {"text": message})

    def _check_battery(self):
        lvl = phone_battery_level()
        if lvl == -1: return
        if lvl <= 15 and self._last_battery > 15: self._send_alert(f"Sir, your phone battery is critically low at {lvl} percent. Please charge it now.")
        elif lvl <= 30 and self._last_battery > 30: self._send_alert(f"Sir, your phone battery is at {lvl} percent. Consider charging soon.")
        self._last_battery = lvl

    def _check_adb(self):
        connected = is_phone_connected()
        if not connected and self._last_adb_state:
            log.warning("[ADB] Phone disconnected! Attempting reconnect...")
            adb("kill-server"); time.sleep(2); adb("start-server")
            self._last_adb_state = False
        elif connected and not self._last_adb_state:
            log.info("[ADB] Phone reconnected!")
            self._send_alert("Sir, your Redmi phone has reconnected via USB ADB.")
            self._last_adb_state = True

    def _check_training(self):
        try:
            log_path = r"C:\Users\Asus\.gemini\antigravity-ide\brain\7b743d62-ee01-421f-9811-857d037f759c\.system_generated\tasks\task-2171.log"
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in reversed(f.readlines()[-10:]):
                        if "100%" in line or "42429/42429" in line:
                            self._send_alert("Sir! GPU LoRA training is complete at 100 percent!")
                            return
        except Exception: pass

    def _check_intruder(self):
        intruder_dir = r"c:\jarvis AI\jarvis\vault_traps\intruder_logs"
        if not os.path.exists(intruder_dir): return
        photos = sorted(os.listdir(intruder_dir), key=lambda x: os.path.getmtime(os.path.join(intruder_dir, x)), reverse=True)
        if photos:
            newest = photos[0]
            mtime = os.path.getmtime(os.path.join(intruder_dir, newest))
            if time.time() - mtime < self._check_interval + 5:
                self._send_alert("Sir! Security alert! An intruder photo was captured on your laptop.")

    def run(self):
        log.info("[MONITOR] Proactive monitor started.")
        while self.running:
            try:
                self._check_battery()
                self._check_adb()
                self._check_training()
                self._check_intruder()
            except Exception as e: log.error(f"[MONITOR] Error: {e}")
            time.sleep(self._check_interval)

    def start(self):
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        return t

class WakeWordListener:
    def __init__(self, task_queue, server_base="http://localhost:8092"):
        self.tq = task_queue
        self.server = server_base
        self.running = True
        self.wake_word = "jarvis"

    def _send_command(self, command):
        try:
            payload = json.dumps({"command": command}).encode("utf-8")
            req = urllib.request.Request(f"{self.server}/api/command", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                reply = result.get("response", "")
                action = result.get("action", "")
                log.info(f"[VOICE] Executed '{command}' -> {action}: {reply}")
                if action == "youtube":
                    query = result.get("data", {}).get("query", command)
                    self.tq.add("youtube_deep", {"query": query})
                speak(reply)
        except Exception as e: log.error(f"[VOICE] Command send failed: {e}")

    def _listen_loop(self):
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            r.energy_threshold = 3000
            r.dynamic_energy_threshold = True
            with sr.Microphone() as mic:
                r.adjust_for_ambient_noise(mic, duration=1)
                log.info("[VOICE] Always-live microphone ACTIVE — Say 'JARVIS' to wake!")
                while self.running:
                    try:
                        audio = r.listen(mic, timeout=5, phrase_time_limit=8)
                        text = r.recognize_google(audio).lower()
                        log.info(f"[VOICE] Heard: '{text}'")
                        if self.wake_word in text:
                            command = text.replace(self.wake_word, "").strip(" ,.")
                            if command:
                                log.info(f"[VOICE] Wake word detected! Command: '{command}'")
                                speak(f"Yes sir, {command}")
                                self._send_command(command)
                            else: speak("Yes sir, I am here. How can I help you?")
                    except Exception: pass
        except ImportError:
            log.warning("[VOICE] SpeechRecognition not installed. Voice mode disabled.")
        except Exception as e: log.error(f"[VOICE] Listener error: {e}")

    def start(self):
        t = threading.Thread(target=self._listen_loop, daemon=True)
        t.start()
        return t
