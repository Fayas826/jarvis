
import os
import shutil
import asyncio
from typing import Dict, Optional
from abc import ABC, abstractmethod

class BaseSkill(ABC):
    """🧩 O.M.E.G.A. SKILL_SYSTEM: Reusable Execution Logic."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    async def execute(self, payload: Dict, controller) -> Dict:
        pass

class OpenAppSkill(BaseSkill):
    def __init__(self):
        super().__init__("open_app", "Launches a specific application by name.")
        
    async def execute(self, payload: Dict, controller) -> Dict:
        app_name = payload.get("app_name")
        return await controller("APP_OPEN", {"app_name": app_name})

class ProjectSetupSkill(BaseSkill):
    def __init__(self):
        super().__init__("setup_project", "Configures a development environment (VS Code, servers, ports).")
        
    async def execute(self, payload: Dict, controller) -> Dict:
        project_path = payload.get("path", os.getcwd())
        steps = [
            {"type": "APP_OPEN", "data": {"app_name": "vscode"}},
            {"type": "OS_COMMAND", "data": {"command": f"cd {project_path} && npm run dev"}},
            {"type": "WINDOW_CONTROL", "data": {"title": "Visual Studio Code", "action": "focus"}}
        ]
        
        results = []
        for step in steps:
            res = await controller(step["type"], step["data"])
            results.append(res)
            await asyncio.sleep(1)
            
        return {"status": "SUCCESS", "steps_completed": len(results), "details": results}

class CleanSystemSkill(BaseSkill):
    def __init__(self):
        super().__init__("clean_system", "Performs safe, non-destructive workspace cleanup.")

    async def execute(self, payload: Dict, controller) -> Dict:
        cleanup_target = payload.get("path", "data/temp")
        absolute_target = os.path.abspath(cleanup_target)

        if not absolute_target.endswith(os.path.normpath("data\\temp")) and not absolute_target.endswith(os.path.normpath("data/temp")):
            return {"status": "ERROR", "error": "SAFE_CLEANUP_PATH_REQUIRED"}

        os.makedirs(absolute_target, exist_ok=True)
        removed = 0
        for entry in os.scandir(absolute_target):
            if entry.is_file() or entry.is_symlink():
                os.remove(entry.path)
                removed += 1
            elif entry.is_dir():
                shutil.rmtree(entry.path)
                removed += 1
        return {"status": "SUCCESS", "detail": f"Cleared {removed} temp item(s)."}

class SkillRegistry:
    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {
            "open_app": OpenAppSkill(),
            "setup_project": ProjectSetupSkill(),
            "clean_system": CleanSystemSkill(),
        }
        
    def get_skill(self, name: str) -> Optional[BaseSkill]:
        return self.skills.get(name)

skill_registry = SkillRegistry()
