"""
JARVIS ADB PATTERN VIDEO RECORDER & VISUAL EXTRACTOR
=====================================================
1. Starts ADB screenrecord for 10s
2. User draws pattern on phone
3. Pulls MP4 video to c:\jarvis AI\jarvis\scratch\pattern_record.mp4
4. Analyzes swipe motion & updates mobile_security_config.json
"""

import subprocess
import time
import os
import json
import logging

ADB_PATH = r"C:\AMD\platform-tools\adb.exe"
CONFIG_PATH = r"c:\jarvis AI\jarvis\data\mobile_security_config.json"
OUTPUT_MP4 = r"c:\jarvis AI\jarvis\scratch\pattern_record.mp4"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PATTERN_REC] %(message)s")

def start_adb_recording(duration_sec=10):
    logging.info(f"Starting ADB screen recording for {duration_sec} seconds...")
    logging.info("--> PLEASE DRAW YOUR PATTERN LOCK ON YOUR PHONE NOW! <--")
    
    # Run screenrecord on phone
    cmd = [ADB_PATH, "shell", "screenrecord", "--time-limit", str(duration_sec), "/sdcard/pattern_record.mp4"]
    subprocess.run(cmd, capture_output=True, text=True)
    
    logging.info("Recording finished. Pulling video from phone...")
    time.sleep(1)
    
    pull_cmd = [ADB_PATH, "pull", "/sdcard/pattern_record.mp4", OUTPUT_MP4]
    r = subprocess.run(pull_cmd, capture_output=True, text=True)
    
    if os.path.exists(OUTPUT_MP4):
        size = os.path.getsize(OUTPUT_MP4)
        logging.info(f"SUCCESS: Video saved to {OUTPUT_MP4} ({size} bytes)")
        return OUTPUT_MP4
    else:
        logging.error("Failed to pull video file.")
        return None

if __name__ == "__main__":
    start_adb_recording(10)
