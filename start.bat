@echo off
REM Rails# Check if conda environment exists
conda info --envs | findstr "pytorch_env" >nul
if errorlevel 1 (
    echo Creating conda environment...
    conda create -n pytorch_env python=3.11 -y
    if errorlevel 1 (
        echo ERROR: Failed to create conda environment
        pause
        exit /b 1
    )
)

# Activate conda environment
echo Activating Rails Migration Assistant conda environment...
call conda activate pytorch_envistant - Windows Startup Script
REM ================================================

echo.
echo =========================================================
echo    RAILS MIGRATION ASSISTANT - PROFESSIONAL EDITION
echo    Automated Rails Upgrade Tool with Local AI
echo =========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "rails_env\Scripts\activate.bat" (
    echo Setting up virtual environment...
    python -m venv rails_env
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating Rails Migration Assistant environment...
call rails_env\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import torch, transformers, faiss" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Launch the application
echo.
echo Starting Rails Migration Assistant...
echo.
python launcher.py %*

if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
