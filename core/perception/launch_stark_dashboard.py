"""
JARVIS O.M.E.G.A. MOBILE CONTROL SERVER v2 (MODULARIZED)
=====================================================
This entry point acts as a router to the `mobile_control` package.
"""

import threading
import time
import webbrowser
import logging

from core.perception.mobile_control import start_server, SERVER_PORT, TAILSCALE_URL, mobile_stay_awake, ADB_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s [JARVIS_MOBILE] %(message)s")

if __name__ == "__main__":
    mobile_stay_awake(True)

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(0.8)

    local_url = f"http://localhost:{SERVER_PORT}/core/perception/stark_dashboard.html"
    tail_url  = f"{TAILSCALE_URL}/core/perception/stark_dashboard.html"

    logging.info(f"Opening: {local_url}")
    webbrowser.open(local_url)

    print(f"""
+==============================================================+
|       JARVIS O.M.E.G.A. MOBILE CONTROL CENTER v2            |
+==============================================================+
| Local:     {local_url:<49}|
| Tailscale: {tail_url:<49}|
| ADB Device: REDMI 22101316UP (Android 14) CONNECTED          |
| ADB Path:   {ADB_PATH:<49}|
+==============================================================+
| KEY ENDPOINTS:                                               |
|  POST /api/command            -- Siri NLP engine             |
|  GET  /api/v1/mobile/screencap-- Live phone screen           |
|  GET  /api/v1/mobile/battery  -- Phone battery               |
|  GET  /api/v1/mobile/devices  -- ADB device list            |
|  POST /api/v1/mobile/call     -- Direct USB phone call       |
|  POST /api/v1/mobile/tap      -- Hardware tap on screen      |
|  POST /api/v1/mobile/swipe    -- Swipe gesture               |
|  POST /api/v1/mobile/type     -- Type text on phone          |
|  GET  /api/processes          -- Running processes           |
|  GET  /api/telemetry          -- Full system telemetry       |
+==============================================================+
Press Ctrl+C to stop.
""")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[JARVIS] Server stopped.")
