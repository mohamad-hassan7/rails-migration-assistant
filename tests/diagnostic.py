#!/usr/bin/env python3
"""
Diagnostic script to check Rails Migration Assistant dependencies and configuration.
"""

import os
import sys

def check_dependencies():
    """Check critical dependencies for Rails Migration Assistant."""
    
    print("🔍 Rails Migration Assistant Diagnostic Report")
    print("=" * 60)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check critical files
    critical_files = [
        "data/faiss_combined.index",
        "data/meta_combined.jsonl", 
        "src/analyzer/hybrid_analyzer.py",
        "src/model/local_llm.py",
        "src/retriever/retriever.py"
    ]
    
    print("\n📁 Critical Files Check:")
    all_files_exist = True
    for file_path in critical_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} - MISSING")
            all_files_exist = False
    
    # Check dependencies
    print("\n📦 Dependencies Check:")
    required_packages = [
        'tkinter',
        'numpy', 
        'faiss',
        'torch',
        'transformers',
        'accelerate'
    ]
    
    available_packages = []
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'faiss':
                import faiss
            elif package == 'numpy':
                import numpy
            elif package == 'torch':
                import torch
            elif package == 'transformers':
                import transformers
            elif package == 'accelerate':
                import accelerate
            else:
                __import__(package)
            print(f"✅ {package}")
            available_packages.append(package)
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    # Diagnosis and recommendations
    print("\n🩺 Diagnosis:")
    if all_files_exist:
        print("✅ All critical files are present")
    else:
        print("❌ Some critical files are missing")
    
    if 'tkinter' in available_packages:
        print("✅ GUI components available")
    else:
        print("❌ GUI components not available")
    
    if 'faiss' in available_packages and 'numpy' in available_packages:
        print("✅ Knowledge base retriever components available")
    else:
        print("❌ Knowledge base retriever components missing")
    
    if 'torch' in available_packages and 'transformers' in available_packages:
        print("✅ AI/LLM components available")
    else:
        print("❌ AI/LLM components missing")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if missing_packages:
        print("📥 Install missing packages:")
        if 'torch' in missing_packages or 'transformers' in missing_packages:
            print("   pip install torch transformers accelerate")
        if 'faiss' in missing_packages:
            print("   pip install faiss-cpu")
        if 'numpy' in missing_packages:
            print("   pip install numpy")
    
    # What should work
    print("\n🚀 Current Capabilities:")
    if 'tkinter' in available_packages:
        print("✅ GUI interface will launch")
    
    if all_files_exist and 'faiss' in available_packages and 'numpy' in available_packages:
        print("✅ Knowledge base retriever should work")
        print("   (Fixed the retriever availability check)")
    
    if 'torch' in missing_packages:
        print("⚠️  AI/LLM features will use fallback responses")
        print("   (Query mode will work with basic responses)")
    else:
        print("✅ Full AI capabilities available")
    
    # Summary
    print(f"\n📊 Summary: {len(available_packages)}/{len(required_packages)} dependencies available")
    
    return len(missing_packages) == 0

if __name__ == "__main__":
    check_dependencies()
