#!/usr/bin/env python3
"""
Test script for Rails upgrade agent - demonstrates the pipeline
"""

from src.model.local_llm import LocalLLM

def test_rails_upgrade_suggestion():
    """Test the LLM's ability to provide Rails upgrade suggestions"""
    
    llm = LocalLLM()
    
    # Test prompt simulating Rails upgrade scenario
    prompt = """# Rails upgrade from 4.2 to 5.0
# Deprecated: find_by_* methods
User.find_by_name("John")

# Convert to Rails 5.0 syntax:"""
    
    print("Testing Rails upgrade suggestion:")
    print(f"Input: {prompt}")
    print("\nLLM Response:")
    response = llm.generate(prompt, max_new_tokens=100)
    print(response)
    print("-" * 50)

if __name__ == "__main__":
    test_rails_upgrade_suggestion()
