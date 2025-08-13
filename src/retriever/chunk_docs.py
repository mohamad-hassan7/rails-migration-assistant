# src/retriever/chunk_docs.py
import argparse
from pathlib import Path
import json
import textwrap

def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return path.read_text(encoding="latin-1")

def chunk_text(text: str, chunk_size=1000, overlap=200):
    # naive character-based chunker with overlap
    start = 0
    L = len(text)
    while start < L:
        end = start + chunk_size
        chunk = text[start:end]
        yield start, min(end, L), chunk.strip()
        start = end - overlap

def process_docs(docs_dir: str, out_path: str, chunk_size=1000, overlap=200):
    docs_dir = Path(docs_dir)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    idx = 0
    with out_path.open("w", encoding="utf-8") as fo:
        for tag_dir in sorted(docs_dir.iterdir()):
            if not tag_dir.is_dir():
                continue
            tag = tag_dir.name
            for file in tag_dir.rglob("*"):
                if file.is_dir():
                    continue
                # skip common binary files
                if file.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".pdf"]:
                    continue
                text = read_text_file(file)
                # split into paragraphs first to avoid breaking sentences too often
                paragraphs = [p for p in text.split("\n\n") if p.strip()]
                for para in paragraphs:
                    for start, end, chunk in chunk_text(para, chunk_size=chunk_size, overlap=overlap):
                        # Use relative path from docs_dir instead of cwd for better portability
                        try:
                            rel_path = file.relative_to(docs_dir)
                            source_path = str(Path(docs_dir.name) / rel_path)
                        except ValueError:
                            # Fallback to absolute path if relative doesn't work
                            source_path = str(file)
                            
                        meta = {
                            "id": idx,
                            "tag": tag,
                            "source_path": source_path,
                            "start_char": start,
                            "end_char": end,
                        }
                        doc = {
                            "id": idx,
                            "text": chunk,
                            "meta": meta
                        }
                        fo.write(json.dumps(doc, ensure_ascii=False) + "\n")
                        idx += 1
    print(f"Wrote {idx} chunks to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", required=True, help="data/docs root")
    parser.add_argument("--out", required=True, help="output chunks jsonl")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=200)
    args = parser.parse_args()
    process_docs(args.docs_dir, args.out, args.chunk_size, args.overlap)
