#!/usr/bin/env python3
"""
End-to-end Rails upgrade agent test
Combines retriever + LLM for upgrade suggestions
"""
import sys
import json
from src.retriever.retriever import Retriever
from src.model.local_llm import LocalLLM

def get_chunk_text(chunk_id: int):
    """Get the actual text for a chunk by ID"""
    with open("data/chunks.jsonl", "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            if line_num == chunk_id:
                chunk_data = json.loads(line)
                return chunk_data["text"]
    return "Text not found"

def rails_upgrade_agent(query: str, from_version: str = None, to_version: str = None):
    """Complete Rails upgrade agent pipeline"""
    
    print(f"🚀 Rails Upgrade Agent")
    print("=" * 60)
    print(f"Query: {query}")
    if from_version and to_version:
        print(f"Upgrade Path: {from_version} → {to_version}")
    print("-" * 60)
    
    # Step 1: Retrieve relevant documentation
    print("🔍 Step 1: Retrieving relevant documentation...")
    retriever = Retriever("data/rails.index", "data/meta.jsonl")
    
    # Enhance query with version info if provided
    enhanced_query = query
    if from_version and to_version:
        enhanced_query = f"{query} Rails {from_version} to {to_version} upgrade"
    
    results = retriever.search(enhanced_query, top_k=5)
    
    # Build context from retrieved documents
    context_pieces = []
    print("\n📋 Retrieved Documentation:")
    for i, result in enumerate(results):
        chunk_text = get_chunk_text(result["id"])
        meta = result["meta"]
        
        print(f"{i+1}. [{meta['tag']}] {meta['source_path']} (Score: {result['score']:.3f})")
        print(f"   {chunk_text[:100]}...")
        
        # Add to context with version info
        context_piece = f"[{meta['tag']}] {chunk_text}"
        context_pieces.append(context_piece)
    
    # Step 2: Generate LLM response with context
    print("\n🤖 Step 2: Generating upgrade suggestions...")
    
    context = "\n\n".join(context_pieces[:3])  # Use top 3 results
    
    prompt = f"""Based on official Rails documentation, provide upgrade guidance:

=== RAILS UPGRADE CONTEXT ===
{context}

=== USER QUERY ===
{query}

=== UPGRADE GUIDANCE ===
Based on the documentation above, here are the key considerations for Rails upgrade:

1. Version Requirements:"""
    
    llm = LocalLLM()
    response = llm.generate(prompt, max_new_tokens=300)
    
    print("\n📝 UPGRADE SUGGESTIONS:")
    print("-" * 40)
    print(response)
    print("\n" + "=" * 60)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python rails_upgrade_agent.py 'query'")
        print("  python rails_upgrade_agent.py 'query' from_version to_version")
        print("\nExamples:")
        print("  python rails_upgrade_agent.py 'ActiveRecord ApplicationRecord Rails 5'")
        print("  python rails_upgrade_agent.py 'upgrade deprecations' v4.2.11 v5.0.0")
        return
    
    query = sys.argv[1]
    from_version = sys.argv[2] if len(sys.argv) > 2 else None
    to_version = sys.argv[3] if len(sys.argv) > 3 else None
    
    rails_upgrade_agent(query, from_version, to_version)

if __name__ == "__main__":
    main()
