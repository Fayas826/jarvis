import os
import re
import json
import time
import urllib.parse
from .adb_core import adb, adb_shell, adb_raw_bytes

def mobile_call(number):
    adb_shell("am", "start", "-a", "android.intent.action.CALL", "-d", "tel:" + number)

def mobile_dialer(number=""):
    adb_shell("am", "start", "-a", "android.intent.action.DIAL", "-d", "tel:" + number)

def mobile_sms(number, msg=""):
    adb_shell("am", "start", "-a", "android.intent.action.SENDTO",
              "-d", "sms:" + number, "--es", "sms_body", msg,
              "--ez", "exit_on_sent", "false")

def mobile_whatsapp(number=""):
    if number:
        num = number.lstrip("0")
        if not num.startswith("+"):
            num = "+91" + num if len(num) == 10 else num
        clean = num.replace("+", "")
        adb_shell("am", "start", "-a", "android.intent.action.VIEW", "-d", "https://wa.me/" + clean)
    else:
        adb_shell("am", "start", "-n", "com.whatsapp/.HomeActivity")

def mobile_youtube(query="", get_yt_id_func=None):
    if query:
        vid = get_yt_id_func(query) if get_yt_id_func else None
        if vid:
            url = "https://www.youtube.com/watch?v=" + vid
        else:
            url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
        adb_shell("am", "start", "-a", "android.intent.action.VIEW", "-d", url)
        return vid
    else:
        adb_shell("am", "start", "-n", "com.google.android.youtube/.HomeActivity")
    return None

def mobile_spotify(track=""):
    if track:
        adb_shell("am", "start", "-a", "android.intent.action.VIEW", "-d", "spotify:search:" + urllib.parse.quote(track))
    else:
        adb_shell("am", "start", "-n", "com.spotify.music/.MainActivity")

def mobile_maps(location=""):
    if location:
        adb_shell("am", "start", "-a", "android.intent.action.VIEW", "-d", "geo:0,0?q=" + urllib.parse.quote(location))
    else:
        adb_shell("am", "start", "-n", "com.google.android.apps.maps/.MapsActivity")

def mobile_camera():
    adb_shell("am", "start", "-a", "android.media.action.IMAGE_CAPTURE")

def mobile_settings():
    adb_shell("am", "start", "-a", "android.settings.SETTINGS")

def mobile_wifi(enable):
    adb_shell("svc", "wifi", "enable" if enable else "disable")

def mobile_bluetooth(enable):
    adb_shell("svc", "bluetooth", "enable" if enable else "disable")

def mobile_tap(x, y):
    adb_shell("input", "tap", str(x), str(y))

def mobile_swipe(x1, y1, x2, y2, ms=300):
    adb_shell("input", "swipe", str(x1), str(y1), str(x2), str(y2), str(ms))

def mobile_type(text):
    safe = text.replace(" ", "%s")
    adb_shell("input", "text", safe)

def mobile_keyevent(key):
    adb_shell("input", "keyevent", str(key))

def mobile_back():   mobile_keyevent(4)
def mobile_home():   mobile_keyevent(3)
def mobile_recent(): mobile_keyevent(187)

def mobile_scroll_down():
    mobile_swipe(540, 1400, 540, 600, 300)

def mobile_scroll_up():
    mobile_swipe(540, 600, 540, 1400, 300)

def mobile_unlock(pin=None):
    mobile_keyevent(224)
    time.sleep(0.5)
    mobile_swipe(500, 1500, 500, 500, 200)
    time.sleep(0.5)
    if pin:
        mobile_type(str(pin))
        time.sleep(0.3)
        mobile_keyevent(66)

def mobile_unlock_pattern(pattern_sequence=None):
    config_path = r"c:\jarvis AI\jarvis\data\mobile_security_config.json"
    coords = {
        1: (270, 1100), 2: (540, 1100), 3: (810, 1100),
        4: (270, 1370), 5: (540, 1370), 6: (810, 1370),
        7: (270, 1640), 8: (540, 1640), 9: (810, 1640)
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not pattern_sequence:
                    pattern_sequence = data.get("pattern_sequence", [7, 5, 9, 1, 2, 3, 6, 8, 4])
                raw_coords = data.get("node_coordinates", {})
                for k, v in raw_coords.items():
                    coords[int(k)] = (v[0], v[1])
        except Exception: pass
    if not pattern_sequence:
        pattern_sequence = [7, 5, 9, 1, 2, 3, 6, 8, 4]

    mobile_keyevent(224)
    time.sleep(0.15)
    for i in range(len(pattern_sequence) - 1):
        p1 = coords[pattern_sequence[i]]
        p2 = coords[pattern_sequence[i+1]]
        mobile_swipe(p1[0], p1[1], p2[0], p2[1], ms=80)

def mobile_stay_awake(enable=True):
    adb_shell("svc", "power", "stayon", "true" if enable else "false")

def mobile_screenshot():
    return adb_raw_bytes("exec-out", "screencap", "-p")

def mobile_battery():
    out, _ = adb_shell("dumpsys", "battery")
    info = {}
    if out:
        for line in out.splitlines():
            if "level:" in line:
                info["level"] = line.split(":")[-1].strip()
            elif "status:" in line:
                val = line.split(":")[-1].strip()
                info["status"] = {"2": "Charging", "3": "Discharging", "4": "Not Charging", "5": "Full"}.get(val, val)
            elif "temperature:" in line:
                try:
                    info["temp_c"] = round(int(line.split(":")[-1].strip()) / 10, 1)
                except Exception: pass
    return info

def mobile_wifi_info():
    out, _ = adb_shell("dumpsys", "wifi")
    ssid = "Unknown"
    if out:
        for line in out.splitlines():
            if "mWifiInfo" in line and "SSID:" in line:
                m = re.search(r"SSID:\s*\"?([^,\s\"]+)\"?", line)
                if m:
                    ssid = m.group(1)
                    break
    return {"ssid": ssid}

def mobile_installed_apps():
    out, _ = adb_shell("pm", "list", "packages", "-3")
    apps = []
    if out:
        for line in out.splitlines():
            pkg = line.replace("package:", "").strip()
            if pkg:
                apps.append(pkg)
    return apps[:50]
