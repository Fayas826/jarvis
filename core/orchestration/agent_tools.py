import os
import subprocess
import glob

def read_file(file_path: str, max_lines: int = 500) -> str:
    """Read contents of a file."""
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) > max_lines:
                return "".join(lines[:max_lines]) + f"\n... (truncated {len(lines) - max_lines} lines)"
            return "".join(lines)
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(file_path: str, content: str) -> str:
    """Write contents to a file."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"

def run_bash_command(command: str, cwd: str = ".") -> str:
    """Execute a bash command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        if not output.strip():
            return "Command executed successfully with no output."
        return output[:2000] # truncate long outputs
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {e}"

def grep_search(pattern: str, search_path: str = ".") -> str:
    """Search for a pattern in files."""
    try:
        # Simple cross-platform grep equivalent in python
        results = []
        for root, _, files in os.walk(search_path):
            if "node_modules" in root or ".venv" in root or ".git" in root:
                continue
            for file in files:
                if not file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.md', '.json')):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f):
                            if pattern in line:
                                results.append(f"{file_path}:{i+1}: {line.strip()}")
                except:
                    pass
        
        if not results:
            return "No matches found."
        
        output = "\n".join(results)
        return output[:2000] + ("\n...(truncated)" if len(output) > 2000 else "")
    except Exception as e:
        return f"Error during search: {e}"

AGENT_TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "run_bash_command": run_bash_command,
    "grep_search": grep_search
}
