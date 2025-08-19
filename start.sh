#!/bin/bash
# Rails Migration Assistant - Unix/Linux/macOS Startup Script
# =========================================================

set -e  # Exit on any error

echo "========================================================="
echo "   RAILS MIGRATION ASSISTANT - PROFESSIONAL EDITION"
echo "   Automated Rails Upgrade Tool with Local AI"
echo "========================================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "   Please install Python 3.9+ from https://python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.9"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "❌ ERROR: Python 3.9+ required (found Python $python_version)"
    exit 1
fi

# Check if conda environment exists
if ! conda info --envs | grep -q "pytorch_env"; then
    echo "🔧 Creating conda environment..."
    conda create -n pytorch_env python=3.11 -y
fi

# Activate conda environment
echo "🚀 Activating Rails Migration Assistant conda environment..."
eval "$(conda shell.bash hook)"
conda activate pytorch_env

# Check if dependencies are installed
if ! python -c "import torch, transformers, faiss" &> /dev/null; then
    echo "📦 Installing dependencies..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
fi

# Launch the application
echo
echo "🎯 Starting Rails Migration Assistant..."
echo
python launcher.py "$@"
