import os
import base64
from core.perception.screen_capture import screen_capturer
from core.orchestration.agent_state_machine import state_machine

class ObserverPipeline:
    @staticmethod
    async def observe(task_description: str):
        """Captures the screen and transitions state machine."""
        state_machine.transition_to("OBSERVING", task_description, "Capturing screenshot")
        before_frame = await screen_capturer.capture_frame_async()
        
        # Save temp frame for VLM chat
        temp_before = "data/temp/before_state.png"
        os.makedirs("data/temp", exist_ok=True)
        with open(temp_before, "wb") as f:
            f.write(base64.b64decode(before_frame.image))
            
        return before_frame, temp_before

observer_pipeline = ObserverPipeline()
