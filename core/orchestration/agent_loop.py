import json
import logging
from core.cognition.reasoning.cloud_llm import cloud_llm_provider
from core.orchestration.agent_tools import AGENT_TOOLS

logging.basicConfig(level=logging.INFO)

class ReActAgent:
    def __init__(self, max_iterations=5):
        self.max_iterations = max_iterations

    async def run(self, task: str) -> str:
        """Runs the ReAct Loop (Reason + Act) until the task is solved."""
        history = []
        
        system_prompt = (
            "You are an autonomous engineering agent with access to tools. "
            "Your available tools are:\n"
            "- read_file(file_path)\n"
            "- write_file(file_path, content)\n"
            "- run_bash_command(command, cwd='.')\n"
            "- grep_search(pattern, search_path='.')\n\n"
            "Respond ONLY with a JSON object in this format:\n"
            "{\n"
            '  "thought": "your reasoning step",\n'
            '  "action": "tool_name OR COMPLETE",\n'
            '  "args": {"arg_name": "arg_value"}\n'
            "}"
        )

        for i in range(self.max_iterations):
            history_str = "\n".join(history)
            prompt = f"Task: {task}\n\nExecution History:\n{history_str}\n\nNext step?"
            
            logging.info(f"[ReAct] Iteration {i+1}/{self.max_iterations}")
            
            # Prefer groq for fast reasoning
            res = None
            if cloud_llm_provider.groq_active:
                res = await cloud_llm_provider.call_groq(prompt, system_prompt)
            
            if not res:
                return "Failed to get LLM response for ReAct loop."

            thought = res.get("thought", "")
            action = res.get("action", "COMPLETE")
            args = res.get("args", {})

            logging.info(f"🤔 Thought: {thought}")
            history.append(f"Thought: {thought}")

            if action == "COMPLETE":
                logging.info(f"✅ Agent completed task.")
                return f"Task Completed. Final Thought: {thought}"

            if action in AGENT_TOOLS:
                logging.info(f"🛠️ Executing: {action}({args})")
                try:
                    tool_func = AGENT_TOOLS[action]
                    observation = tool_func(**args)
                    logging.info(f"👁️ Observation: (length {len(observation)})")
                    history.append(f"Action: {action}({args})\nObservation: {observation}")
                except Exception as e:
                    logging.error(f"Tool execution failed: {e}")
                    history.append(f"Action: {action}({args})\nObservation: ERROR: {e}")
            else:
                logging.warning(f"Unknown action requested: {action}")
                history.append(f"Action: {action}\nObservation: ERROR - Unknown Tool")

        return "Agent exceeded max iterations without completing the task."
