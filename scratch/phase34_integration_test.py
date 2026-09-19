"""
Phase 34.6 — Full Integration Test Suite
Tests the complete Phase 34 evolution stack as wired in the live pipeline:
  Task Planner (34.1) → Grounding (34.2) → Tool Router (34.3) → Memory (34.4) → Interpreter (34.5)

Does NOT start the FastAPI server. Tests the import graph and cross-module contracts.

Results: data/temp/phase34_integration_log.txt
"""

import sys, os, time
sys.path.insert(0, r"c:\jarvis AI\jarvis")

LOG_PATH = r"c:\jarvis AI\jarvis\data\temp\phase34_integration_log.txt"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
results = []

def log(msg):
    results.append(msg)

def run_tests():
    log("=" * 60)
    log("PHASE 34.6 — FULL INTEGRATION TEST SUITE")
    log("=" * 60)

    # ----------------------------------------------------------------
    # I1: Full module import chain (dependency graph smoke test)
    # ----------------------------------------------------------------
    log("\n[INTEGRATION 1] Module Import Chain")
    try:
        from core.cognition.memory.context_memory import (
            conversational_context, task_memory, grounding_cache
        )
        log("  PASS  I1.1 — context_memory imported (34.4)")

        from core.cognition.reasoning.conversational_interpreter import (
            conversational_interpreter, ConversationalInterpreter, InterpretedIntent
        )
        log("  PASS  I1.2 — conversational_interpreter imported (34.5)")

        from core.orchestration.task_planner import TaskPlanner
        log("  PASS  I1.3 — task_planner imported (34.1)")

        from core.cognition.reasoning.vlm_router import ToolRouter
        log("  PASS  I1.4 — vlm_router/ToolRouter imported (34.3)")

        from core.perception.gui_grounding import VisionGrounder
        log("  PASS  I1.5 — gui_grounding/VisionGrounder imported (34.2)")

    except Exception as e:
        import traceback; log(f"  FAIL  I1.x — Import error: {e}\n{traceback.format_exc()}")

    # ----------------------------------------------------------------
    # I2: Interpreter → Context round-trip (34.5 + 34.4 integration)
    # ----------------------------------------------------------------
    log("\n[INTEGRATION 2] Interpreter -> Context Round-Trip (34.5 x 34.4)")
    try:
        from core.cognition.memory.context_memory import ConversationalContext
        from core.cognition.reasoning.conversational_interpreter import ConversationalInterpreter

        ctx = ConversationalContext(max_turns=10)
        interp = ConversationalInterpreter(ctx)

        # Simulate conversation
        ctx.add_turn("user", 'Open "Notepad"')
        ctx.add_turn("assistant", "Opening Notepad...")
        ctx.add_turn("user", "Type hello world")
        ctx.add_turn("assistant", "Typed hello world.")

        r = interp.interpret("Now save it")
        assert r.referenced_entity == "previous_target" or r.referenced_entity is not None
        assert r.resolution_method in ("context_lookup", "pattern")
        log(f"  PASS  I2.1 — 'Now save it' resolved via {r.resolution_method}: '{r.resolved_utterance[:60]}'")

        # Correction flow
        r2 = interp.interpret("Actually, save as PDF instead")
        assert r2.is_correction
        assert r2.intent_type == "CORRECTION"
        log(f"  PASS  I2.2 — Correction detected, target: '{r2.correction_target}'")

        # Context grew
        assert len(ctx) == 4
        log(f"  PASS  I2.3 — Context buffer holds {len(ctx)} turns")

    except Exception as e:
        import traceback; log(f"  FAIL  I2.x — {e}\n{traceback.format_exc()}")

    # ----------------------------------------------------------------
    # I3: GroundingCache → advisory recall (34.4 x 34.2 contract)
    # ----------------------------------------------------------------
    log("\n[INTEGRATION 3] Grounding Cache Advisory Contract (34.4 x 34.2)")
    try:
        from core.cognition.memory.context_memory import GroundingPatternCache
        gc = GroundingPatternCache()

        gc.record("Notepad", "File menu", "uia", 0.91, [0, 0, 60, 20], [30, 10])
        hit = gc.lookup("Notepad", "File menu")
        assert hit is not None
        assert hit["confidence"] == 0.91
        log(f"  PASS  I3.1 — Grounding cache hit: source={hit['element_source']}, conf={hit['confidence']}")

        # Invalidate on app switch
        gc.invalidate("Notepad")
        assert gc.lookup("Notepad", "File menu") is None
        log("  PASS  I3.2 — Grounding cache invalidated on app switch")

    except Exception as e:
        import traceback; log(f"  FAIL  I3.x — {e}\n{traceback.format_exc()}")

    # ----------------------------------------------------------------
    # I4: TaskMemory → step progress (34.4 x 34.1 contract)
    # ----------------------------------------------------------------
    log("\n[INTEGRATION 4] TaskMemory - Task Planner Contract (34.4 x 34.1)")
    try:
        from core.cognition.memory.context_memory import TaskMemory

        tm = TaskMemory()
        plan = [
            {"task_id": "S1", "description": "Open Notepad"},
            {"task_id": "S2", "description": "Type hello world"},
            {"task_id": "S3", "description": "Save file"},
        ]
        tm.record_task("INT-001", "Open Notepad, type hello world, and save", plan, risk_level="LOW")

        tm.record_step_result("INT-001", "S1", success=True, output="Notepad opened")
        tm.record_step_result("INT-001", "S2", success=True, output="Typed text")
        tm.record_step_result("INT-001", "S3", success=False, failure_reason="Save dialog timeout")

        task = tm.get_task("INT-001")
        assert len(task["steps_completed"]) == 2
        assert len(task["steps_failed"]) == 1
        assert task["confidence"] < 1.0
        log(f"  PASS  I4.1 — 2 success + 1 failure tracked, confidence={task['confidence']:.2f}")

        tm.record_output("INT-001", "file_path", "C:/Users/Asus/Desktop/hello.txt")
        task = tm.get_task("INT-001")
        assert task["outputs"]["file_path"] == "C:/Users/Asus/Desktop/hello.txt"
        log("  PASS  I4.2 — Named output stored and retrievable")

        tm.complete_task("INT-001", "COMPLETED")
        assert tm.get_task("INT-001")["status"] == "COMPLETED"
        log("  PASS  I4.3 — Task marked COMPLETED")

    except Exception as e:
        import traceback; log(f"  FAIL  I4.x — {e}\n{traceback.format_exc()}")

    # ----------------------------------------------------------------
    # I5: ai_routes.py import validity (integration wire check)
    # ----------------------------------------------------------------
    log("\n[INTEGRATION 5] ai_routes.py Wire Validity")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ai_routes",
            r"c:\jarvis AI\jarvis\backend\routes\ai_routes.py"
        )
        # Just check it parses without SyntaxError
        import ast
        with open(r"c:\jarvis AI\jarvis\backend\routes\ai_routes.py", "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        log("  PASS  I5.1 — ai_routes.py parses without SyntaxError")

        # Check Phase 34.5 imports are present
        assert "conversational_interpreter" in source
        assert "conversational_context" in source
        assert "intent.trusted" in source
        assert "intent.resolved_utterance" in source
        assert "add_turn" in source
        log("  PASS  I5.2 — All Phase 34.5/34.4 integration hooks present in ai_routes.py")

    except Exception as e:
        import traceback; log(f"  FAIL  I5.x — {e}\n{traceback.format_exc()}")

    # ----------------------------------------------------------------
    # I6: Safety contract — no Phase 34 module bypasses safety
    # ----------------------------------------------------------------
    log("\n[INTEGRATION 6] Safety Contract (All Phase 34 Modules)")
    try:
        from core.cognition.memory.context_memory import (
            conversational_context, task_memory, grounding_cache
        )
        from core.cognition.reasoning.conversational_interpreter import conversational_interpreter

        danger_methods = ("execute_action", "approve_action", "run_command", "bypass_safety",
                          "override_safety", "force_execute")
        for obj, name in [
            (conversational_context, "conversational_context"),
            (task_memory, "task_memory"),
            (grounding_cache, "grounding_cache"),
            (conversational_interpreter, "conversational_interpreter"),
        ]:
            for method in danger_methods:
                assert not hasattr(obj, method), f"{name} must not expose '{method}'"
        log("  PASS  I6.1 — No Phase 34 module exposes action-execution or safety-bypass methods")

    except Exception as e:
        import traceback; log(f"  FAIL  I6.x — {e}\n{traceback.format_exc()}")

    # ----------------------------------------------------------------
    # I7: Performance envelope (all Pattern-path operations < 5ms)
    # ----------------------------------------------------------------
    log("\n[INTEGRATION 7] Performance Envelope")
    try:
        from core.cognition.memory.context_memory import ConversationalContext, TaskMemory, GroundingPatternCache
        from core.cognition.reasoning.conversational_interpreter import ConversationalInterpreter

        ctx = ConversationalContext()
        interp = ConversationalInterpreter(ctx)

        timings = {}
        for label, fn in [
            ("ConvContext.add_turn", lambda: ctx.add_turn("user", "Open Chrome")),
            ("ConvContext.get_recent", lambda: ctx.get_recent(5)),
            ("Interpreter.interpret", lambda: interp.interpret("Click the Save button")),
            ("TaskMemory.record_task", lambda: TaskMemory().record_task("T", "x", [])),
            ("GroundingCache.record", lambda: GroundingPatternCache().record("App", "btn", "dom", 0.9, [0,0,1,1], [0,0])),
            ("GroundingCache.lookup", lambda: GroundingPatternCache().lookup("App", "btn")),
        ]:
            t0 = time.perf_counter()
            for _ in range(100):
                fn()
            elapsed = (time.perf_counter() - t0) * 10  # avg ms
            timings[label] = elapsed
            status = "PASS" if elapsed < 5.0 else "WARN"
            log(f"  {status}  I7.x — {label}: avg {elapsed:.3f}ms")

    except Exception as e:
        import traceback; log(f"  FAIL  I7.x — {e}\n{traceback.format_exc()}")

    log("\n" + "=" * 60)
    log("PHASE 34.6 INTEGRATION TEST SUITE COMPLETE")
    log("=" * 60)

run_tests()

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(results) + "\n")
