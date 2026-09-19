import time
import hashlib
import json
from typing import Dict, Any, Optional

# 🚀 O.M.E.G.A. CACHE_LAYER_V1
# Implements command, embedding, and response caching.

class CacheManager:
    def __init__(self):
        self.command_cache = {} # Exact string match
        self.response_cache = {} # Hash of query -> response
        self.hit_count = 0
        self.total_requests = 0

    def _get_hash(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def get_cached_command(self, text: str) -> Optional[Dict]:
        self.total_requests += 1
        res = self.command_cache.get(text.lower().strip())
        if res:
            self.hit_count += 1
            return res
        return None

    def set_cached_command(self, text: str, action: Dict):
        self.command_cache[text.lower().strip()] = action

    def get_cached_response(self, text: str) -> Optional[Dict]:
        query_hash = self._get_hash(text)
        res = self.response_cache.get(query_hash)
        if res:
            # Check for TTL (e.g., 1 hour)
            if time.time() - res['timestamp'] < 3600:
                self.hit_count += 1
                return res['data']
        return None

    def set_cached_response(self, text: str, response: Dict):
        query_hash = self._get_hash(text)
        self.response_cache[query_hash] = {
            "timestamp": time.time(),
            "data": response
        }

    def get_metrics(self) -> Dict[str, Any]:
        hit_rate = (self.hit_count / self.total_requests * 100) if self.total_requests > 0 else 0
        return {
            "hit_rate": f"{hit_rate:.1f}%",
            "total_requests": self.total_requests,
            "hits": self.hit_count,
            "cache_size": len(self.command_cache) + len(self.response_cache)
        }

cache_manager = CacheManager()
