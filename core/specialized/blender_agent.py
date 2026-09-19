import os
import tempfile
import subprocess
import logging
from typing import Dict, Any

class Blender3DAgent:
    """
    JARVIS Specialized Swarm Member: The 3D Artist.
    Generates Python scripts using the `bpy` library and executes them
    in Blender's headless background mode to autonomously generate 3D assets.
    """
    
    def __init__(self, blender_path: str = "blender"):
        self.blender_path = blender_path
        
    def generate_3d_primitive(self, object_type: str, export_path: str) -> Dict[str, Any]:
        """
        Generates a 3D primitive (e.g., 'cube', 'sphere', 'car_chassis')
        and exports it as an .obj file.
        """
        logging.info(f"[Blender Agent] Generating 3D Asset: {object_type}")
        
        # In a full swarm, an LLM would generate this BPY script dynamically based on prompt.
        # This is a robust template for headless primitive generation and export.
        bpy_script = f"""
import bpy
import os

# Clear existing mesh objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Generate Primitive
obj_type = '{object_type.lower()}'
if obj_type == 'cube' or obj_type == 'car_chassis':
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
elif obj_type == 'sphere':
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
else:
    bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 0))

# Scale to look like a car chassis if requested
if obj_type == 'car_chassis':
    bpy.context.object.scale[0] = 2.0
    bpy.context.object.scale[1] = 4.0
    bpy.context.object.scale[2] = 0.5
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Export to OBJ
export_path = r'{export_path}'
bpy.ops.wm.obj_export(filepath=export_path)
print(f"JARVIS [Blender Agent]: Successfully exported to {{export_path}}")
"""
        try:
            # Save the script to a temporary file
            fd, script_path = tempfile.mkstemp(suffix=".py")
            with os.fdopen(fd, 'w') as f:
                f.write(bpy_script)
                
            logging.info(f"[Blender Agent] BPY Script formulated. Spawning headless Blender process...")
            
            # Execute Blender in Background (Headless) Mode
            cmd = [self.blender_path, "-b", "-P", script_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Cleanup temp script
            os.remove(script_path)
            
            if result.returncode == 0:
                logging.info(f"🎨 [Blender Agent] 3D Asset successfully exported to {export_path}")
                return {"status": "success", "file": export_path}
            else:
                logging.error(f"❌ [Blender Agent] Blender Execution Failed:\n{result.stderr}")
                return {"status": "failed", "error": result.stderr}
                
        except Exception as e:
            logging.error(f"[Blender Agent] Internal Error: {e}")
            return {"status": "error", "message": str(e)}

    def generate_procedural_environment(self, biome_type: str, export_path: str) -> Dict[str, Any]:
        """Procedurally generates a terrain environment (e.g., 'mountains', 'desert')."""
        logging.info(f"[Blender Agent] Generating Procedural Environment: {biome_type}")
        bpy_script = f"""
import bpy
import os
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Generate procedural landscape
bpy.ops.mesh.primitive_grid_add(size=20, x_subdivisions=50, y_subdivisions=50)
terrain = bpy.context.active_object
terrain.name = 'Procedural_{biome_type}'

# Apply displacement modifier
mod = terrain.modifiers.new(name="Displacement", type='DISPLACE')
tex = bpy.data.textures.new("TerrainTex", type='CLOUDS')
tex.noise_scale = 1.5
tex.noise_depth = 2
mod.texture = tex
mod.strength = 2.5 if '{biome_type}' == 'mountains' else 0.5

# Export to OBJ
export_path = r'{export_path}'
bpy.ops.wm.obj_export(filepath=export_path)
print(f"JARVIS [Blender Agent]: Procedural terrain exported to {{export_path}}")
"""
        return self._run_headless_script(bpy_script, export_path)

    def render_scene(self, output_image_path: str) -> Dict[str, Any]:
        """Sets up lighting and renders the scene autonomously."""
        logging.info("[Blender Agent] Initiating rendering pipeline...")
        bpy_script = f"""
import bpy

# Setup Lighting
light_data = bpy.data.lights.new(name="SunLight", type='SUN')
light_data.energy = 5.0
light_obj = bpy.data.objects.new(name="SunLight", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (5.0, 5.0, 10.0)
light_obj.rotation_euler = (0.78, 0, 0.78)

# Setup Camera
cam_data = bpy.data.cameras.new(name="MainCam")
cam_obj = bpy.data.objects.new(name="MainCam", object_data=cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (0, -10, 5)
cam_obj.rotation_euler = (1.1, 0, 0)

# Setup Render Engine
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.render.filepath = r'{output_image_path}'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

bpy.ops.render.render(write_still=True)
print("JARVIS [Blender Agent]: Render complete.")
"""
        return self._run_headless_script(bpy_script, output_image_path)

    def _run_headless_script(self, script_content: str, expected_output: str) -> Dict[str, Any]:
        try:
            fd, script_path = tempfile.mkstemp(suffix=".py")
            with os.fdopen(fd, 'w') as f:
                f.write(script_content)
            
            cmd = [self.blender_path, "-b", "-P", script_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            os.remove(script_path)
            
            if result.returncode == 0:
                return {"status": "success", "file": expected_output}
            else:
                return {"status": "failed", "error": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
