import uuid
import time
from typing import List, Dict, Any
from core.cognition.reasoning.brain import brain
from core.orchestration.task_state import task_state_controller

class GoalIntentEngine:
    """Parses natural-language goals into structured intent scopes with constraints and success criteria."""

    def parse_goal_intent(self, master_objective: str) -> Dict[str, Any]:
        # Rule-based intent analysis
        priority = "MEDIUM"
        risk_level = "LOW"
        forbidden_actions = []
        success_conditions = ["title_check"]
        
        obj_lower = master_objective.lower()
        if "delete" in obj_lower or "remove" in obj_lower or "kill" in obj_lower:
            risk_level = "HIGH"
            priority = "HIGH"
            forbidden_actions = ["format_disk", "delete_system_files"]
        if "confidential" in obj_lower or "secure" in obj_lower:
            risk_level = "CRITICAL"
            forbidden_actions = ["upload_network", "email_payload"]
            
        return {
            "objective": master_objective,
            "priority": priority,
            "risk_level": risk_level,
            "forbidden_actions": forbidden_actions,
            "success_conditions": success_conditions,
            "confidence_requirement": 0.85 if risk_level in ["HIGH", "CRITICAL"] else 0.70
        }

class TaskPlanner:
    """Decomposes complex objectives into a sequence of trackable sub-tasks with DAG dependencies, conditional branches, and retry policies."""

    def __init__(self):
        self.intent_engine = GoalIntentEngine()

    async def create_plan(self, master_objective: str) -> List[Dict[str, Any]]:
        print(f"[PLANNER] [DAG] Generating execution plan for objective: '{master_objective}'")
        
        # Analyze goal intent first
        intent = self.intent_engine.parse_goal_intent(master_objective)
        print(f"[PLANNER] Goal intent analyzed: risk={intent['risk_level']}, priority={intent['priority']}")

        prompt = (
            f"You are JARVIS Master Task Planner. Objective: '{master_objective}'\n"
            f"Intent constraints: Risk level: {intent['risk_level']}. Forbidden: {intent['forbidden_actions']}.\n"
            "Decompose this goal into small, sequential, trackable sub-tasks with DAG dependencies and conditional branches.\n"
            "Return ONLY a JSON list matching this format:\n"
            "[\n"
            "  {\n"
            "    \"task_id\": \"T-001\",\n"
            "    \"parent_id\": null,\n"
            "    \"objective\": \"Step title\",\n"
            "    \"description\": \"Detailed description of what to do\",\n"
            "    \"action_type\": \"CLICK|TYPE|OPEN_APP|WAIT\",\n"
            "    \"dependencies\": [],\n"
            "    \"preconditions\": {},\n"
            "    \"expected_state\": \"Expected active title or coordinate changes\",\n"
            "    \"retry_policy\": {\"max_retries\": 3, \"strategy\": \"reground\"},\n"
            "    \"timeout\": 30.0,\n"
            "    \"risk_level\": \"LOW|MEDIUM|HIGH\",\n"
            "    \"recovery_strategy\": \"replan\",\n"
            "    \"completion_condition\": \"title_check\",\n"
            "    \"status\": \"PENDING\"\n"
            "  }\n"
            "]"
        )
        
        try:
            res = await brain.get_ai_response(prompt)
            tasks = res.get("response") or res.get("payload")
            if isinstance(tasks, list) and len(tasks) > 0:
                # Add default structural keys if missing
                for idx, t in enumerate(tasks):
                    t.setdefault("id", f"TASK-{idx+1:03d}")
                    t.setdefault("task_id", t.get("id"))
                    t.setdefault("parent_id", None)
                    t.setdefault("goal", t.get("objective") or "Execute task node")
                    t.setdefault("description", t.get("description") or t.get("goal"))
                    t.setdefault("action_type", t.get("action_type") or "WAIT")
                    t.setdefault("dependencies", t.get("dependencies") or [])
                    t.setdefault("preconditions", t.get("preconditions") or {})
                    t.setdefault("expected_state", t.get("expected_state") or t.get("acceptance_criteria") or "SUCCESS")
                    t.setdefault("retry_policy", t.get("retry_policy") or {"max_retries": 3, "strategy": "reground"})
                    t.setdefault("timeout", t.get("timeout") or 30.0)
                    t.setdefault("risk_level", intent["risk_level"]) # Inherit intent risk level
                    t.setdefault("recovery_strategy", t.get("recovery_strategy") or "replan")
                    t.setdefault("completion_condition", t.get("completion_condition") or "title_check")
                    t.setdefault("status", "PENDING")
                
                task_state_controller.save_active_plan(tasks)
                task_state_controller.update_state({
                    "current_objective": master_objective,
                    "status": "PLANNING",
                    "active_task_id": None
                })
                try:
                    from core.orchestration.cognitive_state import cognitive_state_manager
                    subgoals = [{"id": t["task_id"], "goal": t["objective"], "status": "PENDING"} for t in tasks]
                    cognitive_state_manager.initialize_goal(master_objective, subgoals)
                except Exception as c_err:
                    print(f"[PLANNER] Cognitive state initialization warning: {c_err}")
                print(f"[PLANNER] [DAG] Decomposed objective into {len(tasks)} tasks.")
                return tasks
        except Exception as e:
            print(f"[PLANNER] Decomposition failed: {e}")
            
        # Basic offline fallback DAG plan for calculator testing
        fallback_tasks = [
            {
                "task_id": "TASK-001",
                "parent_id": None,
                "objective": "Verify screen capture active state",
                "description": "Initialize screen captures and verify active application displays",
                "action_type": "WAIT",
                "dependencies": [],
                "preconditions": {},
                "expected_state": "SUCCESS",
                "retry_policy": {"max_retries": 3, "strategy": "reground"},
                "timeout": 30.0,
                "risk_level": intent["risk_level"],
                "recovery_strategy": "replan",
                "completion_condition": "title_check",
                "status": "PENDING"
            },
            {
                "task_id": "TASK-002",
                "parent_id": "TASK-001",
                "objective": "Launch sandbox Calculator application",
                "description": "Trigger calculator launches and verify title change state",
                "action_type": "OPEN_APP",
                "dependencies": ["TASK-001"],
                "preconditions": {"app_installed": True},
                "expected_state": "Calculator",
                "retry_policy": {"max_retries": 3, "strategy": "reground"},
                "timeout": 30.0,
                "risk_level": intent["risk_level"],
                "recovery_strategy": "replan",
                "completion_condition": "title_check",
                "status": "PENDING"
            }
        ]
        
        # Backward compatibility mappings
        for t in fallback_tasks:
            t["id"] = t["task_id"]
            t["goal"] = t["objective"]
            t["acceptance_criteria"] = t["expected_state"]
            
        task_state_controller.save_active_plan(fallback_tasks)
        task_state_controller.update_state({
            "current_objective": master_objective,
            "status": "PLANNING",
            "active_task_id": None
        })
        try:
            from core.orchestration.cognitive_state import cognitive_state_manager
            subgoals = [{"id": t["task_id"], "goal": t["objective"], "status": "PENDING"} for t in fallback_tasks]
            cognitive_state_manager.initialize_goal(master_objective, subgoals)
        except Exception as c_err:
            print(f"[PLANNER] Cognitive state initialization warning: {c_err}")
        return fallback_tasks

task_planner = TaskPlanner()
