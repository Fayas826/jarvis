import os
import sys
import asyncio

# Setup path resolution to target jarvis workspace root
sys.path.insert(0, r"c:\jarvis AI\jarvis")

# Redirect immediately
os.makedirs("data/temp", exist_ok=True)
log_file = open("data/temp/bridge_test_log.txt", "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

try:
    from core.orchestration.agent_bridge import agent_bridge

    def run_bridge_test():
        print("==================================================")
        print("🧪 JARVIS AGENT BRIDGE VERIFICATION")
        print("==================================================")

        # 1. Enqueue task
        agent_bridge.send_task(
            task_id="t_001",
            objective="Inspect notepad coordinates",
            files=["notepad.py"],
            expected_output="Success"
        )

        # 2. Retrieve task
        task = agent_bridge.get_next_task()
        assert task is not None, "Failed to retrieve next task."
        assert task["task_id"] == "t_001", "Task ID mismatch."
        print(f"✓ Retrieved task: {task['task_id']}")

        # 3. Report progress and complete
        agent_bridge.report_progress("Parsing window frames")
        agent_bridge.mark_complete()
        print("✓ Task marked as complete.")

        print("\n==================================================")
        print("🎉 AGENT BRIDGE VERIFICATION PASSED")
        print("==================================================")

    run_bridge_test()

except Exception as e:
    print(f"\n❌ RUNTIME FAIL: {e}")
    import traceback
    traceback.print_exc()
finally:
    log_file.close()
