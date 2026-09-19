"""
Phase 35 — Unit Test Suite
Tests: 35.3 ActionConfidence | 35.1 ActionExecutor | 35.5 Recovery | 35.4 AppActionMemory

Results: data/temp/phase35_unit_test_log.txt
"""

import sys, os, time, asyncio
sys.path.insert(0, r"c:\jarvis AI\jarvis")

LOG_PATH = r"c:\jarvis AI\jarvis\data\temp\phase35_unit_test_log.txt"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
results = []
total_pass = 0
total_fail = 0

def log(msg):
    results.append(msg)

def section(title):
    log(f"\n{'=' * 60}")
    log(title)
    log('=' * 60)

def check(label, condition, detail=""):
    global total_pass, total_fail
    if condition:
        log(f"  PASS  {label}" + (f" ({detail})" if detail else ""))
        total_pass += 1
    else:
        log(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))
        total_fail += 1

# ============================================================
# 35.3 — ActionConfidence
# ============================================================
section("35.3 — ACTION CONFIDENCE MODEL")
try:
    from core.orchestration.action_confidence import (
        ActionConfidenceBuilder, ActionConfidence, RiskLevel,
        _HIGH_RISK_ACTIONS, _MEDIUM_RISK_ACTIONS, _LOW_RISK_ACTIONS
    )

    # T1: CLICK on valid coords → MEDIUM risk, PASS coords
    r = ActionConfidenceBuilder.build(
        action_type="CLICK", target="Save button",
        target_confidence=0.94, coords=[800, 400],
        screen_width=1920, screen_height=1080,
        target_source="uia", active_window="Notepad"
    )
    check("T35.3.1 — CLICK risk=MEDIUM", r.risk_level == RiskLevel.MEDIUM)
    check("T35.3.2 — coord_validity=PASS", r.coordinate_validity == "PASS")
    check("T35.3.3 — pre_validation=True (conf=0.94)", r.pre_validation_passed)
    check("T35.3.4 — verify_required=True (MEDIUM)", r.verification_required)
    check("T35.3.5 — overall_confidence near 0.94", abs(r.overall_confidence - 0.94) < 0.05, f"{r.overall_confidence:.3f}")

    # T2: OS_COMMAND → HIGH risk
    r2 = ActionConfidenceBuilder.build(
        action_type="OS_COMMAND", target="del /f C:\\test.txt",
        target_confidence=0.99, coords=None,
        screen_width=1920, screen_height=1080,
        target_source="native"
    )
    check("T35.3.6 — OS_COMMAND risk=HIGH", r2.risk_level == RiskLevel.HIGH)
    check("T35.3.7 — coord=N/A for non-click", r2.coordinate_validity == "N/A")
    check("T35.3.8 — verify_required=True (HIGH)", r2.verification_required)

    # T3: SCROLL → LOW risk, no coords needed
    r3 = ActionConfidenceBuilder.build(
        action_type="SCROLL", target="page",
        target_confidence=0.80, coords=None,
        screen_width=1920, screen_height=1080,
        target_source="dom"
    )
    check("T35.3.9 — SCROLL risk=LOW", r3.risk_level == RiskLevel.LOW)
    check("T35.3.10 — verify_required=False (LOW)", not r3.verification_required)

    # T4: CLICK with out-of-bounds coords → FAIL
    r4 = ActionConfidenceBuilder.build(
        action_type="CLICK", target="ghost button",
        target_confidence=0.90, coords=[0, 0],
        screen_width=1920, screen_height=1080,
        target_source="ocr"
    )
    check("T35.3.11 — Out-of-bounds coords → coord=FAIL", r4.coordinate_validity == "FAIL")
    check("T35.3.12 — Pre-validation fails on bad coords", not r4.pre_validation_passed)
    check("T35.3.13 — Overall conf penalised", r4.overall_confidence < 0.5, f"{r4.overall_confidence:.3f}")

    # T5: CLICK low confidence → pre_ok=False
    r5 = ActionConfidenceBuilder.build(
        action_type="CLICK", target="dim element",
        target_confidence=0.40, coords=[500, 300],
        screen_width=1920, screen_height=1080,
        target_source="vlm"
    )
    check("T35.3.14 — Low-confidence CLICK pre_ok=False", not r5.pre_validation_passed)

    # T6: is_safe_to_execute
    check("T35.3.15 — High-conf valid action is_safe=True", r.is_safe_to_execute(0.70))
    check("T35.3.16 — Failed pre-valid is_safe=False", not r4.is_safe_to_execute(0.70))

    # T7: to_dict round-trip
    d = r.to_dict()
    check("T35.3.17 — to_dict has all required fields",
          all(k in d for k in ("action_type", "target", "overall_confidence", "risk_level", "verification_required")))

    # T8: safety contract — no execute methods
    check("T35.3.18 — ActionConfidenceBuilder has no execute method",
          not hasattr(ActionConfidenceBuilder, "execute_action"))

except Exception as e:
    import traceback; log(f"  FAIL  35.3.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# 35.1 — ActionExecutor (import + pre-validation gate, no live desktop)
# ============================================================
section("35.1 — ACTION EXECUTOR (import + pre-validation logic)")
try:
    from core.orchestration.action_executor import ActionExecutor, ActionResult
    from core.orchestration.action_confidence import ActionConfidenceBuilder

    exec_ = ActionExecutor()
    check("T35.1.1 — ActionExecutor instantiable", exec_ is not None)

    # Backend resolver
    check("T35.1.2 — APP_OPEN -> native", exec_._resolve_backend("APP_OPEN") == "native")
    check("T35.1.3 — UI_AUTOMATION -> uia", exec_._resolve_backend("UI_AUTOMATION") == "uia")
    check("T35.1.4 — OS_COMMAND -> os_command", exec_._resolve_backend("OS_COMMAND") == "os_command")

    # Post-verify logic (window title check, no live desktop needed)
    class FakeFrame:
        def __init__(self, window):
            self.active_window = window

    before = FakeFrame("Notepad - test.txt")
    after_same = FakeFrame("Notepad - test.txt")
    after_changed = FakeFrame("Chrome - Google")

    ok, method = exec_._post_verify("OPEN_APP", "notepad", None, before, after_same, {"status": "SUCCESS"})
    check("T35.1.5 — OPEN_APP verify=True when window matches", ok, f"method={method}")

    ok2, m2 = exec_._post_verify("OPEN_APP", "chrome", None, before, after_changed, {"status": "SUCCESS"})
    check("T35.1.6 — OPEN_APP verify=True when Chrome window appears", ok2, f"method={m2}")

    ok3, m3 = exec_._post_verify("TYPE", "textbox", "hello", before, after_same, {"status": "SUCCESS"})
    check("T35.1.7 — TYPE verify=True when window unchanged after typing", ok3, f"method={m3}")

    # Safety contract
    check("T35.1.8 — ActionExecutor has no safety bypass",
          not any(hasattr(exec_, m) for m in ("bypass_safety", "approve_action", "override_gate")))

except Exception as e:
    import traceback; log(f"  FAIL  35.1.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# 35.5 — FailureClassifier + RecoveryStrategyRouter
# ============================================================
section("35.5 — FAILURE CLASSIFIER + RECOVERY STRATEGY ROUTER")
try:
    from core.orchestration.task_recovery import (
        FailureClassifier, RecoveryStrategyRouter,
        FailureType, RecoveryStrategy,
        task_recovery_controller
    )

    fc = FailureClassifier()
    rr = RecoveryStrategyRouter()

    # Classify: BLOCKED
    ft = fc.classify("CLICK", "Save", {"status": "BLOCKED", "message": "confirmation required"})
    check("T35.5.1 — BLOCKED status -> ACTION_BLOCKED", ft == FailureType.ACTION_BLOCKED)

    # Classify: TIMEOUT
    ft = fc.classify("CLICK", "Save", {"status": "ERROR", "error": "timed out waiting"})
    check("T35.5.2 — Timeout error -> TIMEOUT", ft == FailureType.TIMEOUT)

    # Classify: ELEMENT_GONE (window context switched)
    ft = fc.classify("CLICK", "Save", {"status": "ERROR", "error": "element not found"},
                     before_active_window="Notepad - doc.txt", after_active_window="Chrome - Google")
    check("T35.5.3 — Window changed -> ELEMENT_GONE", ft == FailureType.ELEMENT_GONE)

    # Classify: STALE_GROUNDING
    ft = fc.classify("CLICK", "btn", {"status": "ERROR", "error": "click failed"},
                     target_confidence=0.55, grounding_from_cache=True)
    check("T35.5.4 — Cache hit + low confidence -> STALE_GROUNDING", ft == FailureType.STALE_GROUNDING)

    # Classify: WRONG_TARGET (low confidence, not cached)
    ft = fc.classify("CLICK", "btn", {"status": "ERROR", "error": "wrong element"},
                     target_confidence=0.45, grounding_from_cache=False)
    check("T35.5.5 — Low confidence non-cached -> WRONG_TARGET", ft == FailureType.WRONG_TARGET)

    # Classify: BACKEND_ERROR
    ft = fc.classify("CLICK", "btn", {"status": "ERROR", "error": "pyautogui exception raised"})
    check("T35.5.6 — Driver exception -> BACKEND_ERROR", ft == FailureType.BACKEND_ERROR)

    # Strategy routing
    check("T35.5.7 — WRONG_TARGET -> REGROUND_ALT_TOOL",
          rr.select_strategy(FailureType.WRONG_TARGET) == RecoveryStrategy.REGROUND_ALT_TOOL)
    check("T35.5.8 — ELEMENT_GONE -> REGROUND_AND_RETRY",
          rr.select_strategy(FailureType.ELEMENT_GONE) == RecoveryStrategy.REGROUND_AND_RETRY)
    check("T35.5.9 — STALE_GROUNDING -> INVALIDATE_AND_REGROUND",
          rr.select_strategy(FailureType.STALE_GROUNDING) == RecoveryStrategy.INVALIDATE_AND_REGROUND)
    check("T35.5.10 — TIMEOUT -> WAIT_AND_RETRY",
          rr.select_strategy(FailureType.TIMEOUT) == RecoveryStrategy.WAIT_AND_RETRY)
    check("T35.5.11 — ACTION_BLOCKED -> SURFACE_TO_USER",
          rr.select_strategy(FailureType.ACTION_BLOCKED) == RecoveryStrategy.SURFACE_TO_USER)
    check("T35.5.12 — FATAL -> HALT",
          rr.select_strategy(FailureType.FATAL) == RecoveryStrategy.HALT)

    # should_retry / needs_user / is_halt
    check("T35.5.13 — REGROUND_AND_RETRY should_retry=True", rr.should_retry(RecoveryStrategy.REGROUND_AND_RETRY))
    check("T35.5.14 — SURFACE_TO_USER needs_user=True", rr.needs_user(RecoveryStrategy.SURFACE_TO_USER))
    check("T35.5.15 — HALT is_halt=True", rr.is_halt(RecoveryStrategy.HALT))

    # Preserved interface
    check("T35.5.16 — task_recovery_controller.attempt_recovery exists",
          hasattr(task_recovery_controller, "attempt_recovery"))
    check("T35.5.17 — task_recovery_controller.rollback_files exists",
          hasattr(task_recovery_controller, "rollback_files"))

    # describe()
    desc = fc.describe(FailureType.ELEMENT_GONE)
    check("T35.5.18 — describe() returns non-empty string", len(desc) > 10, desc[:40])

except Exception as e:
    import traceback; log(f"  FAIL  35.5.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# 35.4 — AppActionMemory
# ============================================================
section("35.4 — APP ACTION MEMORY")
try:
    from core.cognition.memory.context_memory import AppActionMemory, app_action_memory

    aam = AppActionMemory()

    # Record outcomes
    for _ in range(5):
        aam.record("Chrome", "CLICK", "dom", success=True, latency_ms=12.0)
    for _ in range(2):
        aam.record("Chrome", "CLICK", "dom", success=False, latency_ms=0.0)
    check("T35.4.1 — observation_count=7 after 7 records",
          aam.observation_count("Chrome", "CLICK", "dom") == 7)

    rate = aam.get_success_rate("Chrome", "CLICK", "dom")
    check("T35.4.2 — success_rate = 5/7 ~= 0.71",
          rate is not None and abs(rate - 5/7) < 0.01, f"{rate:.3f}")

    # get_preferred_tool: dom (5/7) vs uia (3/3)
    for _ in range(3):
        aam.record("Chrome", "CLICK", "uia", success=True, latency_ms=50.0)
    preferred = aam.get_preferred_tool("Chrome", "CLICK")
    check("T35.4.3 — UIA preferred (100% > 71%)", preferred == "uia", f"preferred={preferred}")

    # Insufficient observations → None
    aam2 = AppActionMemory()
    aam2.record("Notepad", "TYPE", "uia", success=True)
    none_rate = aam2.get_success_rate("Notepad", "TYPE", "uia")
    check("T35.4.4 — Insufficient obs returns None", none_rate is None)

    # get_app_profile
    profile = aam.get_app_profile("Chrome")
    check("T35.4.5 — get_app_profile has CLICK key", "CLICK" in profile)
    check("T35.4.6 — profile[CLICK][dom] has success_rate", "success_rate" in profile["CLICK"]["dom"])

    # Module singleton
    check("T35.4.7 — app_action_memory singleton is AppActionMemory",
          isinstance(app_action_memory, AppActionMemory))

    # Safety contract
    check("T35.4.8 — No execute/safety bypass methods on AppActionMemory",
          not any(hasattr(aam, m) for m in ("execute_action", "bypass_safety", "run_command")))

except Exception as e:
    import traceback; log(f"  FAIL  35.4.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# SAFETY CONTRACT
# ============================================================
section("SAFETY CONTRACT — All Phase 35 Modules")
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
        for method in danger:
            assert not hasattr(obj, method), f"{name} exposes '{method}'"
        check(f"SAFETY — {name}: no dangerous methods", True)

except Exception as e:
    import traceback; log(f"  FAIL  SAFETY.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# SUMMARY
# ============================================================
log(f"\n{'=' * 60}")
log("PHASE 35 UNIT TEST SUMMARY")
log('=' * 60)
log(f"  TOTAL PASS: {total_pass}")
log(f"  TOTAL FAIL: {total_fail}")
outcome = "PHASE 35 UNITS: ALL PASS" if total_fail == 0 else f"PHASE 35 UNITS: {total_fail} FAILURE(S)"
log(f"  RESULT: {outcome}")
log('=' * 60)

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(results) + "\n")
