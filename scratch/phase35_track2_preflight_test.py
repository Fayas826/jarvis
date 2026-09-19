# scratch/phase35_track2_preflight_test.py
import sys
import os
import asyncio

sys.path.insert(0, r"c:\jarvis AI\jarvis")

async def test_preflight():
    from core.orchestration.action_verifier import action_verifier, ActionObservation

    obs = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=12345,
        dom_context={"elements": [{"text": "Submit Button"}]},
        ocr_text="File Edit View",
        visual_hash="abc"
    )

    # 1. Matches pass
    p1 = {"window_title_contains": ["Notepad"]}
    p2 = {"process_active": ["notepad"]}
    p3 = {"ocr_text_contains": ["View"]}
    p4 = {"dom_element_present": ["Submit"]}

    assert action_verifier.verify_pre_flight(p1, obs) == True
    assert action_verifier.verify_pre_flight(p2, obs) == True
    assert action_verifier.verify_pre_flight(p3, obs) == True
    assert action_verifier.verify_pre_flight(p4, obs) == True

    # 2. Fails reject
    p5 = {"window_title_contains": ["Chrome"]}
    assert action_verifier.verify_pre_flight(p5, obs) == False

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    asyncio.run(test_preflight())
