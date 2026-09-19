import os
import time
import subprocess
import json
import requests

def log(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [JARVIS OMNI-AGENT] {msg}", flush=True)

class JarvisOmniAgent:
    def __init__(self):
        self.workspace = r"c:\jarvis AI\jarvis"
        self.api_url = "http://localhost:8080/v1/chat/completions" # JARVIS Local Omni-Model Endpoint
        self.max_burn_tokens = 1000000 # "Burn tokens if needed"
        self.token_count = 0
        
    def tool_read_file(self, filepath):
        try:
            with open(os.path.join(self.workspace, filepath), 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return str(e)
            
    def tool_write_file(self, filepath, content):
        try:
            with open(os.path.join(self.workspace, filepath), 'w', encoding='utf-8') as f:
                f.write(content)
            return "File updated successfully."
        except Exception as e:
            return str(e)
            
    def tool_execute_terminal(self, command):
        # HARD CONSTRAINT: Docker Pause
        if "docker" in command.lower():
            return "Error: Docker commands are explicitly blocked by User override."
        try:
            result = subprocess.run(command, cwd=self.workspace, capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace')
            return f"Exit Code: {result.returncode}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        except Exception as e:
            return str(e)

    def call_omni_model(self, prompt):
        log("Thinking... (Burning tokens via JARVIS Omni-Model)")
        self.token_count += len(prompt) // 4
        
        # In absolute reality, this executes an HTTP request to the local LLM.
        # Since the 1M dataset is still training, we mock the LLM JSON response here.
        # But this exact code structure (ReAct Loop) is identical to LangChain/AutoGPT.
        try:
            # response = requests.post(self.api_url, json={"messages": [{"role": "user", "content": prompt}]})
            # return response.json()['choices'][0]['message']['content']
            
            time.sleep(2)
            # Simulated Agent Reasoning:
            simulated_response = {
                "thought": "I need to check the backend test logs to find the bug.",
                "action": "execute_terminal",
                "action_input": "npm test"
            }
            return json.dumps(simulated_response)
        except Exception as e:
            log(f"API Error: {e}")
            return None

    def start_infinite_loop(self):
        log("=" * 70)
        log(" JARVIS OMNI-AGENT INITIATED ")
        log("    [MODE: Autonomous System Control]")
        log("    [DOCKER COMMANDS: STRICTLY BLOCKED]")
        log("=" * 70)
        
        current_state = "Wake up. Initialize system audit."
        
        while True:
            log(f"\n--- TOKENS BURNED: {self.token_count} / {self.max_burn_tokens} ---")
            
            # 1. Ask the Brain what to do
            llm_json = self.call_omni_model(current_state)
            if not llm_json:
                time.sleep(10)
                continue
                
            try:
                plan = json.loads(llm_json)
                log(f"Thought: {plan.get('thought')}")
                
                action = plan.get('action')
                action_input = plan.get('action_input')
                
                log(f"Action Executing: {action}('{action_input}')")
                
                # 2. Execute the physical tool
                if action == "execute_terminal":
                    result = self.tool_execute_terminal(action_input)
                elif action == "read_file":
                    result = self.tool_read_file(action_input)
                elif action == "write_file":
                    # Simulated parsing for multi-args
                    result = self.tool_write_file(action_input, "mock_content")
                else:
                    result = "Unknown tool requested."
                
                # 3. Feed the physical result back into the Brain
                current_state = f"Tool result: {result[:500]}... What is the next step?"
                
            except json.JSONDecodeError:
                log("LLM returned malformed JSON. Requesting fix...")
                current_state = "Return strict JSON format only."
                
            log("Resting neural matrix for 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    agent = JarvisOmniAgent()
    agent.start_infinite_loop()
