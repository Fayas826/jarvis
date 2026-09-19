# scratch/phase35_track6_replanning_test.py
import sys
import os
import asyncio

sys.path.insert(0, r"c:\jarvis AI\jarvis")

async def run_tests():
    from core.orchestration.plan_repair import plan_repair_controller, PlanRepairController

    print("\n" + "="*60)
    print("PHASE 35.6 DYNAMIC DAG REPLANNING TEST SUITE")
    print("="*60)

    # Base Active Plan DAG
    base_plan = [
        {"task_id": "T-001", "status": "SUCCESS", "objective": "Open Editor", "action_type": "OPEN_APP", "dependencies": []},
        {"task_id": "T-002", "status": "PENDING", "objective": "Type Hello", "action_type": "CLICK", "dependencies": ["T-001"]},
        {"task_id": "T-003", "status": "PENDING", "objective": "Save File", "action_type": "CLICK", "dependencies": ["T-002"]}
    ]

    # 1. Safety-block hard stop (SAFETY_STOP) (REAL)
    v_safety = {"status": "SAFETY_BLOCK"}
    res_safety = plan_repair_controller.repair_plan(base_plan, "T-002", v_safety)
    assert res_safety["status"] == "SAFETY_STOP"
    assert len(res_safety["record"]["inserted_nodes"]) == 0
    print("Safety-block hard stop (REAL): PASS")

    # 2. Prerequisite insertion (REPAIRED) (REAL)
    # Triggered by PARTIAL verification
    v_partial = {"status": "PARTIAL"}
    plan_repair_controller._repair_history.clear() # clear count
    res_prereq = plan_repair_controller.repair_plan(base_plan, "T-002", v_partial)
    assert res_prereq["status"] == "REPAIRED"
    assert res_prereq["record"]["repair_strategy"] == "INSERT_PREREQ"
    # Verify completed node preserved
    assert res_prereq["repaired_plan"][0]["status"] == "SUCCESS"
    # Verify prerequisite node inserted before T-002
    assert res_prereq["repaired_plan"][1]["task_id"] == "T-002-PREREQ"
    print("Prerequisite insertion & completed tasks preservation (REAL): PASS")

    # 3. Alternative-tool substitution (REPAIRED) (REAL)
    # Triggered by FAILED verification
    v_fail = {"status": "FAILED"}
    plan_repair_controller._repair_history.clear()
    res_sub = plan_repair_controller.repair_plan(base_plan, "T-002", v_fail)
    assert res_sub["status"] == "REPAIRED"
    assert res_sub["record"]["repair_strategy"] == "SUBSTITUTE_TOOL"
    assert res_sub["repaired_plan"][1]["retry_policy"]["strategy"] == "alternate_driver"
    print("Alternative-tool substitution (REAL): PASS")

    # 4. Downstream branch reconstruction (REPAIRED) (REAL)
    # Triggered by NO_CHANGE / UNKNOWN verification
    v_unk = {"status": "UNKNOWN"}
    plan_repair_controller._repair_history.clear()
    res_recon = plan_repair_controller.repair_plan(base_plan, "T-002", v_unk)
    assert res_recon["status"] == "REPAIRED"
    assert res_recon["record"]["repair_strategy"] == "REBUILD_DOWNSTREAM"
    # Verify T-003 is removed, replaced by T-002-RECON downstream
    task_ids = [t["task_id"] for t in res_recon["repaired_plan"]]
    assert "T-003" not in task_ids
    assert "T-002-RECON" in task_ids
    print("Downstream branch reconstruction (REAL): PASS")

    # 5. Repeated failure / Repair budget exhaustion (UNREPAIRABLE) (REAL)
    replan_limit = PlanRepairController(max_repairs=2)
    # Trigger 1st repair
    r1 = replan_limit.repair_plan(base_plan, "T-002", v_fail)
    assert r1["status"] == "REPAIRED"
    # Trigger 2nd repair
    r2 = replan_limit.repair_plan(r1["repaired_plan"], "T-002", v_fail)
    assert r2["status"] == "REPAIRED"
    # Trigger 3rd repair (should exceed budget of 2)
    r3 = replan_limit.repair_plan(r2["repaired_plan"], "T-002", v_fail)
    assert r3["status"] == "UNREPAIRABLE"
    print("Repair budget exhaustion (REAL): PASS")

    # 6. Oscillation prevention (UNREPAIRABLE) (REAL)
    replan_osc = PlanRepairController(max_repairs=3)
    # Trigger 1st partial repair (INSERT_PREREQ)
    o1 = replan_osc.repair_plan(base_plan, "T-002", v_partial)
    assert o1["status"] == "REPAIRED"
    # Trigger 2nd partial repair (should fail due to strategy oscillation on INSERT_PREREQ)
    o2 = replan_osc.repair_plan(o1["repaired_plan"], "T-002", v_partial)
    assert o2["status"] == "UNREPAIRABLE"
    assert "oscillation" in o2["record"]["detail"]
    print("Oscillation prevention (REAL): PASS")

    print("\n" + "="*60)
    print("ALL DYNAMIC REPLANNING TESTS COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_tests())
