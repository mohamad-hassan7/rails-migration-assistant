# 🚄 Rails Migration Assistant

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, AI-powered tool for upgrading Ruby on Rails applications. Features real-time analysis, intelligent code suggestions, and a beautiful React-based interface.

> **⚠️ Project Status**: This project is currently in a developmental state and is not production-ready. While it may not be the most polished tool available, it could still provide value to developers who can benefit from its current capabilities. The project serves as a proof-of-concept and learning resource for AI-powered Rails analysis.

## ✨ Key Features

- 🤖 **AI-Powered Analysis** - Local LLM with deep Rails knowledge (DeepSeek Coder 6.7B)
- ⚡ **Fast Pattern Detection** - Instant recognition of common Rails deprecations
- 🔒 **100% Private** - Your code never leaves your machine
- 📊 **Real-time Progress** - Live progress updates during analysis
- 🎯 **Version Targeting** - Support for Rails 4.0 → 7.1 upgrades
- 💾 **Safe Backups** - Automatic backup before making changes
- 📋 **Detailed Reports** - Professional upgrade documentation

## 🏗️ Architecture

- **Frontend**: React 18 + Electron + Ant Design
- **Backend**: FastAPI + PyTorch + CUDA
- **AI Engine**: DeepSeek Coder 6.7B (4-bit quantized)
- **Knowledge Base**: FAISS vector search with Rails documentation
- **Analysis**: Hybrid approach (AI + Pattern matching)

## 📋 Requirements

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux
- **Memory**: 8GB RAM minimum (16GB recommended)
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional, but recommended)
- **Storage**: 10GB free space

### Software Requirements
- **Python**: 3.11+ 
- **Node.js**: 18+ (for frontend)
- **Conda**: For environment management

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/mohamed7456/rails-migration-assistant.git
cd rails-migration-assistant
```

### 2. Setup Python Environment
```bash
# Create conda environment
conda create -n pytorch_env python=3.11
conda activate pytorch_env

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Launch Application
```bash
# Activate environment
conda activate pytorch_env

# Start full application (backend + frontend)
python launcher.py

# Or start components separately:
python launcher.py --backend   # API server only
python launcher.py --frontend  # Electron app only
```

## 📖 Usage

### Project Mode
1. **Select Rails Project**: Browse to your Rails project directory
2. **Choose Target Version**: Select desired Rails version (6.0, 6.1, 7.0, 7.1)
3. **Configure Backups**: Enable automatic backups (recommended)
4. **Run Analysis**: Click "Analyze Project" for real-time scanning
5. **Review Suggestions**: Navigate through code suggestions with explanations
6. **Manual Application**: Copy suggested changes and apply them manually to your code

> **⚠️ Important**: This tool provides suggestions only and does **not automatically modify your files**. All changes must be manually reviewed and applied. This ensures complete control over your codebase and prevents accidental modifications.

### Query Mode
1. **Ask Questions**: Type Rails-related questions
2. **Get AI Responses**: Receive intelligent answers from the local LLM
3. **Context-Aware**: Responses include relevant Rails documentation

## 📊 Analysis Types

### Tier 1: Pattern Detection
- Fast rule-based detection of common deprecations
- `before_filter` → `before_action`
- `update_attributes` → `update`
- `attr_accessible` removal guidance

### Tier 2: AI Analysis
- Deep code understanding using DeepSeek Coder
- Complex refactoring suggestions
- Best practice recommendations
- Security improvement advice

### Tier 3: Knowledge Base
- FAISS-powered documentation search
- Version-specific guidance
- Historical change analysis

## �️ Safety Features

### Read-Only Analysis
- **No Automatic File Modification**: The tool analyzes code but never automatically modifies your files
- **Suggestion-Based Workflow**: All changes are presented as suggestions requiring manual review
- **Complete User Control**: You decide which suggestions to implement and how

### File Safety
- **Backup Recommendations**: Always create backups before manually applying suggestions
- **Line-by-Line Analysis**: Precise identification of issues with specific line numbers
- **Risk Assessment**: Each suggestion includes confidence levels and risk indicators

### Best Practices
- Review all suggestions carefully before implementing
- Test changes in a development environment first
- Run your Rails test suite after applying changes
- Consider gradual migration rather than bulk changes

## �🔧 Configuration

### Environment Variables
Create `.env` file:
```env
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### GPU vs CPU Performance

⚠️ **Important**: The current model (DeepSeek Coder 6.7B) is computationally intensive and **CPU performance is very slow**. For optimal experience, GPU acceleration is highly recommended.

#### GPU Setup (Recommended)
For users with NVIDIA GPUs (8GB+ VRAM):
```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install additional GPU libraries
pip install bitsandbytes accelerate
```

#### GPU Benefits:
- **10-20x faster** analysis compared to CPU
- **4-bit quantization** for memory efficiency
- **Real-time progress** feels responsive
- **Large projects** complete in reasonable time

#### CPU Limitations:
- **Very slow** analysis (20+ minutes for medium projects)
- **High memory usage** without quantization optimizations
- **Limited scalability** for larger Rails projects
- **Poor user experience** due to long wait times

#### Hardware Recommendations:
- **Ideal**: NVIDIA RTX 3080/4070 or better (8GB+ VRAM)
- **Minimum**: NVIDIA GTX 1660 Super (6GB VRAM)
- **CPU Only**: Not recommended for regular use

#### Cloud GPU Alternatives:
If you don't have local GPU hardware, consider these cloud options:
- **Google Colab Pro** - $10/month with GPU access
- **AWS EC2 GPU instances** - Pay-per-use GPU computing
- **Azure Machine Learning** - GPU-enabled compute instances
- **Paperspace Gradient** - Affordable GPU cloud computing

The tool automatically detects your hardware and configures accordingly, but CPU-only usage should be avoided for production analysis.

## 📁 Project Structure

```
rails-migration-assistant/
├── launcher.py           # Main entry point
├── api_bridge.py         # FastAPI backend server
├── frontend/            # React + Electron frontend
│   ├── src/            # React components
│   ├── main.js         # Electron main process
│   └── package.json    # Frontend dependencies
├── src/                # Core analysis engine
│   ├── analyzer/       # Hybrid analyzer
│   ├── retriever/      # RAG system
│   └── model/         # LLM integration
├── data/              # Knowledge base
│   ├── faiss_combined.index
│   └── meta_combined.jsonl
└── requirements.txt   # Python dependencies
```

## 🛠️ Development

### Backend API
- FastAPI server runs on `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Real-time streaming endpoints for progress updates

### Frontend Development
```bash
cd frontend
npm run dev  # Development server with hot reload
```

## � Troubleshooting

### Common Issues

**GPU Memory Errors**
```bash
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

**Conda Environment Issues**
```bash
conda deactivate
conda activate pytorch_env
python launcher.py --check  # Verify environment
```

**Frontend Connection Issues**
- Ensure backend is running on port 8000
- Check firewall settings
- Verify Node.js installation

**Empty Files After Git Operations**
- Run cleanup to remove empty files: `Get-ChildItem -Recurse -File | Where-Object { $_.Length -eq 0 } | Remove-Item`
- Or use the built-in project scanner to identify issues

### Performance Tips
- Use GPU acceleration for best performance
- Close other GPU-intensive applications
- Use 4-bit quantization for lower memory usage
- Clean up empty files regularly to maintain project hygiene

## 🤝 Contributing

We welcome contributions! Here are some ways to get involved:

### Areas for Improvement
- **Additional Rails Pattern Detection**: Add more deprecation patterns to Tier 1 analyzer
- **Enhanced AI Prompts**: Improve LLM prompts for better code suggestions
- **UI/UX Improvements**: Enhance the React frontend interface
- **Performance Optimizations**: Reduce memory usage and improve analysis speed
- **Testing**: Add comprehensive test coverage
- **Documentation**: Improve inline code documentation

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt` (if available)
4. Make your changes and test thoroughly
5. Submit a pull request with detailed description

### Code Style
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript/React code
- Include type hints where appropriate
- Add docstrings to new functions and classes

## 📞 Support

### Getting Help
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/mohamed7456/rails-migration-assistant/issues)
- **Discussions**: Join conversations on [GitHub Discussions](https://github.com/mohamed7456/rails-migration-assistant/discussions)
- **Documentation**: Check this README and inline code documentation

### Known Limitations
- CPU-only performance is significantly slower than GPU
- Large Rails projects may require substantial processing time
- AI suggestions require manual review and implementation
- Limited to Rails 4.0+ migration paths
- Some complex refactoring patterns may not be detected

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
---
 

*Rails Migration Assistant v2.0 - Modern Edition*
