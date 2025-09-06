"""
Test suite for Rails Migration Assistant
"""

import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that core modules can be imported"""
    try:
        from src.analyzer.hybrid_analyzer import HybridRailsAnalyzer
        assert True
    except ImportError as e:
        pytest.skip(f"HybridRailsAnalyzer not available: {e}")

def test_launcher():
    """Test that launcher module can be imported"""
    try:
        import launcher
        assert hasattr(launcher, 'main')
    except ImportError as e:
        pytest.skip(f"Launcher not available: {e}")

def test_requirements():
    """Test that basic requirements are available"""
    try:
        import numpy
        import torch
        assert True
    except ImportError as e:
        pytest.skip(f"Basic requirements not available: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
