import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

PROJECT_MEMORY_DIR = Path("project_memory")
PROJECT_MEMORY_DIR.mkdir(exist_ok=True)


class ScoredMemoryStore:
    """Persistent memory with trust, importance, and decay metadata."""

    def __init__(self, path: Path | None = None, max_items: int = 1000):
        self.path = path or PROJECT_MEMORY_DIR / "scored_memory.json"
        self.max_items = max_items
        self._ensure_file()

    def _ensure_file(self):
        if not self.path.exists():
            self._write([])

    def _read(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'scored_memory', f'Unhandled exception: {e}')
            return []

    def _write(self, items: List[Dict[str, Any]]):
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(items[-self.max_items:], indent=2), encoding="utf-8")
        os.replace(temp, self.path)

    def remember(self, content: str, source: str = "system", category: str = "general", importance: int = 3, trust: float = 0.7, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        importance = max(1, min(5, int(importance)))
        trust = max(0.0, min(1.0, float(trust)))
        now = time.time()
        item = {
            "id": f"mem-{uuid.uuid4().hex[:12]}",
            "content": content,
            "source": source,
            "category": category,
            "importance": importance,
            "trust": trust,
            "score": round((importance / 5) * 0.55 + trust * 0.45, 3),
            "created_at": now,
            "last_accessed": now,
            "access_count": 0,
            "metadata": metadata or {},
        }
        items = self._read()
        items.append(item)
        self._write(items)
        return item

    def recall(self, query: str = "", limit: int = 8, min_score: float = 0.0) -> List[Dict[str, Any]]:
        query_lower = query.lower().strip()
        items = self._read()
        scored = []
        for item in items:
            if item.get("score", 0) < min_score:
                continue
            content = item.get("content", "")
            category = item.get("category", "")
            haystack = f"{content} {category} {item.get('source', '')}".lower()
            lexical = 0.25 if query_lower and query_lower in haystack else 0.0
            recency = max(0.0, 1.0 - ((time.time() - item.get("created_at", 0)) / (86400 * 30))) * 0.15
            rank = item.get("score", 0) + lexical + recency
            scored.append((rank, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        selected = [item for _, item in scored[:limit]]
        if selected:
            ids = {item["id"] for item in selected}
            for item in items:
                if item.get("id") in ids:
                    item["last_accessed"] = time.time()
                    item["access_count"] = item.get("access_count", 0) + 1
            self._write(items)
        return selected

    def stats(self) -> Dict[str, Any]:
        items = self._read()
        if not items:
            return {"count": 0, "avg_score": 0, "high_trust": 0}
        return {
            "count": len(items),
            "avg_score": round(sum(item.get("score", 0) for item in items) / len(items), 3),
            "high_trust": sum(1 for item in items if item.get("trust", 0) >= 0.8),
        }


scored_memory_store = ScoredMemoryStore()
