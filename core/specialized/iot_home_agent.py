import logging
from typing import Dict, Any

try:
    import requests
except ImportError:
    requests = None

class IoTHomeAgent:
    """
    JARVIS Specialized Swarm Member: The Electrician.
    Connects to physical IoT devices (Smart Plugs, Lights) via MQTT or REST API 
    (like Home Assistant or Tuya) to control real-world environments.
    """
    
    def __init__(self, hub_url: str = "http://localhost:8123/api", api_token: str = "MOCK_TOKEN"):
        self.hub_url = hub_url
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def toggle_device(self, entity_id: str = "switch.desk_lamp", state: str = "toggle") -> Dict[str, Any]:
        """
        Sends an HTTP POST request to the smart home hub to turn a device ON or OFF.
        state can be 'turn_on', 'turn_off', or 'toggle'.
        """
        if not requests:
            return {"status": "error", "message": "Requests library missing."}
            
        logging.info(f"🔌 [IoT Agent] Transmitting Wi-Fi signal to physical device: {entity_id}")
        
        # Determine the Home Assistant service endpoint
        service = state.lower()
        if service not in ['turn_on', 'turn_off', 'toggle']:
            service = 'toggle'
            
        endpoint = f"{self.hub_url}/services/homeassistant/{service}"
        payload = {"entity_id": entity_id}
        
        # We wrap this in a mock mode since the user might not have a live hub running at localhost:8123 yet.
        if self.api_token == "MOCK_TOKEN":
            logging.warning(f"🔌 [IoT Agent] SANDBOX MODE: Physically toggled {entity_id} to {state.upper()}!")
            return {"status": "success", "simulated": True, "entity": entity_id, "state": state}
            
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=3)
            response.raise_for_status()
            logging.info(f"💡 [IoT Agent] Successfully toggled physical device: {entity_id}")
            return {"status": "success", "response": response.json()}
            
        except Exception as e:
            logging.error(f"❌ [IoT Agent] Failed to connect to Smart Hub: {e}")
            return {"status": "failed", "error": str(e)}
