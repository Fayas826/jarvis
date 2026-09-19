import os
import time
import psutil
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
import pyautogui
from action.desktop_control.bio_link import bio_link
from core.cognition.reasoning.shared_state import NEURAL_INSIGHT_CACHE, NEURAL_LOCK

router = APIRouter()

@router.get("/bio/vitals")
async def get_bio_vitals():
    return bio_link.get_vitals()

@router.get("/resonance/vitals")
async def resonance_vitals():
    return {
        "cpu_load": f"{psutil.cpu_percent()}%",
        "ram_load": f"{psutil.virtual_memory().percent}%",
        "gpu": 0,
        "latency": "14ms",
        "network": {"sent": "0MB", "recv": "0MB"},
        "tasks": [],
    }

@router.post("/vision/focal_plane")
async def vision_focal_plane():
    with NEURAL_LOCK:
        insight = NEURAL_INSIGHT_CACHE.get("visual", "Scanning focal plane...")
    return {"status": "SUCCESS", "insight": insight}

@router.get("/iot/state")
async def get_iot_state():
    return {
        "status": "ONLINE",
        "devices": 4
    }

@router.get("/system/screenshot")
async def get_system_screenshot():
    temp_dir = "data/temp"
    os.makedirs(temp_dir, exist_ok=True)
    screenshot_path = os.path.join(temp_dir, "live_screen.png")
    screenshot = pyautogui.screenshot()
    # Downscale slightly for web load performance
    screenshot.thumbnail((1280, 720))
    screenshot.save(screenshot_path, "PNG")
    return FileResponse(screenshot_path, media_type="image/png")
