
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def load_documents():
    return [{"content": "hello world " * 50, "metadata": {}}]

def chunk_documents(docs):
    chunks = []
    for doc in docs:
        c = doc["content"]
        chunks.append({"content": c[:CHUNK_SIZE], "metadata": {}})
    return chunks
