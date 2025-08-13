# Tools Directory

Utility scripts for maintaining and analyzing the Rails Upgrade Assistant project.

## 🛠️ Available Tools

```
tools/
├── analyze_guides.py          # Analyze Rails documentation structure
├── debug_raildiff.py         # Debug RailsDiff data and search
├── deduplicate_docs.py       # Remove duplicate documentation
├── project_summary.py        # Generate project statistics
└── README.md                 # This file
```

## 📊 Tool Descriptions

### `analyze_guides.py`
Analyzes the Rails documentation structure and content:
```bash
python tools/analyze_guides.py
```

**What it does:**
- Scans all Rails guide files across versions
- Identifies file sizes, content changes, and duplicates  
- Generates statistics on documentation coverage
- Helps identify what content to include/exclude

**Output:**
- File-by-file analysis with sizes and versions
- Summary statistics (total files, unique content, duplicates)
- Recommendations for data optimization

### `deduplicate_docs.py`
Removes duplicate documentation to optimize the knowledge base:
```bash
# Dry run (preview changes)
python tools/deduplicate_docs.py --dry-run

# Actually remove duplicates  
python tools/deduplicate_docs.py
```

**What it does:**
- Identifies exact duplicate files across Rails versions
- Preserves files that evolve between versions
- Removes redundant changelogs and release notes
- Optimizes storage and search performance

**Options:**
- `--dry-run`: Preview changes without modifying files
- `--verbose`: Show detailed progress information
- `--backup`: Create backup before making changes

### `debug_raildiff.py`
Debug and analyze RailsDiff data integration:
```bash
python tools/debug_raildiff.py
```

**What it does:**
- Tests RailsDiff data loading and parsing
- Validates semantic chunk generation
- Checks search index integration
- Identifies missing or corrupted data

**Use cases:**
- Troubleshoot RailsDiff search issues
- Validate new RailsDiff data sources
- Test chunk generation improvements

### `project_summary.py`
Generates comprehensive project statistics:
```bash
python tools/project_summary.py
```

**What it does:**
- Counts lines of code by file type
- Analyzes documentation coverage
- Reports knowledge base statistics
- Summarizes feature completeness

**Output includes:**
- Code statistics (Python files, tests, docs)
- Data statistics (chunks, indexes, versions)
- Feature matrix (completed, in-progress, planned)

## 🚀 Usage Examples

### Documentation Maintenance
```bash
# 1. Analyze current documentation
python tools/analyze_guides.py > docs/analysis_report.txt

# 2. Remove duplicates (preview first)
python tools/deduplicate_docs.py --dry-run

# 3. Actually deduplicate
python tools/deduplicate_docs.py

# 4. Rebuild search index
python src/retriever/build_index.py --chunks data/chunks_combined.jsonl
```

### Debugging Search Issues
```bash
# 1. Check RailsDiff integration
python tools/debug_raildiff.py

# 2. Test specific queries
python tests/test_retriever.py

# 3. Analyze search results
python demos/rails_upgrade_enhanced_demo.py "your query"
```

### Project Health Check
```bash
# Generate comprehensive project report
python tools/project_summary.py > PROJECT_STATUS.md
```

## 🔧 Development Tools

### Adding New Tools
When creating new utility scripts:

1. **Follow naming convention**: `verb_noun.py` (e.g., `validate_embeddings.py`)
2. **Add to this directory**: Place in `tools/`
3. **Include help text**: Use argparse with clear descriptions
4. **Update README**: Document the new tool here
5. **Add error handling**: Graceful failure with helpful messages

### Tool Template
```python
#!/usr/bin/env python3
"""
Tool Description

What this tool does and when to use it.

Usage:
    python tools/your_tool.py [options]
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Tool description')
    parser.add_argument('--option', help='Option description')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without executing')
    
    args = parser.parse_args()
    
    try:
        # Tool logic here
        print("✅ Tool completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 📋 Maintenance Schedule

### Weekly
- **Run deduplication**: Keep knowledge base optimized
- **Check project status**: Monitor overall health

### Monthly  
- **Analyze guides**: Check for new Rails documentation
- **Debug RailsDiff**: Ensure search integration works
- **Update statistics**: Refresh project metrics

### Before Releases
- **Full analysis**: Run all tools to ensure data quality
- **Performance check**: Validate search speed and accuracy
- **Documentation sync**: Update all README files

## 🚨 Common Issues

### Import Errors
If tools can't import from `src/`:
```bash
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or modify tool to include:
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
```

### Missing Dependencies
Some tools require additional packages:
```bash
# Install analysis dependencies
pip install matplotlib seaborn  # For advanced analytics
pip install beautifulsoup4       # For web scraping tools
```

### Permission Issues
On Windows, some file operations may need admin rights:
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🤝 Contributing Tools

### Guidelines
1. **Single Responsibility**: Each tool should do one thing well
2. **Clear Documentation**: Include purpose, usage, and examples
3. **Error Handling**: Graceful failure with helpful messages
4. **Dry Run Option**: Let users preview destructive changes
5. **Progress Feedback**: Show what the tool is doing

### Useful Tool Ideas
- **validate_embeddings.py**: Check embedding quality and consistency
- **benchmark_search.py**: Performance testing for search functionality
- **export_knowledge.py**: Export knowledge base in different formats
- **migrate_data.py**: Handle data format migrations
- **health_check.py**: Comprehensive system health validation

---

**Need a new tool?** Check existing tools for patterns and add your utility following the established conventions.
