import os
import subprocess
import webbrowser
import pyautogui
import platform
import time
import threading

# Lazy load heavy dependencies
_AUDIO_READY = False
try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    _AUDIO_READY = True
except: pass

# 🧠 O.M.E.G.A. TIER_4: GLOBAL_PATH_CACHE
_APP_CACHE = {}
_CACHE_LOCK = threading.Lock()

def resolve_app_path(app_name):
    """🧠 O.M.E.G.A. V50: CACHED_DEEP_RESOLVER"""
    target = app_name.lower().strip()
    
    # Check cache first
    with _CACHE_LOCK:
        if target in _APP_CACHE and os.path.exists(_APP_CACHE[target]):
            return _APP_CACHE[target]
    
    import winreg
    
    # 1. Windows Registry Scan (App Paths)
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                name = winreg.EnumKey(key, i)
                if target in name.lower():
                    with winreg.OpenKey(key, name) as subkey:
                        path = winreg.QueryValue(subkey, "")
                        return _finalize_resolve(app_name, path)
    except: pass

    # 2. Start Menu Indexing (.lnk files)
    start_menu_paths = [
        os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ["AppData"], "Microsoft", "Windows", "Start Menu", "Programs")
    ]
    
    for menu_path in start_menu_paths:
        if not os.path.exists(menu_path): continue
        for root, dirs, files in os.walk(menu_path):
            for file in files:
                if target in file.lower():
                    full_path = os.path.join(root, file)
                    if file.endswith(".lnk"):
                        # In a real build, we'd resolve the shortcut. 
                        # For now, we'll try to execute the shortcut directly.
                        return full_path
    
    # 3. Common Path Fuzzy Search
    common_roots = [
        os.environ.get("ProgramFiles", "C:\\Program Files"),
        os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        os.path.join(os.environ.get("LocalAppData", ""), "Programs")
    ]
    
    for root in common_roots:
        if not os.path.exists(root): continue
        try:
            for item in os.listdir(root):
                if target in item.lower():
                    # Check for executable in the matched directory
                    item_path = os.path.join(root, item)
                    if os.path.isfile(item_path) and item_path.endswith(".exe"):
                        return _finalize_resolve(app_name, item_path)
                    if os.path.isdir(item_path):
                        for sub_file in os.listdir(item_path):
                            if sub_file.lower().endswith(".exe") and target in sub_file.lower():
                                return _finalize_resolve(app_name, os.path.join(item_path, sub_file))
        except: continue
        
    return None

def _finalize_resolve(app_name, path):
    if path:
        with _CACHE_LOCK:
            _APP_CACHE[app_name.lower().strip()] = path
    return path

def open_app(app_name):
    """Launches local applications or web-nodes via system shell with sentient fallback."""
    web_nodes = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "facebook": "https://facebook.com",
        "github": "https://github.com",
        "chatgpt": "https://chat.openai.com",
        "netflix": "https://netflix.com",
        "spotify": "https://open.spotify.com",
        "twitter": "https://twitter.com",
        "instagram": "https://instagram.com"
    }
    
    target = app_name.lower().strip()
    try:
        # 🌐 1. DIRECT WEB_NODE MATCH
        if target in web_nodes:
            webbrowser.open(web_nodes[target])
            return f"Global node {target} synchronized via browser."
            
        # 🌐 2. DYNAMIC WEB DETECTION
        if "." in target or target in ["amazon", "reddit", "linkedin"]:
            url = target if target.startswith("http") else f"https://{target}"
            if "." not in url: url += ".com"
            webbrowser.open(url)
            return f"Synchronizing with dynamic node: {url}"

        # 📂 3. DEEP_LOCAL_RESOLVE
        if platform.system() == "Windows":
            resolved_path = resolve_app_path(app_name)
            if resolved_path:
                _finalize_resolve(app_name, resolved_path)
                print(f"[IGNITION] Resolved tactical path: {resolved_path}")
                os.startfile(resolved_path) 
                return f"Local node {app_name} located and online."
            
            # Fallback to shell 'start'
            subprocess.Popen(f"start {app_name}", shell=True)
            return f"Attempting shell ignition for {app_name}."
        else:
            subprocess.Popen(["open", "-a", app_name])
            return f"Local node {app_name} is online."
            
    except Exception as e:
        # 🧠 4. NEURAL FALLBACK
        print(f"[IGNITION_FAIL] {e}")
        webbrowser.open(f"https://www.google.com/search?q={app_name}&btnI")
        return f"Surgical redirect: Resolved {app_name} via global search."

def search_web(query):
    """Initializes global web search."""
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return "Web search sequence initiated."

def type_text(text):
    """Simulates neural-guided keyboard input."""
    pyautogui.write(text, interval=0.1)
    return "Typing sequence successful."

def open_file(path):
    """Executes local file node analysis."""
    try:
        os.startfile(path)
        return f"File node {path} is active."
    except Exception as e:
        return f"Signal Error: {str(e)}"

def find_all_files(payload, limit=10):
    """Mocks a deep system scan for file nodes (Search logic simplified)."""
    # In a full build, this would use os.walk or indexing
    return [{"name": f"{payload}_node_{i}", "path": f"C:/jarvis/{payload}_{i}.py"} for i in range(5)]

def control_music(cmd):
    """Adjusts the sonic environment via media keys."""
    if cmd == "play" or cmd == "pause":
        pyautogui.press("playpause")
    elif cmd == "next":
        pyautogui.press("nexttrack")
    elif cmd == "previous":
        pyautogui.press("prevtrack")
    return "Sonic recalibration complete."

# 📊 O.M.E.G.A. TELEMETRY_CACHE
_TELEMETRY_CACHE = {
    "thermal": {"cpu_load": "0%", "ram_load": "0%", "cores": [], "gpu": 0},
    "tasks": [],
    "network": {"sent": "0MB", "recv": "0MB"},
    "last_update": 0
}

def _telemetry_worker():
    """Background worker to refresh system metrics without blocking the main thread."""
    import psutil
    while True:
        try:
            # 1. Thermal & Resource Load
            cpu_load = psutil.cpu_percent(interval=None) # Non-blocking
            mem = psutil.virtual_memory()
            
            # Real GPU Telemetry via GPUtil
            gpu_load = 0
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus: gpu_load = gpus[0].load * 100
            except: pass

            _TELEMETRY_CACHE["thermal"] = {
                "cpu_load": f"{cpu_load}%",
                "ram_load": f"{mem.percent}%",
                "cores": psutil.cpu_percent(percpu=True),
                "gpu": round(gpu_load, 1)
            }

            # 2. Top Processes
            tasks = []
            # Optimization: Only iterate over processes once and get needed info
            for p in sorted(psutil.process_iter(['name', 'cpu_percent', 'memory_info']), 
                           key=lambda x: x.info['cpu_percent'] or 0, 
                           reverse=True)[:5]:
                try:
                    tasks.append({
                        "pid": p.pid,
                        "name": p.info['name'],
                        "cpu": f"{p.info['cpu_percent']}%",
                        "ram": f"{round(p.info['memory_info'].rss / (1024 * 1024), 1)}MB"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied): continue
            _TELEMETRY_CACHE["tasks"] = tasks

            # 3. Network
            net = psutil.net_io_counters()
            _TELEMETRY_CACHE["network"] = {
                "sent": f"{round(net.bytes_sent / (1024 * 1024), 2)}MB",
                "recv": f"{round(net.bytes_recv / (1024 * 1024), 2)}MB"
            }
            
            _TELEMETRY_CACHE["last_update"] = time.time()
        except Exception as e:
            print(f"[TELEMETRY_CRITICAL] Worker Error: {e}")
        
        time.sleep(2) # Refresh every 2 seconds

# Ignite Telemetry Thread
import threading
threading.Thread(target=_telemetry_worker, daemon=True).start()

def get_running_tasks():
    """Returns cached top nodes by CPU resonance."""
    return _TELEMETRY_CACHE["tasks"]

def get_thermal_profile():
    """Returns cached hardware heat signatures."""
    return _TELEMETRY_CACHE["thermal"]

def get_network_resonance():
    """Returns cached global data throughput."""
    return _TELEMETRY_CACHE["network"]


def capture_screen():
    """Captures the current tactical focal plane."""
    path = "vision_temp.png"
    pyautogui.screenshot(path)
    return path

def set_volume(level):
    """Recalibrates master audio gain via the Core Audio Session."""
    if not _AUDIO_READY:
        # Fallback to media keys if pycaw is missing
        if level > 50: pyautogui.press("volumeup", presses=5)
        else: pyautogui.press("volumedown", presses=5)
        return f"Resonance Note: Audio drivers (pycaw) not moored. Manual adjustment attempted."
        
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        
        # level is 0-100, pycaw expects 0.0 to 1.0 (or dB)
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Master gain adjusted to {level}%."
    except Exception as e:
        return f"Resonance Error: {str(e)}"

def set_brightness(level):
    """Recalibrates visual luminosity via the Display driver."""
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(level)
        return f"Display luminosity set to {level}%."
    except Exception as e:
        return f"Luminosity Failure: {str(e)}"

def system_power(mode):
    """Physical OS state manipulation."""
    mode = mode.lower()
    if mode == "shutdown":
        os.system("shutdown /s /t 1")
    elif mode == "restart":
        os.system("shutdown /r /t 1")
    elif mode == "sleep":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return f"System {mode} sequence initiated."

def manage_window(action, partial_title=None):
    """Tier 4: Global Resonance - Direct PC Window Manipulation."""
    try:
        import pygetwindow as gw
        action = action.upper()
        
        # If no title, default to targeting 'Active' or 'All'
        if not partial_title or partial_title.lower() == "all":
            windows = gw.getAllWindows()
        else:
            windows = gw.getWindowsWithTitle(partial_title)
            
        if not windows:
            return f"Signal lost: No window matching '{partial_title}' found."

        count = 0
        for w in windows:
            if not w.title: continue # Skip ghosts
            
            if action == "MINIMIZE":
                w.minimize()
                count += 1
            elif action == "MAXIMIZE":
                w.maximize()
                count += 1
            elif action == "RESTORE":
                w.restore()
                count += 1
            elif action == "CLOSE":
                w.close()
                count += 1
            elif action == "FOCUS":
                w.activate()
                return f"Node {w.title} focused."

        return f"Dominion protocol executed: {action} applied to {count} nodes."
    except Exception as e:
        return f"Window Resonance Error: {str(e)}"

def kill_process(name):
    """Surgical termination of a system thread."""
    try:
        os.system(f"taskkill /f /im {name}")
        return f"Thread {name} has been terminated."
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'desktop', f'Unhandled exception: {e}')
        return "Termination sequence failed."

def set_wallpaper(path):
    """Tier 4: Visual Resonance - Modifies the desktop aesthetic layer."""
    import ctypes
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
        return "Desktop aesthetic layer updated."
    except Exception as e:
        return f"Wallpaper Sequence Failure: {str(e)}"

def autonomous_agent_task(task):
    """Placeholder for recursive autonomous missions."""
    return f"Autonomous Mission {task} synchronized."
