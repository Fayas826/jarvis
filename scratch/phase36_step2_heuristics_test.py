# scratch/phase36_step2_heuristics_test.py
import sys
import os
import asyncio

sys.path.insert(0, r"c:\jarvis AI\jarvis")

async def run_tests():
    from core.perception.gui_grounding import vision_grounder, GUIElement, ScreenFrame
    from core.orchestration.task_state import task_state_controller

    print("\n" + "="*60)
    print("PHASE 36.2 HEURISTICS & VARIABLE SUBSTITUTION TEST SUITE")
    print("="*60)

    # 1. Variable Substitution check (REAL)
    task_state_controller.set_variable("search_query", "Kerala weather")
    task_node = {
        "task_id": "T-001",
        "objective": "Search for {{search_query}} in Chrome",
        "action_payload": {"text": "Query: {{search_query}}"}
    }
    
    subbed = task_state_controller.substitute_variables(task_node)
    assert "Kerala weather" in subbed["objective"]
    assert "Query: Kerala weather" in subbed["action_payload"]["text"]
    print("Variable Substitution (REAL): PASS")

    # 2. Duplicate coordinate filter check (REAL)
    # Define elements with identical center coordinate but different sources/details
    elements = [
        GUIElement("dom_1", "button", "Save", "button", [10,10,30,30], [20,20], 1.0, True, "dom"),
        GUIElement("uia_1", "button", "Save File", "button", [10,10,30,30], [20,20], 0.9, True, "uia")
    ]
    screen = ScreenFrame(None, 1920, 1080, "Notepad", "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")
    
    # We call internal _score_and_select
    winner = vision_grounder._score_and_select(elements, "Save", screen, min_confidence=0.5)
    assert winner is not None
    # Verify we select the dom element because it has higher source reliability and score
    assert winner.id == "dom_1"
    print("Duplicate coordinates filtering (REAL): PASS")

    print("\n" + "="*60)
    print("ALL PHASE 36.2 TESTS COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_tests())
