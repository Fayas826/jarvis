"""
Phase 5 — Modular Sentinel Entry Point
"""

import os
from dotenv import load_dotenv
from sentinel.audio_hardware import verify_singleton, cleanup_lock
from sentinel.api_client import APIClient

BASE_DIR = r"c:\jarvis AI\jarvis"
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

API_URL = f"http://127.0.0.1:{os.getenv('SENTINEL_API_PORT', '5001')}"

def main():
    lock_file = verify_singleton()
    if not lock_file:
        return
    client = APIClient(API_URL)
    print(f"Sentinel running with API endpoint: {API_URL}")
    try:
        pass # The loop would go here
    finally:
        cleanup_lock(lock_file)

if __name__ == "__main__":
    main()
