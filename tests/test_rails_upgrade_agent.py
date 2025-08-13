#!/usr/bin/env python3
"""
Test Rails upgrade agent with actual documentation
Demonstrates how to use the fetched docs with the LLM
"""
import sys
from pathlib import Path
from src.model.local_llm import LocalLLM

def load_upgrade_guide(version):
    """Load the upgrade guide for a specific Rails version"""
    docs_dir = Path("data/docs")
    upgrade_file = docs_dir / version / "guides" / "source" / "upgrading_ruby_on_rails.md"
    
    if upgrade_file.exists():
        with open(upgrade_file, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def test_upgrade_suggestion(from_version, to_version):
    """Test upgrade suggestion using actual Rails documentation"""
    
    print(f"Testing Rails upgrade: {from_version} → {to_version}")
    print("-" * 50)
    
    # Load upgrade guides
    from_guide = load_upgrade_guide(from_version)
    to_guide = load_upgrade_guide(to_version)
    
    if not from_guide or not to_guide:
        print("❌ Missing documentation for one or both versions")
        return
    
    # Extract key sections (first 1000 chars for demo)
    from_section = from_guide[:1000] + "..."
    to_section = to_guide[:1000] + "..."
    
    # Create prompt with actual Rails documentation
    prompt = f"""Based on official Rails documentation, provide upgrade guidance:

=== UPGRADING FROM RAILS {from_version} ===
{from_section}

=== UPGRADING TO RAILS {to_version} ===
{to_section}

=== UPGRADE TASK ===
A Rails app needs to upgrade from {from_version} to {to_version}.

Key considerations and steps:"""
    
    # Get LLM suggestion
    print("🤖 Loading LLM for upgrade analysis...")
    llm = LocalLLM()
    
    print("🔄 Generating upgrade suggestions...")
    response = llm.generate(prompt, max_new_tokens=200)
    
    print("\n📋 UPGRADE SUGGESTIONS:")
    print(response)
    print("\n" + "=" * 50)

def main():
    if len(sys.argv) != 3:
        print("Usage: python test_rails_upgrade_agent.py <from_version> <to_version>")
        print("Example: python test_rails_upgrade_agent.py v4.2.11 v5.0.0")
        return
    
    from_version = sys.argv[1]
    to_version = sys.argv[2]
    
    test_upgrade_suggestion(from_version, to_version)

if __name__ == "__main__":
    main()
