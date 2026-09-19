"""
Phase 36.8 — Unified JARVIS Orchestrator
==========================================

Integrates all Phase 36 subsystems into a single coherent execution pipeline:

    USER INTENT
        ↓
    GoalIntentEngine          (36.3)
        ↓
    TaskPlanner DAG           (36.3)
        ↓
    TaskStateController       (36.4) — begin_session, persist
        ↓
    HumanInTheLoopManager     (36.7) — authorization gate
        ↓
    PredictiveActionVerifier  (36.6) — pre-flight prediction
        ↓
    [Execution via ComputerUseAgent]
        ↓
    PredictiveActionVerifier  (36.6) — post-flight compare
        ↓
    EnvironmentStateModel     (36.5) — observe state changes
        ↓
    AdaptiveToolSelector      (36.5) — record outcome
        ↓
    GoalMonitor               (36.7) — track progress
        ↓
    AutonomousRecoveryManager (36.6) — decide recovery if needed
        ↓
    EpisodicMemory write      (36.4) — persist episode

SAFETY:
- Safety Kernel (safety_layer.py) is NEVER bypassed.
- SAFETY_BLOCK from any subsystem immediately halts execution.
- Risk levels are NEVER downgraded by orchestrator decisions.
- Specialist agents (when added) CANNOT bypass the orchestrator safety gate.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional

from core.orchestration.task_planner import task_planner, GoalIntentEngine
from core.orchestration.task_state import task_state_controller
from core.orchestration.tool_selector import adaptive_tool_selector
from core.orchestration.environment_model import environment_model
from core.orchestration.predictive_verifier import predictive_verifier, VerificationStatus
from core.orchestration.recovery_manager import autonomous_recovery_manager, RecoveryAction
from core.orchestration.hitl_manager import hitl_manager, RiskLevel
from core.orchestration.goal_monitor import goal_monitor


class JARVISOrchestrator:
    """
    Phase 36 Unified JARVIS Orchestrator.
    Coordinates all subsystems for goal-driven autonomous execution.
    """

    def __init__(self):
        self.intent_engine = GoalIntentEngine()

    async def execute_goal(self, natural_language_goal: str) -> Dict[str, Any]:
        """
        Full Phase 37 pipeline:
        Intent → Plan → Cognitive State Init → Scheduler Load → E2E Execution Loop (Working Memory & Progress Monitoring)
        """
        print(f"\n[ORCHESTRATOR] ═══════ NEW LONG-HORIZON GOAL ═══════")
        print(f"[ORCHESTRATOR] Goal: {natural_language_goal}")

        from core.orchestration.cognitive_state import cognitive_state_manager
        from core.orchestration.working_memory import working_memory
        from core.orchestration.progress_engine import goal_progress_engine
        from core.orchestration.task_scheduler import task_scheduler

        # Clear working memory for new session
        working_memory.clear()
        goal_progress_engine.reset()

        # ── 1. Parse intent ───────────────────────────────────────────────────
        intent = self.intent_engine.parse_goal_intent(natural_language_goal)
        print(f"[ORCHESTRATOR] Intent: risk={intent['risk_level']}, "
              f"forbidden={intent['forbidden_actions']}")

        # ── 2. Start session ──────────────────────────────────────────────────
        plan_id = task_state_controller.begin_session(natural_language_goal, intent)
        print(f"[ORCHESTRATOR] Session started: {plan_id}")

        # ── 3. Check for interrupted session recovery ─────────────────────────
        interrupted = task_state_controller.get_interrupted_session()
        if interrupted:
            recovered_node = task_state_controller.recover_session()
            print(f"[ORCHESTRATOR] Recovered interrupted session. "
                  f"Resuming at: {recovered_node.get('task_id') if recovered_node else 'start'}")

        # ── 4. Generate plan ──────────────────────────────────────────────────
        plan = await task_planner.create_plan(natural_language_goal)
        print(f"[ORCHESTRATOR] Plan generated: {len(plan)} nodes")

        # ── 5. Initialize scheduler & monitor ─────────────────────────────────
        task_scheduler.load_plan(plan)
        goal_monitor.initialize(plan)

        # ── 6. Execute loop via Scheduler ─────────────────────────────────────
        results = []
        
        while True:
            node = task_scheduler.get_next_runnable_task()
            if not node:
                break

            node_id = node.get("task_id", "unknown")
            risk_level = node.get("risk_level", "LOW")

            cognitive_state_manager.set_active_subgoal(node_id)

            # Skip already-completed nodes (from recovery)
            node_status = task_state_controller._record.nodes.get(node_id, {}).get("status", "PENDING") if task_state_controller._record else "PENDING"
            if node_status == "COMPLETED":
                print(f"[ORCHESTRATOR] Node {node_id} already completed — skipping.")
                goal_monitor.record_node_completed(node_id)
                cognitive_state_manager.mark_subgoal_complete(node_id)
                continue

            # ── 6a. HiTL Authorization gate ───────────────────────────────────
            auth = hitl_manager.check_authorization(node, plan_id, intent)
            if not auth["approved"]:
                print(f"[ORCHESTRATOR] Node {node_id} blocked by HiTL: {auth['reason']}")
                task_state_controller.mark_node_failed(node_id, auth["reason"], "HITL_BLOCKED")
                cognitive_state_manager.record_subgoal_failure(node_id, auth["reason"])
                results.append({"node_id": node_id, "status": "HITL_BLOCKED", "reason": auth["reason"]})
                # Terminal halt for blocked action on real desktop
                break

            # ── 6b. Pre-flight prediction ─────────────────────────────────────
            env_snap = environment_model.get_environment_snapshot()
            prediction = predictive_verifier.predict_expected_state(
                node.get("action_type", "WAIT"), node.get("objective", ""), node, env_snap
            )

            # ── 6c. Mark node running ─────────────────────────────────────────
            task_state_controller.mark_node_running(node_id)
            goal_monitor.record_node_start(node_id)

            # ── 6d. Dispatch execution ────────────────────────────────────────
            before_title = env_snap.get("ui_focus", {}).get("window", "")
            exec_result = await self._dispatch_node(node)
            after_title = environment_model.get_active_window().get("window", before_title)

            # ── 6e. Post-flight verification ──────────────────────────────────
            verification = predictive_verifier.compare(
                prediction, before_title, after_title, exec_result
            )
            v_status = verification["status"]
            print(f"[ORCHESTRATOR] Node {node_id}: {v_status}")

            # Observe turn progress and check loop/stagnation metrics
            progress_status = goal_progress_engine.observe_turn(node, verification)
            if progress_status in ("STALLED", "REGRESSING"):
                print(f"[ORCHESTRATOR] Progress warning detected: {progress_status}")

            # ── 6f. Safety block — immediate stop ─────────────────────────────
            if verification["is_terminal"]:
                task_state_controller.mark_node_failed(node_id, "SAFETY_BLOCK", "SAFETY_BLOCK")
                task_state_controller.complete_session("SAFETY_BLOCKED")
                cognitive_state_manager.record_subgoal_failure(node_id, "SAFETY_BLOCK")
                return {"status": "SAFETY_BLOCKED", "plan_id": plan_id, "node_id": node_id,
                        "detail": "Safety kernel blocked execution. Session terminated."}

            # ── 6g. Handle result ─────────────────────────────────────────────
            if v_status == VerificationStatus.SUCCESS:
                task_state_controller.mark_node_completed(node_id, exec_result)
                goal_monitor.record_node_completed(node_id)
                cognitive_state_manager.mark_subgoal_complete(node_id)
                adaptive_tool_selector.record_outcome(
                    node.get("action_type", ""), node.get("action_type", ""), "uia", True
                )
                results.append({"node_id": node_id, "status": "COMPLETED"})

            else:
                # ── 6h. Recovery decision ─────────────────────────────────────
                recovery = autonomous_recovery_manager.decide_recovery(
                    node_id, v_status, node, exec_result
                )
                task_state_controller.record_recovery(node_id, recovery["action"], v_status)
                cognitive_state_manager.record_subgoal_failure(node_id, recovery["reason"])

                if recovery["action"] == RecoveryAction.STOP:
                    task_state_controller.mark_node_failed(node_id, recovery["reason"], "UNRECOVERABLE")
                    task_state_controller.complete_session("FAILED")
                    return {"status": "FAILED", "plan_id": plan_id,
                            "node_id": node_id, "reason": recovery["reason"]}
                elif recovery["action"] == RecoveryAction.ASK_USER:
                    task_state_controller.mark_node_failed(node_id, recovery["reason"], "NEEDS_USER")
                    results.append({"node_id": node_id, "status": "NEEDS_USER", "reason": recovery["reason"]})
                    break
                else:
                    # For automated recoveries (RETRY, REGROUND, etc.) mark as retrying
                    task_state_controller.mark_node_retrying(node_id, 1)
                    results.append({"node_id": node_id, "status": "RETRYING",
                                    "recovery_action": recovery["action"]})

            # ── 6i. Goal monitor check ────────────────────────────────────────
            progress = goal_monitor.get_status()
            if goal_monitor.should_escalate():
                print(f"[ORCHESTRATOR] Goal monitor escalation: {progress['detail']}")
                break

        # ── 7. Complete session ───────────────────────────────────────────────
        final_progress = goal_monitor.get_status()
        final_status = "COMPLETED" if final_progress["status"] == "COMPLETE" else "PARTIAL"
        task_state_controller.complete_session(final_status)

        return {
            "status": final_status,
            "plan_id": plan_id,
            "intent": intent,
            "node_results": results,
            "progress": final_progress,
            "cognitive_summary": cognitive_state_manager.get_context_compression_prompt()
        }

    async def _dispatch_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch a task node for execution through the real ComputerUseAgent pipeline.

        Translates a Phase 36 DAG node into a natural-language task description
        and delegates to the Phase 35 closed-loop execution engine:
            screen capture → AI understand → ground → safety gate → execute →
            verify → re-ground → repair → recover

        Returns a normalized exec_result dict with keys:
            status: "SUCCESS" | "FAILED" | "BLOCKED"
            error: str (if failed)
            history: list (step history from CUA)
        """
        from core.orchestration.computer_use_agent import computer_use_agent

        action_type  = node.get("action_type", "WAIT")
        objective    = node.get("objective", "")
        description  = node.get("description", objective)
        node_id      = node.get("task_id", "unknown")

        # Build a natural-language task description for CUA
        if action_type == "WAIT":
            await asyncio.sleep(0.1)
            environment_model.observe_window(
                environment_model.get_active_window().get("window", "Desktop"),
                0, "system"
            )
            return {"status": "SUCCESS", "action_type": action_type, "node_id": node_id}

        # All real action types are dispatched to CUA
        task_desc = f"{objective}"
        if description and description != objective:
            task_desc = f"{objective}: {description}"

        print(f"[ORCHESTRATOR] Dispatching node {node_id} to CUA: '{task_desc[:80]}'")
        try:
            cua_result = await computer_use_agent.execute_task(task_desc)
            cua_status = cua_result.get("status", "FAILED")

            # Translate CUA result to orchestrator exec_result format
            if cua_status == "SUCCESS":
                return {
                    "status": "SUCCESS",
                    "action_type": action_type,
                    "node_id": node_id,
                    "history": cua_result.get("history", []),
                }
            elif cua_status == "BLOCKED":
                return {
                    "status": "BLOCKED",
                    "error": cua_result.get("reason", "Safety gate blocked"),
                    "action_type": action_type,
                    "node_id": node_id,
                }
            else:
                return {
                    "status": "FAILED",
                    "error": cua_result.get("reason", "Execution failed"),
                    "action_type": action_type,
                    "node_id": node_id,
                }
        except Exception as e:
            print(f"[ORCHESTRATOR] CUA dispatch exception for node {node_id}: {e}")
            return {
                "status": "FAILED",
                "error": str(e),
                "action_type": action_type,
                "node_id": node_id,
            }


jarvis_orchestrator = JARVISOrchestrator()
