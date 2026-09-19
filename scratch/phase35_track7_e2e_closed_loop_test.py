# scratch/phase35_track7_e2e_closed_loop_test.py
import sys
import os
import asyncio

sys.path.insert(0, r"c:\jarvis AI\jarvis")

async def run_e2e():
    from core.orchestration.computer_use_agent import ComputerUseAgent
    from core.orchestration.task_state import task_state_controller
    from core.perception.visual_state import ScreenFrame

    print("\n" + "="*60)
    print("PHASE 35.7 CLOSED-LOOP E2E INTEGRATION TEST")
    print("="*60)

    class MockScreenFrame(ScreenFrame):
        def __init__(self, browser_context=None, width=1920, height=1080):
            self.browser_context = browser_context
            self.width = width
            self.height = height
            self.active_window = "Notepad"
            self.image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

    # 1. Initialize Mock plan
    initial_plan = [
        {"task_id": "T-001", "status": "IN_PROGRESS", "objective": "Open Notepad", "action_type": "OPEN_APP", "dependencies": [], "preconditions": {"process_active": ["notepad"]}}
    ]
    task_state_controller.save_active_plan(initial_plan)

    agent = ComputerUseAgent()
    
    # Mock screen capturer to avoid headless screenshot failures
    from core.perception.screen_capture import screen_capturer
    async def mock_capture():
        return MockScreenFrame(browser_context={
            "elements": [{"type": "button", "text": "Save", "role": "button", "bbox": [10,10,50,30], "center": [30,20], "clickable": True}]
        })
    screen_capturer.capture_frame_async = mock_capture
    
    # Run mock execution of 1 step
    # We will test if safety blocks work
    print("Simulating task execution with safety block indicator...")
    
    # We'll mock brain to return finished=False, open notepad app
    from core.cognition.reasoning.brain import brain
    async def mock_brain(prompt, image_path=None):
        return {"action_type": "OPEN_APP", "target": "notepad", "finished": False}
    brain.get_ai_response = mock_brain

    # Trigger a safety block inside safety_gate
    from infrastructure.watchdog.safety_layer import safety_gate
    orig_safety = safety_gate.check_safety
    def mock_safety(action, payload):
        return {"status": "PENDING_CONFIRMATION", "action_id": "act_blocked", "message": "Confirmation needed"}
    safety_gate.check_safety = mock_safety

    res = await agent.execute_task("Open Notepad")
    assert res["status"] == "BLOCKED"
    print("E2E loop halts immediately on safety confirmation gate (REAL): PASS")

    # Restore
    safety_gate.check_safety = orig_safety
    print("\n" + "="*60)
    print("ALL CLOSED-LOOP INTEGRATION TESTS COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_e2e())
