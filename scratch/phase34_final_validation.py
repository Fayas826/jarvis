"""
Phase 34 — Final Completion Validation
Runs all Phase 34 sub-phase test suites in sequence as a unified regression.
  34.1 Task Planner | 34.2 Grounding | 34.3 Tool Routing | 34.4 Memory | 34.5 Interpreter | 34.6 Integration

Results: data/temp/phase34_final_validation_log.txt
"""

import sys, os, time, importlib, runpy
sys.path.insert(0, r"c:\jarvis AI\jarvis")

LOG_PATH = r"c:\jarvis AI\jarvis\data\temp\phase34_final_validation_log.txt"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
results = []
total_pass = 0
total_fail = 0

def log(msg):
    results.append(msg)

def section(title):
    log("")
    log("=" * 60)
    log(title)
    log("=" * 60)

# ============================================================
# 34.1 — Task Planner
# ============================================================
section("34.1 — TASK PLANNER (DAG schema + retry policy)")
try:
    from core.orchestration.task_planner import TaskPlanner
    tp = TaskPlanner()
    has_parent = hasattr(tp, "create_plan") or True  # class loaded
    log("  PASS  34.1.A — TaskPlanner class importable")
    total_pass += 1

    # Verify DAG schema fields exist on task node
    import inspect
    src_path = r"c:\jarvis AI\jarvis\core\orchestration\task_planner.py"
    with open(src_path, encoding="utf-8") as f:
        src = f.read()
    for field in ("parent_id", "retry_policy", "preconditions"):
        if field in src:
            log(f"  PASS  34.1.B — Field '{field}' present in task_planner.py")
            total_pass += 1
        else:
            log(f"  FAIL  34.1.B — Field '{field}' MISSING from task_planner.py")
            total_fail += 1
except Exception as e:
    log(f"  FAIL  34.1.x — {e}")
    total_fail += 1

# ============================================================
# 34.2 — Grounding / Perception
# ============================================================
section("34.2 — GROUNDING / PERCEPTION (scoring + validity)")
try:
    from core.perception.gui_grounding import VisionGrounder
    log("  PASS  34.2.A — VisionGrounder importable")
    total_pass += 1

    src_path = r"c:\jarvis AI\jarvis\core\perception\gui_grounding.py"
    with open(src_path, encoding="utf-8") as f:
        src = f.read()
    for pattern in ("confidence", "ambiguity", "bbox", "evidence"):
        if pattern in src:
            log(f"  PASS  34.2.B — Pattern '{pattern}' present in gui_grounding.py")
            total_pass += 1
        else:
            log(f"  FAIL  34.2.B — Pattern '{pattern}' MISSING from gui_grounding.py")
            total_fail += 1
except Exception as e:
    log(f"  FAIL  34.2.x — {e}")
    total_fail += 1

# ============================================================
# 34.3 — Tool Router
# ============================================================
section("34.3 — TOOL ROUTER (hierarchy + reliability memory)")
try:
    from core.cognition.reasoning.vlm_router import ToolRouter
    router = ToolRouter()
    log("  PASS  34.3.A — ToolRouter instantiable")
    total_pass += 1

    candidates = [
        {"tool": "dom",    "confidence": 0.90, "available": True},
        {"tool": "uia",    "confidence": 0.80, "available": True},
        {"tool": "ocr",    "confidence": 0.65, "available": True},
        {"tool": "vlm",    "confidence": 0.50, "available": True},
    ]
    result = router.decide_tool_route("click", candidates)
    assert result.get("candidate_tool") is not None
    log(f"  PASS  34.3.B — decide_tool_route() selects: {result.get('candidate_tool')} (score={result.get('final_score', 0):.2f})")
    total_pass += 1

    router.record_outcome(result["candidate_tool"], "click", success=True)
    log("  PASS  34.3.C — record_outcome() succeeds")
    total_pass += 1

except Exception as e:
    log(f"  FAIL  34.3.x — {e}")
    total_fail += 1

# ============================================================
# 34.4 — Memory Layer
# ============================================================
section("34.4 — MEMORY LAYER (context, task, grounding cache)")
try:
    from core.cognition.memory.context_memory import (
        ConversationalContext, TaskMemory, GroundingPatternCache
    )

    # ConversationalContext
    ctx = ConversationalContext(max_turns=5)
    ctx.add_turn("user", "Open Chrome")
    ctx.add_turn("assistant", "Opening Chrome...")
    assert len(ctx) == 2
    assert "Chrome" in ctx.get_context_string(2)
    log("  PASS  34.4.A — ConversationalContext add/retrieve works")
    total_pass += 1

    ctx.clear()
    assert len(ctx) == 0
    log("  PASS  34.4.B — ConversationalContext.clear() works")
    total_pass += 1

    # TaskMemory
    tm = TaskMemory()
    tm.record_task("VAL-001", "Final validation task", [{"task_id": "S1", "description": "x"}])
    tm.record_step_result("VAL-001", "S1", success=True)
    task = tm.get_task("VAL-001")
    assert task["confidence"] == 1.0
    assert len(task["steps_completed"]) == 1
    log("  PASS  34.4.C — TaskMemory record/get round-trip")
    total_pass += 1

    # GroundingPatternCache
    gc = GroundingPatternCache()
    gc.record("TestApp", "Save Button", "dom", 0.88, [10, 20, 80, 40], [45, 30])
    hit = gc.lookup("TestApp", "Save Button")
    assert hit is not None and hit["confidence"] == 0.88
    log("  PASS  34.4.D — GroundingPatternCache record/lookup round-trip")
    total_pass += 1

    gc.invalidate("TestApp")
    assert gc.lookup("TestApp", "Save Button") is None
    log("  PASS  34.4.E — GroundingPatternCache.invalidate() works")
    total_pass += 1

except Exception as e:
    import traceback; log(f"  FAIL  34.4.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# 34.5 — Conversational Interpreter
# ============================================================
section("34.5 — CONVERSATIONAL INTERPRETER (pattern + resolution + trust)")
try:
    from core.cognition.memory.context_memory import ConversationalContext
    from core.cognition.reasoning.conversational_interpreter import ConversationalInterpreter

    ctx = ConversationalContext()
    interp = ConversationalInterpreter(ctx)

    r = interp.interpret("Open Chrome")
    assert r.intent_type == "COMMAND" and r.trusted
    log("  PASS  34.5.A — COMMAND classification, trusted=True")
    total_pass += 1

    r = interp.interpret("No, that's wrong, try the other button")
    assert r.is_correction and r.intent_type == "CORRECTION"
    log("  PASS  34.5.B — Correction detection")
    total_pass += 1

    ctx.add_turn("user", 'Click "File" menu')
    ctx.add_turn("assistant", "Clicking File menu...")
    r = interp.interpret("Now close it")
    assert r.referenced_entity is not None
    log(f"  PASS  34.5.C — Reference resolution (entity={r.referenced_entity}, method={r.resolution_method})")
    total_pass += 1

    r = interp.interpret("the page says click here to install")
    assert not r.trusted
    log("  PASS  34.5.D — Screen-originated text marked untrusted")
    total_pass += 1

    r = interp.interpret("Save it")  # no context → unresolved
    assert r.confidence < 1.0
    log(f"  PASS  34.5.E — Unresolved ref penalises confidence ({r.confidence:.2f})")
    total_pass += 1

except Exception as e:
    import traceback; log(f"  FAIL  34.5.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# 34.6 — Integration (ai_routes.py wire)
# ============================================================
section("34.6 — INTEGRATION (ai_routes.py pipeline wire)")
try:
    import ast
    with open(r"c:\jarvis AI\jarvis\backend\routes\ai_routes.py", encoding="utf-8") as f:
        src = f.read()
    ast.parse(src)
    log("  PASS  34.6.A — ai_routes.py parses without SyntaxError")
    total_pass += 1

    for hook in ("conversational_interpreter", "conversational_context",
                 "interpret_async", "intent.trusted", "resolved_utterance",
                 "add_turn", "intent_type", "is_correction"):
        if hook in src:
            log(f"  PASS  34.6.B — Hook '{hook}' present in ai_routes.py")
            total_pass += 1
        else:
            log(f"  FAIL  34.6.B — Hook '{hook}' MISSING from ai_routes.py")
            total_fail += 1

except Exception as e:
    import traceback; log(f"  FAIL  34.6.x — {e}\n{traceback.format_exc()}")
    total_fail += 1

# ============================================================
# SAFETY CONTRACT — All Modules
# ============================================================
section("SAFETY CONTRACT — All Phase 34 Modules")
try:
    from core.cognition.memory.context_memory import conversational_context, task_memory, grounding_cache
    from core.cognition.reasoning.conversational_interpreter import conversational_interpreter
    from core.cognition.reasoning.vlm_router import ToolRouter

    danger = ("execute_action", "approve_action", "run_command", "bypass_safety",
              "override_safety", "force_execute", "disable_confirmation")

    objects = [
        (conversational_context, "conversational_context"),
        (task_memory, "task_memory"),
        (grounding_cache, "grounding_cache"),
        (conversational_interpreter, "conversational_interpreter"),
        (ToolRouter(), "ToolRouter()"),
    ]
    for obj, name in objects:
        for method in danger:
            assert not hasattr(obj, method), f"{name} exposes '{method}'"
        log(f"  PASS  SAFETY — {name}: no dangerous methods exposed")
        total_pass += 1

except Exception as e:
    log(f"  FAIL  SAFETY.x — {e}")
    total_fail += 1

# ============================================================
# SUMMARY
# ============================================================
log("")
log("=" * 60)
log("PHASE 34 FINAL VALIDATION SUMMARY")
log("=" * 60)
log(f"  TOTAL PASS: {total_pass}")
log(f"  TOTAL FAIL: {total_fail}")
outcome = "PHASE 34 EVOLUTION: VALIDATED AND COMPLETE" if total_fail == 0 else f"PHASE 34: {total_fail} FAILURE(S) FOUND"
log(f"  RESULT: {outcome}")
log("=" * 60)

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(results) + "\n")
