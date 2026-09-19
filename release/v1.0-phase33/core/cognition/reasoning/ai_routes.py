from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict

from core.cognition.reasoning.planner import planner
from core.cognition.reasoning.context_engine import context_engine
from core.orchestration.task_engine import get_task_engine
from core.reliability.experience_engine import experience_engine
from core.reliability.reliability_engine import reliability_engine
from perception.voice.sonic_engine_v2 import sonic_engine

router = APIRouter()


class Query(BaseModel):
    message: str
    metadata: Optional[Dict] = None


def _summarize_task(query_text: str, task) -> str:
    if task.status == "SUCCESS":
        return f"Execution complete for '{query_text}'. {len(task.steps)} step(s) finished cleanly."
    if task.status == "BLOCKED":
        return f"I understood '{query_text}', but I blocked execution because the request was not safe enough to run automatically."
    if task.status == "FAILED":
        failed_step = next((step for step in task.steps if step.status == "FAILED"), None)
        detail = failed_step.description if failed_step else "the execution plan"
        return f"Execution for '{query_text}' failed while running {detail}."
    return f"Execution finished with status {task.status} for '{query_text}'."


@router.post("/jarvis")
async def jarvis_endpoint(query: Query, token: dict = Depends(lambda: {"identity": "verified"})):
    context = context_engine.get_context()
    query.metadata = query.metadata or {}
    query.metadata.update(context)

    task = await planner.create_plan(query.message, context=query.metadata)
    task_engine = get_task_engine()

    if task.status == "BLOCKED" or not task.steps:
        response_text = _summarize_task(query.message, task)
        return {
            "type": "TASK_EXECUTION",
            "status": "BLOCKED",
            "response": response_text,
            "task_id": task.task_id,
            "performance": {"execution_time": 0, "success_rate": 0.0, "context_state": context.get("state")},
            "steps": [],
            "optimizations": [],
        }

    try:
        executed_task = await task_engine.execute_task(task)
    except Exception as exc:
        reliability_engine.analyze_failure("JARVIS_QUERY", str(exc), {"query": query.message})
        executed_task = task
        executed_task.status = "FAILED"

    success_rate = (
        sum(1 for step in executed_task.steps if step.status == "SUCCESS") / len(executed_task.steps)
        if executed_task.steps
        else 0.0
    )

    reliability_engine.verify_repair(
        query.message,
        lambda: executed_task.status == "SUCCESS" or executed_task.status == "BLOCKED",
    )

    response_text = _summarize_task(query.message, executed_task)
    final_status = "NOMINAL" if executed_task.status == "SUCCESS" else executed_task.status

    if response_text and context.get("state") != "FOCUSED" and executed_task.status != "BLOCKED":
        await sonic_engine.speak(response_text)

    return {
        "type": "TASK_EXECUTION",
        "status": final_status,
        "response": response_text,
        "task_id": executed_task.task_id,
        "performance": {
            "execution_time": (executed_task.completed_at - executed_task.created_at) if executed_task.completed_at else 0,
            "success_rate": success_rate,
            "context_state": context.get("state"),
            "ux_telemetry": experience_engine.get_ux_telemetry(),
        },
        "steps": [
            {"description": step.description, "status": step.status, "retries": step.retry_count, "error": step.error}
            for step in executed_task.steps
        ],
        "optimizations": reliability_engine.get_reliability_report().get("recent_patterns", []),
    }
