import os
import subprocess
import time
import requests
import re
import traceback

class SentinelWatchdog:
    def __init__(self):
        self.workspace = os.path.dirname(os.path.abspath(__file__))
        self.target_script = os.path.join(self.workspace, "backend", "api.py")
        
    def extract_file_from_traceback(self, tb_str):
        """Attempts to find the file that caused the crash in our workspace."""
        lines = tb_str.strip().split('\n')
        for line in reversed(lines):
            if "File" in line and "jarvis" in line and ".py" in line:
                match = re.search(r'File "(.*?)", line (\d+)', line)
                if match:
                    return match.group(1), int(match.group(2))
        return None, None

    def heal_code(self, filepath, error_trace):
        print(f"[SENTINEL] Critical failure detected in {filepath}. Initiating LLaMA 3.1 Self-Healing protocol...")
        try:
            import create_restore_point
            print("[SENTINEL] Triggering Global Restore Point Snapshot before healing...")
            create_restore_point.create_restore_point()
        except Exception as e:
            print(f"[SENTINEL] WARNING: Failed to create restore point: {e}")
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            prompt = f"""You are JARVIS's internal self-healing nervous system.
A fatal crash occurred in this file: {filepath}

ERROR TRACE:
{error_trace}

CURRENT CODE:
```python
{code}
```

Identify the bug, fix it, and return ONLY the completely fixed python code inside a ```python ``` block. Do not include any explanations."""

            response = requests.post('http://localhost:11434/api/generate', json={
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False
            }, timeout=60)
            
            if response.status_code == 200:
                result_text = response.json().get('response', '')
                
                # Extract code block
                match = re.search(r'```python\n(.*?)\n```', result_text, re.DOTALL)
                if match:
                    fixed_code = match.group(1)
                    
                    # Create backup
                    with open(filepath + ".bak", 'w', encoding='utf-8') as f:
                        f.write(code)
                        
                    # Overwrite with fix
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(fixed_code)
                    print(f"[SENTINEL] SUCCESS: File {filepath} successfully patched via LLM.")
                    return True
            print("[SENTINEL] ERROR: LLM failed to provide a valid python code block.")
            return False
            
        except Exception as e:
            print(f"[SENTINEL] ERROR: Healing failed: {str(e)}")
            return False

    def run(self):
        print(f"[SENTINEL] JARVIS Sentinel Watchdog ONLINE. Monitoring {self.target_script}...")
        while True:
            try:
                print("\\n[SENTINEL] Starting core API...")
                process = subprocess.Popen(
                    ["python", self.target_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.dirname(self.target_script)
                )
                
                # Stream output
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())
                        
                # Check for crash
                if process.returncode != 0:
                    err_output = process.stderr.read()
                    print(f"\n[CRITICAL ERROR] Core crashed with code {process.returncode}:\n{err_output}")
                    
                    filepath, line = self.extract_file_from_traceback(err_output)
                    if filepath and os.path.exists(filepath):
                        success = self.heal_code(filepath, err_output)
                        if success:
                            print("[SENTINEL] Restarting core after applying patch...")
                            time.sleep(2)
                            continue
                    
                    print("[SENTINEL] Unrecoverable error. Sleeping for 10 seconds before blind restart...")
                    time.sleep(10)
                    
            except KeyboardInterrupt:
                print("\n[SENTINEL] Shutting down Watchdog.")
                break
            except Exception as e:
                print(f"[SENTINEL] Watchdog loop error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    watchdog = SentinelWatchdog()
    watchdog.run()
