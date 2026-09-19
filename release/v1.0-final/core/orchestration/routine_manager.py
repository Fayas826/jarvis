
import asyncio
import time
from datetime import datetime
from core.cognition.reasoning.commands.command_registry import command_registry
from core.orchestration.task_engine import get_task_engine
from core.cognition.reasoning.context_engine import context_engine

class RoutineManager:
    """⏰ O.M.E.G.A. ROUTINE_MANAGER: Daily Life Orchestration."""
    
    def __init__(self):
        self.running = False
        self.completed_today = {}

    async def start(self):
        self.running = True
        print("[ROUTINE] Manager online.")
        while self.running:
            try:
                await self._check_routines()
                await asyncio.sleep(60) # Check every minute
            except Exception as e:
                print(f"[ROUTINE_ERR] {e}")
                await asyncio.sleep(10)

    async def _check_routines(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")
        
        # Reset completed routines at midnight
        if "last_run_date" not in self.completed_today:
            self.completed_today = {"last_run_date": today}
        elif self.completed_today["last_run_date"] != today:
            self.completed_today = {"last_run_date": today}

        # MORNING: Start Dev Environment (e.g., 09:00)
        if current_time == "09:00" and "morning_start" not in self.completed_today:
            await self._trigger_command("start_work")
            self.completed_today.add("morning_start")

        # IDLE: Cleanup & Diagnostics
        context = context_engine.get_context()
        if context["state"] == "IDLE":
            # Only run idle cleanup once every 4 hours
            last_idle = self.completed_today.get("last_idle_time", 0)
            if time.time() - last_idle > 14400:
                await self._trigger_command("cleanup_system")
                self.completed_today["last_idle_time"] = time.time()

        # NIGHT: Shutdown unused services (e.g., 23:00)
        if current_time == "23:00" and "night_shutdown" not in self.completed_today:
            await self._trigger_command("shutdown_all")
            self.completed_today.add("night_shutdown")

    async def _trigger_command(self, cmd_name: str):
        cmd = command_registry.get_command(cmd_name)
        task_engine = get_task_engine()
        if cmd and task_engine:
            print(f"[ROUTINE] Triggering: {cmd_name}")
            task = await cmd.get_task()
            await task_engine.execute_task(task)

routine_manager = RoutineManager()
