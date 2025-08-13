#!/usr/bin/env python3
"""
Rails Upgrade Agent Demo - Shows retrieval + knowledge extraction
Demonstrates the complete pipeline even with limited LLM
"""
import sys
import json
from src.retriever.retriever import Retriever

def get_chunk_text(chunk_id: int):
    """Get the actual text for a chunk by ID"""
    with open("data/chunks.jsonl", "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            if line_num == chunk_id:
                chunk_data = json.loads(line)
                return chunk_data["text"]
    return "Text not found"

def demo_upgrade_agent(query: str):
    """Demo Rails upgrade agent capabilities"""
    
    print(f"🚀 Rails Upgrade Agent Demo")
    print("=" * 80)
    print(f"Query: {query}")
    print("-" * 80)
    
    # Step 1: Retrieve relevant documentation
    print("🔍 STEP 1: RETRIEVING RELEVANT DOCUMENTATION")
    print("-" * 50)
    
    retriever = Retriever("data/faiss.index", "data/meta.jsonl")
    results = retriever.search(query, top_k=5)
    
    print(f"Found {len(results)} relevant documents:\n")
    
    # Group by Rails version for better analysis
    by_version = {}
    for result in results:
        chunk_text = get_chunk_text(result["id"])
        meta = result["meta"]
        version = meta['tag']
        
        if version not in by_version:
            by_version[version] = []
        
        by_version[version].append({
            'text': chunk_text,
            'source': meta['source_path'],
            'score': result['score']
        })
    
    # Display results grouped by version
    for version in sorted(by_version.keys()):
        print(f"📋 {version}:")
        for item in by_version[version][:2]:  # Top 2 per version
            print(f"   Score: {item['score']:.3f}")
            print(f"   Source: {item['source']}")
            print(f"   Content: {item['text'][:150]}...")
            print()
    
    print("🎯 STEP 2: KNOWLEDGE EXTRACTION")
    print("-" * 50)
    
    # Extract key information from retrieved documents
    upgrade_info = extract_upgrade_info(by_version)
    
    print("📝 Extracted Upgrade Knowledge:")
    for info_type, content in upgrade_info.items():
        print(f"\n{info_type}:")
        for item in content:
            print(f"  • {item}")
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE")
    print("This demonstrates the retrieval and knowledge extraction pipeline.")
    print("With a Rails-trained LLM, this would generate specific upgrade suggestions.")

def extract_upgrade_info(by_version):
    """Extract structured upgrade information from retrieved documents"""
    info = {
        "Versions Covered": [],
        "Key Changes Found": [],
        "Documentation Sources": []
    }
    
    for version, items in by_version.items():
        info["Versions Covered"].append(version)
        
        for item in items[:1]:  # Top result per version
            text = item['text'].lower()
            
            # Look for key upgrade-related terms
            if 'deprecat' in text:
                info["Key Changes Found"].append(f"{version}: Contains deprecation information")
            if 'breaking' in text:
                info["Key Changes Found"].append(f"{version}: Contains breaking changes")
            if 'new' in text and 'feature' in text:
                info["Key Changes Found"].append(f"{version}: Contains new features")
            if 'applicationrecord' in text:
                info["Key Changes Found"].append(f"{version}: ApplicationRecord changes")
            if 'zeitwerk' in text:
                info["Key Changes Found"].append(f"{version}: Zeitwerk autoloader")
                
            # Add source types
            source = item['source']
            if 'upgrade' in source:
                info["Documentation Sources"].append("Upgrade Guide")
            elif 'changelog' in source:
                info["Documentation Sources"].append("Changelog")
            elif 'release_notes' in source:
                info["Documentation Sources"].append("Release Notes")
    
    # Remove duplicates
    for key in info:
        info[key] = list(set(info[key]))
    
    return info

def main():
    if len(sys.argv) < 2:
        print("Usage: python rails_upgrade_demo.py 'query'")
        print("\nExample queries:")
        print("  'Rails 5 ApplicationRecord changes'")
        print("  'Rails 6 Zeitwerk autoloader'")
        print("  'Rails 7 Turbo import maps'")
        print("  'deprecated methods Rails upgrade'")
        return
    
    query = " ".join(sys.argv[1:])
    demo_upgrade_agent(query)

if __name__ == "__main__":
    main()
