#!/usr/bin/env python3

import sys
sys.path.append('src')

from src.model.local_llm import LocalLLM
from src.analyzer.code_parser import build_strong_params_prompt

def test_simple_prompt():
    """Test a very simple mass assignment fix."""
    
    print("🧪 TESTING SIMPLE MASS ASSIGNMENT FIX")
    print("=" * 50)
    
    # Initialize LLM
    print("🚀 Loading local LLM...")
    llm = LocalLLM()
    print("✅ LLM loaded")
    
    # Simple test case
    method_content = """def update
  @user.update_attributes(params[:user])
  redirect_to @user
end"""
    
    vulnerable_line = "@user.update_attributes(params[:user])"
    
    prompt = build_strong_params_prompt(method_content, "UsersController", vulnerable_line)
    
    print("\n📝 PROMPT:")
    print("-" * 30)
    print(prompt)
    print("-" * 30)
    
    print("\n🤖 GENERATING AI RESPONSE...")
    
    # Generate with very specific parameters for code generation
    response = llm.generate(
        prompt, 
        max_new_tokens=400,  # Shorter response
        temperature=0.01,    # Very deterministic
        do_sample=False,     # No sampling
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.1,
        pad_token_id=llm.tokenizer.eos_token_id
    )
    
    print("\n✨ AI RESPONSE:")
    print("=" * 50)
    print(repr(response))
    print("=" * 50)
    
    # Analysis
    print("\n🔍 ANALYSIS:")
    print(f"Length: {len(response)}")
    print(f"Contains 'def': {'def' in response}")
    print(f"Contains 'update_attributes': {'update_attributes' in response}")
    print(f"Contains 'update(': {'update(' in response}")
    print(f"Contains 'permit(': {'permit(' in response}")
    print(f"Contains 'require(': {'require(' in response}")
    print(f"Contains 'private': {'private' in response}")
    print(f"Contains C code: {'#include' in response or 'printf' in response}")
    print(f"Contains HTML: {'<' in response and '>' in response}")

if __name__ == "__main__":
    test_simple_prompt()
