# Rails Migration Assistant - Quick Start Guide

## 🚀 **INSTANT SETUP** (30 seconds)

### **Windows Users**
```cmd
# Double-click start.bat or run:
start.bat
```

### **macOS/Linux Users**
```bash
./start.sh
```

### **Manual Python Launch**
```bash
python launcher.py              # GUI mode
python launcher.py --cli        # CLI mode
python launcher.py --analyze /path/to/rails/app
```

## 🎯 **COMMON USE CASES**

### **1. Upgrade Rails 5.2 → 7.0**
1. Open Rails Migration Assistant
2. Select your Rails project folder
3. Click "Analyze Project"
4. Review suggested changes
5. Apply fixes systematically

### **2. Security Audit**
- Automatically detects mass assignment vulnerabilities
- Generates strong parameters
- Identifies deprecated authentication patterns

### **3. Batch Processing**
```bash
python launcher.py --analyze ./app
python launcher.py --analyze ./config
python launcher.py --analyze ./lib
```

## ⚡ **PERFORMANCE TIPS**

- **RAM**: Close other applications (needs 4-8GB)
- **Storage**: SSD recommended for faster model loading
- **Processing**: Analyze large projects in sections
- **GPU**: CUDA acceleration automatically detected

## 🛠️ **TROUBLESHOOTING**

### **Common Issues**
```bash
# Environment check
python launcher.py --check

# Clear model cache
rm -rf ~/.cache/huggingface/

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### **Memory Issues**
- Close browser/other apps
- Restart computer
- Use CLI mode instead of GUI

### **Model Loading Fails**
- Check internet connection (first download only)
- Verify 10GB+ free disk space
- Try: `python -c "import torch; print(torch.cuda.is_available())"`

## 📞 **SUPPORT**

- **Documentation**: See README.md
- **Issues**: GitHub Issues tab
- **CLI Help**: `python launcher.py --help`
