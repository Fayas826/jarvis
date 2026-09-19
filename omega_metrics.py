"""
O.M.E.G.A. Metrics Bridge — Standalone FastAPI server
Runs on port 5001. Provides:
  POST /auth/handshake  — auth
  GET  /ghost_sync      — health/keep-alive
  GET  /system_metrics  — 5D CPU + RAM data for Tesseract4D
"""
import os
import psutil
import jwt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="O.M.E.G.A. Metrics Bridge", version="20.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JARVIS_PIN = os.getenv("JARVIS_PIN", "1234")


class HandshakeRequest(BaseModel):
    pin: str


# ─── AUTH ───────────────────────────────────────────────────────────
@app.post("/auth/handshake")
async def handshake(req: HandshakeRequest):
    if req.pin == JARVIS_PIN:
        token = jwt.encode(
            {"identity": "ZENITH_HUD", "access_level": "CORE"},
            JARVIS_PIN,
            algorithm="HS256",
        )
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=403, detail="INVALID_HANDSHAKE_PIN")


# ─── HEALTH ─────────────────────────────────────────────────────────
@app.get("/ghost_sync")
async def ghost_sync():
    return {"status": "OMEGA_ONLINE", "version": "20.0"}


# ─── 5D SYSTEM METRICS (CPU + RAM → Tesseract breathing) ────────────
@app.get("/system_metrics")
async def system_metrics():
    """
    Real-time CPU and RAM metrics.
    cpu_percent  → XW rotation speed (4D spin axis)
    ram_percent  → breathing amplitude (5D geometry scale)
    """
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    return {
        "cpu_percent":      round(cpu, 2),
        "ram_percent":      round(mem.percent, 2),
        "ram_used_gb":      round(mem.used / (1024 ** 3), 2),
        "ram_total_gb":     round(mem.total / (1024 ** 3), 2),
        "ram_available_gb": round(mem.available / (1024 ** 3), 2),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("omega_metrics:app", host="127.0.0.1", port=5001, reload=True)
