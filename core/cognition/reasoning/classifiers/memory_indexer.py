import json
import numpy as np
from core.cognition.reasoning.onnx_engine import onnx_engine
from infrastructure.config.settings import USER_MEMORY_PATH

MEMORY_PATH = USER_MEMORY_PATH

def semantic_memory_search(query: str, top_k: int = 3) -> list[dict]:
    """
    TIER 5: Finds semantically similar past commands/sessions (ONNX INT8).
    Uses cosine similarity on compressed sentence embeddings.
    """
    try:
        if not MEMORY_PATH.exists():
            return []
        
        with open(MEMORY_PATH, "r") as f:
            memory_data = json.load(f)
        
        history = memory_data.get("history", [])
        if not history:
            return []
        
        corpus = [h.get("command", "") for h in history if h.get("command")]
        if not corpus:
            return []
        
        query_embedding = onnx_engine.get_embeddings([query])
        corpus_embeddings = onnx_engine.get_embeddings(corpus)
        
        dot_product = np.dot(query_embedding, corpus_embeddings.T)[0]
        similarities = dot_product 
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3:
                results.append({
                    "command": history[idx].get("command", ""),
                    "response": history[idx].get("response", ""),
                    "score": float(similarities[idx])
                })
        
        return results
    except Exception as e:
        print(f"[NEURAL_CORE] Semantic search error: {e}")
        return []
