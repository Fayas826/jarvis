"""
Phase 34.4 — Memory Layer Acceptance Test
Exercises ConversationalContext, TaskMemory, and GroundingPatternCache.

Run via:
  pythonw.exe phase34_memory_test.py
Results written to: data/temp/phase34_memory_test_log.txt
"""

import sys
import time
import os

LOG_PATH = r"c:\jarvis AI\jarvis\data\temp\phase34_memory_test_log.txt"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

results = []

def log(msg):
    results.append(msg)

def run_tests():
    sys.path.insert(0, r"c:\jarvis AI\jarvis")

    log("=" * 60)
    log("PHASE 34.4 — MEMORY LAYER ACCEPTANCE TEST")
    log("=" * 60)

    # ----------------------------------------------------------------
    # 1. ConversationalContext
    # ----------------------------------------------------------------
    log("\n[TEST GROUP 1] ConversationalContext")
    try:
        from core.cognition.memory.context_memory import ConversationalContext
        ctx = ConversationalContext(max_turns=5)

        ctx.add_turn("user", "Open the calculator")
        ctx.add_turn("assistant", "Opening Calculator...")
        ctx.add_turn("user", "Now type 27 + 15")
        ctx.add_turn("assistant", "Entering expression...")
        ctx.add_turn("user", "Save the result")

        turns = ctx.get_recent(3)
        assert len(turns) == 3, f"Expected 3 turns, got {len(turns)}"
        assert turns[-1]["content"] == "Save the result"
        log("  PASS  T1.1 — get_recent(3) returns last 3 turns")

        ctx_str = ctx.get_context_string(2)
        assert "Save the result" in ctx_str
        log("  PASS  T1.2 — get_context_string() contains most recent content")

        ctx.add_turn("user", "And open Notepad too")
        assert len(ctx) == 5, f"Window should cap at 5, got {len(ctx)}"
        log("  PASS  T1.3 — Sliding window caps at max_turns=5")

        ctx.clear()
        assert len(ctx) == 0
        log("  PASS  T1.4 — clear() empties buffer")

    except Exception as e:
        log(f"  FAIL  T1.x — ConversationalContext error: {e}")
        import traceback; log(traceback.format_exc())

    # ----------------------------------------------------------------
    # 2. TaskMemory
    # ----------------------------------------------------------------
    log("\n[TEST GROUP 2] TaskMemory")
    try:
        from core.cognition.memory.context_memory import TaskMemory
        tm = TaskMemory()

        plan = [{"task_id": "S1", "description": "Open app"}, {"task_id": "S2", "description": "Click button"}]
        tm.record_task("TASK-001", "Open calculator and compute 27+15", plan)

        task = tm.get_task("TASK-001")
        assert task is not None
        assert task["objective"].startswith("Open calculator")
        log("  PASS  T2.1 — record_task + get_task round-trip")

        tm.record_step_result("TASK-001", "S1", success=True, output="Calculator opened")
        task = tm.get_task("TASK-001")
        assert len(task["steps_completed"]) == 1
        log("  PASS  T2.2 — record_step_result (success) updates steps_completed")

        initial_confidence = task["confidence"]
        tm.record_step_result("TASK-001", "S2", success=False, failure_reason="Target not found")
        task = tm.get_task("TASK-001")
        assert task["confidence"] < initial_confidence
        log(f"  PASS  T2.3 — Failure decays confidence ({initial_confidence:.2f} -> {task['confidence']:.2f})")

        tm.record_output("TASK-001", "calc_result", "42")
        task = tm.get_task("TASK-001")
        assert task["outputs"]["calc_result"] == "42"
        log("  PASS  T2.4 — record_output stores named output value")

        tm.complete_task("TASK-001", status="COMPLETED")
        task = tm.get_task("TASK-001")
        assert task["status"] == "COMPLETED"
        log("  PASS  T2.5 — complete_task sets status correctly")

        assert tm.active_count() == 1
        log("  PASS  T2.6 — active_count() returns 1")

        # TTL expiry simulation
        tm2 = TaskMemory()
        tm2.TASK_TTL_SECONDS = 0  # force immediate expiry
        tm2.record_task("TASK-999", "Expire me", [])
        time.sleep(0.01)
        result = tm2.get_task("TASK-999")
        assert result is None, "Expired task should be None"
        log("  PASS  T2.7 — TTL expiry removes stale tasks")

    except Exception as e:
        log(f"  FAIL  T2.x — TaskMemory error: {e}")
        import traceback; log(traceback.format_exc())

    # ----------------------------------------------------------------
    # 3. GroundingPatternCache
    # ----------------------------------------------------------------
    log("\n[TEST GROUP 3] GroundingPatternCache")
    try:
        from core.cognition.memory.context_memory import GroundingPatternCache
        gc = GroundingPatternCache()

        # Record a successful grounding
        gc.record("Calculator", "equals button", "dom", 0.95, [100, 200, 150, 220], [125, 210])
        entry = gc.lookup("Calculator", "equals button")
        assert entry is not None
        assert entry["element_source"] == "dom"
        log("  PASS  T3.1 — record + lookup round-trip")

        # Low confidence not cached
        gc.record("Calculator", "dim ghost button", "ocr", 0.45, [0, 0, 0, 0], [0, 0])
        assert gc.lookup("Calculator", "dim ghost button") is None
        log("  PASS  T3.2 — Low-confidence entry (< 0.60) not cached")

        # Expiry
        gc2 = GroundingPatternCache()
        gc2.CACHE_TTL_SECONDS = 0
        gc2.record("Notepad", "save button", "uia", 0.90, [50, 50, 100, 70], [75, 60])
        time.sleep(0.01)
        assert gc2.lookup("Notepad", "save button") is None
        log("  PASS  T3.3 — Expired cache entry returns None")

        # Invalidation on navigation
        gc.record("Browser", "search box", "dom", 0.92, [0, 0, 200, 40], [100, 20])
        gc.record("Browser", "submit button", "dom", 0.88, [200, 0, 280, 40], [240, 20])
        gc.invalidate("Browser")
        assert gc.lookup("Browser", "search box") is None
        assert gc.lookup("Browser", "submit button") is None
        log("  PASS  T3.4 — invalidate() clears all entries for app")

        assert gc.cache_size() == 1  # Only Calculator entry remains
        log(f"  PASS  T3.5 — cache_size() = {gc.cache_size()} (expected 1)")

    except Exception as e:
        log(f"  FAIL  T3.x — GroundingPatternCache error: {e}")
        import traceback; log(traceback.format_exc())

    # ----------------------------------------------------------------
    # 4. Safety Contract
    # ----------------------------------------------------------------
    log("\n[TEST GROUP 4] Safety Contract Verification")
    try:
        from core.cognition.memory.context_memory import (
            conversational_context, task_memory, grounding_cache
        )
        # Verify none of these have execute/action methods
        for obj, name in [(conversational_context, "conversational_context"),
                          (task_memory, "task_memory"),
                          (grounding_cache, "grounding_cache")]:
            has_exec = hasattr(obj, "execute_action") or hasattr(obj, "approve_action") or hasattr(obj, "run_command")
            assert not has_exec, f"{name} must not have action execution methods!"
        log("  PASS  T4.1 — None of the memory objects expose action execution methods")
    except Exception as e:
        log(f"  FAIL  T4.x — Safety contract error: {e}")

    log("\n" + "=" * 60)
    log("PHASE 34.4 MEMORY TESTS COMPLETE")
    log("=" * 60)

run_tests()

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(results) + "\n")
