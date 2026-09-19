from fastapi import APIRouter
import asyncio
from core.orchestration.autonomous_orchestrator import autonomous_orchestrator
from core.reliability.reliability_engine import reliability_engine

router = APIRouter()

@router.post("/start")
async def start_orchestrator():
    if not autonomous_orchestrator.running:
        asyncio.create_task(autonomous_orchestrator.start())
    return {"status": "ACTIVE"}

@router.get("/status")
async def get_orchestrator_status():
    return autonomous_orchestrator.get_status()

@router.post("/self_fix")
async def orchestrator_self_fix(payload: dict):
    action_name = payload.get("action_name")
    error = payload.get("error")
    
    reliability_engine.analyze_failure("FRONTEND_INTENT", error, {"intent": action_name})
    
    fix_intent = "RESTART_BACKEND"
    if "audio" in (action_name or "").lower(): fix_intent = "RECONNECT_AUDIO"
    if "lock" in (error or "").lower(): fix_intent = "CLEAR_LOCKS"
    
    result = autonomous_orchestrator._trigger_action(fix_intent, "MEDIUM", "Experience Engine")
    
    if "Success" in result:
        return {"status": "SUCCESS", "detail": f"Autonomous repair successful for {action_name}"}
    return {"status": "FAILED", "detail": "Repair could not resolve the issue autonomously."}

# 👁️ COMPUTER USE ROUTES
from core.orchestration.computer_use_agent import computer_use_agent
from infrastructure.watchdog.safety_layer import safety_gate

@router.post("/computer_use/task")
async def computer_use_task(payload: dict):
    task_desc = payload.get("task")
    # Start task asynchronously in background
    asyncio.create_task(computer_use_agent.execute_task(task_desc))
    return {"status": "IGNITED", "task": task_desc}

@router.get("/computer_use/status")
async def get_computer_use_status():
    return {
        "is_running": computer_use_agent.is_running,
        "current_task": computer_use_agent.current_task,
        "current_step": computer_use_agent.current_step,
        "max_steps": computer_use_agent.max_steps,
        "step_history": computer_use_agent.step_history,
        "bounding_boxes": computer_use_agent.bounding_boxes,
        "agent_state": computer_use_agent.agent_state,
        "confidence_score": computer_use_agent.confidence_score
    }

@router.post("/computer_use/stop")
async def stop_computer_use():
    computer_use_agent.stop()
    return {"status": "STOPPED"}

@router.post("/computer_use/confirm")
async def confirm_computer_use_action(payload: dict):
    action_id = payload.get("action_id")
    # Confirm action in safety gate
    res = safety_gate.confirm_action(action_id)
    if res.get("status") == "ALLOWED":
        # Resume loop by creating task again with the approved payload/action
        action = res["action"]
        asyncio.create_task(computer_use_agent.execute_task(f"Resume: Approved {action['intent']}"))
        return {"status": "APPROVED", "detail": f"Action {action_id} verified and executing."}
    return {"status": "ERROR", "detail": res.get("message", "Confirmation invalid.")}
