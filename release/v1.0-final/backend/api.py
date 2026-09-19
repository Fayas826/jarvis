
import os
import sys
import time
import asyncio
import psutil
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess

# 🧱 ADD ROOT TO PATH
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from infrastructure.config.settings import LOG_DIR, JARVIS_PIN, JWT_SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# 🛡️ O.M.E.G.A. ZERO_WINDOW_ENFORCER
_original_popen = subprocess.Popen
class HiddenPopen(_original_popen):
    def __init__(self, *args, **kwargs):
        creationflags = kwargs.get('creationflags', 0)
        kwargs['creationflags'] = creationflags | 0x08000000
        super().__init__(*args, **kwargs)

subprocess.Popen = HiddenPopen

load_dotenv()

# --- SINGLETON ENFORCEMENT ---
def verify_singleton():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid: continue
            pname = (proc.info.get('name') or "").lower()
            if 'python' not in pname: continue
            cmdline = " ".join(proc.info.get('cmdline') or [])
            if 'api.py' in cmdline: return False
        except: continue
    return True

if not verify_singleton():
    print("[API] Redundant backend detected. Exiting.")
    sys.exit(0)

# --- CORE HANDSHAKE ---
from perception.vision.vision_loop import vision_loop
from infrastructure.watchdog.system_guardian import system_guardian
from core.cognition.reasoning.proactive_engine import proactive_engine
from core.orchestration.task_engine import init_task_engine
from action.desktop_control.desktop_controller import desktop_controller
from core.orchestration.autonomous_orchestrator import autonomous_orchestrator
from core.orchestration.routine_manager import routine_manager
from core.cognition.reasoning.context_engine import context_engine

# Inject Desktop Controller into Task Engine
init_task_engine(desktop_controller.execute)

# --- ROUTERS ---
from backend.routes import health_routes, ai_routes, system_routes, orchestrator_routes, apps_routes

# --- MODELS ---
class HandshakeRequest(BaseModel):
    pin: str

# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    vision_loop.start()
    system_guardian.start()
    proactive_task = asyncio.create_task(proactive_engine.start_loop())
    autonomous_task = asyncio.create_task(autonomous_orchestrator.start())
    routine_task = asyncio.create_task(routine_manager.start())
    yield
    vision_loop.stop()
    system_guardian.stop()
    proactive_task.cancel()
    autonomous_task.cancel()
    routine_task.cancel()

app = FastAPI(title="JARVIS O.M.E.G.A. Core", version="10.0.0", lifespan=lifespan)

@app.get("/api/system/status")
async def get_system_status():
    return context_engine.get_context()

# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH LOGIC ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="NEURAL_LINK_REQUIRED")
    token = auth_header.split(" ")[1]
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'api', f'Unhandled exception: {e}')
        raise HTTPException(status_code=401, detail="INVALID_NEURAL_LINK")

# --- MOUNT ROUTERS ---
app.include_router(health_routes.router, tags=["Health"])
app.include_router(ai_routes.router, prefix="/api", tags=["AI"])
app.include_router(system_routes.router, prefix="/api", tags=["System"])
app.include_router(orchestrator_routes.router, prefix="/api/orchestrator", tags=["Orchestrator"])
app.include_router(apps_routes.router, prefix="/api", tags=["Applications"])

# --- CORE AUTH ENDPOINTS ---
@app.post("/auth/handshake")
async def handshake(req: HandshakeRequest):
    if req.pin == JARVIS_PIN:
        token = create_access_token({"identity": "ZENITH_HUD", "access_level": "CORE"})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=403, detail="INVALID_HANDSHAKE_PIN")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")
