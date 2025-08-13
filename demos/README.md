# Demos Directory

Interactive demonstrations of the Rails Upgrade Assistant functionality.

## 🎬 Available Demos

```
demos/
├── demo_search.py                    # Basic search functionality demo
├── rails_upgrade_demo.py             # Original upgrade agent demo
├── rails_upgrade_enhanced_demo.py    # Advanced demo with dual-mode search
└── README.md                         # This file
```

## 🚀 Demo Descriptions

### `demo_search.py`
Basic demonstration of the search functionality:
```bash
python demos/demo_search.py
```

**Features:**
- Simple query input interface
- Basic search results display
- Good starting point for understanding the system

**Best for:**
- First-time users exploring the system
- Testing search functionality
- Understanding document retrieval

### `rails_upgrade_demo.py`
Original Rails upgrade agent demonstration:
```bash
python demos/rails_upgrade_demo.py "ApplicationRecord Rails 5"
```

**Features:**
- Command-line query interface
- Basic upgrade suggestions
- Simple result formatting

**Best for:**
- Understanding the original concept
- Quick testing of upgrade queries
- Baseline comparison with enhanced version

### `rails_upgrade_enhanced_demo.py` ⭐
Advanced demonstration with comprehensive search capabilities:
```bash
python demos/rails_upgrade_enhanced_demo.py "Turbo Rails 7 JavaScript"
```

**Features:**
- **Dual-mode search**: Documentation + RailsDiff code changes
- **Categorized results**: Separates docs from code diffs
- **Rich formatting**: Clear, readable output with emojis and sections
- **Comprehensive analysis**: Shows both conceptual and practical changes

**Best for:**
- Showcasing full system capabilities
- Understanding the difference between docs and code changes
- Getting comprehensive upgrade information

## 🎯 Usage Examples

### Quick Search Test
```bash
# Test basic search
python demos/demo_search.py
> Enter query: ApplicationRecord

# Test original agent  
python demos/rails_upgrade_demo.py "Rails 5 ApplicationRecord"

# Test enhanced version
python demos/rails_upgrade_enhanced_demo.py "ApplicationRecord Rails 5"
```

### Comprehensive Rails Upgrade Queries
```bash
# JavaScript/Frontend Changes
python demos/rails_upgrade_enhanced_demo.py "Turbo Rails 7 JavaScript migration"

# Database and Model Changes
python demos/rails_upgrade_enhanced_demo.py "ApplicationRecord Rails 5 models"

# Configuration and Setup
python demos/rails_upgrade_enhanced_demo.py "load_defaults Rails 6 configuration"

# WebSocket and Real-time Features
python demos/rails_upgrade_enhanced_demo.py "ActionCable Rails 6 WebSocket"

# File Upload Changes
python demos/rails_upgrade_enhanced_demo.py "ActiveStorage Rails 6 file uploads"
```

### Version-Specific Queries
```bash
# Rails 4 → 5 Migration
python demos/rails_upgrade_enhanced_demo.py "Rails 4.2.11 to 5.0.0 upgrade ApplicationRecord"

# Rails 6 → 7 Migration  
python demos/rails_upgrade_enhanced_demo.py "Rails 6.1.7 to 7.0.8 JavaScript migration"

# Specific Feature Changes
python demos/rails_upgrade_enhanced_demo.py "JavaScript Migrated from Turbolinks to Turbo Rails"
```

## 📊 Demo Output Comparison

### Basic Demo Output
```
Found 5 results for: ApplicationRecord
1. Rails 5.0 Release Notes - ApplicationRecord introduction...
2. Active Record Changelog - New base class...
```

### Enhanced Demo Output
```
🚀 Enhanced Rails Upgrade Agent Demo
================================================================================
Query: ApplicationRecord Rails 5
--------------------------------------------------------------------------------
🔍 STEP 1: RETRIEVING RELEVANT CONTENT
--------------------------------------------------
Found 8 total results (5 docs, 3 code changes):

📚 DOCUMENTATION RESULTS:
------------------------------
📋 v5.0.0:
   Score: 0.819
   Source: docs\v5.0.0\guides\source\5_0_release_notes.md
   Content: ApplicationRecord is a new base class for all models...

🔄 CODE CHANGE RESULTS:
------------------------------
🔄 4.2.11 → 5.0.0:
   Score: 0.891
   File: app/models/application_record.rb
   Change: Added ApplicationRecord class with self.abstract_class = true
```

## 🎮 Interactive Features

### Demo Flow
1. **Input**: Enter your Rails upgrade query
2. **Search**: System searches documentation and code changes
3. **Display**: Results shown in categorized, formatted output
4. **Analysis**: Integration knowledge extraction (enhanced demo)

### Query Tips for Best Results

**✅ Effective Queries:**
- Include Rails version numbers: "Rails 5", "Rails 6.1 to 7.0"
- Mention specific features: "ApplicationRecord", "Turbo", "ActionCable"
- Use migration keywords: "upgrade", "migration", "changed from X to Y"

**❌ Less Effective Queries:**
- Too generic: "Rails help", "upgrade issues"  
- No version context: "JavaScript changes" (without Rails version)
- Too specific: "app/models/user.rb line 42"

### Understanding Results

**📚 Documentation Results:**
- Official Rails guides and changelogs
- High-level conceptual information  
- Best practices and migration guides
- Version-specific release notes

**🔄 Code Change Results:**
- Actual file-level changes between versions
- Specific code patterns that changed
- Before/after code examples
- File paths and implementation details

## 🔧 Demo Development

### Adding New Demos
When creating new demonstration scripts:

1. **Follow naming convention**: `demo_*.py` or `*_demo.py`
2. **Include documentation**: Clear usage instructions
3. **Add to this README**: Document the new demo
4. **Test thoroughly**: Ensure it works with current data
5. **Handle errors gracefully**: Good user experience

### Demo Template
```python
#!/usr/bin/env python3
"""
Demo Name

Description of what this demo shows and when to use it.

Usage:
    python demos/your_demo.py [query]
"""

import sys
import os
# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("Enter your query: ").strip()
    
    if not query:
        print("Please provide a query")
        return
        
    print(f"🚀 Demo: {query}")
    print("=" * 50)
    
    try:
        # Demo logic here
        print("✅ Demo completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
```

## 🎯 Demo Performance

### Current Stats
- **Search Speed**: ~1-2 seconds for typical queries
- **Result Quality**: High relevance for specific Rails queries
- **Coverage**: Rails 4.2 → 7.0 documentation + 3 major version diffs

### Benchmarking
```bash
# Time search performance
time python demos/rails_upgrade_enhanced_demo.py "ApplicationRecord"

# Memory usage
python -m memory_profiler demos/rails_upgrade_enhanced_demo.py "Rails 5"
```

## 🚨 Troubleshooting Demos

### Common Issues

**Import Errors:**
```bash
# Ensure src/ is accessible
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**No Search Results:**
- Check if FAISS index files exist in `data/`
- Verify embeddings are properly loaded
- Try different query terms

**API Errors (for AI-powered demos):**
- Set `GEMINI_API_KEY` environment variable
- Check API key permissions and quotas

**Memory Issues:**
- Large embeddings may require 4GB+ RAM
- Close other applications if needed

### Debug Commands
```bash
# Check search functionality
python tests/test_retriever.py

# Validate data files
ls -la data/*.index data/*.jsonl

# Test basic imports
python -c "import sys; sys.path.append('src'); from retriever.retriever import Retriever; print('✅ OK')"
```

---

**Ready to explore?** Start with the enhanced demo: `python demos/rails_upgrade_enhanced_demo.py "ApplicationRecord Rails 5"` 🚀
