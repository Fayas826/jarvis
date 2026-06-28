import os
import json
import uuid
import datetime
import threading
import shutil
from pathlib import Path

import numpy as np

from infrastructure.config.settings import SENTIENT_VECTOR_DIR, SENTIENT_FALLBACK_PATH, SOUL_LATTICE_PATH


class NeuralEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class SentientMemory:
    def __init__(self):
        self._lock = threading.Lock()
        self.db_path = SENTIENT_VECTOR_DIR
        self.fallback_path = SENTIENT_FALLBACK_PATH
        self.collection = None
        self.client = None
        self.fallback_entries = []
        self.mood = "CALM"
        self.personality_tuning = 0.8
        self.soul_file = SOUL_LATTICE_PATH
        self.soul_data = self._load_soul()
        self._load_fallback()
        self._init_db()

    def _save_soul(self):
        with self._lock:
            temp_file = str(self.soul_file) + ".tmp"
            try:
                self.soul_file.parent.mkdir(parents=True, exist_ok=True)
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(self.soul_data, f, indent=4, cls=NeuralEncoder)
                if self.soul_file.exists():
                    self.soul_file.unlink()
                shutil.move(temp_file, str(self.soul_file))
            except Exception as e:
                print(f"[SENTIENT_MEMORY] Soul save fail: {e}")
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except OSError:
                        pass

    def _load_soul(self):
        if not self.soul_file.exists():
            default_soul = {
                "name": "Sir Fayas",
                "role": "The Architect",
                "preferences": {
                    "theme": "Dark",
                    "coding_language": "Python/JS",
                    "mood_lighting": "Cyan",
                },
                "emotional_baseline": "FOCUSED",
                "habits": [],
                "notable_achievements": [],
            }
            self.soul_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.soul_file, "w", encoding="utf-8") as f:
                json.dump(default_soul, f, indent=4)
            return default_soul
        with open(self.soul_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_fallback(self):
        try:
            if self.fallback_path.exists():
                with open(self.fallback_path, "r", encoding="utf-8") as f:
                    self.fallback_entries = json.load(f)
        except Exception as e:
            print(f"[SENTIENT_MEMORY] Fallback load fail: {e}")
            self.fallback_entries = []

    def _save_fallback(self):
        try:
            self.fallback_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.fallback_path, "w", encoding="utf-8") as f:
                json.dump(self.fallback_entries[-200:], f, indent=4, cls=NeuralEncoder)
        except Exception as e:
            print(f"[SENTIENT_MEMORY] Fallback save fail: {e}")

    def update_soul(self, key, value):
        if key in self.soul_data:
            self.soul_data[key] = value
        else:
            self.soul_data.setdefault("preferences", {})[key] = value
        self._save_soul()

    def record_emotion(self, emotion, confidence):
        timestamp = str(datetime.datetime.now())
        self.soul_data.setdefault("emotional_history", []).append(
            {"timestamp": timestamp, "emotion": emotion, "confidence": confidence}
        )
        if len(self.soul_data["emotional_history"]) > 50:
            self.soul_data["emotional_history"].pop(0)
        self.soul_data["emotional_baseline"] = emotion
        self._save_soul()

    def get_soul_context(self):
        prefs = ", ".join([f"{k}: {v}" for k, v in self.soul_data["preferences"].items()])
        return (
            f"USER_PROFILE: {self.soul_data['name']} ({self.soul_data['role']}). "
            f"PREFERENCES: {prefs}. BASELINE: {self.soul_data['emotional_baseline']}."
        )

    def _init_db(self):
        try:
            import chromadb

            self.db_path.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(self.db_path))
            self.collection = self.client.get_or_create_collection(
                name="jarvis_long_term_memory",
                metadata={"hnsw:space": "cosine"},
            )
            print(f"[SENTIENT_MEMORY] Vector Store ONLINE | Count: {self.collection.count()}")
        except Exception as e:
            self.collection = None
            self.client = None
            print(f"[SENTIENT_MEMORY] Initialization fallback active: {e}")

    def _embed(self, text: str):
        from core.cognition.reasoning.onnx_engine import onnx_engine

        return onnx_engine.get_embeddings(text).squeeze().tolist()

    def teach(self, command: str, response: str, metadata: dict = None):
        doc = f"User: {command}\nJARVIS: {response}"
        entry = {
            "id": str(uuid.uuid4()),
            "command": command,
            "response": response,
            "document": doc,
            "metadata": {
                "timestamp": str(datetime.datetime.now()),
                "type": "interaction",
                **(metadata or {}),
            },
        }

        if self.collection is not None:
            try:
                self.collection.add(
                    documents=[doc],
                    embeddings=[self._embed(doc)],
                    metadatas=[entry["metadata"]],
                    ids=[entry["id"]],
                )
            except Exception as e:
                print(f"[SENTIENT_MEMORY] Learning fallback: {e}")
                self.collection = None

        self.fallback_entries.append(entry)
        self._save_fallback()

    def remember(self, query: str, top_k: int = 3):
        if self.collection is not None:
            try:
                results = self.collection.query(query_embeddings=[self._embed(query)], n_results=top_k)
                memories = []
                if results and results.get("documents"):
                    for i in range(len(results["documents"][0])):
                        memories.append(
                            {
                                "content": results["documents"][0][i],
                                "metadata": results["metadatas"][0][i],
                                "distance": results["distances"][0][i],
                            }
                        )
                if memories:
                    return memories
            except Exception as e:
                print(f"[SENTIENT_MEMORY] Retrieval fallback: {e}")
                self.collection = None

        query_terms = set(query.lower().split())
        ranked = []
        for entry in self.fallback_entries[-200:]:
            document = entry["document"].lower()
            overlap = len(query_terms.intersection(document.split()))
            if overlap:
                ranked.append(
                    {
                        "content": entry["document"],
                        "metadata": entry["metadata"],
                        "distance": 1 / (overlap + 1),
                        "score": overlap,
                    }
                )
        ranked.sort(key=lambda item: (-item.get("score", 0), item["distance"]))
        return ranked[:top_k]

    def get_recent_emotions(self):
        history = self.soul_data.get("emotional_history", [])
        return history[-10:]

    def analyze_mood(self, recent_logs):
        positive = ["sir", "thanks", "good", "perfect", "amazing", "stark"]
        negative = ["error", "fail", "bad", "dimmed", "issue"]

        score = 0
        text = " ".join(recent_logs).lower()
        for word in positive:
            if word in text:
                score += 1
        for word in negative:
            if word in text:
                score -= 1

        if score > 2:
            self.mood = "EXCITED"
        elif score < -2:
            self.mood = "CAUTIOUS"
        else:
            self.mood = "CALM"
        return self.mood


sentient_memory = SentientMemory()
