from core.perception.gui_grounding import vision_grounder
from core.perception.coordinate_mapper import coordinate_mapper
from core.orchestration.agent_state_machine import state_machine

class GrounderPipeline:
    @staticmethod
    async def ground(task_description: str, target: str, before_frame: 'ScreenFrame') -> dict:
        state_machine.transition_to("GROUNDING", task_description, "Resolving target coordinates")
        element = await vision_grounder.find_target(before_frame, target)
        
        coords = None
        mapped_coords = None
        confidence_score = 40
        bounding_boxes = []
        element_source = "none"
        
        if element:
            coords = element.center
            confidence_score = int(element.confidence * 100)
            element_source = element.source
            bounding_boxes = [{
                "label": target,
                "coords": element.center,
                "bbox": element.bbox,
                "source": element.source
            }]
            mapped_coords = list(coordinate_mapper.map_coords(
                coords[0], coords[1], before_frame.width, before_frame.height
            ))
            
        return {
            "coords": coords,
            "mapped_coords": mapped_coords,
            "confidence_score": confidence_score,
            "bounding_boxes": bounding_boxes,
            "element_source": element_source,
            "element": element
        }

grounder_pipeline = GrounderPipeline()
