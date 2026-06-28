def check_permission(intent_data):
    """Verifies user authorization for high-level tactical operations."""
    # O.M.E.G.A. IX: STARK SECURITY PROTOCOLS
    intent_name = intent_data.get("intent", "unknown")
    text = intent_data.get("meta_text", "").lower()
    
    # 🔓 XCVI: THE_MASTER_OVERRIDE (Protocol XVIII)
    if "override protocol xviii" in text:
        return "ALLOW"
    
    # 🚨 CRITICAL OPERATIONS: Require Confirmation
    critical_intents = ["kill_process", "shutdown", "refactor", "molecular_sync", "system_power"]
    if intent_name in critical_intents:
        return "CONFIRM"
    
    # 🔓 NOMINAL OPERATIONS: Auto-Authorize
    nominal_intents = ["chat", "weather", "news", "time", "diagnostic", "open_app", "search", "music"]
    if intent_name in nominal_intents:
        return "ALLOW"
    
    # 🛑 DENIED OPERATIONS (Placeholder)
    if intent_name == "override":
        return "DENY"

    return "ALLOW"
