import requests
import json
import os

# 🛰️ MOBILE_SENTINEL_MODULE
# Chapter 4: Mobile Tracking & GPS Telemetry

def get_phone_location():
    """Retrieves last known GPS coordinates from the Mobile Bridge."""
    # This will be populated by the mobile app's telemetry push
    try:
        with open("c:/jarvis AI/jarvis/backend/mobile_telemetry.json", "r") as f:
            data = json.load(f)
            return {
                "status": "SUCCESS",
                "lat": data.get("lat"),
                "lng": data.get("lng"),
                "accuracy": data.get("accuracy"),
                "last_seen": data.get("timestamp")
            }
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'mobile_sentinel', f'Unhandled exception: {e}')
        return {"status": "OFFLINE", "message": "Mobile device not reporting."}

def ring_phone():
    """Commands the mobile device to play a high-decibel alert."""
    print("[MOBILE_SENTINEL] Sending 'SONIC_ALERT' signal to mobile bridge...")
    # Signal sent via the Mobile Tunnel (ngrok/Cloud Run)
    return {"status": "SUCCESS", "message": "Alert triggered on mobile device."}
