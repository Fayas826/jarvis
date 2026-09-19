import os
import time
import asyncio
from typing import Dict, Any, List

# Core imports
from core.perception.screen_capture import screen_capturer
from core.perception.visual_state import ActionResult
from action.desktop_control.desktop_controller import desktop_controller
from core.orchestration.agent_state_machine import state_machine
from core.orchestration.task_recovery import (
    failure_classifier, recovery_strategy_router, RecoveryStrategy
)
from core.cognition.memory.context_memory import app_action_memory
from core.perception.gui_grounding import action_regrounder
from core.orchestration.plan_repair import plan_repair_controller
from core.orchestration.action_verifier import action_verifier, ActionObservation, action_delta_classifier
from core.orchestration.computer_use.observer import observer_pipeline
from core.orchestration.computer_use.planner import planner_pipeline
from core.orchestration.computer_use.grounder import grounder_pipeline
from core.orchestration.computer_use.actor import actor_pipeline

class ComputerUseAgent:
    """🤖 O.M.E.G.A. COMPUTER_USE_AGENT: Upgraded Pipeline (Observer -> Planner -> Grounder -> Actor)."""
    
    def __init__(self):
        self.is_running = False
        self.current_task = None
        self.step_history: List[Dict[str, Any]] = []
        self.max_steps = 10
        self.current_step = 0
        self.bounding_boxes = [] # Active bounding box highlights
        self.agent_state = "STANDBY"
        self.confidence_score = 100
        self.max_retries = 3

    async def execute_task(self, task_description: str) -> Dict[str, Any]:
        """Runs the pipeline execution loop with failure recovery."""
        self.is_running = True
        self.current_task = task_description
        self.step_history = []
        self.current_step = 0
        self.bounding_boxes = []
        
        active_recipe = None
        try:
            from core.cognition.memory.action_memory import action_memory
            active_recipe = action_memory.query_recipe(task_description, "Desktop")
            if active_recipe:
                print(f"[COMPUTER_USE] Found successful cached recipe: {task_description}")
        except Exception as e:
            print(f"[COMPUTER_USE] Failed querying action memory: {e}")

        while self.is_running and self.current_step < self.max_steps:
            self.current_step += 1
            print(f"[COMPUTER_USE] Cycle Step {self.current_step}/{self.max_steps}")
            
            # 1. OBSERVE
            self.agent_state = "OBSERVING"
            before_frame, temp_before_path = await observer_pipeline.observe(task_description)
            
            # 2. PLAN
            self.agent_state = "UNDERSTANDING"
            plan_res = await planner_pipeline.plan(task_description, self.current_step, self.max_steps, temp_before_path, active_recipe)
            
            if plan_res.get("finished"):
                print("[COMPUTER_USE] Loop terminated: Completed flag resolved.")
                break
                
            action_type = plan_res.get("action_type")
            target = plan_res.get("target") or "Screen target"
            text_payload = plan_res.get("text_payload")
            
            # 3. GROUND
            self.agent_state = "GROUNDING"
            ground_res = await grounder_pipeline.ground(task_description, target, before_frame)
            self.confidence_score = ground_res["confidence_score"]
            self.bounding_boxes = ground_res["bounding_boxes"]
            mapped_coords = ground_res["mapped_coords"]
            element_source = ground_res["element_source"]
            element = ground_res["element"]

            if self.confidence_score < 70 and action_type in ["CLICK", "TYPE", "MOVE"]:
                print(f"[COMPUTER_USE] Grounding match confidence too low ({self.confidence_score}%). Aborting step.")
                self.agent_state = "REPLANNING"
                state_machine.transition_to("REPLANNING", task_description, "Grounding match score below threshold")
                self.is_running = False
                return {"status": "FAILED", "reason": f"LOW_CONFIDENCE: Grounding match score below threshold for '{target}'."}

            # 4. SAFETY & ACT
            safety_res = actor_pipeline.check_safety(action_type, target, mapped_coords, text_payload, self.confidence_score, task_description)
            if safety_res["safety_status"] == "PENDING_CONFIRMATION":
                print("[COMPUTER_USE] Perimeter gate intercepted. Confirmation required.")
                self.is_running = False
                return {
                    "status": "BLOCKED",
                    "action_id": safety_res["action_id"],
                    "message": safety_res["safety_message"],
                    "action": safety_res["normalized_action"].to_dict()
                }

            self.agent_state = "ACTING"
            exec_result_35 = await actor_pipeline.act(
                action_type=action_type, target=target, mapped_coords=mapped_coords,
                text_payload=text_payload, before_frame=before_frame,
                confidence_score=self.confidence_score, element_source=element_source,
                controller_action=safety_res["controller_action"],
                controller_payload=safety_res["controller_payload"],
                task_description=task_description
            )

            # --- POST FLIGHT (Legacy Phase 35) ---
            self.agent_state = "VERIFYING"
            state_machine.transition_to("VERIFYING", task_description, "Verify action results state transition")
            verification_success = exec_result_35.success

            after_frame_35 = None
            try:
                after_frame_35 = await screen_capturer.capture_frame_async()
            except Exception as e:
                from core.reliability.system_logger import system_logger
                system_logger.log('ERROR', 'computer_use_agent', f'Unhandled exception: {e}')
                pass

            pre_obs = ActionObservation(
                active_window_title=getattr(before_frame, 'active_window', 'Desktop') or 'Desktop',
                active_process_name=getattr(before_frame, 'active_process', 'none') or 'none',
                active_pid=0,
                dom_context=getattr(before_frame, 'browser_context', None),
                ocr_text=""
            )
            post_obs = ActionObservation(
                active_window_title=getattr(after_frame_35, 'active_window', 'Desktop') or 'Desktop' if after_frame_35 else 'Desktop',
                active_process_name=getattr(after_frame_35, 'active_process', 'none') or 'none' if after_frame_35 else 'none',
                active_pid=0,
                dom_context=getattr(after_frame_35, 'browser_context', None) if after_frame_35 else None,
                ocr_text=""
            )

            expected_state = {}
            if not expected_state and target:
                expected_state = {"ocr_text_contains": [target]}

            exec_res_dict = {"status": "SUCCESS"}
            if not verification_success:
                exec_res_dict = {"status": "ERROR", "error": exec_result_35.error or ""}

            verification_report = action_verifier.verify_post_flight(expected_state, pre_obs, post_obs, exec_res_dict)
            delta_report = action_delta_classifier.classify_delta(pre_obs, post_obs, expected_state, exec_res_dict)

            if verification_report["status"] == "SAFETY_BLOCK" or delta_report["category"] == "SAFETY_BLOCKED":
                self.is_running = False
                self.agent_state = "STANDBY"
                return {"status": "BLOCKED", "reason": "SAFETY_BLOCKED", "verification": verification_report}

            if verification_report["status"] in ["PARTIAL", "FAILED"]:
                reground_res = await action_regrounder.attempt_reground(
                    instruction=target, screen=after_frame_35 or before_frame, pre_element=element,
                    delta_metadata=delta_report.get("changed_metadata"), action_execution_result=exec_res_dict
                )
                if reground_res["status"] == "SAFETY_BLOCK":
                    self.is_running = False
                    self.agent_state = "STANDBY"
                    return {"status": "BLOCKED", "reason": "SAFETY_BLOCKED: Re-ground safety block."}

            action_result = ActionResult(
                action=safety_res["normalized_action"],
                success=verification_success,
                before_state=before_frame,
                after_state=after_frame_35,
                error=exec_result_35.error if not verification_success else None
            )
            self.step_history.append({
                **action_result.to_dict(),
                "confidence_report": exec_result_35.confidence.to_dict(),
                "verification_method": exec_result_35.verification_method,
                "backend_used": exec_result_35.backend_used,
                "latency_ms": exec_result_35.latency_ms,
            })

            try:
                active_app = getattr(before_frame, 'active_window', 'Desktop') or 'Desktop'
                app_action_memory.record(
                    app_name=active_app, action_type=action_type, tool=exec_result_35.backend_used,
                    success=verification_success, latency_ms=exec_result_35.latency_ms,
                )
            except Exception: pass

            if not verification_success:
                self.agent_state = "REPLANNING"
                state_machine.transition_to("REPLANNING", task_description, f"Recovery: {action_type} failed.")
                failure_type = failure_classifier.classify(
                    action_type=action_type, target=target, exec_result=exec_res_dict,
                    target_confidence=self.confidence_score / 100.0,
                    before_active_window=pre_obs.active_window_title,
                    after_active_window=post_obs.active_window_title,
                    grounding_from_cache=False,
                )
                strategy = recovery_strategy_router.select_strategy(failure_type)
                
                if recovery_strategy_router.needs_user(strategy) or recovery_strategy_router.is_halt(strategy):
                    self.is_running = False
                    self.agent_state = "STANDBY"
                    return {"status": "FAILED" if recovery_strategy_router.is_halt(strategy) else "BLOCKED", "failure_type": failure_type}

        self.agent_state = "STANDBY"
        self.is_running = False
        return {"status": "SUCCESS", "history": self.step_history}

    def stop(self):
        self.is_running = False
        self.agent_state = "STANDBY"

computer_use_agent = ComputerUseAgent()
