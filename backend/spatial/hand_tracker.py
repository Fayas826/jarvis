import cv2
import mediapipe as mp
import math
import asyncio
import websockets
import json
import threading
import pyautogui
import os

import logging
logger = logging.getLogger("hand_tracker")

# Disable pyautogui failsafe for this prototype (so moving to corners doesn't crash it)
pyautogui.FAILSAFE = False

cursor_data = {
    "x": 0.5,
    "y": 0.5,
    "is_pinching": False,
    "is_tracking": False
}

system_state = {
    "camera_active": False
}

def vision_loop():
    global cursor_data, system_state
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    cap = None

    last_x = 0.5
    swipe_cooldown = 0
    
    while True:
        if not system_state["camera_active"]:
            if cap is not None:
                cap.release()
                cap = None
                cursor_data["is_tracking"] = False
            # Sleep briefly to save CPU when standby
            cv2.waitKey(100)
            continue
            
        if cap is None:
            cap = cv2.VideoCapture(0)
            
        success, image = cap.read()
        if not success:
            continue
            
        image = cv2.flip(image, 1)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_image)
        
        if swipe_cooldown > 0:
            swipe_cooldown -= 1

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                idx_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thm_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                
                cx = idx_tip.x
                cy = idx_tip.y
                
                # OS Level Swipe Gesture Detection
                # If we move more than 30% of the screen horizontally very quickly
                if swipe_cooldown == 0:
                    if last_x - cx > 0.3:
                        logger.info("SWIPE LEFT DETECTED! Opening Zoom...")
                        import subprocess
                        # Use subprocess.Popen (shell=False) to avoid command injection
                        try:
                            subprocess.Popen(["zoom.exe"], shell=False)
                        except FileNotFoundError:
                            subprocess.Popen(["calc.exe"], shell=False)
                        swipe_cooldown = 30 # wait ~30 frames before another swipe
                        last_x = cx
                    elif cx - last_x > 0.3:
                        logger.info("SWIPE RIGHT DETECTED! Throwing windows away...")
                        # Win + D throws all windows to the desktop
                        pyautogui.hotkey('win', 'd')
                        swipe_cooldown = 30
                        last_x = cx
                    else:
                        # Only update last_x if no swipe happened, to allow accumulation of fast movement
                        last_x = last_x * 0.8 + cx * 0.2 
                
                dist = math.hypot(idx_tip.x - thm_tip.x, idx_tip.y - thm_tip.y)
                is_pinching = dist < 0.05
                
                cursor_data["x"] = cx
                cursor_data["y"] = cy
                cursor_data["is_pinching"] = is_pinching
                cursor_data["is_tracking"] = True
        else:
            cursor_data["is_tracking"] = False

async def handle_client(websocket):
    global system_state
    
    # Task to receive commands from the React UI
    async def receive_commands():
        try:
            async for message in websocket:
                data = json.loads(message)
                if data.get("action") == "START_CAMERA":
                    system_state["camera_active"] = True
                    logger.info("Spatial Link Initiated: Camera ON")
                elif data.get("action") == "STOP_CAMERA":
                    system_state["camera_active"] = False
                    logger.info("Spatial Link Severed: Camera OFF")
        except websockets.exceptions.ConnectionClosed:
            system_state["camera_active"] = False # Auto-off if UI closes

    # Task to broadcast telemetry to the React UI
    async def send_telemetry():
        try:
            while True:
                await websocket.send(json.dumps(cursor_data))
                await asyncio.sleep(1/60) # 60 FPS
        except websockets.exceptions.ConnectionClosed:
            pass

    await asyncio.gather(receive_commands(), send_telemetry())

async def main():
    async with websockets.serve(handle_client, "localhost", 8766):
        logger.info("Spatial OS Controller running on ws://localhost:8766")
        await asyncio.Future()

if __name__ == "__main__":
    t = threading.Thread(target=vision_loop, daemon=True)
    t.start()
    asyncio.run(main())
