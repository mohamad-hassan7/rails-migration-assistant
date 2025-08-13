# 🚀 Rails Migration Assistant

A comprehensive AI-powered Rails upgrade assistance system with dual LLM support for secure, professional Rails application modernization.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

> **Transform your Rails applications** from legacy versions to modern Rails 7.0+ with AI-powered guidance, smart documentation analysis, and secure offline processing.

## 🌟 Features

### 🤖 Dual AI Backend Support
- **Gemini API**: Fast, cloud-based processing for development environments
- **Local LLM**: Secure, offline processing using DeepSeek Coder 6.7B for enterprise/production environments

### � Intelligent Documentation System
- **85,126 optimized documentation chunks** from Rails 4.2 → 7.0
- **Smart deduplication** reducing storage by 68% while maintaining accuracy
- **Semantic search** with FAISS indexing for rapid context retrieval

### 🔄 RailsDiff Integration
- **Code change analysis** from official Rails upgrade diffs
- **Semantic understanding** of breaking changes and migration patterns
- **Version-specific suggestions** covering Rails 4.2 → 5.0 → 6.0 → 7.0

### 🖥️ Multiple Interfaces
- **GUI Application**: Interactive Tkinter interface with model switching
- **CLI Tool**: Command-line batch processing for automation
- **Python API**: Programmatic access for integration

### 🔒 Security & Privacy
- **Local processing option** for sensitive codebases
- **No API calls required** in local mode
- **4-bit quantization** for efficient memory usage
- **CUDA acceleration** for faster inference

## � Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended for local LLM)
- 8GB+ RAM (16GB+ recommended for local LLM)

### Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up Gemini API (optional, for API mode)
export GEMINI_API_KEY=your_api_key_here
```

## � Quick Start

### Command Line Interface

```bash
# Basic usage with Gemini API
python rails_upgrade_suggestions.py "upgrade ActiveRecord validations"

# Use local LLM for secure processing
python rails_upgrade_suggestions.py "update routing for Rails 7" --local

# Limit search results for faster processing
python rails_upgrade_suggestions.py "Rails 7 ActionCable changes" --max-results 5

# Save suggestions to file
python rails_upgrade_suggestions.py "update Gemfile" --output suggestions.json
```

### Graphical User Interface

```bash
# Launch GUI application
python rails_upgrade_gui.py
```

**GUI Features:**
- 🔄 **Model Selection**: Switch between Gemini API and Local LLM
- 📝 **Interactive Queries**: Real-time suggestion generation
- 🎯 **Code Review**: Side-by-side old/new code comparison
- 💾 **Export Options**: Save suggestions as JSON or patches
- 🔍 **Context Viewer**: See documentation sources used

### Python API

```python
from rails_upgrade_suggestions import RailsUpgradeSuggestionGenerator

# Initialize with Gemini API (default)
generator = RailsUpgradeSuggestionGenerator()
suggestions = generator.generate_suggestions("Rails 7 deprecations")

# Initialize with Local LLM for secure processing
local_generator = RailsUpgradeSuggestionGenerator(use_local_llm=True)
secure_suggestions = local_generator.generate_suggestions("update controllers")

# Display results
generator.display_suggestions(suggestions)
```

## 📊 System Architecture

```
Rails Upgrade Agent
├── 🎯 User Interfaces
│   ├── CLI Tool (rails_upgrade_suggestions.py)
│   ├── GUI App (rails_upgrade_gui.py)
│   └── Python API
├── 🧠 AI Backends
│   ├── Gemini API (Cloud)
│   └── Local LLM (DeepSeek Coder 6.7B)
├── 📚 Knowledge Base
│   ├── Rails Documentation (85K chunks)
│   ├── RailsDiff Code Changes (12 chunks)
│   └── FAISS Vector Index
├── � Retrieval System
│   ├── Semantic Search
│   ├── Context Ranking
│   └── Result Filtering
└── � Output Generation
    ├── Structured Suggestions
    ├── Code Examples
    └── Export Formats
```

## 📈 Performance

### Benchmark Results
| Mode | Model Loading | Query Processing | Memory Usage | Accuracy |
|------|--------------|------------------|--------------|-----------|
| Gemini API | Instant | ~2-5 seconds | <1GB | High |
| Local LLM | ~15 seconds | ~5-10 seconds | ~4GB | Very High |

### System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8GB | 16GB+ |
| Storage | 10GB | 20GB+ |
| GPU | Optional | CUDA-compatible |
| CPU | 4 cores | 8+ cores |

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_complete_system.py
```

**Test Coverage:**
- ✅ CLI with Gemini API
- ✅ CLI with Local LLM  
- ✅ GUI Initialization
- ✅ Documentation Retriever
- ✅ Agent Runner
- ✅ End-to-end workflows
    ├── rails_upgrade_agent.py     # CLI agent
    ├── rails_upgrade_gui.py       # GUI application
    └── rails_upgrade_suggestions.py # Batch processor
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to project
cd rails_upgrade_assistant

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API key
GEMINI_API_KEY=your_api_key_here
```

### 3. Choose Your Interface

**🖥️ GUI Application (Recommended)**
```bash
python rails_upgrade_gui.py
```

**⌨️ Command Line**
```bash
python rails_upgrade_suggestions.py "ApplicationRecord Rails 5"
```

**🔍 Quick Search Demo**
```bash
python demos/rails_upgrade_enhanced_demo.py "Turbo Rails 7"
```

## 🎯 Usage Examples

### GUI Workflow
1. **Launch**: `python rails_upgrade_gui.py`
2. **Search**: Enter query like "ApplicationRecord Rails 5"
3. **Review**: Compare old vs new code side-by-side
4. **Decide**: Accept ✅, Reject ❌, or Skip ⏭️ suggestions
5. **Export**: Generate reports for team review

### Command Line Batch Processing
```bash
# Generate suggestions for multiple topics
python rails_upgrade_suggestions.py "ApplicationRecord Rails 5" -o app_record.json
python rails_upgrade_suggestions.py "Turbo Rails 7" -o turbo.json
python rails_upgrade_suggestions.py "ActionCable" -o cable.json
```

### Search Queries That Work Well
- `"ApplicationRecord Rails 5.0 upgrade"`
- `"Turbo Rails 7 JavaScript migration"`
- `"ActionCable WebSocket Rails 6"`
- `"ActiveStorage file uploads"`
- `"load_defaults configuration Rails 6"`

## 🧪 Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_retriever.py
```

### Data Management
```bash
# Rebuild search index
python src/retriever/build_index.py --chunks data/chunks_combined.jsonl

# Analyze documentation
python tools/analyze_guides.py

# Deduplicate data
python tools/deduplicate_docs.py --dry-run
```

### Adding New Data Sources
```bash
# Fetch Rails documentation
python src/ingest/smart_docs_fetcher.py

# Fetch RailsDiff data
python src/ingest/raildiff_fetcher.py

# Process into searchable chunks
python src/ingest/raildiff_ingest.py
```

## 📊 Project Stats

- **📚 Knowledge Base**: 85,138 searchable chunks
- **📖 Documentation**: 6 Rails versions (4.2→7.0)
- **🔄 Code Diffs**: 3 major version transitions
- **🤖 AI Model**: Gemini 1.5 Flash
- **🎯 Search Engine**: FAISS vector similarity

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit** pull request

### Code Structure
- **src/**: Core library - keep it modular
- **tests/**: Comprehensive test coverage
- **docs/**: User and developer documentation
- **tools/**: Utility scripts for maintenance

### Adding New Features
- Follow existing patterns in `src/` modules
- Add tests in `tests/` directory
- Update relevant documentation
- Consider both CLI and GUI interfaces

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Rails Community** for comprehensive documentation
- **RailsDiff** for version comparison data
- **Google** for Gemini AI API
- **FAISS** for fast similarity search

## 📞 Support

- **Documentation**: Check `docs/` directory
- **Examples**: See `examples/` and `demos/`
- **Issues**: Create GitHub issue with details
- **Testing**: Use `tools/` scripts for debugging

---

**Ready to upgrade your Rails app?** Start with the GUI: `python rails_upgrade_gui.py` 🚀


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

