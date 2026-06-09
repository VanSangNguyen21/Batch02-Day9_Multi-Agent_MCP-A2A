
def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    res = candidates[:top_k]
    for i, r in enumerate(res):
        r["score"] = float(1.0 - i*0.1)
    return res
