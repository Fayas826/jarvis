import os
import subprocess
import json

class AntigravityCore:
    """
    JARVIS Antigravity Core (Software Engineer Agent)
    Allows JARVIS to execute arbitrary commands, read, and write files on the host machine.
    """
    def __init__(self):
        self.workspace = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    def run_command(self, command: str) -> str:
        """Executes a terminal command and returns the output."""
        try:
            print(f"[ANTIGRAVITY] Running command: {command}")
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=self.workspace, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return f"Command executed. Output:\n{output}"
        except Exception as e:
            return f"Failed to execute command: {str(e)}"

    def write_file(self, filepath: str, content: str) -> str:
        """Writes content to a file."""
        try:
            # Ensure path is relative to workspace or absolute
            target = os.path.join(self.workspace, filepath) if not os.path.isabs(filepath) else filepath
            
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(target), exist_ok=True)
            
            with open(target, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[ANTIGRAVITY] Wrote to file: {target}")
            return f"Successfully wrote to {target}"
        except Exception as e:
            return f"Failed to write file: {str(e)}"

    def read_file(self, filepath: str) -> str:
        """Reads content from a file."""
        try:
            target = os.path.join(self.workspace, filepath) if not os.path.isabs(filepath) else filepath
            with open(target, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Failed to read file: {str(e)}"

    def grep_search(self, query: str, search_path: str = ".") -> str:
        """Searches for exact text patterns inside files in a directory."""
        try:
            target = os.path.join(self.workspace, search_path) if not os.path.isabs(search_path) else search_path
            # Very basic native grep equivalent using python for cross-platform
            results = []
            for root, _, files in os.walk(target):
                if '.git' in root or 'node_modules' in root or '__pycache__' in root:
                    continue
                for file in files:
                    if file.endswith(('.py', '.js', '.jsx', '.json', '.md', '.txt')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                for i, line in enumerate(f):
                                    if query in line:
                                        rel_path = os.path.relpath(filepath, self.workspace)
                                        results.append(f"{rel_path}:{i+1}: {line.strip()}")
                                        if len(results) > 50:
                                            return "\n".join(results) + "\n...[Too many results, truncated]"
                        except Exception as e:
                            from core.reliability.system_logger import system_logger
                            system_logger.log('ERROR', 'antigravity_core', f'Unhandled exception: {e}')
                            continue
            if not results:
                return "No matches found."
            return "\n".join(results)
        except Exception as e:
            return f"Failed to search: {str(e)}"

    def list_dir(self, directory: str = ".") -> str:
        """Lists files and folders in a directory."""
        try:
            target = os.path.join(self.workspace, directory) if not os.path.isabs(directory) else directory
            items = os.listdir(target)
            result = []
            for item in items:
                path = os.path.join(target, item)
                if os.path.isdir(path):
                    result.append(f"[DIR]  {item}")
                else:
                    result.append(f"[FILE] {item}")
            return "\n".join(result)
        except Exception as e:
            return f"Failed to list directory: {str(e)}"

antigravity_core = AntigravityCore()
