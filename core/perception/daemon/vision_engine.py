import json
import urllib.request
import logging
from .adb_client import phone_screenshot_bytes

log = logging.getLogger("jarvis_daemon")

def screenshot_to_text():
    img_bytes = phone_screenshot_bytes()
    if not img_bytes: return ""
    try:
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(img_bytes))
        try:
            import easyocr
            reader = easyocr.Reader(["en"], gpu=True, verbose=False)
            result = reader.readtext(img_bytes, detail=0)
            return "\n".join(result)
        except Exception: pass
        try:
            import pytesseract
            return pytesseract.image_to_string(img)
        except Exception: pass
        return ""
    except Exception as e:
        log.warning(f"OCR failed: {e}")
        return ""

def analyse_screen_content(text, context="youtube"):
    if not text.strip(): return "Screen appears to be empty or unreadable."
    try:
        payload = json.dumps({
            "model": "phi3:latest",
            "prompt": (f"You are JARVIS AI. The following text was extracted from the phone screen "
                       f"(context: {context}).\n\nScreen content:\n{text[:2000]}\n\n"
                       f"Summarise what is on screen in 2-3 sentences, and if it is YouTube "
                       f"results, list the top video titles."),
            "stream": False
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("response", "No analysis available.").strip()
    except Exception as e:
        log.warning(f"Ollama analysis failed: {e}")
        return f"Screen text captured: {text[:200]}..."
