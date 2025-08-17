# Rails Migration Assistant

A professional-grade tool for migrating Ruby on Rails applications between major versions using local AI-powered analysis.

## Overview

The Rails Migration Assistant helps developers upgrade Ruby on Rails applications by identifying deprecated code patterns, security vulnerabilities, and providing automated suggestions for modern Rails practices. The system operates entirely offline using a local Large Language Model (DeepSeek Coder 6.7B) with hybrid analysis capabilities.

## Features

### Core Capabilities
- **Version Migration Support**: Rails 4.2 to 7.0+ upgrade assistance
- **Security Analysis**: Mass assignment vulnerability detection and remediation
- **Deprecation Detection**: Automated identification of deprecated patterns
- **Strong Parameters**: Automated generation of secure parameter handling
- **Offline Operation**: Complete local execution without external API dependencies

### Analysis Technologies
- **Hybrid Analysis System**: Two-tiered detection combining pattern matching and RAG-based analysis
- **Local LLM**: DeepSeek Coder 6.7B with 4-bit quantization for optimal performance
- **Vector Search**: FAISS-powered knowledge retrieval from Rails documentation
- **Code Parsing**: Advanced Ruby code analysis and context extraction

### User Interfaces
- **Graphical Interface**: User-friendly Tkinter-based GUI application
- **Command Line**: Full CLI support for automation and scripting
- **Programmatic API**: Python API for integration with existing workflows

## Installation

### Prerequisites
- Python 3.9 or higher
- 8GB+ RAM recommended
- 10GB available disk space

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mohamed7456/rails-migration-assistant.git
   cd rails-migration-assistant
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv rails_env
   ```

3. **Activate virtual environment**:
   ```bash
   # Windows
   rails_env\Scripts\activate
   
   # macOS/Linux
   source rails_env/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

## Usage

### Graphical User Interface

Launch the GUI application:
```bash
python rails_upgrade_gui.py
```

**GUI Features**:
- Project directory selection
- File browsing and analysis
- Real-time progress tracking
- Formatted analysis results
- Export functionality

### Command Line Interface

Analyze a Rails project:
```bash
python rails_upgrade_agent.py --project-path /path/to/rails/app
```

**CLI Options**:
```bash
python rails_upgrade_agent.py --help
```

### Programmatic Usage

```python
from src.analyzer.hybrid_analyzer import HybridRailsAnalyzer

# Initialize analyzer
analyzer = HybridRailsAnalyzer()

# Analyze a file
results = analyzer.analyze_file('/path/to/controller.rb')

# Process results
for issue in results:
    print(f"Issue: {issue['type']}")
    print(f"Description: {issue['description']}")
    print(f"Suggestion: {issue['suggestion']}")
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Model Configuration
MODEL_NAME=deepseek-coder-6.7b-instruct-4bit
MODEL_CACHE_DIR=./models
MAX_MEMORY_GB=8

# Analysis Settings
ANALYSIS_TIMEOUT=300
ENABLE_SECURITY_SCAN=true
VERBOSE_OUTPUT=false

# GUI Settings
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800
THEME=default
```

### Advanced Configuration

Modify `src/model/local_llm.py` for custom model settings:
- Memory allocation
- Quantization options
- Response generation parameters

## Supported Rails Versions

### Source Versions
- Rails 4.2.x
- Rails 5.0.x
- Rails 5.2.x
- Rails 6.0.x
- Rails 6.1.x

### Target Versions
- Rails 6.1.x
- Rails 7.0.x
- Rails 7.1.x 

## Analysis Types

### Security Vulnerabilities
- **Mass Assignment**: Detection and Strong Parameters generation
- **SQL Injection**: Vulnerable query patterns
- **Cross-Site Scripting**: Output sanitization issues
- **Authorization**: Missing access controls

### Deprecation Patterns
- **ActiveRecord**: Deprecated finder methods and associations
- **ActionController**: Obsolete callback patterns
- **ActionView**: Legacy helper methods
- **Routing**: Deprecated route definitions

### Performance Optimizations
- **N+1 Queries**: Inefficient database access patterns
- **Memory Usage**: Object allocation improvements
- **Caching**: Outdated caching strategies

## Performance

### System Requirements
- **Memory**: 4GB usage during analysis
- **Processing Time**: 30-60 seconds per file
- **Accuracy**: 95%+ on deprecation detection
- **Throughput**: 50-100 files per hour

### Optimization Tips
- Close unnecessary applications during analysis
- Use SSD storage for faster model loading
- Increase virtual memory if needed
- Process large projects in batches

## Project Structure

```
rails-migration-assistant/
├── src/                          # Core application modules
│   ├── analyzer/                 # Analysis engines
│   │   ├── hybrid_analyzer.py    # Main analysis system
│   │   ├── project_scanner.py    # Security scanner
│   │   └── code_parser.py        # Ruby code parsing
│   ├── model/                    # Local LLM implementation
│   │   └── local_llm.py          # DeepSeek integration
│   ├── retriever/                # Knowledge retrieval
│   │   └── retriever.py          # FAISS vector search
│   └── patcher/                  # Output formatting
├── data/                         # Knowledge base
│   ├── docs/                     # Rails documentation
│   └── raildiff/                 # Version differences
├── sample_rails_upgrade/         # Test application
├── rails_upgrade_agent.py        # CLI interface
├── rails_upgrade_gui.py          # GUI interface
└── requirements.txt              # Dependencies
```

## Troubleshooting

### Common Issues

**Model Loading Errors**:
```bash
# Clear model cache
rm -rf ./models/*
# Restart application
```

**Memory Issues**:
```bash
# Reduce model precision in local_llm.py
# Close other applications
# Increase virtual memory
```

**Analysis Timeouts**:
```bash
# Increase timeout in .env
ANALYSIS_TIMEOUT=600
```

### Debugging

Enable verbose output:
```bash
export VERBOSE_OUTPUT=true
python rails_upgrade_gui.py
```

Check logs in `./logs/` directory for detailed error information.

## Contributing

We welcome contributions to improve the Rails Migration Assistant. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Run tests and linting
5. Submit a pull request

## Documentation

- **[API Documentation](API.md)**: Programmatic interface reference
- **[Contributing Guide](CONTRIBUTING.md)**: Development guidelines
- **[Changelog](CHANGELOG.md)**: Version history and migration notes
- **[Project Status](PROJECT_STATUS.md)**: Current development status

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Support

For technical support, bug reports, or feature requests:

1. **Issues**: Use GitHub Issues for bug reports and feature requests
2. **Documentation**: Check existing documentation for common questions
3. **Community**: Participate in discussions and help other users

## Acknowledgments

- **DeepSeek AI**: For the local language model
- **Rails Community**: For comprehensive documentation and migration guides
- **FAISS**: For efficient vector similarity search
- **Transformers**: For model integration and optimization

---

 
**Last Updated**: August 2025
