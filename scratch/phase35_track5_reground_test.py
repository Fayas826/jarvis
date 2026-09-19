# scratch/phase35_track5_reground_test.py
import sys
import os
import asyncio

sys.path.insert(0, r"c:\jarvis AI\jarvis")

async def run_tests():
    from core.perception.gui_grounding import action_regrounder, GUIElement, ScreenFrame, vision_grounder

    print("\n" + "="*60)
    print("PHASE 35.5 AUTONOMOUS RE-GROUNDING TEST SUITE")
    print("="*60)

    class MockScreenFrame(ScreenFrame):
        def __init__(self, browser_context=None, width=1920, height=1080):
            self.browser_context = browser_context
            self.width = width
            self.height = height
            self.active_window = "Notepad"
            self.image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

    # Base elements
    orig_el = GUIElement("dom_0", "button", "Save", "button", [10,10,50,30], [30,20], 1.0, True, "dom")
    screen_unchanged = MockScreenFrame(browser_context={
        "elements": [{"type": "button", "text": "Save", "role": "button", "bbox": [10,10,50,30], "center": [30,20], "clickable": True}]
    })

    # 1. Unchanged target (NO_REGROUND_REQUIRED) (REAL)
    action_regrounder._history_centers.clear()
    res = await action_regrounder.attempt_reground("Save", screen_unchanged, orig_el, delta_metadata={})
    assert res["status"] == "NO_REGROUND_REQUIRED"
    print("Unchanged target (REAL): PASS")

    # 2. Window title change (REGROUND_SUCCESS) (REAL)
    action_regrounder._history_centers.clear()
    screen_win = MockScreenFrame(browser_context={
        "elements": [{"type": "button", "text": "Save", "role": "button", "bbox": [10,10,50,30], "center": [30,20], "clickable": True}]
    })
    res_win = await action_regrounder.attempt_reground(
        "Save", screen_win, orig_el, 
        delta_metadata={"win_title_changed": True}
    )
    assert res_win["status"] == "REGROUND_SUCCESS"
    assert res_win["element"].center == [30, 20]
    print("Window title change (REAL): PASS")

    # 3. Target moved (REGROUND_SUCCESS) (REAL)
    action_regrounder._history_centers.clear()
    screen_moved = MockScreenFrame(browser_context={
        "elements": [{"type": "button", "text": "Save", "role": "button", "bbox": [100,100,150,130], "center": [125,115], "clickable": True}]
    })
    res_moved = await action_regrounder.attempt_reground(
        "Save", screen_moved, orig_el, 
        delta_metadata={"ocr_similarity": 0.5}
    )
    assert res_moved["status"] == "REGROUND_SUCCESS"
    assert res_moved["element"].center == [125, 115]
    print("Target moved (REAL): PASS")

    # 4. DOM mutation (REGROUND_SUCCESS) (REAL)
    action_regrounder._history_centers.clear()
    screen_dom = MockScreenFrame(browser_context={
        "elements": [{"type": "button", "text": "Save", "role": "button", "bbox": [10,10,50,30], "center": [30,20], "clickable": True}]
    })
    res_dom = await action_regrounder.attempt_reground(
        "Save", screen_dom, orig_el, 
        delta_metadata={"added_dom_count": 1}
    )
    assert res_dom["status"] == "REGROUND_SUCCESS"
    print("DOM mutation (REAL): PASS")

    # 5. Safety/security rejection (SAFETY_BLOCK) (REAL)
    res_safety = await action_regrounder.attempt_reground(
        "Save", screen_unchanged, orig_el, 
        action_execution_result={"status": "BLOCKED"}
    )
    assert res_safety["status"] == "SAFETY_BLOCK"
    print("Safety/security rejection (REAL): PASS")

    # 6. Oscillation prevention (REGROUND_AMBIGUOUS) (REAL)
    reground_osc = action_regrounder.__class__(max_attempts=3)
    # Mock find_target returning same center twice to trigger ambiguous
    orig_find = vision_grounder.find_target
    async def mock_find(sc, inst):
        return GUIElement("dom_x", "button", "Save", "button", [10,10,50,30], [30,20], 1.0, True, "dom")
    vision_grounder.find_target = mock_find

    # Trigger first reground (stores center)
    res_o1 = await reground_osc.attempt_reground("Save", screen_unchanged, orig_el, delta_metadata={"win_title_changed": True})
    assert res_o1["status"] == "REGROUND_SUCCESS"

    # Trigger second reground with same mock (should hit oscillation blocker)
    res_o2 = await reground_osc.attempt_reground("Save", screen_unchanged, orig_el, delta_metadata={"win_title_changed": True})
    assert res_o2["status"] == "REGROUND_AMBIGUOUS"
    print("Oscillation prevention (REAL): PASS")

    # Restore grounder find_target
    vision_grounder.find_target = orig_find

    # 7. Maximum attempts exhaustion (REGROUND_FAILED) (REAL)
    reground_fail = action_regrounder.__class__(max_attempts=2)
    async def mock_find_none(sc, inst):
        return None
    vision_grounder.find_target = mock_find_none

    res_fail = await reground_fail.attempt_reground("Save", screen_unchanged, orig_el, delta_metadata={"win_title_changed": True})
    assert res_fail["status"] == "REGROUND_FAILED"
    print("Maximum attempts exhaustion (REAL): PASS")

    # Restore
    vision_grounder.find_target = orig_find

    # 8. Backward compatibility (REAL)
    res_back = await vision_grounder.ground_target(screen_unchanged, "Save")
    assert res_back == [30, 20]
    print("Backward compatibility (REAL): PASS")

    print("\n" + "="*60)
    print("ALL RE-GROUNDING TESTS COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_tests())
