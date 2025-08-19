#!/usr/bin/env python3
"""
Rails Migration Assistant - Data Regeneration Script

This script regenerates all data from scratch:
1. Fetches fresh Rails documentation
2. Processes Rails diffs  
3. Chunks documents
4. Rebuilds search indices

Usage:
    python regenerate_data.py [--full]
    
Options:
    --full    Include intermediate versions (slower but more comprehensive)
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Regenerate Rails Migration Assistant data")
    parser.add_argument("--full", action="store_true", 
                       help="Include intermediate versions (slower)")
    args = parser.parse_args()
    
    print("🚀 Rails Migration Assistant - Data Regeneration")
    print("=" * 50)
    
    # Step 1: Fetch Rails documentation
    if args.full:
        doc_cmd = [sys.executable, "src/ingest/smart_docs_fetcher.py", "--include-intermediates"]
    else:
        doc_cmd = [sys.executable, "src/ingest/smart_docs_fetcher.py", "--tags", "v4.2.11", "v7.0.8"]
    
    if not run_command(doc_cmd, "Fetching Rails documentation"):
        return 1
    
    # Step 2: Fetch Rails diffs
    if not run_command([sys.executable, "src/ingest/raildiff_fetcher.py"], "Fetching Rails diffs"):
        return 1
    
    # Step 3: Process Rails diffs
    if not run_command([sys.executable, "src/ingest/raildiff_ingest.py"], "Processing Rails diffs"):
        return 1
    
    # Step 4: Chunk documents
    if not run_command([sys.executable, "-m", "src.retriever.chunk_docs", 
                       "--docs-dir", "data/docs", "--out", "data/chunks.jsonl"], 
                      "Chunking documents"):
        return 1
    
    # Step 5: Build search index
    if not run_command([sys.executable, "-m", "src.retriever.build_index"], 
                      "Building search index"):
        return 1
    
    print("\n🎉 Data regeneration completed successfully!")
    print("Your Rails Migration Assistant is ready with fresh data.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
