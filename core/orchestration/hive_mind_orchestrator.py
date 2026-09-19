import requests
from action.coding_agent.tool_agent import tool_agent

class HiveMindOrchestrator:
    """
    JARVIS Hive Mind Router.
    Analyzes prompts and routes them to the correct lob of the brain.
    - Prefrontal Cortex: LLaMA 3.1 (Conversation)
    - Parietal Lobe: Qwen 2.5 (Coding & Tool Calling via tool_agent)
    """
    def __init__(self):
        self.router_url = "http://localhost:11434/api/generate"
        self.router_model = "phi3" # Ultra fast tiny model just for routing classification

    def route_request(self, user_prompt: str, context: str = "") -> str:
        print("[HIVE_MIND] Analyzing request routing...")
        
        # 1. Ask Phi-3 to classify the request
        classify_prompt = f"""You are a router. The user said: "{user_prompt}"
Does this require writing code, fixing a bug, searching files, or executing system commands?
Answer with EXACTLY the word "CODE" or "CHAT"."""

        try:
            resp = requests.post(self.router_url, json={
                "model": self.router_model,
                "prompt": classify_prompt,
                "stream": False
            }, timeout=10)
            
            classification = resp.json().get('response', '').strip().upper()
            
            if "CODE" in classification or "FIX" in classification or "SEARCH" in classification:
                print("[HIVE_MIND] Routing to Parietal Lobe (Qwen 2.5 Tool Agent)...")
                return tool_agent.execute_task(
                    system_prompt="You are JARVIS's technical lobe. Fix code, search files, and run commands as needed.",
                    user_request=user_prompt + f"\nContext: {context}"
                )
            else:
                print("[HIVE_MIND] Routing to Prefrontal Cortex (LLaMA 3.1 Conversation)...")
                # Route to pure conversation
                chat_resp = requests.post("http://localhost:11434/api/generate", json={
                    "model": "llama3.1",
                    "prompt": f"You are JARVIS. Answer this: {user_prompt}",
                    "stream": False
                }, timeout=30)
                return chat_resp.json().get('response', '')
                
        except Exception as e:
            print(f"[HIVE_MIND] Router Failure, defaulting to LLaMA 3.1: {e}")
            chat_resp = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3.1",
                "prompt": f"You are JARVIS. Answer this: {user_prompt}",
                "stream": False
            }, timeout=30)
            return chat_resp.json().get('response', '')

hive_mind_orchestrator = HiveMindOrchestrator()
