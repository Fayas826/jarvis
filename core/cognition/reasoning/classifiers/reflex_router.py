import re

REGEX_MAP = {
    r"(?:open|launch|start)\s+(chrome|spotify|vscode|discord|notepad|browser|explorer|youtube|calculator|cmd)": "open_app",
    r"(?:search|google|look up)\s+(.+)": "search",
    r"(?:play|pause|next|previous|skip|stop)\s+(?:music|song|track)": "control_music",
    r"(?:volume|sound)\s+(up|down|mute|unmute|set to\s+\d+)": "set_volume",
    r"(?:shutdown|restart|reboot|sleep|power off)": "system_power",
    r"(?:status|diagnostic|health check|vitals)": "diagnostic",
    r"(?:weather|temperature|forecast)": "weather",
    r"(?:type|write)\s+(.+)": "type_text",
    r"(?:news|intel|briefing)": "nexus",
    r"(?:build|architect|design|create|code)\s+(.+)": "architect",
    r"(?:remember|memory|who is|what was)\s+(.+)": "memory_query",
    r"(?:think|analyze|reason|calculate)\s+(.+)": "deep_thinking",
    r"(?:plan|strategy|roadmap|schedule)\s+(.+)": "planning",
}

def classify_intent_reflex(text: str) -> tuple[str, str | None]:
    """TIER 0: Ultra-fast regex matching for core reflexes."""
    for pattern, intent in REGEX_MAP.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            payload = match.group(1) if match.groups() else None
            return intent, payload
    return None, None
