"""
JARVIS APPLICATION TAB — Backend Routes
Provides process listing, window enumeration, app launching, and kill APIs
for the Stark Dashboard's 🖥️ APPLICATIONS tab.
"""

import os
import subprocess
import psutil
import ctypes
import ctypes.wintypes
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# ─────────────────────────────────────────
#  MODELS
# ─────────────────────────────────────────

class LaunchRequest(BaseModel):
    app: str

class KillRequest(BaseModel):
    pid: int

class FocusRequest(BaseModel):
    handle: int


# ─────────────────────────────────────────
#  APP LAUNCH MAP (name → command/path)
# ─────────────────────────────────────────

APP_LAUNCH_MAP = {
    "browser":         ["start", "chrome"],
    "notepad":         ["notepad.exe"],
    "terminal":        ["powershell.exe"],
    "calculator":      ["calc.exe"],
    "explorer":        ["explorer.exe"],
    "task_manager":    ["taskmgr.exe"],
    "jarvis_frontend": ["cmd", "/c", "start", "http://localhost:5173"],
    "ollama_ui":       ["cmd", "/c", "start", "http://localhost:11434"],
    "spotify":         ["start", "spotify:"],
    "discord":         ["cmd", "/c", "start", "discord://"],
    "vs_code":         ["code", "."],
    "screenshot":      ["snippingtool"],
}


# ─────────────────────────────────────────
#  ENDPOINTS
# ─────────────────────────────────────────

@router.post("/apps/launch")
async def launch_app(req: LaunchRequest):
    """Launch a named application on the host machine."""
    app_id = req.app.lower()
    cmd = APP_LAUNCH_MAP.get(app_id)
    if not cmd:
        raise HTTPException(status_code=404, detail=f"Unknown app: {app_id}")
    try:
        subprocess.Popen(cmd, shell=False)
        return {"status": "LAUNCHED", "app": app_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes")
async def list_processes():
    """Return a list of running processes with PID, CPU %, and memory usage."""
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            mem = proc.info.get('memory_info')
            procs.append({
                "pid":       proc.info['pid'],
                "name":      proc.info['name'] or "unknown",
                "cpu":       round(proc.info.get('cpu_percent') or 0.0, 1),
                "memory_mb": round((mem.rss / 1024 / 1024) if mem else 0, 1),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    # Sort by CPU descending, cap at 60 entries for mobile perf
    procs.sort(key=lambda p: p["cpu"], reverse=True)
    return procs[:60]


@router.post("/processes/kill")
async def kill_process(req: KillRequest):
    """Terminate a process by PID (with safety guards)."""
    PROTECTED_PIDS = {0, 4}  # System Idle + System
    if req.pid in PROTECTED_PIDS:
        raise HTTPException(status_code=403, detail="Cannot terminate protected system process.")
    try:
        proc = psutil.Process(req.pid)
        name = proc.name()
        proc.terminate()
        return {"status": "TERMINATED", "pid": req.pid, "name": name}
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=404, detail="Process not found.")
    except psutil.AccessDenied:
        raise HTTPException(status_code=403, detail="Access denied — insufficient privileges.")


@router.get("/windows")
async def list_windows():
    """Enumerate visible top-level windows using Win32 API."""
    windows = []

    try:
        EnumWindows = ctypes.windll.user32.EnumWindows
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        def callback(hwnd, _):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buf, length + 1)
                    title = buf.value.strip()
                    if title:
                        windows.append({"handle": hwnd, "title": title})
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        EnumWindows(WNDENUMPROC(callback), 0)
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'apps_routes', f'Unhandled exception: {e}')
        # Fallback: return empty list if Win32 call fails
        pass

    return windows[:30]  # Cap for mobile display


@router.post("/windows/focus")
async def focus_window(req: FocusRequest):
    """Bring a window to foreground by handle."""
    try:
        SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
        ShowWindow = ctypes.windll.user32.ShowWindow
        SW_RESTORE = 9
        ShowWindow(req.handle, SW_RESTORE)
        SetForegroundWindow(req.handle)
        return {"status": "FOCUSED", "handle": req.handle}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/telemetry")
async def get_telemetry():
    """Hardware telemetry: CPU, RAM, GPU temperature + training status."""
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent

    # GPU temperature via nvidia-smi (graceful fallback)
    gpu_temp = 55
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            gpu_temp = int(result.stdout.strip())
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'apps_routes', f'Unhandled exception: {e}')
        pass

    # Training status from log file (if present)
    training_status = "IDLE — No active training"
    try:
        log_path = r"c:\jarvis AI\jarvis\logs\training.log"
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                lines = f.readlines()
                if lines:
                    training_status = lines[-1].strip()
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'apps_routes', f'Unhandled exception: {e}')
        pass

    return {
        "cpu_load": round(cpu, 1),
        "ram_load": round(ram, 1),
        "gpu_temp": gpu_temp,
        "training_status": training_status,
    }
