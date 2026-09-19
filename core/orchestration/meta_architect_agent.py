import os
import json
import time
import logging
import datetime
import asyncio
from typing import Dict, List, Optional, Any
from core.orchestration.agent_loop import ReActAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [META-ARCHITECT] %(message)s")

JARVIS_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
PLAN_PATH = os.path.join(JARVIS_ROOT, "project_memory", "active_plan.json")
UPGRADE_LOG_PATH = os.path.join(JARVIS_ROOT, "project_memory", "self_upgrade_history.json")

class FailurePatternDetector:
    def scan_active_plan(self) -> List[Dict]:
        if not os.path.exists(PLAN_PATH): return []
        try:
            with open(PLAN_PATH, "r", encoding="utf-8") as f:
                plan = json.load(f)
        except: return []

        tasks_list = plan.get("tasks", []) if isinstance(plan, dict) else (plan if isinstance(plan, list) else [])
        flagged = []
        for task in tasks_list:
            if not isinstance(task, dict): continue
            status = task.get("status", "")
            retries = task.get("retry_count", 0)
            error_msg = task.get("previous_error", "") or task.get("error", "")

            if status == "BLOCKED" or retries >= 3:
                flagged.append({
                    "task_id": task.get("task_id"),
                    "description": task.get("description", ""),
                    "error": error_msg,
                    "retries": retries,
                    "status": status,
                })
        return flagged

class MetaArchitectAgent:
    """
    The self-upgrading brain of JARVIS.
    Now supercharged with a Cursor-style ReAct loop for autonomous codebase editing.
    """
    def __init__(self):
        self.detector = FailurePatternDetector()
        self.react_engine = ReActAgent(max_iterations=8)
        self._upgrade_history = self._load_upgrade_history()

    async def run_analysis_cycle(self) -> Dict[str, Any]:
        logging.info("🧠 Meta-Architect analysis cycle initiated...")
        report = {"cycle_timestamp": datetime.datetime.utcnow().isoformat(), "actions": []}

        blocked_tasks = self.detector.scan_active_plan()
        if not blocked_tasks:
            logging.info("✅ No blocked tasks found. System is healthy.")
            return report

        for task in blocked_tasks:
            action = await self._escalate(task)
            if action:
                report["actions"].append(action)
                self._upgrade_history.append(action)

        self._save_upgrade_history()
        return report

    async def _escalate(self, task: Dict) -> Optional[Dict]:
        task_id = task["task_id"]
        error_msg = task["error"]
        retries = task["retries"]

        logging.info(f"🔍 Task '{task_id}' | Retries: {retries}")
        
        action_taken = {
            "task_id": task_id,
            "retries": retries,
            "tier": 3,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }

        # 🧠 TIER 3: ReAct Agent Codebase Surgery
        logging.warning(f"🔧 Tier 3 SOURCE SURGERY activated for task '{task_id}'!")
        
        prompt = (
            f"JARVIS has encountered a critical failure in task '{task_id}': {task['description']}\n"
            f"Error Trace:\n{error_msg}\n\n"
            f"Use your tools to investigate the codebase, find the failing file, and write a fix."
        )
        
        result = await self.react_engine.run(prompt)
        action_taken["result"] = f"ReAct Surgery Result: {result}"
        
        return action_taken

    def watch(self, interval_seconds: int = 120):
        logging.info(f"👁️ Meta-Architect watch daemon started. Polling every {interval_seconds}s.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while True:
            try:
                loop.run_until_complete(self.run_analysis_cycle())
            except Exception as e:
                logging.error(f"Meta-Architect cycle error: {e}")
            time.sleep(interval_seconds)

    def _load_upgrade_history(self) -> List[Dict]:
        if os.path.exists(UPGRADE_LOG_PATH):
            try:
                with open(UPGRADE_LOG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return []

    def _save_upgrade_history(self):
        os.makedirs(os.path.dirname(UPGRADE_LOG_PATH), exist_ok=True)
        with open(UPGRADE_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(self._upgrade_history, f, indent=2)

meta_architect = MetaArchitectAgent()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="JARVIS Meta-Architect Agent")
    parser.add_argument("--watch", action="store_true", help="Run continuous monitoring daemon")
    parser.add_argument("--interval", type=int, default=120, help="Polling interval in seconds")
    args = parser.parse_args()

    if args.watch:
        meta_architect.watch(interval_seconds=args.interval)
    else:
        loop = asyncio.new_event_loop()
        report = loop.run_until_complete(meta_architect.run_analysis_cycle())
        print(json.dumps(report, indent=2))
