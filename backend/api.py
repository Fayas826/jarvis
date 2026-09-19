import os
import sys
import json
import time

# Ensure project root is on sys.path when launched from backend/ or via pythonw
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# #region agent log
def _debug_log(location, message, data=None, hypothesis_id="A"):
    try:
        payload = {
            "sessionId": "d2db55",
            "runId": os.getenv("JARVIS_DEBUG_RUN", "startup"),
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000),
        }
        with open(os.path.join(ROOT_DIR, "debug-d2db55.log"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
    except Exception:
        pass
# #endregion

_debug_log("backend/api.py:path", "sys.path bootstrap", {"root_dir": ROOT_DIR, "cwd": os.getcwd(), "in_path": ROOT_DIR in sys.path})

import psutil
import jwt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.middleware.saas_billing import saas_rate_limiter_middleware
from starlette.middleware.base import BaseHTTPMiddleware
try:
    from backend.routes.stripe_webhooks import router as stripe_router
except ModuleNotFoundError:
    stripe_router = None
from backend.routes.orchestrator_routes import router as orchestrator_router
from backend.routes.stream_routes import router as stream_router
from core.orchestration.world_state_engine import world_state_engine
from core.orchestration.situational_agent_router import situational_agent_router
from core.cognition.memory.scored_memory import scored_memory_store
from core.cognition.reasoning.model_backed_reasoner import model_backed_reasoner
from core.orchestration.rollback_tool_executor import rollback_tool_executor
from core.perception.perception_session import perception_session

app = FastAPI(title="O.M.E.G.A. Neural Core API", version="20.0")

# CORS — allow Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register SaaS Token Bucket Rate Limiter
app.add_middleware(BaseHTTPMiddleware, dispatch=saas_rate_limiter_middleware)

# Register Webhook Routes
if stripe_router is not None:
    app.include_router(stripe_router)
else:
    @app.get("/webhooks/stripe/status")
    async def stripe_webhook_status():
        return {"status": "DISABLED", "reason": "python_stripe_package_missing"}
        
app.include_router(orchestrator_router, prefix="/orchestrator")
app.include_router(stream_router)

JARVIS_PIN = os.getenv("JARVIS_PIN", "1234")


class HandshakeRequest(BaseModel):
    pin: str


def create_access_token(payload: dict):
    access_token = jwt.encode(payload, JARVIS_PIN, algorithm="HS256")
    return access_token


# ─── AUTH ───
@app.post("/auth/handshake")
async def handshake(req: HandshakeRequest):
    if req.pin == JARVIS_PIN:
        token = create_access_token({"identity": "ZENITH_HUD", "access_level": "CORE"})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=403, detail="INVALID_HANDSHAKE_PIN")


# ─── GHOST SYNC (keep-alive / health) ───
@app.get("/ghost_sync")
async def ghost_sync():
    return {"status": "OMEGA_ONLINE", "version": "20.0"}


# ─── 5D SYSTEM METRICS (CPU + RAM → Tesseract breathing) ───
@app.get("/system_metrics")
async def system_metrics():
    """
    Returns real-time CPU and RAM metrics that drive the 5th dimension
    of the Tesseract4D component (geometry breathing + spin rate).
    """
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": round(cpu, 2),
        "ram_percent": round(mem.percent, 2),
        "ram_used_gb": round(mem.used / (1024 ** 3), 2),
        "ram_total_gb": round(mem.total / (1024 ** 3), 2),
        "ram_available_gb": round(mem.available / (1024 ** 3), 2),
    }

@app.get("/health")
async def health():
    return world_state_engine.health()


@app.get("/world/state")
async def world_state():
    return world_state_engine.snapshot()


@app.post("/world/event")
async def world_event(payload: dict):
    event_type = payload.get("type", "CUSTOM_EVENT")
    source = payload.get("source", "hud")
    event_payload = payload.get("payload", {})
    event = world_state_engine.record_event(event_type, event_payload, source)
    return {"status": "RECORDED", "event": event, "world": world_state_engine.snapshot()}


@app.post("/action/execute")
async def action_execute(payload: dict):
    intent = payload.get("intent", "unknown")
    result = world_state_engine.verify_action(intent, payload)
    return result


@app.post("/agents/route")
async def agents_route(payload: dict):
    situation = payload.get("situation") or payload.get("error") or payload.get("intent") or "unknown situation"
    return situational_agent_router.route(situation, payload)


@app.get("/agents/status")
async def agents_status():
    return situational_agent_router.status()


@app.get("/system_diagnostic")
async def system_diagnostic():
    health_state = world_state_engine.health()
    world = world_state_engine.snapshot()
    agent_state = situational_agent_router.status()
    return [
        {"module": "CORE_API", "details": health_state["status"]},
        {"module": "WORLD_4D_ENGINE", "details": f"events={world['dimensions']['d4_timeline_events']}"},
        {"module": "CONFIDENCE_5D_GATE", "details": f"confidence={world['confidence']} risk={world['risk']['level']}"},
        {"module": "AGENT_ROUTER", "details": agent_state["status"]},
        {"module": "ACTION_CONTRACT", "details": "verified_results_enabled"},
    ]


# ─── MEMORY ───
@app.post("/memory/sync")
async def memory_sync(payload: dict):
    scored_memory_store.remember("User preferences sync", "hud", "preferences", 5, 1.0, payload)
    return {"status": "SYNCED"}

@app.get("/memory/load")
async def memory_load():
    memories = scored_memory_store.recall("User preferences sync", limit=1)
    return {"preferences": memories[0]["metadata"] if memories else {}}

@app.get("/memory/integrity")
async def memory_integrity():
    stats = scored_memory_store.stats()
    return {"status": "STABLE" if stats["avg_score"] > 0 else "DEGRADED", "stats": stats}

# ─── REASONING ───
@app.post("/reason")
async def reason(payload: dict):
    prompt = payload.get("prompt", "")
    context = payload.get("context", {})
    return model_backed_reasoner.reason(prompt, context)

# ─── TOOLS (ROLLBACK LEDGER) ───
@app.post("/tools/prepare")
async def tools_prepare(payload: dict):
    return rollback_tool_executor.prepare(payload.get("tool"), payload.get("intent"), payload.get("payload"))

@app.post("/tools/execute")
async def tools_execute(payload: dict):
    return rollback_tool_executor.mark_executed(payload.get("id"), payload.get("result"))

@app.post("/tools/rollback")
async def tools_rollback(payload: dict):
    return rollback_tool_executor.rollback(payload.get("id"))

@app.get("/tools/ledger")
async def tools_ledger():
    return {"ledger": rollback_tool_executor.ledger()}

# ─── PERCEPTION ───
@app.post("/perception/session")
async def perception_session_state(payload: dict):
    action = payload.get("action", "start")
    if action == "start":
        return perception_session.start()
    return perception_session.stop()

@app.get("/vision/analyze")
async def vision_analyze():
    if not perception_session.active:
        perception_session.start()
    return perception_session.analyze_frame()
