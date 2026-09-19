from core.orchestration.action_executor import action_executor
from action.desktop_control.desktop_controller import desktop_controller
from core.perception.screen_capture import screen_capturer
from core.orchestration.agent_state_machine import state_machine
from infrastructure.watchdog.safety_layer import safety_gate
from core.perception.visual_state import Action

class ActorPipeline:
    @staticmethod
    def check_safety(action_type: str, target: str, mapped_coords: list, text_payload: str, confidence_score: int, task_description: str) -> dict:
        state_machine.transition_to("SAFETY_CHECK", task_description, "Checking safety perimeter")
        
        controller_action = action_type
        payload = {}
        if action_type == "OPEN_APP":
            controller_action = "APP_OPEN"
            payload = {"app_name": target}
        elif action_type == "CLICK" and mapped_coords:
            controller_action = "UI_AUTOMATION"
            payload = {"action": "click", "coords": mapped_coords}
        elif action_type == "TYPE" and mapped_coords:
            controller_action = "UI_AUTOMATION"
            payload = {"action": "type", "coords": mapped_coords, "text": text_payload or ""}
        elif action_type == "WAIT":
            controller_action = "OS_COMMAND"
            payload = {"command": "echo waiting"}

        safety = safety_gate.check_safety(controller_action, payload)
        
        normalized_action = Action(
            action_type=action_type,
            target=target,
            coords=mapped_coords,
            text_payload=text_payload,
            confidence=confidence_score / 100.0
        )
        
        return {
            "safety_status": safety["status"],
            "safety_message": safety.get("message", ""),
            "action_id": safety.get("action_id", ""),
            "controller_action": controller_action,
            "controller_payload": payload,
            "normalized_action": normalized_action
        }

    @staticmethod
    async def act(action_type: str, target: str, mapped_coords: list, text_payload: str, before_frame, confidence_score: int, element_source: str, controller_action: str, controller_payload: dict, task_description: str):
        state_machine.transition_to("EXECUTING", task_description, f"Execute {action_type} action")
        
        exec_result = await action_executor.execute(
            action_type=action_type,
            target=target,
            coords=mapped_coords,
            text_payload=text_payload,
            before_frame=before_frame,
            screen_width=getattr(before_frame, 'width', 1920),
            screen_height=getattr(before_frame, 'height', 1080),
            target_confidence=confidence_score / 100.0,
            target_source=element_source,
            controller_action=controller_action,
            controller_payload=controller_payload,
            desktop_controller=desktop_controller,
            screen_capturer=screen_capturer,
        )
        return exec_result

actor_pipeline = ActorPipeline()
