import json
import time
from pathlib import Path
from typing import Dict

from infrastructure.config.settings import LONG_TERM_VECTOR_DIR, LONG_TERM_FALLBACK_PATH
from core.cognition.reasoning.onnx_engine import onnx_engine


class LongTermMemory:
    def __init__(self):
        self.degraded = False
        self.client = None
        self.episodic = None
        self.semantic = None
        self.procedural = None
        self.persist_directory = LONG_TERM_VECTOR_DIR
        self.fallback_path = LONG_TERM_FALLBACK_PATH
        self.fallback_data = {"episodic": [], "semantic": [], "procedural": []}
        self._load_fallback()
        self._init_db()

    def _load_fallback(self):
        try:
            if self.fallback_path.exists():
                with open(self.fallback_path, "r", encoding="utf-8") as f:
                    self.fallback_data = json.load(f)
        except Exception as e:
            print(f"[MEMORY_FALLBACK_LOAD] {e}")

    def _save_fallback(self):
        try:
            self.fallback_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.fallback_path, "w", encoding="utf-8") as f:
                json.dump(self.fallback_data, f, indent=4)
        except Exception as e:
            print(f"[MEMORY_FALLBACK_SAVE] {e}")

    def _init_db(self):
        try:
            import chromadb

            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            self.episodic = self.client.get_or_create_collection(
                name="episodic_memory",
                metadata={"hnsw:space": "cosine"},
            )
            self.semantic = self.client.get_or_create_collection(
                name="semantic_memory",
                metadata={"hnsw:space": "cosine"},
            )
            self.procedural = self.client.get_or_create_collection(
                name="procedural_memory",
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            print(f"[MEMORY_CRITICAL] Fallback memory mode active: {e}")
            self.degraded = True

    def _get_embedding(self, text: str):
        return onnx_engine.get_embeddings(text).squeeze().tolist()

    def add_episodic(self, command: str, response: str, metadata: Dict = None):
        doc = f"User: {command} | JARVIS: {response}"
        event_id = f"evt_{int(time.time() * 1000)}"
        meta = metadata or {}
        meta.update({"timestamp": time.time(), "type": "episodic"})

        if self.episodic is not None:
            try:
                self.episodic.add(
                    ids=[event_id],
                    embeddings=[self._get_embedding(doc)],
                    documents=[doc],
                    metadatas=[meta],
                )
            except Exception as e:
                print(f"[MEMORY_EPISODIC_FALLBACK] {e}")
                self.episodic = None

        self.fallback_data["episodic"].append({"id": event_id, "document": doc, "metadata": meta})
        self.fallback_data["episodic"] = self.fallback_data["episodic"][-200:]
        self._save_fallback()

    def search_context(self, query: str, limit: int = 5) -> str:
        if self.semantic is not None and self.episodic is not None:
            try:
                embedding = self._get_embedding(query)
                sem_res = self.semantic.query(query_embeddings=[embedding], n_results=3)
                epi_res = self.episodic.query(query_embeddings=[embedding], n_results=limit)

                context_parts = []
                if sem_res["documents"][0]:
                    context_parts.append("RELEVANT_CONCEPTS: " + " | ".join(sem_res["documents"][0]))
                if epi_res["documents"][0]:
                    context_parts.append("PAST_EXPERIENCES: " + " | ".join(epi_res["documents"][0]))
                return "\n".join(context_parts)
            except Exception as e:
                print(f"[MEMORY_SEARCH_FALLBACK] {e}")
                self.semantic = None
                self.episodic = None

        query_terms = set(query.lower().split())
        semantic_matches = []
        episodic_matches = []

        for item in self.fallback_data.get("semantic", []):
            overlap = len(query_terms.intersection(item["concept"].lower().split()))
            if overlap:
                semantic_matches.append(item["details"])

        for item in self.fallback_data.get("episodic", [])[-limit * 3 :]:
            overlap = len(query_terms.intersection(item["document"].lower().split()))
            if overlap:
                episodic_matches.append(item["document"])

        context_parts = []
        if semantic_matches:
            context_parts.append("RELEVANT_CONCEPTS: " + " | ".join(semantic_matches[:3]))
        if episodic_matches:
            context_parts.append("PAST_EXPERIENCES: " + " | ".join(episodic_matches[:limit]))
        return "\n".join(context_parts)

    def add_semantic(self, concept: str, details: str):
        concept_id = f"sem_{int(time.time() * 1000)}"
        metadata = {"concept": concept, "timestamp": time.time()}

        if self.semantic is not None:
            try:
                self.semantic.add(
                    ids=[concept_id],
                    embeddings=[self._get_embedding(concept)],
                    documents=[details],
                    metadatas=[metadata],
                )
            except Exception as e:
                print(f"[MEMORY_SEMANTIC_FALLBACK] {e}")
                self.semantic = None

        self.fallback_data["semantic"].append({"id": concept_id, "concept": concept, "details": details, "metadata": metadata})
        self.fallback_data["semantic"] = self.fallback_data["semantic"][-200:]
        self._save_fallback()

    def consolidate_memory(self, brain_callback):
        recent = self.fallback_data.get("episodic", [])[-20:]
        if not recent:
            return

        history_str = "\n".join(item["document"] for item in recent)
        prompt = (
            "Analyze these recent interactions. Extract 2-3 key semantic facts or user preferences. "
            "Format as a JSON list of objects: [{'concept': '...', 'details': '...'}]"
        )

        try:
            abstraction = brain_callback(history_str + "\n\n" + prompt)
            if isinstance(abstraction, list):
                for item in abstraction:
                    self.add_semantic(item["concept"], item["details"])
        except Exception as e:
            print(f"[MEMORY_CONSOLIDATION_FAIL] {e}")


ltm = LongTermMemory()
