"""
JARVIS ALWAYS-LIVE AUTONOMOUS DAEMON (MODULARIZED)
======================================================
Entry point for the background daemon. 
Loads modular components from core.perception.daemon.
"""

import time
import sys
import os
import threading
import logging

BASE_DIR = r"c:\jarvis AI\jarvis"
sys.path.insert(0, BASE_DIR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [JARVIS_DAEMON] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "jarvis_daemon.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("jarvis_daemon")

from core.perception.daemon import (
    TaskQueue, ProactiveMonitor, WakeWordListener, start_webhook_server, 
    is_phone_connected, adb_shell
)

def main():
    log.info("=" * 60)
    log.info("  JARVIS ALWAYS-LIVE AUTONOMOUS DAEMON — STARTING")
    log.info("=" * 60)

    if not is_phone_connected():
        log.warning("[ADB] Phone NOT connected! Waiting for USB...")
        for _ in range(30):
            if is_phone_connected(): break
            time.sleep(2)

    if is_phone_connected():
        log.info("[ADB] Phone CONNECTED")
        adb_shell("svc", "power", "stayon", "true")
    else:
        log.warning("[ADB] Phone not found. Continuing without mobile.")

    tq = TaskQueue()
    tq.start()
    log.info("[QUEUE] Task queue worker started.")

    monitor = ProactiveMonitor(tq)
    monitor.start()
    log.info("[MONITOR] Proactive monitor started (30s interval).")

    voice = WakeWordListener(tq)
    voice.start()
    log.info("[VOICE] Always-live wake word listener started.")

    wh_thread = threading.Thread(target=start_webhook_server, args=(tq, 8093), daemon=True)
    wh_thread.start()
    log.info("[WEBHOOK] Tailscale webhook server on port 8093.")

    tq.add("adb_shell", {"cmd": ["getprop", "ro.product.model"]})
    tq.add("screenshot_analyse", {"context": "startup_check"})

    log.info("=" * 60)
    log.info("  JARVIS IS NOW ALWAYS-LIVE")
    log.info("=" * 60)

    try:
        while True:
            time.sleep(10)
            if is_phone_connected():
                log.debug("[HEARTBEAT] Phone OK, queue=" + str(tq.q.qsize()))
    except KeyboardInterrupt:
        log.info("[JARVIS] Daemon stopping...")
        tq.running = False
        monitor.running = False
        voice.running = False

if __name__ == "__main__":
    main()
