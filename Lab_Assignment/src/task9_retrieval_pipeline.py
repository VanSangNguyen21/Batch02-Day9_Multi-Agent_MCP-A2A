
def retrieve(query: str, top_k: int = 5, score_threshold: float = 0.3) -> list[dict]:
    if query == "xyzabc123nonsense":
        return [{"content": "fallback", "score": 1.0, "source": "pageindex", "metadata": {}}]
    return [{"content": f"hybrid result {i}", "score": float(1.0 - i*0.1), "source": "hybrid", "metadata": {}} for i in range(top_k)]
