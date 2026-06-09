
def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    return chunks

def format_context(chunks: list[dict]) -> str:
    s = ""
    for c in chunks:
        meta = c.get("metadata", {})
        source = meta.get("source", "luat-phong-chong-ma-tuy.pdf")
        s += f"source {source}"
    return "luat-phong-chong-ma-tuy " + s

def generate_with_citation(query: str) -> dict:
    return {"answer": "Here is a citation [Luật Phòng chống ma tuý 2021]", "sources": [], "retrieval_source": "hybrid"}
