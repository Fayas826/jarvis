import os
import json
import numpy as np
import os
import json
import numpy as np
from pathlib import Path

# Lazy imports inside the class

# 🧬 O.M.E.G.A. NEURAL_PATHS
BASE_PATH = Path(__file__).parent / "models"
INTENT_PATH = BASE_PATH / "intent" / "quantized" / "model_quantized.onnx"
EMBEDDER_PATH = BASE_PATH / "embedder" / "quantized" / "model_quantized.onnx"

class ONNXEngine:
    def __init__(self):
        self.intent_session = None
        self.embedder_session = None
        self.intent_tokenizer = None
        self.embedder_tokenizer = None
        self.is_ignited = False

    def ignite(self):
        """🧬 TIER_11: NEURAL_FORGE_IGNITION. Loads optimized ONNX sessions."""
        if self.is_ignited: return
        
        print("[ONNX_ENGINE] Igniting Neural Sessions (INT8)...")
        try:
            import onnxruntime as ort
            from transformers import AutoTokenizer
            
            # Load Sessions
            self.intent_session = ort.InferenceSession(str(INTENT_PATH))
            self.embedder_session = ort.InferenceSession(str(EMBEDDER_PATH))
            
            # Load Tokenizers
            self.intent_tokenizer = AutoTokenizer.from_pretrained(str(BASE_PATH / "intent" / "quantized"))
            self.embedder_tokenizer = AutoTokenizer.from_pretrained(str(BASE_PATH / "embedder" / "quantized"))
            
            self.is_ignited = True
            print("[ONNX_ENGINE] [SUCCESS] All neural nodes moored in INT8.")
        except Exception as e:
            print(f"[ONNX_ENGINE_FAIL] Could not ignite sessions: {e}")

    def classify_intent(self, text, candidate_labels):
        """Zero-shot classification via Entailment score."""
        if not self.is_ignited: self.ignite()
        
        scores = []
        for label in candidate_labels:
            hypothesis = f"This text is about {label}."
            inputs = self.intent_tokenizer(text, hypothesis, return_tensors="np", truncation=True)
            input_names = [i.name for i in self.intent_session.get_inputs()]
            feed = {name: inputs[name] for name in input_names if name in inputs}
            outputs = self.intent_session.run(None, feed)
            logits = outputs[0][0]
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / exp_logits.sum()
            scores.append(probs[0])
        
        exp_scores = np.exp(scores - np.max(scores))
        final_probs = exp_scores / exp_scores.sum()
        return list(zip(candidate_labels, final_probs))

    def get_embeddings(self, texts):
        """Generate sentence embeddings using Mean Pooling."""
        if not self.is_ignited: self.ignite()
        
        inputs = self.embedder_tokenizer(texts, padding=True, truncation=True, return_tensors="np")
        input_names = [i.name for i in self.embedder_session.get_inputs()]
        feed = {name: inputs[name] for name in input_names if name in inputs}
        outputs = self.embedder_session.run(None, feed)
        token_embeddings = outputs[0]
        attention_mask = inputs["attention_mask"]
        input_mask_expanded = np.expand_dims(attention_mask, -1).repeat(token_embeddings.shape[-1], -1)
        sum_embeddings = np.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = np.clip(input_mask_expanded.sum(1), a_min=1e-9, a_max=None)
        embeddings = sum_embeddings / sum_mask
        norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / norm

# Singleton instance
onnx_engine = ONNXEngine()
