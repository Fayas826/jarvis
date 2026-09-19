# scratch/phase35_track3_postflight_test.py
import sys
import os
import asyncio

sys.path.insert(0, r"c:\jarvis AI\jarvis")

async def run_tests():
    from core.orchestration.action_verifier import action_verifier, ActionObservation

    print("\n" + "="*60)
    print("PHASE 35.3 POST-FLIGHT VERIFICATION TEST SUITE")
    print("="*60)

    # Pre-action observation baseline
    pre_obs = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=1234,
        dom_context={"elements": []},
        ocr_text=""
    )

    # 1. Successful state transition (REAL)
    post_success = ActionObservation(
        active_window_title="Doc1 - Notepad",
        active_process_name="notepad.exe",
        active_pid=1234,
        dom_context={"elements": []},
        ocr_text="Hello World"
    )
    expected_success = {
        "window_title_contains": ["Doc1"],
        "ocr_text_contains": ["Hello"]
    }
    res = action_verifier.verify_post_flight(expected_success, pre_obs, post_success)
    assert res["status"] == "VERIFIED"
    assert res["confidence"] == 1.0
    print("Successful state transition (REAL): PASS")

    # 2. Unchanged state (REAL)
    expected_change = {
        "window_title_contains": ["Doc1"]
    }
    res_unchanged = action_verifier.verify_post_flight(expected_change, pre_obs, pre_obs)
    assert res_unchanged["status"] == "FAILED"
    assert res_unchanged["confidence"] == 0.0
    print("Unchanged state (REAL): PASS")

    # 3. Partial state transition (REAL)
    expected_partial = {
        "window_title_contains": ["Doc1"],      # fails (Untitled)
        "ocr_text_contains": ["Edit"]            # passes (contains Edit)
    }
    post_partial = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=1234,
        dom_context={"elements": []},
        ocr_text="File Edit View"
    )
    res_partial = action_verifier.verify_post_flight(expected_partial, pre_obs, post_partial)
    assert res_partial["status"] == "PARTIAL"
    assert res_partial["confidence"] == 0.5   # 0.3/0.6
    print("Partial state transition (REAL): PASS")

    # 4. Contradictory evidence (REAL)
    expected_contradict = {
        "window_title_contains": ["Untitled"],  # passes
        "ocr_text_contains": ["Doc1"]            # fails
    }
    res_contradict = action_verifier.verify_post_flight(expected_contradict, pre_obs, pre_obs)
    assert res_contradict["status"] == "PARTIAL"
    assert res_contradict["confidence"] == 0.5
    print("Contradictory evidence (REAL): PASS")

    # 5. Missing evidence (REAL)
    res_missing = action_verifier.verify_post_flight({}, pre_obs, post_success)
    assert res_missing["status"] == "UNKNOWN"
    print("Missing expected state predicates (REAL): PASS")

    # 6. OCR-only verification (REAL)
    expected_ocr = {"ocr_text_contains": ["Hello"]}
    res_ocr = action_verifier.verify_post_flight(expected_ocr, pre_obs, post_success)
    assert res_ocr["status"] == "VERIFIED"
    assert res_ocr["confidence"] == 1.0
    print("OCR-only verification (REAL): PASS")

    # 7. DOM/UIA verification (MOCK/CONTRACT)
    expected_dom = {"dom_element_present": ["Submit"]}
    post_dom = ActionObservation(
        active_window_title="Chrome",
        active_process_name="chrome.exe",
        active_pid=5555,
        dom_context={"elements": [{"text": "Submit Button"}]}
    )
    res_dom = action_verifier.verify_post_flight(expected_dom, pre_obs, post_dom)
    assert res_dom["status"] == "VERIFIED"
    print("DOM/UIA verification (MOCK/CONTRACT): PASS")

    # 8. Process-state verification (REAL)
    expected_proc = {"process_active": ["notepad"]}
    res_proc = action_verifier.verify_post_flight(expected_proc, pre_obs, pre_obs)
    assert res_proc["status"] == "VERIFIED"
    print("Process-state verification (REAL): PASS")

    # 9. Filesystem verification (REAL)
    temp_file = r"c:\jarvis AI\jarvis\scratch\verifier_fs_test.txt"
    if os.path.exists(temp_file): os.remove(temp_file)
    expected_fs = {"file_exists": [temp_file]}
    
    res_fs_fail = action_verifier.verify_post_flight(expected_fs, pre_obs, pre_obs)
    assert res_fs_fail["status"] == "FAILED"
    
    with open(temp_file, "w") as f: f.write("test")
    res_fs_pass = action_verifier.verify_post_flight(expected_fs, pre_obs, pre_obs)
    assert res_fs_pass["status"] == "VERIFIED"
    
    if os.path.exists(temp_file): os.remove(temp_file)
    print("Filesystem verification (REAL): PASS")

    # 10. Safety-block handling (REAL)
    exec_blocked = {"status": "BLOCKED", "error": "Safety block trigger"}
    res_blocked = action_verifier.verify_post_flight(expected_success, pre_obs, post_success, exec_blocked)
    assert res_blocked["status"] == "SAFETY_BLOCK"
    assert res_blocked["confidence"] == 0.0
    print("Safety-block handling (REAL): PASS")

    # 11. Confidence boundary cases (REAL)
    expected_bound = {
        "dom_element_present": ["Submit"],       # weight 0.4 - matches
        "window_title_contains": ["Doc1"]        # weight 0.3 - fails (Untitled)
    }
    # earned = 0.4, total = 0.7. confidence = 0.571 -> PARTIAL
    res_bound = action_verifier.verify_post_flight(expected_bound, pre_obs, post_dom)
    assert res_bound["status"] == "PARTIAL"
    assert res_bound["confidence"] == 0.571
    print("Confidence boundary cases (REAL): PASS")

    # 12. Backward compatibility (REAL)
    pre_result = action_verifier.verify_pre_flight({"window_title_contains": ["Notepad"]}, pre_obs)
    assert pre_result == True
    print("Backward compatibility with pre-flight check (REAL): PASS")

    print("\n" + "="*60)
    print("ALL POST-FLIGHT TESTS COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_tests())
