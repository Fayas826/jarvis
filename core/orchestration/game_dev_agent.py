import os
import subprocess
import asyncio
from typing import Dict, Any

from core.cognition.reasoning.brain import brain

class GameDevAgent:
    """dY - O.M.E.G.A. GAME_DEV_AGENT: Autonomous Blender and Unity orchestration."""
    
    def __init__(self):
        self.blender_executable = os.getenv("BLENDER_PATH", "blender")
        self.scratch_dir = os.path.join(os.getcwd(), "scratch")
        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

    async def execute_task(self, task_description: str) -> Dict[str, Any]:
        """Entry point for the Game Dev Agent."""
        print(f"[GAME DEV AGENT] Analyzing task: {task_description}")
        
        # Determine engine
        if "blender" in task_description.lower() or "render" in task_description.lower() or "3d" in task_description.lower():
            return await self._execute_blender_automation(task_description)
        elif "unity" in task_description.lower() or "unreal" in task_description.lower() or "godot" in task_description.lower():
            return await self._execute_engine_scripting(task_description)
        else:
            print("[GAME DEV AGENT] Unrecognized game engine. Defaulting to Blender.")
            return await self._execute_blender_automation(task_description)

    async def _execute_blender_automation(self, task_description: str) -> Dict[str, Any]:
        print("[GAME DEV AGENT] Initiating Blender Automation Protocol...")
        
        # Generate the bpy script using the main JARVIS Brain
        prompt = f"""
        You are an expert Blender Python (bpy) developer.
        The user wants to: {task_description}
        Write a complete, self-contained Python script using the 'bpy' library to achieve this.
        Do NOT wrap the code in markdown blocks like ```python. Just output the raw python code.
        The script should delete default objects, create the requested scene, set up a camera, and save a .blend file or render an image.
        """
        
        print("[GAME DEV AGENT] Generating bpy script via Neural Engine...")
        script_code = await brain.process_complex_logic(prompt)
        
        # Clean markdown if the LLM hallucinated it
        if script_code.startswith("```python"):
            script_code = script_code.split("```python")[1].split("```")[0].strip()
        elif script_code.startswith("```"):
            script_code = script_code.split("```")[1].split("```")[0].strip()

        # Save to scratch folder
        script_path = os.path.join(self.scratch_dir, "jarvis_blender_auto.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_code)
            
        print(f"[GAME DEV AGENT] Saved automation script to {script_path}")
        print("[GAME DEV AGENT] Executing Blender CLI in background...")
        
        # Execute Blender in background mode
        try:
            # Command: blender --background --python script_path
            process = subprocess.Popen(
                [self.blender_executable, "-b", "-P", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Non-blocking wait
            stdout, stderr = await asyncio.to_thread(process.communicate)
            
            if process.returncode == 0:
                print("[GAME DEV AGENT] Blender execution completed successfully.")
                return {"status": "success", "engine": "blender", "log": stdout}
            else:
                print(f"[GAME DEV AGENT] Blender execution failed: {stderr}")
                return {"status": "error", "engine": "blender", "log": stderr}
                
        except Exception as e:
            print(f"[GAME DEV AGENT] Error hooking into Blender CLI: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _execute_engine_scripting(self, task_description: str) -> Dict[str, Any]:
        print("[GAME DEV AGENT] Initiating Unity/Unreal Engine Script Generation...")
        
        prompt = f"""
        You are an expert Game Engine Developer (C# for Unity, C++ for Unreal).
        The user wants to: {task_description}
        Generate the raw code file needed for this feature. Include proper MonoBehaviour/Actor boilerplate.
        """
        
        code = await brain.process_complex_logic(prompt)
        print("[GAME DEV AGENT] Script Generated. Ready for injection into project hierarchy.")
        
        return {"status": "success", "engine": "generic_game_engine", "code": code}

game_dev_agent = GameDevAgent()
