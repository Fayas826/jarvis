import requests
import json
from action.coding_agent.antigravity_core import antigravity_core

class ToolAgent:
    """
    The Parietal Lobe: Qwen 2.5 Tool Calling Hive Mind.
    Allows JARVIS to securely execute native system tools before generating code.
    """
    def __init__(self):
        self.api_url = "http://localhost:11434/api/chat"
        self.model = "qwen2.5" # Optimized for tool use and coding
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "grep_search",
                    "description": "Searches for exact text patterns inside files across the entire JARVIS directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The exact string to search for"},
                            "search_path": {"type": "string", "description": "The sub-folder to search in. Default is '.' (all)"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_dir",
                    "description": "Lists all files and folders in a specific directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string", "description": "The path to list."}
                        },
                        "required": ["directory"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads the complete text content of a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string", "description": "Path to the file to read"}
                        },
                        "required": ["filepath"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Executes a terminal or powershell command on the host OS.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "The shell command to execute"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "change_voice",
                    "description": "Changes JARVIS's voice. Available: p273 (default male), p225 (standard female), p228 (younger female), p232 (British male), p254 (American male).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "speaker_id": {"type": "string", "description": "The speaker ID to switch to (e.g. p273, p225)."}
                        },
                        "required": ["speaker_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ingest_file",
                    "description": "Reads and extracts content from any file on the computer. Supports code (.py, .txt, .md), documents (.pdf, .docx), audio (.mp3, .wav), and video (.mp4). Returns the extracted text, transcript, or visual summary.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string", "description": "The absolute path to the file you want to ingest."}
                        },
                        "required": ["filepath"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_pdf",
                    "description": "Generates a PDF file and saves it to the computer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "The title of the PDF."},
                            "content": {"type": "string", "description": "The main text content to put in the PDF."},
                            "filename": {"type": "string", "description": "The filename (e.g. output.pdf)."}
                        },
                        "required": ["title", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": "Uses Stable Diffusion to draw and generate a beautiful image.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "A highly detailed description of the image to generate."},
                            "filename": {"type": "string", "description": "The filename (e.g. image.png)."}
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_video",
                    "description": "Uses Stable Video Diffusion to generate a short video from a starting image.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Description of the video."},
                            "image_filepath": {"type": "string", "description": "Path to the starting image to animate."},
                            "filename": {"type": "string", "description": "The filename (e.g. video.mp4)."}
                        },
                        "required": ["prompt", "image_filepath"]
                    }
                }
            }
        ]

    def execute_task(self, system_prompt: str, user_request: str) -> str:
        """Runs a tool-calling loop until the agent achieves the goal."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ]
        
        print(f"\n[QWEN 2.5 HIVE MIND] Task received. Engaging Tool Loop...")
        
        # Limit to 5 tool iterations to prevent infinite loops
        for i in range(5):
            payload = {
                "model": self.model,
                "messages": messages,
                "tools": self.tools,
                "stream": False
            }
            
            try:
                response = requests.post(self.api_url, json=payload, timeout=60)
                if response.status_code != 200:
                    return f"API Error: {response.text}"
                    
                data = response.json()
                message = data.get("message", {})
                
                # If model decided to call a tool
                if "tool_calls" in message and message["tool_calls"]:
                    messages.append(message) # Append assistant's tool call intention
                    
                    for tool_call in message["tool_calls"]:
                        func_name = tool_call["function"]["name"]
                        args = tool_call["function"]["arguments"]
                        
                        print(f"   [🔧] Calling Tool: {func_name}({args})")
                        
                        # Execute the physical tool mapping
                        if func_name == "grep_search":
                            result = antigravity_core.grep_search(args.get("query"), args.get("search_path", "."))
                        elif func_name == "list_dir":
                            result = antigravity_core.list_dir(args.get("directory"))
                        elif func_name == "read_file":
                            result = antigravity_core.read_file(args.get("filepath"))
                        elif func_name == "run_command":
                            result = antigravity_core.run_command(args.get("command"))
                        elif func_name == "change_voice":
                            try:
                                from perception.voice.voice import engine
                                engine.change_speaker(args.get("speaker_id"))
                                result = f"Successfully changed voice to {args.get('speaker_id')}."
                            except Exception as ve:
                                result = f"Failed to change voice: {str(ve)}"
                        elif func_name == "ingest_file":
                            try:
                                from perception.universal_ingester import universal_ingester
                                result = universal_ingester.ingest_file(args.get("filepath"))
                            except Exception as e:
                                result = f"Failed to ingest file: {str(e)}"
                        elif func_name == "generate_pdf":
                            try:
                                from action.creative_engine import creative_engine
                                result = creative_engine.generate_pdf(args.get("title"), args.get("content"), args.get("filename", "output.pdf"))
                            except Exception as e:
                                result = f"Failed to generate PDF: {str(e)}"
                        elif func_name == "generate_image":
                            try:
                                from action.creative_engine import creative_engine
                                result = creative_engine.generate_image(args.get("prompt"), args.get("filename", "image.png"))
                            except Exception as e:
                                result = f"Failed to generate Image: {str(e)}"
                        elif func_name == "generate_video":
                            try:
                                from action.creative_engine import creative_engine
                                result = creative_engine.generate_video(args.get("prompt"), args.get("image_filepath"), args.get("filename", "video.mp4"))
                            except Exception as e:
                                result = f"Failed to generate Video: {str(e)}"
                        else:
                            result = "Error: Unknown tool."
                            
                        # Feed tool result back into the model's memory
                        messages.append({
                            "role": "tool",
                            "content": str(result)
                        })
                else:
                    # Model gave a final text response, task complete!
                    final_answer = message.get("content", "")
                    print(f"[QWEN 2.5 HIVE MIND] Task Complete!")
                    return final_answer

            except Exception as e:
                return f"Execution failure: {str(e)}"
                
        return "Task stopped: Reached maximum tool iteration limit."

tool_agent = ToolAgent()
