import os
import json
from typing import Dict, Any, List

PROJECT_MEMORY_DIR = "project_memory"

class ContextCompressor:
    """Monitors token budget usages and compresses execution histories."""

    def compress_history(self) -> float:
        """
        Compresses completed task details from execution history into key summaries
        inside project_memory/decisions.json, clearing up active buffer space.
        """
        history_path = os.path.join(PROJECT_MEMORY_DIR, "execution_history.json")
        decisions_path = os.path.join(PROJECT_MEMORY_DIR, "decisions.json")
        
        if not os.path.exists(history_path):
            return 0.0
            
        try:
            with open(history_path, "r") as f:
                history = json.load(f)
                
            if len(history) > 10:
                print(f"[COMPRESSOR] Compressing {len(history)} history events.")
                decisions = []
                if os.path.exists(decisions_path):
                    with open(decisions_path, "r") as f:
                        decisions = json.load(f)
                        
                # Extract simple decision facts to store in long-term memory
                for event in history:
                    decisions.append({
                        "timestamp": event.get("timestamp"),
                        "decision": f"Completed task {event.get('task_id')}: {event.get('objective')}"
                    })
                    
                with open(decisions_path, "w") as f:
                    json.dump(decisions[-50:], f, indent=2)
                    
                # Empty active history buffer
                with open(history_path, "w") as f:
                    json.dump([], f)
                    
                return 1.0 # budget reset indicator
        except Exception as e:
            print(f"[COMPRESSOR] Compression failed: {e}")
            
        return 0.0

context_compressor = ContextCompressor()
