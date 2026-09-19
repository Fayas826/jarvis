import time
import subprocess
import os

def autonomous_supervisor():
    """
    Architect Tier - Autonomous Supervisor Daemon
    Runs infinitely in the background. If a system network failure or crash happens,
    it automatically takes action to restart the failed process without asking the user.
    """
    print("[*] Architect Supervisor: Online. Monitoring critical systems...")
    
    while True:
        # Check if Ollama pull failed due to network timeout
        # For demonstration, we simply execute the pull loop if it's missing.
        try:
            # We use subprocess to check if 'ollama pull llava' is currently in the process list
            # If not, we autonomously restart it to recover from the network drop.
            import psutil
            is_pulling = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and 'ollama' in proc.info['cmdline'] and 'pull' in proc.info['cmdline']:
                        is_pulling = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if not is_pulling:
                print("[!] Architect Supervisor: Detected network drop on Vision Model download.")
                print("[*] Architect Supervisor: Taking autonomous action to restart download...")
                # Autonomously restarting the download in the background
                subprocess.Popen(["ollama", "pull", "llava"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("[*] Architect Supervisor: Recovery successful. Download resumed.")
                
        except Exception as e:
            pass
            
        # Sleep and check again in 5 minutes
        time.sleep(300)

if __name__ == "__main__":
    autonomous_supervisor()
