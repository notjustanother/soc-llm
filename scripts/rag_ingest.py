#!/usr/bin/env python3
"""Minimal RAG ingest demo:
- Loads small ATT&CK-like and Sigma snippets
- Embeds using sentence-transformers
- Indexes into an in-memory Qdrant collection
- Demonstrates a top-k retrieval function
"""
import json, os, sys
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
KN_DIR = ROOT / "data" / "knowledge"
ATTACK_PATH = KN_DIR / "attack.json"
SIGMA_PATH = KN_DIR / "sigma_rules.yml"

def load_sigma_blocks(path):
    # naive split on '---' for this demo
    text = Path(path).read_text()
    blocks = [b.strip() for b in text.split('---') if b.strip()]
    docs = []
    for i, b in enumerate(blocks):
        title = None
        for line in b.splitlines():
            if line.lower().startswith("title:"):
                title = line.split(":",1)[1].strip()
                break
        docs.append({"id": f"SIGMA:{i+1}", "title": title or f"Sigma {i+1}", "content": b})
    return docs

def main():
    attack = json.loads(Path(ATTACK_PATH).read_text())
    sigma_docs = load_sigma_blocks(SIGMA_PATH)

    # Build corpus
    corpus = []
    for a in attack:
        corpus.append({
            "id": f"ATTACK:{a['id']}",
            "title": f"{a['id']} - {a['name']}",
            "content": f"{a['desc']} Detection: {a['detection']}"
        })
    corpus += sigma_docs

    # Embed
    model_name = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    st = SentenceTransformer(model_name)
    texts = [f"{d['title']}
{d['content']}" for d in corpus]
    vecs = st.encode(texts, normalize_embeddings=True)

    # Qdrant in-memory client
    client = QdrantClient(":memory:")
    COL = "soc_knowledge"
    client.recreate_collection(
        collection_name=COL,
        vectors_config=VectorParams(size=vecs.shape[1], distance=Distance.COSINE)
    )

    points = [PointStruct(id=i, vector=vecs[i].tolist(), payload=corpus[i]) for i in range(len(corpus))]
    client.upsert(collection_name=COL, points=points)

    # Simple search
    def search(query, top_k=3):
        qv = st.encode([query], normalize_embeddings=True)[0]
        res = client.search(collection_name=COL, query_vector=qv.tolist(), limit=top_k)
        return [{"score": r.score, **r.payload} for r in res]

    # demo query
    demo_q = os.environ.get("QUERY", "suspicious access to lsass.exe handle")
    results = search(demo_q, top_k=3)
    print("\nTop results for:", demo_q)
    for r in results:
        print(f"- ({r['score']:.3f}) {r['title']} -> {r['id']}")

if __name__ == "__main__":
    main()
