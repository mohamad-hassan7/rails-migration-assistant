#!/usr/bin/env python3
"""
Rails Migration Assistant - GitHub Preparation Script
This script prepares the project for GitHub publication.
"""

import os
import shutil
import subprocess
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def initialize_git_repo():
    """Initialize git repository and make initial commit."""
    print("\n📦 Initializing Git Repository...")
    
    commands = [
        ("git init", "Initialize git repository"),
        ("git add .", "Stage all files"),
        ('git commit -m "Initial commit: Rails Migration Assistant v1.0.0"', "Initial commit"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def create_release_info():
    """Create release information."""
    print("\n📋 Creating release information...")
    
    release_info = {
        "name": "Rails Migration Assistant",
        "version": "1.0.0",
        "description": "AI-powered Rails upgrade assistance with dual LLM support",
        "features": [
            "🤖 Dual AI Backend Support (Gemini API + Local LLM)",
            "📚 Smart Documentation System (85K+ optimized chunks)",
            "🔄 RailsDiff Integration",
            "🖥️ Multiple Interfaces (GUI, CLI, API)",
            "🔒 Secure Offline Processing",
            "📊 Comprehensive Testing Suite"
        ],
        "requirements": {
            "python": ">=3.8",
            "ram": "8GB+ (16GB+ recommended for local LLM)",
            "gpu": "CUDA-compatible (recommended for local LLM)",
            "storage": "10GB+ for documentation and models"
        },
        "installation": [
            "git clone https://github.com/your-username/rails-migration-assistant.git",
            "cd rails-migration-assistant",
            "python -m venv .venv",
            "source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate",
            "pip install -r requirements.txt"
        ],
        "usage": {
            "cli": "python rails_upgrade_suggestions.py 'upgrade ActiveRecord'",
            "cli_local": "python rails_upgrade_suggestions.py 'upgrade ActiveRecord' --local",
            "gui": "python rails_upgrade_gui.py"
        }
    }
    
    with open("RELEASE_INFO.json", "w", encoding='utf-8') as f:
        json.dump(release_info, f, indent=2)
    
    print("✅ Release information created")

def create_github_readme():
    """Create GitHub-specific README additions."""
    github_additions = """

## 🌟 Quick Demo

```bash
# Install dependencies
pip install -r requirements.txt

# Try with Gemini API (fast)
python rails_upgrade_suggestions.py "Rails 7 security updates"

# Try with Local LLM (secure)
python rails_upgrade_suggestions.py "update controllers" --local

# Launch GUI
python rails_upgrade_gui.py
```

## 📺 Screenshots

### Command Line Interface
```
🚀 Rails Migration Assistant - CLI Mode
🔍 Searching for: upgrade ActiveRecord validations
✅ Found 10 relevant results
🤖 Generating upgrade suggestions...
✅ Generated 1 suggestions using Gemini API

================================================================================
GENERATED UPGRADE SUGGESTIONS
================================================================================

📝 SUGGESTION 1
----------------------------------------
📁 File: app/models/user.rb
🏷️  Type: deprecation
🎯 Rails Version: 7.0
💪 Confidence: high
...
```

### Graphical User Interface
*GUI screenshot would go here*

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/your-username/rails-migration-assistant.git
cd rails-migration-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Rails Team for comprehensive documentation
- HuggingFace for transformer models
- DeepSeek for the excellent Coder model
- Google for Gemini API access

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/rails-migration-assistant&type=Date)](https://star-history.com/#your-username/rails-migration-assistant&Date)

---

**Made with ❤️ for the Rails community**
"""
    
    # Append to existing README
    with open("README.md", "a", encoding='utf-8') as f:
        f.write(github_additions)
    
    print("✅ GitHub README additions created")

def main():
    """Main preparation function."""
    print("🚀 Rails Migration Assistant - GitHub Preparation")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists("rails_upgrade_suggestions.py"):
        print("❌ Please run this script from the project root directory")
        return
    
    # Create additional files
    create_release_info()
    create_github_readme()
    
    # Initialize git repository
    if not os.path.exists(".git"):
        initialize_git_repo()
    else:
        print("📦 Git repository already initialized")
    
    print("\n🎉 GitHub Preparation Complete!")
    print("\n📋 Next Steps:")
    print("1. Update the GitHub repository URL in setup.py and pyproject.toml")
    print("2. Update your email in setup.py and pyproject.toml") 
    print("3. Set up GEMINI_API_KEY secret in GitHub repository settings")
    print("4. Create repository on GitHub and push:")
    print("   git remote add origin https://github.com/your-username/rails-migration-assistant.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print("5. Add topics/tags: rails, ai, llm, migration, python, ruby, upgrade")
    print("\n✨ Your Rails Migration Assistant is ready for the world! ✨")

if __name__ == "__main__":
    main()
