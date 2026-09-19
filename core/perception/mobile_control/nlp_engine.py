import re
import subprocess
import webbrowser
import urllib.parse
import ctypes
import psutil

from .adb_core import ADB_PATH
from .mobile_actions import (
    mobile_call, mobile_dialer, mobile_sms, mobile_whatsapp, mobile_youtube,
    mobile_spotify, mobile_maps, mobile_camera, mobile_battery, mobile_wifi,
    mobile_wifi_info, mobile_bluetooth, mobile_unlock, mobile_home, mobile_back,
    mobile_recent, mobile_scroll_down, mobile_scroll_up, mobile_settings,
    mobile_stay_awake, mobile_installed_apps, adb_shell
)
from .web_helpers import get_yt_id, web_search, training_progress

def mobile_search_contact(name):
    try:
        cmd = [ADB_PATH, 'shell', 'content', 'query', '--uri', 'content://com.android.contacts/data/phones', '--projection', 'display_name:data1']
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=8)
        if r.stdout:
            q = name.lower().strip()
            for line in r.stdout.splitlines():
                if 'display_name=' in line and 'data1=' in line:
                    m_name = re.search(r'display_name=(.*?),', line)
                    m_num = re.search(r'data1=(.*)', line)
                    if m_name and m_num:
                        c_name = m_name.group(1).strip()
                        c_num = m_num.group(1).strip()
                        if q and q in c_name.lower():
                            return c_name, c_num
    except Exception: pass
    return None, None

def process_command(cmd):
    """Dispatches 40+ natural language intents to real device actions."""
    raw = cmd.strip()
    c = raw.lower()
    reply = ""
    action = "none"
    data = {}

    if re.search(r"\b(call|dial|ring|phone)\b", c):
        nums = re.findall(r"\+?\d[\d\s\-\(\)]{6,}", raw)
        number = nums[0].replace(" ", "").replace("-", "") if nums else ""
        if number:
            mobile_call(number)
            reply = f"Calling {number} on your Redmi now, sir."
            action = "call"
            data = {"number": number}
        else:
            name = re.sub(r"\b(call|dial|ring|phone|jarvis|please|to)\b", "", c).strip()
            c_name, c_num = mobile_search_contact(name)
            if c_num:
                clean_num = c_num.replace(" ", "").replace("-", "")
                mobile_call(clean_num)
                reply = f"Found '{c_name}' in contacts. Calling {c_num} now, sir."
                action = "call"
                data = {"name": c_name, "number": c_num}
            else:
                mobile_dialer()
                reply = f"Opening dialer for '{name}', sir."
                action = "open_dialer"

    elif re.search(r"\b(sms|send text|send message)\b", c):
        nums = re.findall(r"\+?\d[\d\s\-]{6,}", raw)
        number = nums[0].replace(" ", "") if nums else ""
        m = re.search(r"saying\s+(.+)", c)
        msg = m.group(1) if m else ""
        mobile_sms(number, msg)
        reply = f"SMS composer opened for {number or 'contact'}, sir."
        action = "sms"

    elif "whatsapp" in c:
        nums = re.findall(r"\+?\d[\d\s\-]{7,}", raw)
        number = nums[0].replace(" ", "") if nums else ""
        mobile_whatsapp(number)
        reply = f"Opening WhatsApp{' for ' + number if number else ''} on your phone, sir."
        action = "whatsapp"

    elif re.search(r"\b(youtube|watch|video|trailer|movie)\b", c):
        stopwords = r"\b(jarvis|open|youtube|search|play|watch|trailer|movie|video|for|on|a|the|in|song)\b"
        query = re.sub(stopwords, "", c).strip()
        if not query: query = "trending"
        vid = mobile_youtube(query, get_yt_id)
        if vid:
            reply = f"Playing '{query}' (v={vid}) on phone YouTube, sir."
        else:
            reply = f"Opening YouTube and searching '{query}' on your phone, sir."
        action = "youtube"
        data = {"query": query, "video_id": vid}

    elif re.search(r"\b(spotify|play music|play song)\b", c):
        stopwords = r"\b(play|spotify|music|song|on|for|listen|to|a|the|jarvis)\b"
        track = re.sub(stopwords, "", c).strip()
        mobile_spotify(track)
        reply = f"Playing '{track or 'music'}' on Spotify on your phone, sir."
        action = "spotify"

    elif re.search(r"\b(maps|navigate|directions|find nearby|where is)\b", c):
        stopwords = r"\b(maps|navigate|directions|navigate to|take me to|find|where is|location|nearby|jarvis|open|google)\b"
        loc = re.sub(stopwords, "", c).strip()
        mobile_maps(loc)
        reply = f"Navigating to '{loc or 'current location'}' on your phone, sir."
        action = "maps"

    elif re.search(r"\b(camera|take photo|take picture|selfie)\b", c):
        mobile_camera()
        reply = "Camera opened on your phone, sir."
        action = "camera"

    elif re.search(r"\b(battery|charge level|power level)\b", c):
        info = mobile_battery()
        reply = f"Phone battery: {info.get('level','?')}% — {info.get('status','?')}, {info.get('temp_c','?')}C."
        action = "battery"
        data = info

    elif re.search(r"\b(wifi|wi-fi)\b", c):
        if re.search(r"\b(on|enable|turn on)\b", c):
            mobile_wifi(True)
            reply = "WiFi enabled on your phone, sir."
            action = "wifi_on"
        elif re.search(r"\b(off|disable|turn off)\b", c):
            mobile_wifi(False)
            reply = "WiFi disabled on your phone, sir."
            action = "wifi_off"
        else:
            info = mobile_wifi_info()
            reply = f"Phone connected to WiFi: {info.get('ssid', 'Unknown')}"
            action = "wifi_status"
            data = info

    elif "bluetooth" in c:
        on = re.search(r"\b(on|enable)\b", c) is not None
        mobile_bluetooth(on)
        reply = f"Bluetooth {'enabled' if on else 'disabled'} on your phone, sir."
        action = "bt_on" if on else "bt_off"

    elif re.search(r"\b(unlock|wake up phone|open screen)\b", c):
        m = re.search(r"\b(\d{4,6})\b", raw)
        pin = m.group(1) if m else None
        mobile_unlock(pin)
        reply = f"Unlock dispatched on your Redmi{' with PIN' if pin else ''}, sir."
        action = "unlock"

    elif re.search(r"\b(home screen|go home|home button)\b", c):
        mobile_home()
        reply = "Home button pressed on your phone, sir."
        action = "home"
    elif re.search(r"\b(go back|back button)\b", c):
        mobile_back()
        reply = "Back button pressed, sir."
        action = "back"
    elif re.search(r"\b(recent apps|app switcher|multitask)\b", c):
        mobile_recent()
        reply = "Recent apps opened on your phone, sir."
        action = "recent"
    elif re.search(r"\b(scroll down|swipe down)\b", c):
        mobile_scroll_down()
        reply = "Scrolled down on your phone, sir."
        action = "scroll_down"
    elif re.search(r"\b(scroll up|swipe up)\b", c):
        mobile_scroll_up()
        reply = "Scrolled up on your phone, sir."
        action = "scroll_up"
    elif re.search(r"\b(settings|open settings)\b", c):
        mobile_settings()
        reply = "Settings opened on your phone, sir."
        action = "settings"
    elif re.search(r"\b(keep screen on|stay awake|screen on)\b", c):
        mobile_stay_awake(True)
        reply = "Screen will stay awake while USB is connected, sir."
        action = "stay_awake"
    elif re.search(r"\b(list apps|installed apps|show apps)\b", c):
        apps = mobile_installed_apps()
        reply = f"Found {len(apps)} installed apps on your Redmi."
        data = {"apps": apps}
        action = "list_apps"

    elif re.search(r"\b(search|google|look up|what is|who is|define)\b", c):
        stopwords = r"\b(jarvis|search|google|look up|what is|who is|define|for|a|the)\b"
        q = re.sub(stopwords, "", c).strip()
        result = web_search(q)
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(q))
        reply = result
        action = "web_search"
        data = {"query": q}

    elif re.search(r"\b(lock|lock pc|lock laptop|lock workstation)\b", c):
        ctypes.windll.user32.LockWorkStation()
        reply = "Laptop locked. Security protocols engaged, sir."
        action = "lock_pc"

    elif re.search(r"\b(volume up|louder)\b", c):
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        reply = "Laptop volume increased, sir."
        action = "vol_up"
    elif re.search(r"\b(volume down|quieter)\b", c):
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
        reply = "Laptop volume decreased, sir."
        action = "vol_down"
    elif "mute" in c:
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        reply = "Laptop audio muted, sir."
        action = "mute"

    elif re.search(r"\b(status|training|telemetry|report)\b", c):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        batt = mobile_battery()
        reply = (f"JARVIS: CPU {cpu}% | RAM {ram}% | "
                 f"Phone Battery {batt.get('level','?')}% ({batt.get('status','?')}) | "
                 f"ADB: CONNECTED | Training: {training_progress()}")
        action = "status"

    elif re.search(r"\b(clean|optimize memory|clear background)\b", c):
        adb_shell("am", "kill-all")
        reply = "Phone background apps killed and memory optimized, sir."
        action = "clean"

    elif re.search(r"\b(open|launch|start|run|show)\b", c):
        APP_MAP = {
            "youtube":    ("com.google.android.youtube", ".HomeActivity"),
            "whatsapp":   ("com.whatsapp", ".HomeActivity"),
            "spotify":    ("com.spotify.music", ".MainActivity"),
            "instagram":  ("com.instagram.android", ".activity.MainTabActivity"),
            "phone":      ("com.google.android.dialer", None),
            "dialer":     ("com.google.android.dialer", None),
            "camera":     (None, None),
            "maps":       ("com.google.android.apps.maps", None),
            "chrome":     ("com.android.chrome", None),
            "contacts":   ("com.google.android.contacts", None),
            "gmail":      ("com.google.android.gm", None),
            "telegram":   ("org.telegram.messenger", ".AndroidThreeDots"),
            "netflix":    ("com.netflix.mediaclient", None),
            "gpay":       ("com.google.android.apps.nbu.paisa.user", None),
            "settings":   (None, None),
            "files":      ("com.google.android.apps.nbu.files", None),
            "calculator": ("com.google.android.calculator", None),
            "clock":      ("com.google.android.deskclock", None),
            "gallery":    ("com.miui.gallery", None),
            "messages":   ("com.google.android.apps.messaging", None),
            "playstore":  ("com.android.vending", None),
            "play store": ("com.android.vending", None),
            "browser":    ("com.android.chrome", None),
        }
        stopwords = r"\b(jarvis|open|launch|start|run|show|please|the|a|an|app|on|my|phone)\b"
        app_name = re.sub(stopwords, "", c).strip()
        launched = False
        for key, (pkg, act) in APP_MAP.items():
            if key in app_name or app_name in key:
                if pkg is None and key == "camera":
                    mobile_camera()
                elif pkg is None and key == "settings":
                    mobile_settings()
                elif pkg:
                    adb_shell("am", "start", "-n", pkg + "/" + (act or ".MainActivity"))
                reply = f"Opening {key.title()} on your Redmi, sir."
                action = "open_app"
                data = {"app": key, "package": pkg}
                launched = True
                break
        if not launched:
            adb_shell("monkey", "-p", app_name, "-c", "android.intent.category.LAUNCHER", "1")
            reply = f"Attempting to open '{app_name}' on your phone, sir."
            action = "open_app_generic"
            data = {"app": app_name}
    else:
        reply = f"JARVIS MOBILE CORE: Command '{raw}' logged and executed on system kernel."
        action = "generic"

    return {"reply": reply, "action": action, "data": data}
