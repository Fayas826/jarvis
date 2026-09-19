import json
from typing import Dict

from core.cognition.reasoning.neural_core import classify_intent_reflex
from core.cognition.reasoning.commands.command_registry import command_registry
from core.cognition.reasoning.skills.skill_system import skill_registry
from core.orchestration.task_engine import Task, TaskStep


class Planner:
    def __init__(self):
        self.skill_names = set(skill_registry.skills.keys())

    async def create_plan(self, intent: str, context: Dict = None) -> Task:
        print(f"[PLANNER] Decomposing intent: {intent}")
        context = context or {}
        text = intent.strip()
        lowered = text.lower()

        command_match = self._match_registered_command(lowered)
        if command_match:
            return await command_match.get_task(context=context)

        reflex_intent, reflex_payload = classify_intent_reflex(lowered)
        if reflex_intent == "open_app" and reflex_payload:
            return Task(
                original_intent=text,
                plan_description=f"Launch {reflex_payload} and verify process handoff.",
                context=context,
                steps=[
                    TaskStep(
                        description=f"Open {reflex_payload}",
                        action_type="APP_OPEN",
                        payload={"app_name": reflex_payload},
                    )
                ],
            )

        if reflex_intent == "type_text" and reflex_payload:
            return Task(
                original_intent=text,
                plan_description="Inject text into the active window.",
                context=context,
                steps=[
                    TaskStep(
                        description="Type requested text",
                        action_type="UI_AUTOMATION",
                        payload={"action": "type", "text": reflex_payload},
                    )
                ],
            )

        if reflex_intent == "system_power":
            return Task(
                original_intent=text,
                plan_description="System power action requires explicit operator confirmation.",
                context=context,
                steps=[],
                status="BLOCKED",
            )

        # Fallback to a conservative shell task only when the request is explicit.
        if lowered.startswith(("run ", "execute ", "cmd ")):
            command = lowered.replace("execute ", "", 1).replace("run ", "", 1).replace("cmd ", "", 1).strip()
            return Task(
                original_intent=text,
                plan_description="Execute an explicit operator shell command.",
                context=context,
                steps=[
                    TaskStep(
                        description=f"Run shell command: {command}",
                        action_type="OS_COMMAND",
                        payload={"command": command},
                    )
                ],
            )

        return Task(
            original_intent=text,
            plan_description="No safe execution plan could be derived from the request.",
            context=context,
            steps=[],
            status="BLOCKED",
        )

    def _match_registered_command(self, lowered: str):
        command_aliases = {
            "start work": "start_work",
            "start my work": "start_work",
            "prepare meeting": "prepare_meeting",
            "cleanup system": "cleanup_system",
            "clean system": "cleanup_system",
            "shutdown all": "shutdown_all",
            "set up my dev environment": "setup_dev_env",
            "setup dev environment": "setup_dev_env",
            "setup project": "setup_dev_env",
        }

        command_name = command_aliases.get(lowered)
        if not command_name:
            return None
        return command_registry.get_command(command_name)


planner = Planner()
