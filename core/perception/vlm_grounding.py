import os
import base64
from typing import List, Optional
from core.perception.visual_state import ScreenFrame, GUIElement

async def query_vlm_fallback(screen: ScreenFrame, instruction: str, elements: List[GUIElement]) -> Optional[GUIElement]:
    if not elements:
        return None

    # Draw numbered bounding boxes (Set-of-Mark)
    import cv2
    import numpy as np
    
    # Decode image
    img_data = base64.b64decode(screen.image)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    element_map = {}
    for idx, el in enumerate(elements):
        x1, y1, x2, y2 = el.bbox
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, str(idx), (x1, max(y1-5, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        element_map[str(idx)] = el

    temp_path = "data/temp/som_grounding.png"
    os.makedirs("data/temp", exist_ok=True)
    cv2.imwrite(temp_path, img)
    
    # Encode back to base64
    with open(temp_path, "rb") as f:
        som_b64 = base64.b64encode(f.read()).decode('utf-8')

    # Query VLM (Check for Online Models via LiteLLM first, fallback to LLaVA)
    import litellm
    
    prompt = f"I have overlaid numbered bounding boxes on this UI. Which number corresponds to the target: '{instruction}'? Reply with ONLY the number."
    
    try:
        # Check Cloud API Keys
        if os.getenv("OPENAI_API_KEY"):
            print("[GROUNDER] Routing vision task to GPT-4o...")
            response = litellm.completion(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{som_b64}"}}
                        ]
                    }
                ]
            )
            answer = response.choices[0].message.content.strip()
        elif os.getenv("ANTHROPIC_API_KEY"):
            print("[GROUNDER] Routing vision task to Claude-3.5-Sonnet...")
            response = litellm.completion(
                model="claude-3-5-sonnet-20240620",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{som_b64}"}}
                        ]
                    }
                ]
            )
            answer = response.choices[0].message.content.strip()
        else:
            # Local LLaVA Fallback
            import requests
            print("[GROUNDER] Routing vision task to local LLaVA...")
            resp = requests.post('http://127.0.0.1:11434/api/generate', json={
                "model": "llava:latest",
                "prompt": prompt,
                "images": [som_b64],
                "stream": False
            }, timeout=60)
            if resp.status_code == 200:
                answer = resp.json().get('response', '').strip()
            else:
                return None
                
        # Map the answer back to the exact coordinate
        import re
        numbers = re.findall(r'\d+', answer)
        if numbers and numbers[0] in element_map:
            target_el = element_map[numbers[0]]
            print(f"[GROUNDER] VLM successfully resolved target to Box #{numbers[0]} at {target_el.center}")
            target_el.confidence = 0.95
            target_el.evidence = {"som_vlm_fallback": True, "vlm_raw_answer": answer}
            return target_el
            
    except Exception as e:
        print(f"[GROUNDER] VLM Set-of-Mark query fail: {e}")
        
    return None
