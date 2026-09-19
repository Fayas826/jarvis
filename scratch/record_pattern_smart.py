"""
JARVIS 15-SECOND PATTERN RECORDER WITH DOUBLE-VIBRATION SIGNAL
===============================================================
Vibration Signals:
  1. DOUBLE VIBRATION (Bzzt-Bzzt): RECORDING IS LIVE NOW -> DRAW PATTERN NOW!
  2. SINGLE LONG VIBRATION (Bzzzzzt): RECORDING COMPLETE!
"""

import subprocess
import time
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

ADB_PATH = r"C:\AMD\platform-tools\adb.exe"
OUTPUT_MP4 = r"c:\jarvis AI\jarvis\scratch\yt_pattern_draw_live.mp4"
OUTPUT_TOUCH = r"c:\jarvis AI\jarvis\scratch\touch_events_live.txt"

def adb_cmd(args):
    return subprocess.run([ADB_PATH] + args, capture_output=True, text=True)

def record_pattern_live(duration=15):
    print("==========================================================")
    print(" 🔴 STARTING 15-SECOND PATTERN RECORDING WITH VIBRATION  ")
    print("==========================================================")
    
    # 1. Double Vibration Alert (Bzzt-Bzzt) to signal START
    print("\n[ALERT] Sending DOUBLE VIBRATION to your phone now...")
    adb_cmd(["shell", "cmd", "vibrator", "vibrate", "200"])
    time.sleep(0.3)
    adb_cmd(["shell", "cmd", "vibrator", "vibrate", "200"])
    
    print(f"\n🔴 RECORDING IS LIVE FOR {duration} SECONDS! DRAW YOUR PATTERN NOW ON PHONE! 🔴")
    
    # Start screenrecord & raw getevent touch logger
    rec_proc = subprocess.Popen([ADB_PATH, "shell", "screenrecord", "--time-limit", str(duration), "/sdcard/yt_pattern_draw_live.mp4"])
    touch_proc = subprocess.Popen([ADB_PATH, "shell", "getevent", "-lt"], stdout=open(OUTPUT_TOUCH, "w"))
    
    # Wait for 15 seconds
    for i in range(duration, 0, -1):
        print(f"Recording... {i} seconds remaining...", end="\r", flush=True)
        time.sleep(1)
    print("\n")
    
    touch_proc.terminate()
    rec_proc.wait()
    
    # 2. Long Vibration Alert (Bzzzzzt) to signal FINISH
    adb_cmd(["shell", "cmd", "vibrator", "vibrate", "800"])
    print("[ALERT] Single Long Vibration sent — Recording finished!")
    
    time.sleep(1)
    adb_cmd(["pull", "/sdcard/yt_pattern_draw_live.mp4", OUTPUT_MP4])
    
    if os.path.exists(OUTPUT_MP4):
        size = os.path.getsize(OUTPUT_MP4)
        print(f"SUCCESS: Recorded Video saved to {OUTPUT_MP4} ({size} bytes)")

if __name__ == "__main__":
    record_pattern_live(15)
