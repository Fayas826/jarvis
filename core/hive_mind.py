import os
import requests
import asyncio
from dotenv import load_dotenv
from core.orchestration.game_dev_agent import game_dev_agent

load_dotenv()

class HiveMindOrchestrator:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
    def process_prompt(self, user_prompt, selected_model="hive_mind"):
        """Routes the prompt based on the dropdown selection."""
        print(f"[HIVE MIND] Incoming prompt routed to: {selected_model.upper()}")
        
        if selected_model == "jarvis_local":
            return self._run_local_alpha_core(user_prompt)
        elif selected_model == "claude":
            return self._run_claude_api(user_prompt)
        elif selected_model == "openai":
            return self._run_openai_api(user_prompt)
        elif selected_model == "hive_mind":
            return self._execute_swarm_logic(user_prompt)
        else:
            return "Model not recognized."

    def _execute_swarm_logic(self, prompt):
        print("[HIVE MIND] Initiating Swarm Protocol. Delegating tasks...")
        
        # Game Dev Routing
        game_keywords = ["blender", "render", "unity", "unreal", "godot", "3d model"]
        if any(keyword in prompt.lower() for keyword in game_keywords):
            print("[HIVE MIND] Game Development Context Detected. Routing to GameDevAgent...")
            try:
                # Synchronously run the async execute_task for integration simplicity
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(game_dev_agent.execute_task(prompt))
                return f"[JARVIS GAME DEV] Task Executed. Status: {result['status']}. Logs: {result.get('log', 'Code generated.')}"
            except Exception as e:
                return f"[JARVIS GAME DEV] Error invoking Game Dev Agent: {str(e)}"
        
        # In a real swarm, JARVIS would parse the prompt and split it. 
        # For now, we ask both models the same question and combine them.
        claude_response = self._run_claude_api(prompt)
        openai_response = self._run_openai_api(prompt)
        
        print("[HIVE MIND] Swarm tasks complete. Synthesizing final response...")
        final_answer = f"[JARVIS ALPHA] I have consulted the hive.\n\n[CLAUDE'S ANALYSIS]:\n{claude_response}\n\n[OPENAI'S ANALYSIS]:\n{openai_response}\n\n[JARVIS CONCLUSION]: The data is compiled. Proceeding as commanded."
        return final_answer
        
    def _run_local_alpha_core(self, prompt):
        return "[JARVIS ALPHA] Local Neural Network activated. Processing natively on GPU."
        
    def _run_claude_api(self, prompt):
        if not self.anthropic_key or "your_" in self.anthropic_key.lower():
            return "[ERROR] Missing Anthropic API Key in .env file."
            
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": "claude-3-5-sonnet-20240620",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            print("[CLAUDE] Reaching out to Anthropic servers...")
            response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
            return response.json().get('content', [{}])[0].get('text', "No response")
        except Exception as e:
            return f"Claude API Failed: {e}"
        
    def _run_openai_api(self, prompt):
        if not self.openai_key or "your_" in self.openai_key.lower():
            return "[ERROR] Missing OpenAI API Key in .env file."
            
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            print("[OPENAI] Reaching out to OpenAI servers...")
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            return response.json().get('choices', [{}])[0].get('message', {}).get('content', "No response")
        except Exception as e:
            return f"OpenAI API Failed: {e}"

if __name__ == "__main__":
    # Test script
    hive = HiveMindOrchestrator()
    print(hive.process_prompt("What is 2+2?", "hive_mind"))
