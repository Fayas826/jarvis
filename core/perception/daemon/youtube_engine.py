import time
import os
import re
import urllib.parse
import urllib.request
import logging

from .adb_client import phone_wake, adb_shell, phone_screenshot_bytes
from .vision_engine import screenshot_to_text, analyse_screen_content

log = logging.getLogger("jarvis_daemon")
BASE_DIR = r"c:\jarvis AI\jarvis"

def get_yt_video_id(query):
    try:
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            vids = re.findall(r"/watch\?v=([a-zA-Z0-9_-]{11})", html)
            if vids: return vids[0]
    except Exception: pass
    return None

def deep_youtube_play_and_analyse(query):
    log.info(f"[YOUTUBE_DEEP] Starting deep YouTube flow for: '{query}'")
    vid_id = get_yt_video_id(query)
    if vid_id:
        url = "https://www.youtube.com/watch?v=" + vid_id
        log.info(f"[YOUTUBE_DEEP] Resolved video: {vid_id}")
    else:
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
        log.info(f"[YOUTUBE_DEEP] No direct match, opening search results")

    phone_wake()
    time.sleep(0.5)
    adb_shell("am", "start", "-a", "android.intent.action.VIEW", "-d", url)
    log.info("[YOUTUBE_DEEP] YouTube launched on phone")
    time.sleep(5)

    log.info("[YOUTUBE_DEEP] Capturing screen for analysis...")
    screen_text = screenshot_to_text()

    img_bytes = phone_screenshot_bytes()
    if img_bytes:
        spath = os.path.join(BASE_DIR, "vision_temp_yt.png")
        with open(spath, "wb") as f: f.write(img_bytes)
        log.info(f"[YOUTUBE_DEEP] Screenshot saved: {spath}")

    log.info("[YOUTUBE_DEEP] Sending screen content to Ollama for analysis...")
    analysis = analyse_screen_content(screen_text, context="youtube")
    log.info(f"[YOUTUBE_DEEP] Analysis: {analysis}")

    return {
        "video_id": vid_id,
        "url": url,
        "screen_text": screen_text[:500],
        "analysis": analysis,
    }
