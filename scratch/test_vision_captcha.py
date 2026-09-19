import sys
import os
import time
import webbrowser
import asyncio
import logging

try:
    import pyautogui
except ImportError:
    pass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.perception.screen_capture import screen_capturer
from core.perception.gui_grounding import vision_grounder
from core.perception.visual_state import ScreenFrame

logging.basicConfig(level=logging.INFO)

async def run_captcha_test():
    print("==========================================")
    print(" JARVIS LIVE VLM CAPTCHA TEST (GUI GROUNDING)")
    print("==========================================")
    
    url = "https://www.google.com/recaptcha/api2/demo"
    print(f"[*] Opening Chrome to: {url}")
    webbrowser.open(url)
    
    print("[*] Waiting 6 seconds for page to load...")
    time.sleep(6)
    
    # NEW: Hardware Engineer Intervention
    from core.specialized.hardware_engineer_agent import hardware_engineer
    print("\n[*] Consulting Hardware Surveillance Engineer...")
    # LLaVA typically requires ~2800MB of System RAM (CUDA_Host Buffer) and some VRAM
    safety_report = hardware_engineer.evaluate_launch_safety("Vision_Agent_LLaVA", req_ram_mb=2800)
    print(safety_report["diagnosis"])
    
    if not safety_report["safe"]:
        print("\n[!] Hardware Engineer halted execution. Waiting for training to free resources is recommended.")
        return
        
    print("\n[*] Activating Vision-Language Model...")
    print("[*] Taking physical screenshot of the desktop...")
    
    # Take screenshot
    screen: ScreenFrame = screen_capturer.capture_frame()
    
    print(f"[*] Visual State Captured: {screen.width}x{screen.height} (Active Window: {screen.active_window})")
    
    instruction = "I'm not a robot"
    print(f"[*] Running VLM Grounding Engine to locate: '{instruction}'")
    print(f"[*] (This will pass the image to LLaVA / GPT-4o to scan for the CAPTCHA checkbox)")
    
    target = await vision_grounder.find_target(screen, instruction)
    
    if target:
        print(f"\n[SUCCESS] VLM Grounding found the target!")
        print(f"[>] Type: {target.role}")
        print(f"[>] Coordinates (X, Y): {target.center}")
        print(f"[>] Confidence: {target.confidence * 100:.1f}%")
        
        print("\n[*] Taking control of the mouse...")
        x, y = target.center
        
        # Move mouse smoothly like a human
        pyautogui.moveTo(x, y, duration=1.5, tween=pyautogui.easeInOutQuad)
        print("[*] Mouse positioned over CAPTCHA checkbox.")
        
        # Click
        pyautogui.click()
        print("[*] CLIKED! CAPTCHA Checkbox activated.")
    else:
        print("\n[FAILED] The VLM could not confidently locate the CAPTCHA checkbox on the screen.")
        print("[!] Ensure the browser window is visible on the primary monitor and not obscured.")

if __name__ == "__main__":
    asyncio.run(run_captcha_test())
