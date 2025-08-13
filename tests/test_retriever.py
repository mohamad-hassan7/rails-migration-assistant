#!/usr/bin/env python3
"""
Test the Rails upgrade retriever
"""
import sys
from pathlib import Path
from src.retriever.retriever import Retriever

def test_retriever():
    """Test the retriever with Rails upgrade queries"""
    
    print("🔍 Testing Rails Upgrade Retriever")
    print("=" * 50)
    
    # Initialize retriever
    print("Loading retriever...")
    retriever = Retriever("data/rails.index", "data/meta.jsonl")
    print("✅ Retriever loaded successfully\n")
    
    # Test queries
    test_queries = [
        "Rails 5 ActiveRecord ApplicationRecord",
        "upgrading from Rails 4.2 to Rails 5.0",
        "Zeitwerk autoloader Rails 6",
        "deprecated find_by Rails upgrade",
        "Rails 7 Turbo import maps",
        "Rails migration breaking changes"
    ]
    
    for query in test_queries:
        print(f"🔎 Query: '{query}'")
        print("-" * 40)
        
        results = retriever.search(query, top_k=3)
        
        for i, result in enumerate(results):
            meta = result["meta"]
            score = result["score"]
            
            print(f"{i+1}. Score: {score:.3f}")
            print(f"   Version: {meta['tag']}")
            print(f"   Source: {meta['source_path']}")
            print(f"   Text: {result['meta']['text'] if 'text' in result['meta'] else 'N/A'}...")
            print()
        
        print("-" * 40)
        print()

def test_specific_query(query: str):
    """Test retriever with a specific query"""
    retriever = Retriever("data/faiss_combined.index", "data/meta_combined.jsonl")
    
    print(f"Query: '{query}'")
    print("=" * 60)
    
    results = retriever.search(query, top_k=10)
    
    raildiff_found = 0
    
    for i, result in enumerate(results):
        meta = result["meta"]
        score = result["score"]
        source_type = meta.get('source_type', 'docs')
        
        if source_type.startswith('raildiff'):
            raildiff_found += 1
            print(f"\n🔧 RAILDIFF RESULT {raildiff_found}:")
            print(f"   Score: {score:.3f}")
            print(f"   Type: {source_type}")
            print(f"   Versions: {meta.get('old_version', 'N/A')} → {meta.get('new_version', 'N/A')}")
            print(f"   File: {meta.get('file_path', 'N/A')}")
            
            # Get the text from the combined chunks
            with open("data/chunks_combined.jsonl", "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f):
                    if line_num == result["id"]:
                        import json
                        chunk_data = json.loads(line)
                        text = chunk_data["text"]
                        print(f"   Text: {text}")
                        break
        else:
            if i < 3:  # Show first 3 doc results
                print(f"\n📚 DOC RESULT {i+1}:")
                print(f"   Score: {score:.3f} | Version: {meta.get('tag', 'N/A')}")
                print(f"   Source: {meta.get('source_path', 'N/A')}")
                
                # Get the text from the combined chunks  
                with open("data/chunks_combined.jsonl", "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f):
                        if line_num == result["id"]:
                            import json
                            chunk_data = json.loads(line)
                            text = chunk_data["text"]
                            print(f"   Text: {text[:200]}...")
                            break
    
    print(f"\n📊 SUMMARY: Found {raildiff_found} raildiff results out of {len(results)} total results")
    print("-" * 60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        test_specific_query(query)
    else:
        test_retriever()
