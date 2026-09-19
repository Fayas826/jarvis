
import asyncio
import time
from core.cognition.reasoning.context_engine import context_engine
from core.orchestration.task_engine import get_task_engine, Task, TaskStep
from core.cognition.reasoning.habit_tracker import habit_tracker
from core.cognition.reasoning.commands.command_registry import command_registry

class AutonomousOrchestrator:
    """🤖 O.M.E.G.A. AUTONOMOUS_ACTION: Pre-emptive Intelligence."""
    
    def __init__(self):
        self.running = False
        self.last_auto_task = 0
        self.safe_patterns = ["vscode", "chrome", "spotify", "terminal"]

    async def start(self):
        self.running = True
        print("[AUTONOMOUS] Orchestrator online.")
        while self.running:
            try:
                await self._tick()
                await asyncio.sleep(300) # Check every 5 minutes for proactive
            except Exception as e:
                print(f"[AUTONOMOUS_ERR] {e}")
                await asyncio.sleep(10)

    async def _tick(self):
        context = context_engine.get_context()
        state = context["state"]
        
        # 1. CRITICAL REPAIR (Highest Priority)
        if state == "CRITICAL":
            await self._run_emergency_repair()
            return

        # 2. PROACTIVE HABITS (Controlled Prediction)
        likely_apps = habit_tracker.get_likely_apps()
        task_engine = get_task_engine()
        if not task_engine:
            return
        for app in likely_apps:
            if app in self.safe_patterns:
                print(f"[PROACTIVE] You usually use {app} now. Launching...")
                await task_engine.execute_task(Task(
                    original_intent=f"Proactive Launch: {app}",
                    steps=[TaskStep(description=f"Launch {app}", action_type="APP_OPEN", payload={"app_name": app})]
                ))

        # 3. IDLE OPTIMIZATION
        if state == "IDLE" and time.time() - self.last_auto_task > 3600:
            await self._run_safe_cleanup()

    def get_status(self):
        return {
            "running": self.running,
            "last_auto_task": self.last_auto_task,
            "safe_patterns": self.safe_patterns,
            "mode": "periodic_safe_autonomy"
        }

    def _trigger_action(self, intent, risk="MEDIUM", source="orchestrator"):
        if risk in {"HIGH", "CRITICAL"}:
            return f"Blocked: {intent} requires human approval."
        self.last_auto_task = time.time()
        return f"Success: {intent} accepted from {source}."

    async def _run_safe_cleanup(self):
        print("[AUTONOMOUS] System IDLE. Running safe cleanup...")
        task_engine = get_task_engine()
        if not task_engine:
            return
        cmd = command_registry.get_command("cleanup_system")
        if cmd:
            task = await cmd.get_task()
            await task_engine.execute_task(task)
        self.last_auto_task = time.time()

    async def _run_emergency_repair(self):
        print("[AUTONOMOUS] System CRITICAL. Emergency resource recovery...")
        # Logic to clear caches or throttle non-essential JARVIS loops
        self.last_auto_task = time.time()

autonomous_orchestrator = AutonomousOrchestrator()
