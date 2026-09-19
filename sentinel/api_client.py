import requests
from colorama import Fore
from core.reliability.system_logger import system_logger

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def send_wake_event(self, timestamp):
        try:
            payload = {"event": "WAKE_WORD_DETECTED", "timestamp": timestamp}
            res = requests.post(f"{self.base_url}/wake", json=payload, timeout=2.0)
            if res.status_code == 200:
                print(Fore.GREEN + "[API] Wake signal accepted.")
            else:
                print(Fore.YELLOW + f"[API] Unexpected response: {res.status_code}")
        except requests.exceptions.RequestException as e:
            system_logger.log('ERROR', 'api_client', f'API Error: {e}')
            print(Fore.RED + "[API] Disconnected.")
