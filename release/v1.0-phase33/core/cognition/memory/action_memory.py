import os
import json
import time
from typing import Dict, Any, List, Optional

PROJECT_MEMORY_DIR = "project_memory"

class ActionMemory:
    """Manages Action Memory recipes for caching and reusing successful workflows."""

    def __init__(self):
        os.makedirs(PROJECT_MEMORY_DIR, exist_ok=True)
        self.recipes_path = os.path.join(PROJECT_MEMORY_DIR, "action_memory.json")

    def load_recipes(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.recipes_path):
            try:
                with open(self.recipes_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                from core.reliability.system_logger import system_logger
                system_logger.log('ERROR', 'action_memory', f'Unhandled exception: {e}')
                return []
        return []

    def save_recipes(self, recipes: List[Dict[str, Any]]):
        with open(self.recipes_path, "w") as f:
            json.dump(recipes, f, indent=2)

    def learn_recipe(self, intent: str, app: str, action_sequence: List[Dict[str, Any]], verification_condition: str):
        """Learns and registers a successful workflow recipe."""
        recipes = self.load_recipes()
        
        # Check for duplicates
        for r in recipes:
            if r.get("intent").lower() == intent.lower() and r.get("application").lower() == app.lower():
                r["success_rate"] = min(1.0, r.get("success_rate", 1.0) + 0.05)
                r["reuse_count"] = r.get("reuse_count", 0) + 1
                r["last_used"] = time.time()
                self.save_recipes(recipes)
                print(f"[ACTION_MEMORY] Updated success rate and reuse count for recipe: {intent}")
                return

        new_recipe = {
            "recipe_id": f"rec_{int(time.time())}",
            "intent": intent,
            "application": app,
            "action_sequence": action_sequence,
            "verification_condition": verification_condition,
            "success_rate": 1.0,
            "reuse_count": 0,
            "last_used": time.time()
        }
        
        recipes.append(new_recipe)
        self.save_recipes(recipes)
        print(f"[ACTION_MEMORY] Logged new successful recipe: {intent}")

    def query_recipe(self, intent: str, app: str) -> Optional[Dict[str, Any]]:
        """Queries for a cached successful workflow matching intent and app constraints."""
        recipes = self.load_recipes()
        for r in recipes:
            if r.get("intent").lower() == intent.lower() and r.get("application").lower() == app.lower():
                return r
        return None

action_memory = ActionMemory()
