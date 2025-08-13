#!/usr/bin/env python3
"""
Test script to verify Gemini API setup
Run this after setting your GEMINI_API_KEY in .env
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.gemini_llm import GeminiLLM

def test_gemini():
    print("🧪 Testing Gemini API Setup")
    print("=" * 30)
    
    try:
        print("Initializing Gemini LLM...")
        gemini = GeminiLLM()
        
        print("Testing simple generation...")
        response = gemini.generate(
            "Hello! Please respond with a brief message about Rails upgrade analysis.", 
            max_new_tokens=100
        )
        
        print(f"✅ Success! Response received:")
        print(f"📝 {response}")
        print(f"\n🎉 Gemini API is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Make sure to:")
        print("1. Set GEMINI_API_KEY in your .env file")
        print("2. Ensure google-generativeai is installed: pip install google-generativeai")
        print("3. Check your API key is valid and has quota remaining")
        
if __name__ == "__main__":
    test_gemini()
