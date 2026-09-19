import logging
from typing import Dict, Any

try:
    from duckduckgo_search import DDGS
except ImportError:
    logging.warning("duckduckgo-search missing. Install via: python -m pip install duckduckgo-search")
    DDGS = None

class WebSearchAgent:
    """
    JARVIS Specialized Swarm Member: The Researcher.
    Connects to the Global Internet via DuckDuckGo API to completely bypass
    Google CAPTCHAs and silently feed live data back to the Orchestrator.
    """
    
    def __init__(self):
        pass

    def execute_search(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """
        Executes a stealth DuckDuckGo search.
        """
        if not DDGS:
            return {"status": "error", "message": "Missing duckduckgo_search library."}
            
        logging.info(f"🌐 [Web Search Agent] Accessing Stealth Internet. Query: '{query}'")
        
        try:
            results = []
            with DDGS() as ddgs:
                ddg_results = ddgs.text(query, max_results=num_results)
                for r in ddg_results:
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", "")
                    })
                    
            logging.info(f"[Web Search Agent] Extracted {len(results)} live results without triggering CAPTCHAs.")
            return {"status": "success", "results": results}
            
        except Exception as e:
            logging.error(f"❌ [Web Search Agent] Search Failed: {e}")
            return {"status": "failed", "error": str(e)}
