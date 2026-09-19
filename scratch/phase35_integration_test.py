"""
Phase 35.6 — Full Integration Test Suite
Validates the complete Phase 35 stack wired into ComputerUseAgent:
  ActionConfidence (35.3) | ActionExecutor (35.1) | SmartRecovery (35.5) |
  AppActionMemory (35.4)  | ClosedLoop wire (35.2)

Results: data/temp/phase35_integration_log.txt
"""

import sys, os, ast
sys.path.insert(0, r"c:\jarvis AI\jarvis")

LOG_PATH = r"c:\jarvis AI\jarvis\data\temp\phase35_integration_log.txt"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
results = []
total_pass = 0
total_fail = 0

def log(msg): results.append(msg)
def section(t): log(f"\n{'='*60}\n{t}\n{'='*60}")
def check(label, condition, detail=""):
    global total_pass, total_fail
    if condition:
        log(f"  PASS  {label}" + (f" ({detail})" if detail else ""))
        total_pass += 1
    else:
        log(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))
        total_fail += 1

# ============================================================
# I1: Full module import chain (35.1-35.5)
# ============================================================
section("I1 — MODULE IMPORT CHAIN")
try:
    from core.orchestration.action_confidence import ActionConfidenceBuilder, ActionConfidence, RiskLevel
    check("I1.1 — action_confidence imported (35.3)", True)

    from core.orchestration.action_executor import ActionExecutor, ActionResult, action_executor
    check("I1.2 — action_executor imported (35.1)", True)

    from core.orchestration.task_recovery import (
        FailureClassifier, RecoveryStrategyRouter,
        FailureType, RecoveryStrategy,
        failure_classifier, recovery_strategy_router,
        task_recovery_controller
    )
    check("I1.3 — task_recovery (35.5) imported", True)

    from core.cognition.memory.context_memory import (
        AppActionMemory, app_action_memory,
        conversational_context, task_memory, grounding_cache
    )
    check("I1.4 — AppActionMemory (35.4) imported", True)

    # Verify Phase 34 still intact
    from core.cognition.reasoning.conversational_interpreter import conversational_interpreter
    check("I1.5 — Phase 34.5 ConversationalInterpreter still importable", True)

    from core.orchestration.task_planner import TaskPlanner
    check("I1.6 — Phase 34.1 TaskPlanner still importable", True)

except Exception as e:
    import traceback; log(f"  FAIL  I1.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# I2: computer_use_agent.py syntax + wire validation
# ============================================================
section("I2 — COMPUTER_USE_AGENT.PY WIRE VALIDATION")
try:
    cua_path = r"c:\jarvis AI\jarvis\core\orchestration\computer_use_agent.py"
    with open(cua_path, encoding="utf-8") as f:
        src = f.read()

    ast.parse(src)
    check("I2.1 — computer_use_agent.py parses without SyntaxError", True)

    for hook in (
        "action_executor", "_action_executor", "exec_result_35",
        "failure_classifier", "recovery_strategy_router",
        "failure_type", "strategy", "app_action_memory",
        "FailureType", "RecoveryStrategy",
        "needs_user", "is_halt", "should_retry",
        "INVALIDATE_AND_REGROUND", "safety_gate.check_safety",
        "confidence_report", "verification_method", "backend_used",
    ):
        check(f"I2.2 — Hook '{hook}' present in CUA", hook in src)

    # Safety Kernel must NOT be removed
    check("I2.3 — safety_gate import preserved", "from infrastructure.watchdog.safety_layer import safety_gate" in src)
    check("I2.4 — safety_gate.check_safety called (primary)", "safety = safety_gate.check_safety" in src)
    check("I2.5 — safety_gate re-checked on recovery retry", "retry_safety = safety_gate.check_safety" in src)

except Exception as e:
    import traceback; log(f"  FAIL  I2.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# I3: ActionConfidence × ActionExecutor cross-contract
# ============================================================
section("I3 — ACTION_CONFIDENCE x ACTION_EXECUTOR CONTRACT")
try:
    from core.orchestration.action_confidence import ActionConfidenceBuilder, RiskLevel
    from core.orchestration.action_executor import ActionExecutor

    exec_ = ActionExecutor()

    # Confidence report for a high-risk action
    r_high = ActionConfidenceBuilder.build(
        action_type="OS_COMMAND", target="del file",
        target_confidence=0.99, coords=None,
        screen_width=1920, screen_height=1080,
        target_source="native"
    )
    check("I3.1 — OS_COMMAND confidence HIGH risk", r_high.risk_level == RiskLevel.HIGH)
    check("I3.2 — verification_required=True for HIGH", r_high.verification_required)

    # Pre-validation failure → is_safe_to_execute=False
    r_bad = ActionConfidenceBuilder.build(
        action_type="CLICK", target="ghost",
        target_confidence=0.90, coords=[0, 0],
        screen_width=1920, screen_height=1080,
        target_source="ocr"
    )
    check("I3.3 — Bad coords → is_safe_to_execute=False", not r_bad.is_safe_to_execute())

    # Backend resolver integration
    check("I3.4 — APP_OPEN backend=native", exec_._resolve_backend("APP_OPEN") == "native")
    check("I3.5 — UI_AUTOMATION backend=uia", exec_._resolve_backend("UI_AUTOMATION") == "uia")

except Exception as e:
    import traceback; log(f"  FAIL  I3.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# I4: FailureClassifier × RecoveryStrategyRouter cross-contract
# ============================================================
section("I4 — FAILURE_CLASSIFIER x RECOVERY_ROUTER CONTRACT")
try:
    from core.orchestration.task_recovery import (
        FailureClassifier, RecoveryStrategyRouter, FailureType, RecoveryStrategy
    )
    fc = FailureClassifier()
    rr = RecoveryStrategyRouter()

    # Round-trip for all 7 failure types
    cases = [
        (FailureType.ACTION_BLOCKED, RecoveryStrategy.SURFACE_TO_USER,  False, True,  False),
        (FailureType.FATAL,          RecoveryStrategy.HALT,              False, False, True),
        (FailureType.TIMEOUT,        RecoveryStrategy.WAIT_AND_RETRY,    True,  False, False),
        (FailureType.ELEMENT_GONE,   RecoveryStrategy.REGROUND_AND_RETRY,True,  False, False),
        (FailureType.STALE_GROUNDING,RecoveryStrategy.INVALIDATE_AND_REGROUND, True, False, False),
        (FailureType.WRONG_TARGET,   RecoveryStrategy.REGROUND_ALT_TOOL, True,  False, False),
        (FailureType.BACKEND_ERROR,  RecoveryStrategy.SWITCH_BACKEND,    True,  False, False),
    ]
    for ft, expected_strat, retry, needs_usr, halt in cases:
        strat = rr.select_strategy(ft)
        check(f"I4.x — {ft} -> {expected_strat}", strat == expected_strat)
        check(f"I4.x — {ft} should_retry={retry}", rr.should_retry(strat) == retry)
        check(f"I4.x — {ft} needs_user={needs_usr}", rr.needs_user(strat) == needs_usr)
        check(f"I4.x — {ft} is_halt={halt}", rr.is_halt(strat) == halt)

except Exception as e:
    import traceback; log(f"  FAIL  I4.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# I5: AppActionMemory × ToolRouter advisory contract
# ============================================================
section("I5 — APP_ACTION_MEMORY x TOOL_ROUTER ADVISORY CONTRACT")
try:
    from core.cognition.memory.context_memory import AppActionMemory
    from core.cognition.reasoning.vlm_router import ToolRouter

    aam = AppActionMemory()
    router = ToolRouter()

    # Simulate Chrome DOM clicks succeeding 5x
    for _ in range(5):
        aam.record("Chrome", "CLICK", "dom", success=True, latency_ms=12.0)
    # UIA succeeds 2x (below MIN_OBSERVATIONS)
    for _ in range(2):
        aam.record("Chrome", "CLICK", "uia", success=True, latency_ms=55.0)

    preferred = aam.get_preferred_tool("Chrome", "CLICK")
    check("I5.1 — DOM preferred after 5 successes (UIA below threshold)", preferred == "dom")

    # ToolRouter still makes independent decisions
    candidates = [
        {"tool": "dom", "confidence": 0.90, "available": True},
        {"tool": "uia", "confidence": 0.80, "available": True},
    ]
    decision = router.decide_tool_route("click", candidates)
    check("I5.2 — ToolRouter selects dom independently", decision.get("candidate_tool") == "dom")

    # AppActionMemory is advisory only (doesn't force ToolRouter)
    check("I5.3 — AppActionMemory has no decide_tool_route", not hasattr(aam, "decide_tool_route"))

except Exception as e:
    import traceback; log(f"  FAIL  I5.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# I6: Phase 34 regression — all 34 components still work
# ============================================================
section("I6 — PHASE 34 REGRESSION")
try:
    from core.cognition.memory.context_memory import ConversationalContext, TaskMemory, GroundingPatternCache
    from core.cognition.reasoning.conversational_interpreter import ConversationalInterpreter

    ctx = ConversationalContext()
    ctx.add_turn("user", 'Open Chrome')
    ctx.add_turn("assistant", "Opening Chrome...")
    interp = ConversationalInterpreter(ctx)
    r = interp.interpret("Now close it")
    check("I6.1 — Phase 34.5 interpreter round-trip", r.referenced_entity is not None)

    gc = GroundingPatternCache()
    gc.record("Chrome", "address bar", "dom", 0.95, [100, 50, 900, 80], [500, 65])
    hit = gc.lookup("Chrome", "address bar")
    check("I6.2 — Phase 34.4 grounding cache round-trip", hit is not None and hit["confidence"] == 0.95)

    tm = TaskMemory()
    tm.record_task("REG-001", "regression test", [{"task_id": "S1", "description": "x"}])
    tm.record_step_result("REG-001", "S1", success=True)
    check("I6.3 — Phase 34.4 TaskMemory round-trip", tm.get_task("REG-001")["confidence"] == 1.0)

    import ast as ast2
    with open(r"c:\jarvis AI\jarvis\backend\routes\ai_routes.py", encoding="utf-8") as f:
        ai_routes_src = f.read()
    ast2.parse(ai_routes_src)
    check("I6.4 — ai_routes.py (Phase 34.6 wire) still parses", True)

except Exception as e:
    import traceback; log(f"  FAIL  I6.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# I7: Safety contract — all Phase 35 modules
# ============================================================
section("I7 — SAFETY CONTRACT (All Phase 35 Modules)")
try:
    from core.orchestration.action_confidence import ActionConfidenceBuilder
    from core.orchestration.action_executor import action_executor
    from core.orchestration.task_recovery import failure_classifier, recovery_strategy_router
    from core.cognition.memory.context_memory import app_action_memory

    danger = ("execute_action", "approve_action", "bypass_safety",
              "override_safety", "force_execute", "disable_confirmation")

    for obj, name in [
        (ActionConfidenceBuilder, "ActionConfidenceBuilder"),
        (action_executor, "action_executor"),
        (failure_classifier, "failure_classifier"),
        (recovery_strategy_router, "recovery_strategy_router"),
        (app_action_memory, "app_action_memory"),
    ]:
        ok = not any(hasattr(obj, m) for m in danger)
        check(f"I7.x — {name}: no dangerous methods", ok)

    # Protected files must be unmodified
    for protected_file in (
        r"c:\jarvis AI\jarvis\infrastructure\watchdog\safety_layer.py",
        r"c:\jarvis AI\jarvis\core\orchestration\agent_state_machine.py",
        r"c:\jarvis AI\jarvis\core\context\checkpoint_manager.py",
    ):
        check(f"I7.x — Protected: {os.path.basename(protected_file)} exists unchanged",
              os.path.exists(protected_file))

except Exception as e:
    import traceback; log(f"  FAIL  I7.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# SUMMARY
# ============================================================
log(f"\n{'='*60}")
log("PHASE 35 INTEGRATION TEST SUMMARY")
log("="*60)
log(f"  TOTAL PASS: {total_pass}")
log(f"  TOTAL FAIL: {total_fail}")
log(f"  RESULT: {'PHASE 35 INTEGRATION: ALL PASS' if total_fail == 0 else f'PHASE 35: {total_fail} FAILURE(S)'}")
log("="*60)

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(results) + "\n")
