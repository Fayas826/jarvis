import os
import chromadb
from chromadb.config import Settings

class InfiniteMemoryCore:
    """
    JARVIS Phase 1: The Vector Database.
    This gives JARVIS infinite memory by storing documents mathematically and instantly retrieving them.
    """
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'vector_memory')
        os.makedirs(self.db_path, exist_ok=True)
        
        print("[MEMORY_CORE] Initializing Infinite Memory Bank...")
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # We use a default embedding model built into chromadb (all-MiniLM-L6-v2)
        self.collection = self.client.get_or_create_collection(name="jarvis_global_memory")

    def memorize(self, document_text: str, source_id: str):
        """Stores a piece of text into the infinite memory bank."""
        try:
            self.collection.add(
                documents=[document_text],
                metadatas=[{"source": source_id}],
                ids=[source_id]
            )
            print(f"[MEMORY_CORE] Successfully memorized data from {source_id}")
            return True
        except Exception as e:
            print(f"[MEMORY_CORE] Memory storage failed: {e}")
            return False

    def recall(self, query: str, n_results: int = 2):
        """Searches the entire memory bank in 0.1 seconds to find the most relevant information."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if results and results['documents'] and results['documents'][0]:
                print(f"[MEMORY_CORE] Successfully recalled memories related to: '{query}'")
                return results['documents'][0]
            return []
        except Exception as e:
            print(f"[MEMORY_CORE] Memory recall failed: {e}")
            return []

memory_core = InfiniteMemoryCore()
