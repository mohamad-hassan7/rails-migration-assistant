# src/retriever/retriever.py
import json
from pathlib import Path
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, index_path: str, meta_path: str, embed_model="all-MiniLM-L6-v2"):
        self.index_path = index_path
        self.meta_path = meta_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedder = SentenceTransformer(embed_model, device=self.device)
        self.index = faiss.read_index(index_path)
        # load metas into a list where position = doc id
        self.metas = []
        with open(meta_path, "r", encoding="utf-8") as f:
            for line in f:
                self.metas.append(json.loads(line))

    def search(self, query: str, top_k: int = 5):
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        # normalize
        faiss.normalize_L2(q_emb)
        D, I = self.index.search(q_emb, top_k)
        scores = D[0]
        ids = I[0]
        results = []
        for sid, score in zip(ids, scores):
            if sid < 0:
                continue
            meta = self.metas[sid]
            results.append({
                "id": sid,
                "score": float(score),
                "meta": meta,
            })
        return results
