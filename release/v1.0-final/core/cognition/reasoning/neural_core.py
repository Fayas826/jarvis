# 🧠 O.M.E.G.A. NEURAL_INTELLIGENCE_LAYER
# BERT + scikit-learn + HuggingFace Transformers
# Runs BEFORE the LLM — routes fast intents instantly, scores threats, enables semantic memory search
# This makes JARVIS respond in <100ms for known commands without touching Llama3/GPT

import json
import time
import threading
from pathlib import Path
import numpy as np
from core.cognition.reasoning.onnx_engine import onnx_engine

# ============================================================
# TIER 1: LAZY LOAD GATE — models only load when first used
# ============================================================
_sklearn_threat_model = None
_sklearn_intent_model = None
_label_encoder = None
_neural_lock = threading.Lock()

from infrastructure.config.settings import USER_MEMORY_PATH
MEMORY_PATH = USER_MEMORY_PATH

# ============================================================
# TIER 2: INTENT LABELS — Maps to JARVIS action intents
# ============================================================
INTENT_LABELS = [
    "open_app",        # "open chrome", "start spotify", "launch vscode"
    "search",          # "search for", "google", "look up"
    "control_music",   # "play music", "pause", "next track", "previous"
    "set_volume",      # "mute", "volume up", "set volume to 80"
    "system_power",    # "shutdown", "restart", "sleep"
    "diagnostic",      # "status", "diagnostic", "how are systems"
    "weather",         # "weather", "temperature outside"
    "type_text",       # "type hello", "write this"
    "chat",            # General conversation / questions
    "architect",       # "build", "create file", "code", "make a script"
    "vitals",          # "cpu usage", "memory", "ram", "gpu load"
    "nexus",           # "news", "intel", "global status"
]

# Training sentences for scikit-learn intent model (fast, no GPU)
TRAINING_DATA = [
    # open_app
    ("open chrome", "open_app"), ("start spotify", "open_app"), ("launch vscode", "open_app"),
    ("open notepad", "open_app"), ("start discord", "open_app"), ("open browser", "open_app"),
    ("run terminal", "open_app"), ("launch steam", "open_app"), ("open chrome browser", "open_app"),
    ("launch the app", "open_app"), ("start the program", "open_app"), ("open explorer", "open_app"),
    # search
    ("search for python tutorials", "search"), ("google jarvis ai", "search"),
    ("look up the weather", "search"), ("find information about", "search"),
    ("search the web for", "search"), ("search google", "search"), ("look this up", "search"),
    # control_music
    ("play music", "control_music"), ("pause the song", "control_music"),
    ("next track", "control_music"), ("skip song", "control_music"),
    ("previous track", "control_music"), ("stop music", "control_music"),
    ("play something", "control_music"), ("pause music", "control_music"),
    ("resume the track", "control_music"), ("skip to next", "control_music"),
    # set_volume
    ("mute the volume", "set_volume"), ("unmute", "set_volume"),
    ("volume up", "set_volume"), ("set volume to 50", "set_volume"),
    ("turn up the sound", "set_volume"), ("silence", "set_volume"),
    ("increase volume", "set_volume"), ("lower the volume", "set_volume"),
    # system_power
    ("shutdown", "system_power"), ("restart the computer", "system_power"),
    ("sleep mode", "system_power"), ("power off", "system_power"),
    ("reboot system", "system_power"), ("turn off the computer", "system_power"),
    # diagnostic
    ("run diagnostic", "diagnostic"), ("system status", "diagnostic"),
    ("how are the systems", "diagnostic"), ("run a check", "diagnostic"),
    ("health report", "diagnostic"), ("full diagnostic", "diagnostic"),
    ("check all systems", "diagnostic"), ("systems diagnostic", "diagnostic"),
    # weather
    ("what's the weather", "weather"), ("temperature outside", "weather"),
    ("weather forecast", "weather"), ("is it raining", "weather"),
    ("check the weather", "weather"), ("weather today", "weather"),
    # type_text
    ("type hello world", "type_text"), ("write this text", "type_text"),
    ("input the following", "type_text"), ("type this for me", "type_text"),
    # chat
    ("how are you", "chat"), ("tell me a joke", "chat"),
    ("what do you think about", "chat"), ("explain quantum computing", "chat"),
    ("who are you", "chat"), ("what can you do", "chat"),
    ("hello jarvis", "chat"), ("good morning", "chat"),
    # architect
    ("build a python script", "architect"), ("create a file", "architect"),
    ("code a website", "architect"), ("make a program", "architect"),
    ("write a function", "architect"), ("develop an app", "architect"),
    ("write me a script", "architect"), ("build this for me", "architect"),
    # vitals
    ("cpu usage", "vitals"), ("memory usage", "vitals"), ("gpu load", "vitals"),
    ("ram status", "vitals"), ("system performance", "vitals"),
    ("how is the cpu", "vitals"), ("check memory", "vitals"),
    # nexus
    ("latest news", "nexus"), ("global intel", "nexus"),
    ("what's happening in the world", "nexus"), ("news briefing", "nexus"),
    ("give me the news", "nexus"), ("current events", "nexus"),
]


# ============================================================
# TIER 3: SKLEARN INTENT CLASSIFIER (Lightning fast, ~1ms)
# ============================================================
def _build_sklearn_intent_classifier():
    """Builds a TF-IDF + LogisticRegression pipeline. No GPU. ~1ms inference."""
    global _sklearn_intent_model, _label_encoder
    with _neural_lock:
        if _sklearn_intent_model is not None:
            return True
        try:
            from sklearn.pipeline import Pipeline
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.preprocessing import LabelEncoder
            from sklearn.model_selection import train_test_split
            
            texts = [t for t, _ in TRAINING_DATA]
            labels = [l for _, l in TRAINING_DATA]
            
            _label_encoder = LabelEncoder()
            y = _label_encoder.fit_transform(labels)
        
            _sklearn_intent_model = Pipeline([
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
                ("clf", LogisticRegression(max_iter=1000, C=5.0))
            ])
            
            _sklearn_intent_model.fit(texts, y)
            print("[NEURAL_CORE] [OK] scikit-learn Intent Classifier ONLINE -- ~1ms inference")
            return True
        except ImportError:
            print("[NEURAL_CORE] [WARN] scikit-learn not installed. Run: pip install scikit-learn")
            return False
        except Exception as e:
            print(f"[NEURAL_CORE] [FAIL] sklearn build failed: {e}")
            return False


def classify_intent_fast(text: str) -> tuple[str, float]:
    """
    TIER 3: Lightning-fast intent classification using TF-IDF + LogReg.
    Returns (intent_label, confidence_score).
    Sub-1ms — used as the first routing gate.
    """
    global _sklearn_intent_model, _label_encoder
    
    if _sklearn_intent_model is None:
        if not _build_sklearn_intent_classifier():
            return "chat", 0.0
    
    try:
        proba = _sklearn_intent_model.predict_proba([text.lower()])[0]
        max_idx = np.argmax(proba)
        confidence = float(proba[max_idx])
        intent = _label_encoder.inverse_transform([max_idx])[0]
        return intent, confidence
    except Exception as e:
        print(f"[NEURAL_CORE] sklearn inference error: {e}")
        return "chat", 0.0


# ============================================================
# TIER 4: BERT ZERO-SHOT CLASSIFIER (Semantic, no fine-tuning needed)
# ============================================================
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


# ============================================================
# TIER 5: SEMANTIC MEMORY SEARCH (HuggingFace Sentence Embeddings)
# ============================================================
def semantic_memory_search(query: str, top_k: int = 3) -> list[dict]:
    """
    TIER 5: Finds semantically similar past commands/sessions (ONNX INT8).
    Uses cosine similarity on compressed sentence embeddings.
    """
    try:
        # Load memory
        if not MEMORY_PATH.exists():
            return []
        
        with open(MEMORY_PATH, "r") as f:
            memory_data = json.load(f)
        
        history = memory_data.get("history", [])
        if not history:
            return []
        
        # Build corpus from history
        corpus = [h.get("command", "") for h in history if h.get("command")]
        if not corpus:
            return []
        
        # Encode query and corpus via ONNX
        query_embedding = onnx_engine.get_embeddings([query])
        corpus_embeddings = onnx_engine.get_embeddings(corpus)
        
        # Cosine similarity
        dot_product = np.dot(query_embedding, corpus_embeddings.T)[0]
        similarities = dot_product 
        
        # Get top_k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Minimum relevance threshold
                results.append({
                    "command": history[idx].get("command", ""),
                    "response": history[idx].get("response", ""),
                    "score": float(similarities[idx])
                })
        
        return results
    except Exception as e:
        print(f"[NEURAL_CORE] Semantic search error: {e}")
        return []


# ============================================================
# TIER 6: SKLEARN THREAT ANALYZER (Vitals anomaly detection)
# ============================================================
def analyze_threat_from_vitals(cpu: float, gpu: float, memory: float, processes: int = 0) -> dict:
    global _sklearn_threat_model
    try:
        from sklearn.ensemble import IsolationForest
        if _sklearn_threat_model is None:
            normal_data = np.array([
                [15, 10, 40, 0.3], [20, 15, 50, 0.4], [25, 20, 55, 0.5],
                [30, 25, 60, 0.5], [10, 5, 35, 0.2], [18, 12, 45, 0.35],
                [22, 18, 52, 0.45], [28, 22, 58, 0.55], [12, 8, 38, 0.25],
                [35, 30, 62, 0.6], [40, 35, 65, 0.65], [5, 3, 30, 0.15],
            ])
            _sklearn_threat_model = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
            _sklearn_threat_model.fit(normal_data)
        
        proc_norm = min(processes / 200.0, 1.0) if processes > 0 else 0.5
        sample = np.array([[cpu, gpu, memory, proc_norm]])
        prediction = _sklearn_threat_model.predict(sample)[0]
        anomaly_score = float(_sklearn_threat_model.score_samples(sample)[0])
        
        if prediction == -1:
            if anomaly_score < -0.5:
                threat = "CRITICAL"
                reason = f"Severe anomaly: CPU={cpu:.0f}% GPU={gpu:.0f}% MEM={memory:.0f}%"
            else:
                threat = "ELEVATED"
                reason = f"Elevated signatures: CPU={cpu:.0f}% GPU={gpu:.0f}% MEM={memory:.0f}%"
        else:
            if cpu > 90 or gpu > 90 or memory > 90:
                threat = "ELEVATED"
                reason = f"High load detected — resources near saturation"
            else:
                threat = "NOMINAL"
                reason = "All systems operating within normal parameters"
        
        return {
            "threat_level": threat,
            "anomaly_score": round(anomaly_score, 4),
            "vitals": {"cpu": cpu, "gpu": gpu, "memory": memory},
            "reason": reason
        }
    except ImportError:
        return {"threat_level": "NOMINAL", "anomaly_score": 0.0, "reason": "sklearn unavailable"}
    except Exception as e:
        return {"threat_level": "NOMINAL", "anomaly_score": 0.0, "reason": str(e)}


# ============================================================
# TIER 7: MASTER ROUTER — The Neural Intelligence Gateway
# ============================================================
SKLEARN_CONFIDENCE_THRESHOLD = 0.75
BERT_CONFIDENCE_THRESHOLD = 0.80

# ============================================================
# TIER 0: REGEX_REFLEX_LAYER (Sub-1ms Bypass)
# ============================================================
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

import re

def classify_intent_reflex(text: str) -> tuple[str, str | None]:
    """TIER 0: Ultra-fast regex matching for core reflexes."""
    for pattern, intent in REGEX_MAP.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Extract payload if group exists
            payload = match.group(1) if match.groups() else None
            return intent, payload
    return None, None

# ============================================================
# TIER 7: MASTER ROUTER — The Neural Intelligence Gateway
# ============================================================
SKLEARN_CONFIDENCE_THRESHOLD = 0.70
BERT_CONFIDENCE_THRESHOLD = 0.75

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

def get_neural_core_status() -> dict:
    sklearn_ok = _sklearn_intent_model is not None
    return {
        "sklearn_intent_classifier": "ONLINE" if sklearn_ok else "STANDBY",
        "threat_analyzer": "ONLINE" if _sklearn_threat_model is not None else "STANDBY",
        "routing_thresholds": {
            "sklearn": f"{SKLEARN_CONFIDENCE_THRESHOLD:.0%}",
            "bert": f"{BERT_CONFIDENCE_THRESHOLD:.0%}"
        }
    }
