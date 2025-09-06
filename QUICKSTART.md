# ⚡ Quick Start Guide

Get the Rails Migration Assistant up and running in under 5 minutes!

## 🚀 One-Minute Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- 8GB+ RAM
- **NVIDIA GPU strongly recommended** (CPU is very slow with current model)

### Installation
```bash
# 1. Clone repository
git clone https://github.com/mohamed7456/rails-migration-assistant.git
cd rails-migration-assistant

# 2. Setup Python environment  
conda create -n pytorch_env python=3.11 -y
conda activate pytorch_env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup frontend
cd frontend && npm install && cd ..

# 5. Launch application
python launcher.py
```

## 🎯 First Analysis

### GUI Mode (Recommended)
1. **Start the app**: `python launcher.py`
2. **Select project**: Click "Browse" and select your Rails project folder
3. **Choose target**: Select Rails version (6.0, 6.1, 7.0, 7.1)
4. **Analyze**: Click "Analyze Project" and watch real-time progress
5. **Review**: Browse through suggestions and apply fixes

### Command Line Mode
```bash
python launcher.py --analyze /path/to/your/rails/project
```

## 🔧 Test with Sample Project

```bash
# Analyze the included sample Rails app
python launcher.py --analyze sample_rails_upgrade/
```

This sample contains common legacy patterns perfect for testing.

## 🐛 Common Issues

**Environment not found?**
```bash
conda activate pytorch_env
```

**Port 8000 in use?**
```bash
# Check what's using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                # Mac/Linux
```

**Need GPU acceleration?**
```bash
# Install CUDA support (for NVIDIA GPUs 8GB+)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install bitsandbytes accelerate
```

**CPU too slow?**
```bash
# CPU analysis is 10-20x slower than GPU
# Consider using a cloud GPU service like:
# - Google Colab Pro
# - AWS EC2 with GPU
# - Azure ML with GPU instances
```

## 📊 What to Expect

**First Run:**
- Model download: ~2-5 minutes
- Knowledge base loading: ~30 seconds
- Frontend startup: ~10 seconds

**Analysis Speed (with GPU):**
- Small projects (< 100 files): 1-2 minutes
- Medium projects (100-500 files): 3-5 minutes  
- Large projects (500+ files): 5-15 minutes

**Analysis Speed (CPU only - NOT recommended):**
- Small projects: 10-30 minutes
- Medium projects: 1-2 hours
- Large projects: 3-8 hours

⚠️ **CPU Warning**: Analysis is extremely slow without GPU acceleration. Consider GPU cloud services if you don't have local GPU hardware.

## 🎉 Success!

You should see:
- ✅ Backend API at `http://localhost:8000`
- ✅ Modern React interface opens automatically
- ✅ Real-time progress during analysis
- ✅ Intelligent Rails upgrade suggestions

## � Next Steps

- Read the full [README.md](README.md) for detailed features
- Explore different Rails versions and migration paths
- Try the Query mode for Rails-specific questions

---

*Get upgrading in minutes! 🚀*
