import sys
import os
import asyncio
from unittest.mock import AsyncMock, patch

log_path = r"c:\jarvis AI\jarvis\scratch\intent_out.log"
err_path  = r"c:\jarvis AI\jarvis\scratch\intent_err.log"

sys.stdout = open(log_path, "w", buffering=1)
sys.stderr = open(err_path, "w", buffering=1)

sys.path.insert(0, r"c:\jarvis AI\jarvis")

async def run_tests():
    from core.orchestration.task_planner import GoalIntentEngine, TaskPlanner
    from core.orchestration.task_state import task_state_controller

    print("="*60)
    print("PHASE 36.3 INTENT & PLANNER TEST SUITE")
    print("="*60)

    engine = GoalIntentEngine()

    # Test 1: LOW risk (REAL)
    intent_low = engine.parse_goal_intent("Open Chrome and search weather")
    assert intent_low["risk_level"] == "LOW", f"Expected LOW, got {intent_low['risk_level']}"
    assert len(intent_low["forbidden_actions"]) == 0
    assert intent_low["confidence_requirement"] == 0.70
    print("GoalIntentEngine LOW risk check (REAL): PASS")

    # Test 2: HIGH risk (REAL)
    intent_high = engine.parse_goal_intent("Delete all temp log files")
    assert intent_high["risk_level"] == "HIGH", f"Expected HIGH, got {intent_high['risk_level']}"
    assert "format_disk" in intent_high["forbidden_actions"]
    assert intent_high["confidence_requirement"] == 0.85
    print("GoalIntentEngine HIGH risk check (REAL): PASS")

    # Test 3: CRITICAL risk (REAL)
    intent_critical = engine.parse_goal_intent("Secure confidential payload transfer")
    assert intent_critical["risk_level"] == "CRITICAL", f"Expected CRITICAL, got {intent_critical['risk_level']}"
    assert "upload_network" in intent_critical["forbidden_actions"]
    print("GoalIntentEngine CRITICAL risk check (REAL): PASS")

    # Test 4: Planner fallback risk propagation — mock brain so AI call is skipped (MOCK)
    # This tests that the planner properly propagates intent risk_level to fallback nodes
    planner = TaskPlanner()
    with patch("core.orchestration.task_planner.brain") as mock_brain:
        mock_brain.get_ai_response = AsyncMock(side_effect=Exception("MOCK: no AI backend"))
        plan = await planner.create_plan("Delete sandbox cache files")
    assert len(plan) > 0, "Plan should not be empty"
    for t in plan:
        assert t["risk_level"] == "HIGH", f"Expected HIGH propagation, got {t['risk_level']}"
    print("TaskPlanner DAG risk propagation (MOCK fallback path): PASS")

    # Test 5: Plan persistence (REAL)
    saved_plan = task_state_controller.load_active_plan()
    assert len(saved_plan) > 0, "Saved plan should not be empty"
    print("TaskState plan persistence check (REAL): PASS")

    # Test 6: Variable injection after planning (REAL)
    task_state_controller.set_variable("app_name", "Calculator")
    raw_node = {"objective": "Open {{app_name}} and verify"}
    subbed = task_state_controller.substitute_variables(raw_node)
    assert "Calculator" in subbed["objective"], f"Got: {subbed['objective']}"
    print("Variable injection post-planning check (REAL): PASS")

    print("="*60)
    print("ALL PHASE 36.3 TESTS COMPLETED SUCCESSFULLY (5 REAL + 1 MOCK)")
    print("="*60)

try:
    asyncio.run(run_tests())
except Exception as e:
    import traceback
    print(f"FATAL: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
finally:
    sys.stdout.flush()
    sys.stderr.flush()
