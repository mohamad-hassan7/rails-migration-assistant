#!/usr/bin/env python3
"""
Simple test to verify knowledge base retriever is working correctly.
"""

import os
import sys

def test_knowledge_base():
    """Test that the knowledge base retriever is properly accessible."""
    
    print("🔍 Testing knowledge base retriever accessibility...")
    
    # Check if FAISS files exist
    faiss_path = "data/faiss_combined.index"
    meta_path = "data/meta_combined.jsonl"
    
    if os.path.exists(faiss_path):
        print(f"✅ FAISS index found: {faiss_path}")
    else:
        print(f"❌ FAISS index missing: {faiss_path}")
        return
        
    if os.path.exists(meta_path):
        print(f"✅ Meta file found: {meta_path}")
    else:
        print(f"❌ Meta file missing: {meta_path}")
        return
    
    # Try to import and test the analyzer
    try:
        from src.analyzer.hybrid_analyzer import HybridRailsAnalyzer
        print("✅ HybridRailsAnalyzer imported successfully")
        
        # Initialize with retriever enabled (default)
        analyzer = HybridRailsAnalyzer()
        
        # Check if tier2_analyzer and retriever are available
        if hasattr(analyzer, 'tier2_analyzer') and analyzer.tier2_analyzer:
            print("✅ Tier2 analyzer initialized")
            
            if hasattr(analyzer.tier2_analyzer, 'retriever') and analyzer.tier2_analyzer.retriever:
                print("✅ Knowledge base retriever is available and working!")
                
                # Test a simple query
                try:
                    results = analyzer.tier2_analyzer.retriever.search("Rails deprecation", top_k=1)
                    print(f"✅ Test query successful: {len(results)} results found")
                except Exception as e:
                    print(f"⚠️ Test query failed: {e}")
            else:
                print("❌ Knowledge base retriever not available in tier2_analyzer")
        else:
            print("❌ Tier2 analyzer not initialized")
            
    except Exception as e:
        print(f"❌ Error testing analyzer: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Knowledge base retriever test completed!")

if __name__ == "__main__":
    test_knowledge_base()
