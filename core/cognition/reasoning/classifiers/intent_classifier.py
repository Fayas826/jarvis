import threading
import numpy as np

# Lazy load globals
_sklearn_intent_model = None
_label_encoder = None
_neural_lock = threading.Lock()

INTENT_LABELS = [
    "open_app", "search", "control_music", "set_volume", "system_power", 
    "diagnostic", "weather", "type_text", "chat", "architect", "vitals", "nexus",
    "system_admin", "multi_app_workflow", "computer_use", "file_management", "self_heal"
]

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
    # system_admin
    ("kill high cpu processes", "system_admin"), ("flush dns", "system_admin"),
    ("clean temp files", "system_admin"), ("audit network latency", "system_admin"),
    ("terminate runaway process", "system_admin"), ("system health audit", "system_admin"),
    ("kill any background process consuming more than 15% cpu", "system_admin"),
    ("clean up temporary update files", "system_admin"),
    # multi_app_workflow
    ("open presentation take screenshot and send to whatsapp", "multi_app_workflow"),
    ("copy from chrome and paste into notepad", "multi_app_workflow"),
    ("extract summary and save to desktop file", "multi_app_workflow"),
    ("chain multiple apps together", "multi_app_workflow"),
    ("write a summary and save it to desktop", "multi_app_workflow"),
    # computer_use
    ("click on the button", "computer_use"), ("automate the desktop", "computer_use"),
    ("click the grounded target", "computer_use"), ("control the mouse and keyboard", "computer_use"),
    # file_management
    ("open downloads and move invoices", "file_management"), ("organize my documents", "file_management"),
    ("create a folder on desktop", "file_management"), ("copy powerpoint files to archive", "file_management"),
    # self_heal
    ("app is frozen", "self_heal"), ("restart frozen window", "self_heal"),
    ("application not responding", "self_heal"), ("kill hung process", "self_heal"),
]

def build_sklearn_intent_classifier():
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
            print("[NEURAL_CORE] [WARN] scikit-learn not installed.")
            return False
        except Exception as e:
            print(f"[NEURAL_CORE] [FAIL] sklearn build failed: {e}")
            return False

def classify_intent_fast(text: str) -> tuple[str, float]:
    """TIER 3: Lightning-fast intent classification using TF-IDF + LogReg."""
    global _sklearn_intent_model, _label_encoder
    
    if _sklearn_intent_model is None:
        if not build_sklearn_intent_classifier():
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

def get_intent_classifier_status() -> str:
    return "ONLINE" if _sklearn_intent_model is not None else "STANDBY"
