import mss
import mss.tools
import base64
import os
import logging
from typing import Dict, Any

class VisionQAAgent:
    """
    Self-Healing Swarm Member: The Eyes.
    Captures screenshots and passes them to a Vision Language Model (VLM)
    to detect visual bugs, CSS misalignment, and 3D rendering errors.
    """
    
    def __init__(self, temp_dir="c:/jarvis AI/jarvis/scratch/"):
        self.temp_dir = temp_dir
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
    def _capture_screen(self) -> str:
        """Takes a screenshot using MSS and returns the file path."""
        file_path = os.path.join(self.temp_dir, "vision_qa_capture.png")
        with mss.mss() as sct:
            # Capture primary monitor
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=file_path)
        logging.info(f"[Vision QA] Screen captured at {file_path}")
        return file_path
        
    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_ui_for_bugs(self, target_context: str = "CSS Alignment") -> Dict[str, Any]:
        """
        Takes a screenshot, encodes it, and queries the VLM to find visual bugs.
        """
        logging.info("[Vision QA] Activating VLM Bug Detection...")
        
        screenshot_path = self._capture_screen()
        base64_image = self._encode_image(screenshot_path)
        
        # Here we would send `base64_image` to Qwen-VL or GPT-4o
        # Mocking the VLM response for now.
        
        vlm_prompt = f"Analyze this image for {target_context} bugs. Return exact (x, y) coordinates of the issue."
        
        # Simulated VLM response
        mock_vlm_response = {
            "bug_detected": True,
            "description": "The primary 'Submit' button is overlapping with the footer text.",
            "coordinates": {"x": 840, "y": 950},
            "suggested_fix": "Increase margin-bottom on the main container by 20px."
        }
        
        logging.info(f"[Vision QA] VLM Diagnosis Complete: {mock_vlm_response['description']}")
        
        return mock_vlm_response
