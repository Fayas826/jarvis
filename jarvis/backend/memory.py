import chromadb

client = chromadb.Client()
collection = client.create_collection(name="jarvis_memory")

def save_memory(text):
    collection.add(
        documents=[text],
        ids=[str(hash(text))]
    )

def get_memory(query):
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    return results["documents"]
