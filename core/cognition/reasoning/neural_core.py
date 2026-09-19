# 🧠 O.M.E.G.A. NEURAL_INTELLIGENCE_LAYER
# Refactored: Facade Router integrating distributed classifiers
# Runs BEFORE the LLM — routes fast intents instantly, scores threats, enables semantic memory search
# This makes JARVIS respond in <100ms for known commands without touching Llama3/GPT

import time

from core.cognition.reasoning.classifiers.intent_classifier import classify_intent_fast, get_intent_classifier_status
from core.cognition.reasoning.classifiers.semantic_classifier import classify_intent_bert
from core.cognition.reasoning.classifiers.reflex_router import classify_intent_reflex
from core.cognition.reasoning.classifiers.threat_analyzer import analyze_threat_from_vitals, get_threat_analyzer_status
from core.cognition.reasoning.classifiers.memory_indexer import semantic_memory_search

SKLEARN_CONFIDENCE_THRESHOLD = 0.70
BERT_CONFIDENCE_THRESHOLD = 0.75

def _build_action(intent: str, text: str, payload_override: str = None, source: str = "LOCAL_SKLEARN") -> dict:
    text_lower = text.lower()
    
    def get_payload(prefix_list):
        if payload_override: return payload_override
        p = text_lower
        for prefix in prefix_list:
            p = p.replace(prefix, "")
        return p.strip()

    action_map = {
        "open_app": lambda: {
            "type": "ACTION", "intent": "open_app",
            "payload": get_payload(["open", "launch", "start"]),
            "response": f"Launching, Sir.", "mode": "reactor", "source": source
        },
        "search": lambda: {
            "type": "ACTION", "intent": "search",
            "payload": get_payload(["search", "google", "look up"]),
            "response": "Scanning global nodes.", "mode": "hud", "source": source
        },
        "control_music": lambda: {
            "type": "ACTION", "intent": "control_music",
            "payload": "pause" if "pause" in text_lower else ("play" if "play" in text_lower else "next"),
            "response": "Sonic recalibration complete.", "mode": "grid", "source": source
        },
        "set_volume": lambda: {
            "type": "ACTION", "intent": "set_volume",
            "payload": 0 if "mute" in text_lower else 50,
            "response": "Audio channel adjusted.", "mode": "system", "source": source
        },
        "system_power": lambda: {
            "type": "ACTION", "intent": "system_power",
            "payload": "shutdown" if "shutdown" in text_lower else ("restart" if "restart" in text_lower else "sleep"),
            "response": "Power sequence initiated. Authorization verified.", "mode": "offline", "source": source
        },
        "diagnostic": lambda: {
            "type": "ACTION", "intent": "diagnostic",
            "response": "Initiating O.M.E.G.A. Protocol. All systems nominal.", "mode": "hud", "source": source
        },
        "weather": lambda: {
            "type": "ACTION", "intent": "weather",
            "response": "Analyzing atmospheric conditions.", "mode": "hud", "source": source
        },
        "type_text": lambda: {
            "type": "ACTION", "intent": "type_text",
            "payload": text_lower.replace("type", "").replace("write", "").strip(),
            "response": "Neural input sequence initiated.", "mode": "grid", "source": source
        },
        "architect": lambda: {
            "type": "CHAT", "intent": "architect",
            "response": "Routing to Sub-Cortex architect. Standing by for build parameters, Sir.",
            "mode": "grid", "source": source
        },
        "vitals": lambda: {
            "type": "ACTION", "intent": "vitals",
            "response": "Pulling system vitals. Neural load analysis commencing.", "mode": "hud", "source": source
        },
        "nexus": lambda: {
            "type": "ACTION", "intent": "nexus",
            "response": "Uplink to global intelligence network established.", "mode": "hud", "source": source
        },
        "chat": lambda: None,
    }
    builder = action_map.get(intent, lambda: None)
    return builder()

def neural_route(text: str) -> dict | None:
    t0 = time.time()
    text_lower = text.lower().strip()
    
    # 🧬 TIER 0: REGEX_REFLEX
    reflex_intent, reflex_payload = classify_intent_reflex(text_lower)
    if reflex_intent:
        ms = int((time.time() - t0) * 1000)
        print(f"[NEURAL_CORE] [REFLEX] routed -> {reflex_intent} in {ms}ms")
        return _build_action(reflex_intent, text, payload_override=reflex_payload, source="LOCAL_REFLEX")

    # 🧬 TIER 1: SKLEARN_INTENT
    sklearn_intent, sklearn_conf = classify_intent_fast(text_lower)
    if sklearn_conf >= SKLEARN_CONFIDENCE_THRESHOLD:
        ms = int((time.time() - t0) * 1000)
        print(f"[NEURAL_CORE] [SKLEARN] routed -> {sklearn_intent} ({sklearn_conf:.0%}) in {ms}ms")
        return _build_action(sklearn_intent, text, source="LOCAL_SKLEARN")
    
    # 🧬 TIER 2: BERT_SEMANTIC
    bert_intent, bert_conf = classify_intent_bert(text_lower)
    if bert_conf >= BERT_CONFIDENCE_THRESHOLD:
        ms = int((time.time() - t0) * 1000)
        print(f"[NEURAL_CORE] [BERT] routed -> {bert_intent} ({bert_conf:.0%}) in {ms}ms")
        return _build_action(bert_intent, text, source="LOCAL_BERT")
    
    ms = int((time.time() - t0) * 1000)
    print(f"[NEURAL_CORE] [LLM] Routing to LLM (sklearn={sklearn_conf:.0%}, BERT={bert_conf:.0%}) in {ms}ms")
    return None

def get_neural_core_status() -> dict:
    return {
        "sklearn_intent_classifier": get_intent_classifier_status(),
        "threat_analyzer": get_threat_analyzer_status(),
        "routing_thresholds": {
            "sklearn": f"{SKLEARN_CONFIDENCE_THRESHOLD:.0%}",
            "bert": f"{BERT_CONFIDENCE_THRESHOLD:.0%}"
        }
    }
