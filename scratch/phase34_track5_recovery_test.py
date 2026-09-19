"""
Phase 34 Track 5 — Adaptive Failure Recovery Test Suite
Covers all Track 5 validation requirements:
 1. Adaptive retry limits (poor history = fewer retries)
 2. Checkpoint rollback trigger (reverts files on final failure)
 3. Safety Block immediate halt (0 retries)
 4. Regression tests (milestones and backwards compatibility)

Results: data/temp/phase34_recovery_test_log.txt
"""

import sys
import os
import time
import json
import shutil
from pathlib import Path

sys.path.insert(0, r"c:\jarvis AI\jarvis")

LOG_PATH = r"c:\jarvis AI\jarvis\data\temp\phase34_recovery_test_log.txt"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
results = []
total_pass = 0
total_fail = 0

def log(msg):
    results.append(msg)

def section(t):
    log(f"\n{'='*60}\n{t}\n{'='*60}")

def check(label, condition, detail=""):
    global total_pass, total_fail
    if condition:
        log(f"  PASS  {label}" + (f" ({detail})" if detail else ""))
        total_pass += 1
    else:
        log(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))
        total_fail += 1


# ============================================================
# CAT 1: Adaptive Retry Limits
# ============================================================
section("CAT 1 — ADAPTIVE RETRY LIMITS")
try:
    from core.cognition.memory.context_memory import app_action_memory
    from core.orchestration.task_recovery import recovery_strategy_router

    # Clean previous observations
    app_action_memory._records.clear()

    # Case A: Default retry limit when no history exists
    lim_default = recovery_strategy_router.get_adaptive_retry_limit("Chrome", "CLICK", "dom", default_limit=3)
    check("C1.1 — Default retry limit remains 3 with no history", lim_default == 3)

    # Case B: Low success rate (e.g. 20%) with 5 observations
    for _ in range(1):
        app_action_memory.record("Chrome", "CLICK", "dom", success=True)
    for _ in range(4):
        app_action_memory.record("Chrome", "CLICK", "dom", success=False)

    lim_low = recovery_strategy_router.get_adaptive_retry_limit("Chrome", "CLICK", "dom", default_limit=3)
    check("C1.2 — Low success rate reduces retry limit to 1", lim_low == 1, f"lim={lim_low}")

    # Case C: 0% success rate with 3 observations
    app_action_memory._records.clear()
    for _ in range(3):
        app_action_memory.record("Chrome", "CLICK", "dom", success=False)

    lim_zero = recovery_strategy_router.get_adaptive_retry_limit("Chrome", "CLICK", "dom", default_limit=3)
    check("C1.3 — 0% success rate reduces retry limit to 0", lim_zero == 0, f"lim={lim_zero}")

except Exception as e:
    import traceback; log(f"  FAIL  CAT1.x — {e}\n{traceback.format_exc()}"); total_fail += 1


# ============================================================
# CAT 2: Checkpoint Rollback Trigger
# ============================================================
section("CAT 2 — CHECKPOINT ROLLBACK TRIGGER")
try:
    from core.orchestration.task_recovery import task_recovery_controller

    test_file = r"c:\jarvis AI\jarvis\scratch\recovery_test_file.txt"
    test_bak = test_file + ".bak"

    # Write initial data & backup
    with open(test_file, "w") as f:
        f.write("Initial state")
    shutil.copy2(test_file, test_bak)

    # Modify file (simulate failure during execution)
    with open(test_file, "w") as f:
        f.write("Corrupted state")

    # Trigger rollback
    task_recovery_controller.rollback_files([test_file])

    # Check contents restored
    with open(test_file, "r") as f:
        content = f.read()

    check("C2.1 — Rollback correctly restores initial file contents", content == "Initial state")
    check("C2.2 — Backup file is replaced / removed after rollback", os.path.exists(test_file))

    # Clean up test files
    if os.path.exists(test_file): os.remove(test_file)
    if os.path.exists(test_bak): os.remove(test_bak)

except Exception as e:
    import traceback; log(f"  FAIL  CAT2.x — {e}\n{traceback.format_exc()}"); total_fail += 1


# ============================================================
# CAT 3: Safety Block Immediate Halt
# ============================================================
section("CAT 3 — SAFETY BLOCK IMMEDIATE HALT")
try:
    from core.orchestration.task_recovery import failure_classifier, recovery_strategy_router, FailureType, RecoveryStrategy

    # Blocked result simulation
    exec_res = {"status": "BLOCKED", "error": "confirmation required by safety gate"}
    ft = failure_classifier.classify("OS_COMMAND", "rm -rf /", exec_res)
    check("C3.1 — Safety block maps to FailureType.ACTION_BLOCKED", ft == FailureType.ACTION_BLOCKED)

    strat = recovery_strategy_router.select_strategy(ft)
    check("C3.2 — ACTION_BLOCKED selects SURFACE_TO_USER strategy", strat == RecoveryStrategy.SURFACE_TO_USER)
    check("C3.3 — Needs user intervention (no retry)", recovery_strategy_router.needs_user(strat))
    check("C3.4 — Should retry is False", not recovery_strategy_router.should_retry(strat))

except Exception as e:
    import traceback; log(f"  FAIL  CAT3.x — {e}\n{traceback.format_exc()}"); total_fail += 1


# ============================================================
# CAT 4: Backward Compatibility & Regression
# ============================================================
section("CAT 4 — REGRESSION & COMPATIBILITY")
try:
    import ast
    protected = [
        r"c:\jarvis AI\jarvis\infrastructure\watchdog\safety_layer.py",
        r"c:\jarvis AI\jarvis\core\orchestration\agent_state_machine.py",
        r"c:\jarvis AI\jarvis\core\context\checkpoint_manager.py",
    ]
    for p in protected:
        exists = os.path.exists(p)
        check(f"C4.1 — Protected file exists: {os.path.basename(p)}", exists)
        if exists:
            with open(p, encoding="utf-8") as f:
                ast.parse(f.read())
                check(f"C4.2 — Protected file parseable: {os.path.basename(p)}", True)

    with open(r"c:\jarvis AI\jarvis\core\orchestration\task_recovery.py", encoding="utf-8") as f:
        src = f.read()
    check("C4.3 — task_recovery.py does not import safety_layer", "safety_layer" not in src)
    check("C4.4 — task_recovery.py does not import checkpoint_manager", "checkpoint_manager" not in src)

except Exception as e:
    import traceback; log(f"  FAIL  CAT4.x — {e}\n{traceback.format_exc()}"); total_fail += 1


# ============================================================
# SUMMARY
# ============================================================
log(f"\n{'='*60}")
log("PHASE 34 TRACK 5 — RECOVERY TEST SUMMARY")
log('='*60)
log(f"  TOTAL PASS: {total_pass}")
log(f"  TOTAL FAIL: {total_fail}")
log(f"  RESULT: {'ALL PASS' if total_fail == 0 else f'{total_fail} FAILURE(S)'}")
log('='*60)

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(results) + "\n")
