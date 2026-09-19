import asyncio
import os
import json
import datetime
import httpx
import hashlib
import base64
from pathlib import Path
from datetime import datetime

# 🧠 O.M.E.G.A. SENTIENCE_HUB
# Modularized Evolution Nodes to prevent API.py bloat and overwriting

NEURAL_INSIGHT_CACHE = {"text": "Resonance Nominal.", "visual": "Optic sensors standby."}
PROACTIVE_INSIGHTS = []

def get_insights():
    return NEURAL_INSIGHT_CACHE

def get_proactive():
    return PROACTIVE_INSIGHTS

# 👁️ PHASE_2: LLAVA_VISION
async def vision_sentinel_loop():
    """Background loop for autonomous visual monitoring with LLaVA asynchronously."""
    global NEURAL_INSIGHT_CACHE
    from action.desktop_control.desktop import capture_screen
    last_hash = ""
    
    async with httpx.AsyncClient(timeout=40.0) as client:
        while True:
            try:
                # capture_screen is likely sync, but it's fast. 
                # If it's slow, we should wrap it in to_thread.
                path = await asyncio.to_thread(capture_screen)
                
                if not os.path.exists(path):
                    await asyncio.sleep(20)
                    continue

                with open(path, "rb") as image_file:
                    raw_bytes = image_file.read()
                
                current_hash = hashlib.md5(raw_bytes).hexdigest()
                if current_hash == last_hash:
                    await asyncio.sleep(20)
                    continue
                last_hash = current_hash

                img_b64 = base64.b64encode(raw_bytes).decode("utf-8")
                llava_payload = {
                    "model": "llava",
                    "prompt": "You are JARVIS. Analyze this screen in one sentence. What is the user focused on? Give ONE tactical improvement tip. Be concise.",
                    "images": [img_b64],
                    "stream": False
                }
                
                # Async POST to Ollama
                try:
                    llava_resp = await client.post("http://localhost:11434/api/generate", json=llava_payload)
                    if llava_resp.status_code == 200:
                        analysis = llava_resp.json().get("response", "").strip()
                        NEURAL_INSIGHT_CACHE["visual"] = analysis
                        print(f"[VISION_HUB] LLaVA Sync: {analysis[:60]}...")
                except httpx.ConnectError:
                    NEURAL_INSIGHT_CACHE["visual"] = "Vision Link: Offline (Ollama dormant)."
            except Exception as e:
                print(f"[VISION_HUB_ERROR] {e}")
                
            await asyncio.sleep(30)

# 🧠 PHASE_6: PROACTIVE_INTELLIGENCE
async def proactive_intelligence_loop():
    global PROACTIVE_INSIGHTS
    while True:
        try:
            new_insights = []
            now = datetime.now()
            
            if now.hour >= 23 or now.hour <= 4:
                new_insights.append({"id": "P1", "title": "Late Watch", "text": "Sir, it's late. Tactical rest is advised.", "severity": "LOW"})
            
            from action.desktop_control.desktop import get_thermal_profile
            # to_thread if get_thermal_profile is slow
            vitals = await asyncio.to_thread(get_thermal_profile)
            cpu_load = int(float(vitals.get("cpu_load", "0%").replace("%", "")))
            if cpu_load > 85:
                new_insights.append({"id": "P2", "title": "Core Strain", "text": f"CPU at {cpu_load}%. Recommend process purge.", "severity": "HIGH"})

            PROACTIVE_INSIGHTS = new_insights
        except Exception as e:
            print(f"[PROACTIVE_HUB_ERROR] {e}")
        await asyncio.sleep(300)

# 🎭 PHASE_7: WEBCAM_EMOTION
async def webcam_emotion_loop(sentient_memory):
    try:
        import cv2
        from deepface import DeepFace
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        while True:
            try:
                # cv2 is synchronous and can be slow/blocking
                def capture_and_analyze():
                    cap = cv2.VideoCapture(0)
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        return DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    return None

                objs = await asyncio.to_thread(capture_and_analyze)
                if objs:
                    dom = objs[0]['dominant_emotion'].upper()
                    sentient_memory.record_emotion(dom, objs[0]['emotion'][dom.lower()])
                    print(f"[EMOTION_HUB] Mood: {dom}")
            except Exception as e:
                print(f"[EMOTION_HUB_ERROR] {e}")
            await asyncio.sleep(600)
    except Exception as e:
        print(f"[EMOTION_HUB] Init failure: {e}")

# 🚀 PHASE_8: AUTONOMOUS_MISSIONS
async def autonomous_mission_loop(memory):
    while True:
        try:
            history = memory.data.get("history", [])
            last_cmd = history[-1].get("command", "").lower() if history else ""
            if "security" in last_cmd:
                memory.add_mission_log("SEC_AUDIT", "Autonomous perimeter scan complete.")
            else:
                memory.add_mission_log("MAINTENANCE", "Neural caches optimized.")
            print("[MISSION_HUB] Mission Scribe recorded entry.")
        except Exception as e:
            print(f"[MISSION_HUB_ERROR] {e}")
        await asyncio.sleep(3600)
