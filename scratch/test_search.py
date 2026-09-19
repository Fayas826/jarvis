import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.specialized.web_search_agent import WebSearchAgent

def main():
    print("==========================================")
    print(" JARVIS LIVE INTERNET SEARCH DEMO")
    print("==========================================")
    
    agent = WebSearchAgent()
    query = "Current price of Bitcoin today"
    
    print(f"[*] Accessing Global Internet via WebSearchAgent...")
    print(f"[*] Executing Search: '{query}'\n")
    
    result = agent.execute_search(query, num_results=2)
    
    if result["status"] == "success":
        for idx, res in enumerate(result["results"], 1):
            print(f"Result {idx}:")
            print(f"Title: {res['title']}")
            print(f"Snippet: {res['snippet']}")
            print(f"URL: {res['url']}\n")
    else:
        print("Search Failed:", result.get("error"))

if __name__ == "__main__":
    main()
