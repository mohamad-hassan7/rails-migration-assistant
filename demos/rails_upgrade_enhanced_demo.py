#!/usr/bin/env python3
"""
rails_upgrade_enhanced_demo.py

Enhanced Rails upgrade assistant that searches both:
1. Rails documentation and guides
2. RailsDiff data showing actual code changes between versions

Usage:
  python rails_upgrade_enhanced_demo.py 'ApplicationRecord Rails 5'
  python rails_upgrade_enhanced_demo.py 'Turbo Rails 7 JavaScript'
  python rails_upgrade_enhanced_demo.py 'load_defaults configuration'
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.retriever.retriever import Retriever
import json

def categorize_results(results):
    """Categorize search results by source type."""
    docs = []
    raildiff = []
    
    for result in results:
        source_type = result.get('meta', {}).get('source_type', 'docs')
        if source_type.startswith('raildiff'):
            raildiff.append(result)
        else:
            docs.append(result)
    
    return docs, raildiff

def format_raildiff_result(result):
    """Format a raildiff result for display."""
    meta = result.get('meta', {})
    text = result.get('text', '')
    score = result.get('score', 0.0)
    
    old_version = meta.get('old_version', '')
    new_version = meta.get('new_version', '')
    source_type = meta.get('source_type', '')
    file_path = meta.get('file_path', '')
    
    print(f"🔄 {old_version} → {new_version}:")
    print(f"   Score: {score:.3f}")
    if file_path and file_path != 'overview':
        print(f"   File: {file_path}")
    print(f"   Change: {text}")

def format_docs_result(result):
    """Format a documentation result for display."""
    meta = result.get('meta', {})
    text = result.get('text', '')
    score = result.get('score', 0.0)
    
    tag = meta.get('tag', '')
    source_path = meta.get('source_path', '')
    
    print(f"📋 {tag}:")
    print(f"   Score: {score:.3f}")
    print(f"   Source: {source_path}")
    print(f"   Content: {text[:200]}{'...' if len(text) > 200 else ''}")

def demo_enhanced_upgrade_agent(query: str):
    """
    Demo the enhanced Rails upgrade agent with both docs and raildiff data.
    """
    print("🚀 Enhanced Rails Upgrade Agent Demo")
    print("=" * 80)
    print(f"Query: {query}")
    print("-" * 80)
    
    # Step 1: Retrieve relevant content from both sources
    print("🔍 STEP 1: RETRIEVING RELEVANT CONTENT")
    print("-" * 50)
    
    retriever = Retriever("data/faiss_combined.index", "data/meta_combined.jsonl")
    results = retriever.search(query, top_k=8)  # Get more results to show both types
    
    # Categorize results
    docs_results, raildiff_results = categorize_results(results)
    
    print(f"Found {len(results)} total results ({len(docs_results)} docs, {len(raildiff_results)} code changes):\n")
    
    # Show documentation results
    if docs_results:
        print("📚 DOCUMENTATION RESULTS:")
        print("-" * 30)
        for result in docs_results[:3]:  # Show top 3
            format_docs_result(result)
            print()
    
    # Show raildiff results
    if raildiff_results:
        print("🔧 CODE CHANGE RESULTS:")
        print("-" * 30)
        for result in raildiff_results:  # Show all raildiff results
            format_raildiff_result(result)
            print()
    
    # Step 2: Knowledge extraction with both sources
    print("🎯 STEP 2: INTEGRATED KNOWLEDGE EXTRACTION")
    print("-" * 50)
    
    # Extract version information
    versions_found = set()
    code_changes_found = []
    doc_sources_found = set()
    
    for result in docs_results:
        tag = result.get('meta', {}).get('tag', '')
        if tag:
            versions_found.add(tag)
        source = result.get('meta', {}).get('source_path', '')
        if 'guides' in source:
            doc_sources_found.add('Rails Guides')
        elif 'CHANGELOG' in source:
            doc_sources_found.add('Component Changelogs')
    
    for result in raildiff_results:
        meta = result.get('meta', {})
        old_ver = meta.get('old_version', '')
        new_ver = meta.get('new_version', '')
        if old_ver and new_ver:
            code_changes_found.append(f"{old_ver} → {new_ver}")
    
    print("📝 Integrated Analysis:")
    print()
    
    if versions_found:
        print("Documentation Versions:")
        for version in sorted(versions_found):
            print(f"  • {version}")
        print()
    
    if code_changes_found:
        print("Code Changes Identified:")
        for change in sorted(set(code_changes_found)):
            print(f"  • {change}")
        print()
    
    if doc_sources_found:
        print("Documentation Sources:")
        for source in sorted(doc_sources_found):
            print(f"  • {source}")
        print()
    
    # Show specific insights based on raildiff data
    if raildiff_results:
        print("🎯 Specific Code Change Insights:")
        for result in raildiff_results:
            text = result.get('text', '')
            if 'ApplicationRecord' in text:
                print("  • Model inheritance pattern changed")
            elif 'load_defaults' in text:
                print("  • Application configuration updated")
            elif 'turbo' in text.lower() or 'turbolinks' in text.lower():
                print("  • JavaScript/Frontend framework migration needed")
            elif 'javascript_pack_tag' in text or 'importmap' in text:
                print("  • Asset pipeline changes required")
    
    print()
    print("=" * 80)
    print("✅ ENHANCED DEMO COMPLETE")
    print("This demonstrates combined search across Rails documentation AND actual code changes!")
    if not raildiff_results:
        print("💡 Try queries like 'ApplicationRecord', 'load_defaults', or 'Turbo Rails' to see code changes.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python rails_upgrade_enhanced_demo.py 'query'")
        print("\nExample queries:")
        print("  'ApplicationRecord Rails 5 models'")
        print("  'Turbo Rails 7 JavaScript migration'") 
        print("  'load_defaults configuration changes'")
        print("  'Rails version upgrade Gemfile'")
        sys.exit(1)
    
    query = sys.argv[1]
    demo_enhanced_upgrade_agent(query)

if __name__ == "__main__":
    main()
