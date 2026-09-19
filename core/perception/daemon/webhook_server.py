import http.server
import socketserver
import json
import logging

log = logging.getLogger("jarvis_daemon")

def start_webhook_server(task_queue, port=8093):
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _json(self, data, code=200):
            b = json.dumps(data).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Content-Length", "0")
            self.end_headers()
        def do_GET(self):
            if self.path == "/status": self._json(task_queue.status())
            else: self._json({"jarvis": "Always-Live Daemon", "port": port})
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(body)
                if self.path == "/task":
                    task_queue.add(payload.get("type", "screenshot_analyse"), payload.get("params", {}))
                    self._json({"status": "queued"})
                elif self.path == "/command":
                    cmd = payload.get("command", "")
                    task_queue.add("adb_shell", {"cmd": ["echo", cmd]})
                    self._json({"status": "received", "command": cmd})
                else: self._json({"error": "unknown endpoint"}, 404)
            except Exception as e: self._json({"error": str(e)}, 500)

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", port), Handler) as srv:
        log.info(f"[WEBHOOK] Webhook server live on port {port}")
        srv.serve_forever()
