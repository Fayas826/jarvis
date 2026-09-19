import http.server
import socketserver
import json
import urllib.parse
import os
import psutil
import time
import glob
import ctypes
import socket
import subprocess
import logging

from .adb_core import adb, adb_shell
from .mobile_actions import (
    mobile_battery, mobile_wifi_info, mobile_installed_apps,
    mobile_unlock, mobile_screenshot, mobile_camera, mobile_settings,
    mobile_tap, mobile_swipe, mobile_type, mobile_call, mobile_keyevent,
    mobile_stay_awake
)
from .web_helpers import training_progress, get_yt_id
from .nlp_engine import process_command

SERVER_PORT = 8092
DIRECTORY = r"c:\jarvis AI\jarvis"
INTRUDER_LOG = r"c:\jarvis AI\jarvis\vault_traps\intruder_logs"
TAILSCALE_URL = "https://asus-a15.tail0eb81f.ts.net"

class JarvisHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, fmt, *args):
        pass

    def send_json(self, data, status=200):
        try:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception: pass

    def send_bytes(self, data, mime="image/png"):
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, x-api-key")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if path in ("/manifest.json", "/core/perception/manifest.json"):
            mf = r"c:\jarvis AI\jarvis\core\perception\manifest.json"
            if os.path.exists(mf):
                with open(mf, "rb") as f: d = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/manifest+json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(d)))
                self.end_headers()
                self.wfile.write(d)
            return

        if path in ("/api/telemetry", "/api/v1/metrics"):
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            batt = mobile_battery()
            out, _ = adb("devices")
            connected = "uozd6pcuijqozhh6" in (out or "")
            self.send_json({
                "cpu_load": f"{cpu}%", "cpu_percent": cpu,
                "ram_load": f"{ram}%", "heap_memory": f"{ram}%",
                "gpu_temp": 55, "queue_depth": 1, "agents_active": "6/6",
                "smart_status": "PASSED (100%)", "training_status": training_progress(),
                "mobile": {"connected": connected, "device": "REDMI 22101316UP", "battery": batt},
                "tailscale": TAILSCALE_URL, "timestamp": time.time(),
            })
            return

        if path == "/api/v1/tasks":
            self.send_json({"tasks": [
                {"id": "task-2171", "type": "generate", "description": "GPU LoRA Training: " + training_progress(), "status": "running"},
                {"id": "task-mobile-adb", "type": "hardware", "description": "USB ADB Mobile CONNECTED", "status": "running"},
            ]})
            return

        if path == "/api/v1/agents":
            self.send_json({"agents": [
                {"name": "Prime Directress", "status": "Orchestrating swarm", "badge": "active"},
                {"name": "Mobile ADB Controller", "status": "USB REDMI connected", "badge": "active"},
            ]})
            return

        if path == "/api/v1/mobile/screencap":
            img = mobile_screenshot()
            if img: self.send_bytes(img, "image/png")
            else: self.send_json({"error": "Screencap failed"}, 503)
            return

        if path == "/api/v1/mobile/devices":
            out, _ = adb("devices", "-l")
            devices = [line.strip() for line in (out or "").splitlines()[1:] if "device" in line and "List" not in line]
            self.send_json({"devices": devices, "count": len(devices)})
            return

        if path == "/api/v1/mobile/battery":
            self.send_json(mobile_battery())
            return
        if path == "/api/v1/mobile/wifi":
            self.send_json(mobile_wifi_info())
            return
        if path == "/api/v1/mobile/apps":
            self.send_json({"apps": mobile_installed_apps()})
            return
        if path == "/api/v1/mobile/unlock":
            pwd = qs.get("password", [None])[0]
            mobile_unlock(pwd)
            self.send_json({"status": "UNLOCK_DISPATCHED", "pin_used": pwd is not None})
            return

        if path == "/api/android/launch":
            app_id = qs.get("app", [None])[0]
            if app_id == "camera": mobile_camera()
            elif app_id == "settings": mobile_settings()
            elif app_id: adb_shell("monkey", "-p", f"com.{app_id}", "-c", "android.intent.category.LAUNCHER", "1")
            self.send_json({"status": "LAUNCHED", "app": app_id})
            return

        if path == "/api/v1/tts":
            text = qs.get("text", ["Hello sir"])[0]
            try:
                import edge_tts, asyncio, tempfile
                async def gen():
                    comm = edge_tts.Communicate(text, "en-US-AndrewNeural", rate="+0%", pitch="+0Hz")
                    fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    fp.close()
                    await comm.save(fp.name)
                    with open(fp.name, "rb") as f: content = f.read()
                    os.remove(fp.name)
                    return content
                audio = asyncio.run(gen())
                self.send_bytes(audio, "audio/mpeg")
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        if path == "/api/v1/yt_resolve":
            query = qs.get("query", ["AI"])[0]
            vid = get_yt_id(query)
            self.send_json({"query": query, "video_id": vid, "watch_url": ("https://www.youtube.com/watch?v=" + vid) if vid else None})
            return

        if path == "/api/intruders":
            photos = sorted(glob.glob(os.path.join(INTRUDER_LOG, "*.jpg")), key=os.path.getmtime, reverse=True)
            self.send_json({"intruder_photos": [os.path.basename(p) for p in photos[:10]]})
            return
        if path.startswith("/api/intruder_photo"):
            fname = qs.get("file", [None])[0]
            if fname:
                fp = os.path.join(INTRUDER_LOG, os.path.basename(fname))
                if os.path.exists(fp):
                    with open(fp, "rb") as f: self.send_bytes(f.read(), "image/jpeg")
                    return
            self.send_json({"error": "Photo not found"}, 404)
            return
        if path == "/api/processes":
            procs = []
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                try:
                    mem = p.info.get("memory_info")
                    procs.append({"pid": p.info["pid"], "name": p.info["name"] or "?", "cpu": round(p.info.get("cpu_percent") or 0, 1), "memory_mb": round((mem.rss / 1024 / 1024) if mem else 0, 1)})
                except Exception: continue
            procs.sort(key=lambda x: x["cpu"], reverse=True)
            self.send_json(procs[:60])
            return
        if path == "/api/windows":
            wins = []
            try:
                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
                def cb(hwnd, _):
                    if ctypes.windll.user32.IsWindowVisible(hwnd):
                        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                        if length > 0:
                            buf = ctypes.create_unicode_buffer(length + 1)
                            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                            t = buf.value.strip()
                            if t: wins.append({"handle": hwnd, "title": t})
                    return True
                ctypes.windll.user32.EnumWindows(WNDENUMPROC(cb), 0)
            except Exception: pass
            self.send_json(wins[:30])
            return

        if path in ("/api/v1/status", "/api/status"):
            out, _ = adb("devices")
            connected = "uozd6pcuijqozhh6" in (out or "")
            batt = mobile_battery() if connected else {}
            self.send_json({"jarvis": "OPERATIONAL", "tailscale": TAILSCALE_URL, "server_port": SERVER_PORT, "adb_connected": connected, "battery": batt, "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "training": training_progress()})
            return

        super().do_GET()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try: payload = json.loads(body)
        except Exception: payload = {}

        if path in ("/api/command", "/api/v1/tasks"):
            cmd = payload.get("command") or payload.get("input", {}).get("prompt", "") or ""
            result = process_command(cmd)
            self.send_json({"status": "success", "response": result["reply"], "action": result["action"], "data": result["data"], "task": {"status": "completed"}, "timestamp": time.time()})
            return

        if path == "/api/android/launch":
            app_id = payload.get("app", "")
            if app_id == "camera": mobile_camera()
            elif app_id == "settings": mobile_settings()
            elif app_id: adb_shell("monkey", "-p", f"com.{app_id}", "-c", "android.intent.category.LAUNCHER", "1")
            self.send_json({"status": "LAUNCHED", "app": app_id})
            return
        if path == "/api/v1/mobile/tap":
            mobile_tap(payload.get("x", 540), payload.get("y", 960))
            self.send_json({"status": "TAPPED"})
            return
        if path == "/api/v1/mobile/swipe":
            mobile_swipe(payload.get("x1", 540), payload.get("y1", 1400), payload.get("x2", 540), payload.get("y2", 600), payload.get("ms", 300))
            self.send_json({"status": "SWIPED"})
            return
        if path == "/api/v1/mobile/type":
            mobile_type(payload.get("text", ""))
            self.send_json({"status": "TYPED"})
            return
        if path == "/api/v1/mobile/call":
            number = payload.get("number", "")
            mobile_call(number)
            self.send_json({"status": "CALLING", "number": number})
            return
        if path == "/api/v1/mobile/keyevent":
            mobile_keyevent(str(payload.get("key", "3")))
            self.send_json({"status": "KEYEVENT"})
            return
        if path == "/api/v1/mobile/adb_shell":
            cmd_args = payload.get("cmd", "").split()
            out, err = adb_shell(*cmd_args)
            self.send_json({"stdout": out, "stderr": err})
            return
        if path in ("/api/system/lock", "/api/v1/lock"):
            ctypes.windll.user32.LockWorkStation()
            self.send_json({"status": "LOCKED"})
            return
        if path == "/api/v1/wol":
            try:
                mac = bytes.fromhex("94BB43B58954")
                magic = b"\xff" * 6 + mac * 16
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    s.sendto(magic, ("<broadcast>", 9))
            except Exception: pass
            self.send_json({"status": "WOL_DISPATCHED"})
            return
        if path == "/api/processes/kill":
            pid = payload.get("pid")
            if pid:
                try:
                    psutil.Process(int(pid)).terminate()
                    self.send_json({"status": "TERMINATED", "pid": pid})
                except Exception as e: self.send_json({"error": str(e)}, 500)
            else: self.send_json({"error": "pid required"}, 400)
            return
        if path == "/api/apps/launch":
            app = payload.get("app", "")
            cmd = ["explorer.exe"]
            subprocess.Popen(cmd, shell=True)
            self.send_json({"status": "LAUNCHED", "app": app})
            return
        if path == "/api/windows/focus":
            handle = payload.get("handle")
            if handle:
                ctypes.windll.user32.ShowWindow(handle, 9)
                ctypes.windll.user32.SetForegroundWindow(handle)
                self.send_json({"status": "FOCUSED"})
            else: self.send_json({"error": "handle required"}, 400)
            return

        self.send_json({"error": "Unknown endpoint"}, 404)

def start_server():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", SERVER_PORT), JarvisHandler) as httpd:
        logging.info(f"JARVIS MOBILE SERVER live on port {SERVER_PORT}")
        httpd.serve_forever()
