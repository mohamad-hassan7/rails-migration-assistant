# src/retriever/build_index.py
import argparse
import json
from pathlib import Path
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def load_chunks(chunks_path):
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def build_embeddings(chunks_path, model_name="all-MiniLM-L6-v2", device=None):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = SentenceTransformer(model_name, device=device)
    texts = []
    metas = []
    for c in load_chunks(chunks_path):
        texts.append(c["text"])
        metas.append(c["meta"])
    # compute embeddings in batches
    embeddings = model.encode(texts, batch_size=64, convert_to_numpy=True, show_progress_bar=True)
    return embeddings, metas

def build_faiss_index(embeddings: np.ndarray, index_path: str, normalize=True):
    d = embeddings.shape[1]
    if normalize:
        # L2 normalize for cosine similarity via inner product
        faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(d) if normalize else faiss.IndexFlatL2(d)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    print(f"Saved FAISS index to {index_path}")

def save_meta(metas, meta_path):
    with open(meta_path, "w", encoding="utf-8") as fo:
        for m in metas:
            fo.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"Saved {len(metas)} metadata records to {meta_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks", required=True, help="chunks jsonl path")
    parser.add_argument("--index-out", required=True, help="output faiss index path")
    parser.add_argument("--meta-out", required=True, help="output meta jsonl path")
    parser.add_argument("--model", default="all-MiniLM-L6-v2")
    args = parser.parse_args()

    embeddings, metas = build_embeddings(args.chunks, model_name=args.model)
    # embeddings is numpy array (N, d)
    build_faiss_index(embeddings, args.index_out, normalize=True)
    save_meta(metas, args.meta_out)
