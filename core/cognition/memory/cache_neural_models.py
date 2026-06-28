# O.M.E.G.A. Neural Model Pre-Cacher
# Downloads and caches BERT + sentence-transformer models permanently
# Run once with internet — after this, everything works 100% offline

import sys
import time

print("=" * 60)
print("  O.M.E.G.A. NEURAL MODEL CACHE IGNITION")
print("  Downloading BERT + Semantic Memory models...")
print("=" * 60)

# ── STEP 1: scikit-learn (already installed, just verify) ──────
print("\n[1/3] Verifying scikit-learn classifier...")
try:
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import IsolationForest
    print("      [OK] scikit-learn -- READY (no download needed)")
except ImportError as e:
    print(f"      [FAIL] scikit-learn missing: {e}")
    print("      Run: pip install scikit-learn")
    sys.exit(1)

# ── STEP 2: BERT Zero-Shot (distilbert ~262MB) ─────────────────
print("\n[2/3] Downloading BERT Zero-Shot Classifier...")
print("      Model: typeform/distilbert-base-uncased-mnli")
print("      Size:  ~262MB  (one-time download)")
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    
    t0 = time.time()
    print("      [DOWNLOADING] Please wait...")
    
    # This triggers the download + caches to ~/.cache/huggingface/
    clf = pipeline(
        "zero-shot-classification",
        model="typeform/distilbert-base-uncased-mnli",
        device=-1
    )
    
    # Test it works
    result = clf("open chrome browser", ["launch application", "search web", "chat"])
    elapsed = time.time() - t0
    
    print(f"      [OK] BERT Zero-Shot -- CACHED & VERIFIED in {elapsed:.1f}s")
    print(f"      Test: 'open chrome' -> {result['labels'][0]} ({result['scores'][0]:.0%})")
    
except Exception as e:
    print(f"      [FAIL] BERT download failed: {e}")
    print("      Check internet connection and try again.")
    sys.exit(1)

# ── STEP 3: Sentence Transformers (~90MB) ──────────────────────
print("\n[3/3] Downloading Semantic Memory Engine...")
print("      Model: all-MiniLM-L6-v2")
print("      Size:  ~90MB  (one-time download)")
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    
    t0 = time.time()
    print("      [DOWNLOADING] Please wait...")
    
    # This triggers the download + caches
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Test it works
    test_embeddings = model.encode(["open chrome", "launch browser"])
    similarity = float(np.dot(test_embeddings[0], test_embeddings[1]) / 
                      (np.linalg.norm(test_embeddings[0]) * np.linalg.norm(test_embeddings[1])))
    elapsed = time.time() - t0
    
    print(f"      [OK] Semantic Memory Engine -- CACHED & VERIFIED in {elapsed:.1f}s")
    print(f"      Test similarity ('open chrome' vs 'launch browser'): {similarity:.2%}")
    
except Exception as e:
    print(f"      [FAIL] Sentence-transformer download failed: {e}")
    print("      Run: pip install sentence-transformers")
    sys.exit(1)

# ── FINAL STATUS ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("  NEURAL INTELLIGENCE LAYER -- FULLY ARMED")
print()
print("  [ONLINE] scikit-learn TF-IDF + LogReg  (~1ms routing)")
print("  [ONLINE] BERT Zero-Shot Classifier      (~300ms semantic)")
print("  [ONLINE] Sentence Transformer Embeddings (~50ms search)")
print("  [ONLINE] IsolationForest Threat Engine   (~5ms anomaly)")
print()
print("  All models are cached. JARVIS is now OFFLINE-SOVEREIGN.")
print("  You can disconnect from internet -- models won't re-download.")
print("=" * 60)
