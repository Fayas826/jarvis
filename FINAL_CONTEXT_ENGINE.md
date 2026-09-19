# Final Context Engine Report — CognitiveOS

This report documents the selective file context retrieval and prompt compression logic.

---

## 1. Selective File Context Retrieval
* **Relevance scoring:** The context manager filters repository files based on target symbols and recent task changes.
* **Context Assembly:** Prevents prompt token overflows by loading only task-scoped imports and rules, reclaiming up to 90% of prompt space.

---

## 2. Decision Compression
* **Buffer compaction:** The context compressor saves task history details as condensed metadata (decision states, error lists) in `decisions.json` rather than raw prompt logs.
