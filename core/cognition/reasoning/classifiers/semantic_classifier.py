from core.cognition.reasoning.onnx_engine import onnx_engine

def classify_intent_bert(text: str) -> tuple[str, float]:
    """
    TIER 4: BERT-powered zero-shot semantic classification (ONNX INT8).
    More accurate than TF-IDF for nuanced/novel phrasing.
    ~50ms inference — used when sklearn confidence < threshold.
    """
    try:
        candidate_labels = [
            "launch or open an application",
            "search the internet or google something",
            "control music playback",
            "change the volume or mute audio",
            "power off, restart or sleep the computer",
            "run a system diagnostic or status check",
            "check weather or temperature",
            "type or input text automatically",
            "general chat or conversation",
            "write code or build a software project",
            "check CPU, GPU or memory vitals",
            "get news or global intelligence briefing",
        ]
        
        # 🧬 O.M.E.G.A. V55: ONNX_NEURAL_RESTORATION
        results = onnx_engine.classify_intent(text, candidate_labels)
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        top_label, confidence = results[0]
        
        # Map back to INTENT_LABELS
        label_map = {
            "launch or open an application": "open_app",
            "search the internet or google something": "search",
            "control music playback": "control_music",
            "change the volume or mute audio": "set_volume",
            "power off, restart or sleep the computer": "system_power",
            "run a system diagnostic or status check": "diagnostic",
            "check weather or temperature": "weather",
            "type or input text automatically": "type_text",
            "general chat or conversation": "chat",
            "write code or build a software project": "architect",
            "check CPU, GPU or memory vitals": "vitals",
            "get news or global intelligence briefing": "nexus",
        }
        
        intent = label_map.get(top_label, "chat")
        return intent, float(confidence)
    except Exception as e:
        print(f"[NEURAL_CORE] ONNX BERT inference error: {e}")
        return "chat", 0.0
