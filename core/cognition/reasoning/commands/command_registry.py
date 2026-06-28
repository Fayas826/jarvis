
from core.orchestration.task_engine import Task, TaskStep

class CommandBase:
    """🛠️ O.M.E.G.A. COMMAND_LAYER: High-level User Intents."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def get_task(self, context: dict = None) -> Task:
        raise NotImplementedError

class StartWorkCommand(CommandBase):
    def __init__(self):
        super().__init__("start_work", "Prepares the entire development workspace.")

    async def get_task(self, context: dict = None) -> Task:
        return Task(
            original_intent="Start Work",
            plan_description="Igniting dev environment, launching VS Code, and verifying services.",
            steps=[
                TaskStep(description="Open VS Code", action_type="APP_OPEN", payload={"app_name": "vscode"}),
                TaskStep(description="Start Dev Server", action_type="OS_COMMAND", payload={"command": "npm run dev"}),
                TaskStep(description="Focus Editor", action_type="WINDOW_CONTROL", payload={"title": "Visual Studio Code", "action": "focus"})
            ]
        )

class CleanupSystemCommand(CommandBase):
    def __init__(self):
        super().__init__("cleanup_system", "Clears junk and optimizes system performance.")

    async def get_task(self, context: dict = None) -> Task:
        return Task(
            original_intent="Cleanup System",
            plan_description="Purging only the safe JARVIS temp workspace and freeing up memory.",
            steps=[
                TaskStep(description="Purge JARVIS Temp Cache", action_type="SKILL", payload={"skill_name": "clean_system", "path": "data/temp"})
            ]
        )

class PrepareMeetingCommand(CommandBase):
    def __init__(self):
        super().__init__("prepare_meeting", "Cleans up workspace for screen sharing.")

    async def get_task(self, context: dict = None) -> Task:
        return Task(
            original_intent="Prepare Meeting",
            plan_description="Minimizing distracting windows and silencing notifications.",
            steps=[
                TaskStep(description="Minimize Non-Dev Windows", action_type="WINDOW_CONTROL", payload={"title": "Spotify", "action": "minimize"}),
                TaskStep(description="Minimize Chrome", action_type="WINDOW_CONTROL", payload={"title": "Chrome", "action": "minimize"}),
                TaskStep(description="Focus VS Code", action_type="WINDOW_CONTROL", payload={"title": "Visual Studio Code", "action": "focus"})
            ]
        )

class ShutdownAllCommand(CommandBase):
    def __init__(self):
        super().__init__("shutdown_all", "Safely closes all work applications.")

    async def get_task(self, context: dict = None) -> Task:
        return Task(
            original_intent="Shutdown All",
            plan_description="Closing dev tools and saving session state.",
            steps=[
                TaskStep(description="Close VS Code", action_type="WINDOW_CONTROL", payload={"title": "Visual Studio Code", "action": "close"}),
                TaskStep(description="Kill Dev Process", action_type="OS_COMMAND", payload={"command": "taskkill /F /IM node.exe"})
            ]
        )

class SetupDevEnvCommand(CommandBase):
    def __init__(self):
        super().__init__("setup_dev_env", "Installs dependencies and prepares a fresh project.")

    async def get_task(self, context: dict = None) -> Task:
        return Task(
            original_intent="Setup Dev Env",
            plan_description="Initializing project dependencies.",
            steps=[
                TaskStep(description="Install NPM Packages", action_type="OS_COMMAND", payload={"command": "npm install"}),
                TaskStep(description="Run Structural Diagnostics", action_type="OS_COMMAND", payload={"command": "python -m compileall backend core infrastructure action perception"})
            ]
        )

class CommandRegistry:
    def __init__(self):
        self.commands = {
            "start_work": StartWorkCommand(),
            "cleanup_system": CleanupSystemCommand(),
            "prepare_meeting": PrepareMeetingCommand(),
            "shutdown_all": ShutdownAllCommand(),
            "setup_dev_env": SetupDevEnvCommand()
        }

    def get_command(self, name: str) -> CommandBase:
        return self.commands.get(name)

command_registry = CommandRegistry()
