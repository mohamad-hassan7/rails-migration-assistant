# Rails Migration Assistant

A professional AI-powered tool for upgrading Ruby on Rails applications between major versions. Uses local LLM analysis to identify deprecated patterns, security vulnerabilities, and provide automated upgrade suggestions.

## 🚀 Features

- **Multi-version Rails Support**: Upgrade from Rails 4.0+ to Rails 7.1+
- **Local AI Analysis**: DeepSeek Coder 6.7B with GPU acceleration
- **Security Detection**: Mass assignment vulnerabilities and automated strong parameters
- **Pattern Recognition**: Advanced deprecation detection and modern Rails patterns
- **Hybrid Analysis**: Combines rule-based patterns with AI-powered code understanding
- **User-Friendly GUI**: Professional Tkinter interface with real-time progress
- **Offline Operation**: Complete local execution without external API dependencies

## 📋 Requirements

- **Python**: 3.8+ (3.11 recommended)
- **Memory**: 8GB+ RAM 
- **Storage**: 10GB+ free space
- **GPU**: NVIDIA GPU with 8GB+ VRAM 
- **OS**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+

## ⚡ Quick Start

### One-Command Launch

```bash
python launcher.py              # Launch GUI
python launcher.py --analyze /path/to/rails/project  # Direct analysis
```

The launcher automatically:
- Checks environment compatibility
- Installs missing dependencies
- Configures GPU acceleration if available
- Launches the appropriate interface

### Manual Setup (if needed)

1. **Clone Repository**
   ```bash
   git clone https://github.com/mohamed7456/rails-migration-assistant.git
   cd rails-migration-assistant
   ```

2. **Create Environment** (Conda recommended for GPU)
   ```bash
   conda create -n pytorch_env python=3.11
   conda activate pytorch_env
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage Examples

### GUI Interface
```bash
python launcher.py
```
- Select Rails project folder
- Click "Analyze Project"
- Review suggestions and apply fixes

### Command Line
```bash
python launcher.py --analyze /path/to/rails/project
```

### Programmatic API
```python
from src.analyzer.hybrid_analyzer import HybridRailsAnalyzer

analyzer = HybridRailsAnalyzer()
results = analyzer.analyze_project('/path/to/rails/project')

for suggestion in results['suggestions']:
    print(f"File: {suggestion['file_path']}")
    print(f"Issue: {suggestion['issue_type']}")
    print(f"Fix: {suggestion['refactored_code']}")
```

## 🔧 Configuration

### GPU Acceleration (Recommended)
If you have an NVIDIA GPU with 8GB+ VRAM:
```bash
# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install bitsandbytes accelerate
```

### Environment Variables
Create `.env` file:
```env
# GPU Settings
CUDA_VISIBLE_DEVICES=0
MODEL_DEVICE=cuda

# Performance
MAX_ANALYSIS_TIME=300
BATCH_SIZE=4
QUANTIZATION=4bit
```

## 📊 Supported Rails Migrations

| From Version | To Version | Status | Key Features |
|-------------|------------|--------|--------------|
| Rails 4.0.x | Rails 4.1+ | ✅ Full | Secrets management, session config |
| Rails 4.1.x | Rails 4.2+ | ✅ Full | Transactional callbacks, CSRF |
| Rails 4.2.x | Rails 5.0+ | ✅ Full | Strong parameters, API mode |
| Rails 5.0.x | Rails 5.1+ | ✅ Full | Encrypted credentials, capybara |
| Rails 5.1.x | Rails 5.2+ | ✅ Full | Bootsnap, credentials encryption |
| Rails 5.2.x | Rails 6.0+ | ✅ Full | Zeitwerk, multiple databases |
| Rails 6.0.x | Rails 6.1+ | ✅ Full | Redis support, Webpacker improvements |
| Rails 6.1.x | Rails 7.0+ | ✅ Full | Turbo-Rails, importmap |
| Rails 7.0.x | Rails 7.1+ | ✅ Full | Latest features and optimizations |

## 🔍 Analysis Capabilities

### Security Analysis
- **Mass Assignment**: Automatic strong parameters generation
- **SQL Injection**: Vulnerable query pattern detection
- **XSS Prevention**: Output sanitization recommendations
- **CSRF Protection**: Token verification improvements

### Deprecation Detection
- **ActiveRecord**: Finder methods, associations, callbacks
- **ActionController**: Filter chains, parameter handling
- **ActionView**: Helper methods, rendering patterns
- **Routing**: RESTful routes, namespace changes

### Code Modernization
- **Ruby Syntax**: Modern Ruby idioms and patterns
- **Rails Conventions**: Current best practices
- **Performance**: Optimization recommendations
- **Testing**: Modern testing patterns

## 📁 Project Structure

```
rails-migration-assistant/
├── launcher.py                 # Main entry point
├── src/
│   ├── analyzer/              # Analysis engines
│   ├── model/                 # LLM integration
│   ├── retriever/             # Knowledge base
│   └── patcher/               # Code transformation
├── data/
│   ├── docs/                  # Rails documentation (v4.0-v7.1)
│   └── raildiff/              # Version diff data
├── sample_rails_upgrade/      # Test Rails application
└── requirements.txt           # Dependencies
```

## 🧪 Testing

Test with the included sample Rails application:
```bash
python launcher.py --analyze sample_rails_upgrade/
```

The sample app contains common legacy patterns:
- Mass assignment vulnerabilities
- Deprecated ActiveRecord methods
- Legacy routing syntax
- Outdated gem dependencies

## 🔧 Troubleshooting

### Common Issues

**GPU Not Detected:**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

**Memory Issues:**
```bash
# Use CPU-only mode
export MODEL_DEVICE=cpu
python launcher.py
```

**Model Download Fails:**
```bash
# Clear cache and retry
rm -rf ~/.cache/huggingface/
python launcher.py
```

### Performance Tips

**For GPU Systems:**
- Ensure 8GB+ GPU memory available
- Close other GPU applications
- Use 4-bit quantization (default)

**For CPU Systems:**
- Close unnecessary applications
- Increase virtual memory
- Process large projects in sections

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/mohamed7456/rails-migration-assistant.git
cd rails-migration-assistant
pip install -e .
python -m pytest tests/
```

## 📚 Documentation

- **[API Reference](API.md)** - Programmatic interface
- **[Quick Start](QUICKSTART.md)** - 30-second setup guide
- **[Contributing](CONTRIBUTING.md)** - Development guidelines

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **DeepSeek AI** - Local language model
- **Rails Core Team** - Comprehensive upgrade documentation
- **Hugging Face** - Model hosting and transformers library
- **FAISS** - Vector similarity search

---
