# scratch/phase35_track4_delta_test.py
import sys
import os
import asyncio

sys.path.insert(0, r"c:\jarvis AI\jarvis")

async def run_tests():
    from core.orchestration.action_verifier import ActionObservation, action_delta_classifier, action_verifier

    print("\n" + "="*60)
    print("PHASE 35.4 DELTA CLASSIFIER TEST SUITE")
    print("="*60)

    # Base observations
    pre_obs = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=1001,
        dom_context={"elements": [{"text": "File Menu"}]},
        uia_context=[{"id": "uia_file"}],
        ocr_text="File Edit",
        visual_hash="hash1"
    )

    # 1. Identical frames (NO_CHANGE) (REAL)
    res = action_delta_classifier.classify_delta(pre_obs, pre_obs)
    assert res["category"] == "NO_CHANGE"
    assert res["score"] == 0.0
    print("Identical frames (REAL): PASS")

    # 2. Added DOM node (MINOR_CHANGE) (MOCK/CONTRACT)
    post_added_dom = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=1001,
        dom_context={"elements": [{"text": "File Menu"}, {"text": "Save Button"}]},
        uia_context=[{"id": "uia_file"}],
        ocr_text="File Edit",
        visual_hash="hash1"
    )
    res_dom = action_delta_classifier.classify_delta(pre_obs, post_added_dom)
    assert res_dom["category"] == "MINOR_CHANGE"
    assert res_dom["changed_metadata"]["added_dom_count"] == 1
    print("Added DOM node (MOCK/CONTRACT): PASS")

    # 3. Removed DOM node (MINOR_CHANGE) (MOCK/CONTRACT)
    post_removed_dom = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=1001,
        dom_context={"elements": []},
        uia_context=[{"id": "uia_file"}],
        ocr_text="File Edit",
        visual_hash="hash1"
    )
    res_rem_dom = action_delta_classifier.classify_delta(pre_obs, post_removed_dom)
    assert res_rem_dom["category"] == "MINOR_CHANGE"
    assert res_rem_dom["changed_metadata"]["removed_dom_count"] == 1
    print("Removed DOM node (MOCK/CONTRACT): PASS")

    # 4. UIA control mutation (MINOR_CHANGE) (MOCK/CONTRACT)
    post_uia = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=1001,
        dom_context={"elements": [{"text": "File Menu"}]},
        uia_context=[{"id": "uia_file"}, {"id": "uia_save"}],
        ocr_text="File Edit",
        visual_hash="hash1"
    )
    res_uia = action_delta_classifier.classify_delta(pre_obs, post_uia)
    assert res_uia["category"] == "MINOR_CHANGE"
    assert res_uia["changed_metadata"]["added_uia_count"] == 1
    print("UIA control mutation (MOCK/CONTRACT): PASS")

    # 5. OCR text addition/removal (MINOR_CHANGE) (REAL)
    post_ocr = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=1001,
        dom_context={"elements": [{"text": "File Menu"}]},
        uia_context=[{"id": "uia_file"}],
        ocr_text="File Edit Save As",
        visual_hash="hash1"
    )
    res_ocr = action_delta_classifier.classify_delta(pre_obs, post_ocr)
    assert res_ocr["category"] == "MINOR_CHANGE"
    print("OCR text addition/removal (REAL): PASS")

    # 6. OCR minor recognition noise (NO_CHANGE) (REAL)
    post_ocr_noise = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=1001,
        dom_context={"elements": [{"text": "File Menu"}]},
        uia_context=[{"id": "uia_file"}],
        ocr_text="File Edit", # same text, noise ignored
        visual_hash="hash2" # visual mismatch but no structural change
    )
    res_noise = action_delta_classifier.classify_delta(pre_obs, post_ocr_noise)
    assert res_noise["category"] == "NO_CHANGE"
    print("OCR minor recognition noise / Tiny visual noise (REAL): PASS")

    # 7. Window creation / Process transition (MAJOR_CHANGE) (REAL)
    post_win = ActionObservation(
        active_window_title="Untitled - Chrome",
        active_process_name="chrome.exe",
        active_pid=2002,
        dom_context={"elements": [{"text": "File Menu"}]},
        uia_context=[{"id": "uia_file"}],
        ocr_text="File Edit",
        visual_hash="hash1"
    )
    res_win = action_delta_classifier.classify_delta(pre_obs, post_win)
    assert res_win["category"] == "MAJOR_CHANGE"
    assert res_win["changed_metadata"]["win_title_changed"] == True
    print("Window creation / Process transition (REAL): PASS")

    # 8. Contradictory multimodal evidence (CONTRADICTORY_CHANGE) (REAL)
    post_contradict = ActionObservation(
        active_window_title="Untitled - Notepad",
        active_process_name="notepad.exe",
        active_pid=1001,
        dom_context={"elements": [{"text": "File Menu"}, {"text": "Submit Button"}]},
        uia_context=[{"id": "uia_file"}],
        ocr_text="", # DOM registered new element but visual OCR text is empty
        visual_hash="hash2"
    )
    res_contradict = action_delta_classifier.classify_delta(
        pre_obs, 
        post_contradict, 
        expected_state={"ocr_text_contains": ["Submit"]}
    )
    assert res_contradict["category"] == "CONTRADICTORY_CHANGE"
    assert res_contradict["reason_code"] == "EVIDENCE_CONTRADICTION"
    print("Contradictory multimodal evidence (REAL): PASS")

    # 9. Safety-block preservation (UNEXPECTED_CHANGE) (REAL)
    res_blocked = action_delta_classifier.classify_delta(
        pre_obs, 
        post_win, 
        action_execution_result={"status": "BLOCKED"}
    )
    assert res_blocked["category"] == "UNEXPECTED_CHANGE"
    assert res_blocked["reason_code"] == "SAFETY_BLOCKED"
    assert res_blocked["score"] == 0.0
    print("Safety-block preservation (REAL): PASS")

    # 10. Expected Change satisfaction (EXPECTED_CHANGE) (REAL)
    res_expected = action_delta_classifier.classify_delta(
        pre_obs, 
        post_ocr, 
        expected_state={"ocr_text_contains": ["Save"]}
    )
    assert res_expected["category"] == "EXPECTED_CHANGE"
    assert res_expected["score"] == 1.0
    print("Expected Change satisfaction (REAL): PASS")

    # 11. Backward compatibility check (REAL)
    assert action_verifier.verify_pre_flight({"window_title_contains": ["Notepad"]}, pre_obs) == True
    print("Backward compatibility check (REAL): PASS")

    print("\n" + "="*60)
    print("ALL DELTA CLASSIFIER TESTS COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_tests())
