
def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    return [{"content": f"semantic result {i}", "score": float(1.0 - i*0.1), "metadata": {}} for i in range(top_k)]
