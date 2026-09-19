import time
import subprocess
import requests
import logging

logging.basicConfig(
    filename='c:/jarvis AI/jarvis/infrastructure/daemon.log',
    level=logging.INFO,
    format='%(asctime)s - [SENTINEL] - %(message)s'
)

API_URL = "http://127.0.0.1:8000/docs"
BACKEND_SCRIPT = "c:/jarvis AI/jarvis/backend/main.py"
UVICORN_CMD = ["uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]

def start_backend():
    logging.info("Initiating JARVIS Core Backend in Stealth Mode...")
    # Suppress console output for true stealth
    return subprocess.Popen(
        UVICORN_CMD, 
        cwd="c:/jarvis AI/jarvis",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True
    )

def main():
    logging.info("Sentinel Watchdog Agent Online. Monitoring Core Systems.")
    
    # 1. Start Biometrics Listener
    import sys
    sys.path.append("c:/jarvis AI/jarvis")
    from core.perception.biometrics_agent import BiometricsAudioAgent
    biometrics = BiometricsAudioAgent()
    biometrics.start_listening()

    # 2. Start Core API Backend
    backend_process = start_backend()
    
    while True:
        try:
            # Ping the FastAPI server to ensure it's alive
            response = requests.get(API_URL, timeout=3)
            if response.status_code != 200:
                raise Exception(f"API Returned {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Core Backend Unresponsive! Triggering Self-Healing Restart. Error: {e}")
            if backend_process.poll() is None:
                backend_process.terminate()
            backend_process = start_backend()
            
        # Check every 5 seconds
        time.sleep(5)

if __name__ == "__main__":
    main()
