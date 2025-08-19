#!/usr/bin/env python3
"""
Rails Migration Assistant - Production Launcher
==============================================

This launcher provides a clean entry point for the Rails Migration Assistant
with automatic environment setup and error handling.

Usage:
    python launcher.py              # Launch GUI
    python launcher.py --cli        # Launch CLI mode
    python launcher.py --analyze PROJECT_PATH  # Direct analysis
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 Checking environment...")
    
    # Check if we're in conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print(f"🐍 Conda environment: {conda_env}")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    
    # Check core packages (essential)
    core_packages = ['tkinter']
    missing_core = []
    
    for package in core_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
        except ImportError:
            missing_core.append(package)
    
    # Check optional AI packages
    ai_packages = ['torch', 'transformers', 'faiss', 'accelerate', 'numpy', 'datasets']
    missing_ai = []
    
    for package in ai_packages:
        try:
            if package == 'faiss':
                import faiss  # faiss-cpu imports as 'faiss'
            else:
                __import__(package)
        except ImportError:
            missing_ai.append(package)
    
    if missing_core:
        print(f"❌ Missing critical packages: {', '.join(missing_core)}")
        return False
    
    if missing_ai:
        print(f"⚠️  AI packages missing: {', '.join(missing_ai)}")
        print("💡 For full functionality: pip install torch transformers faiss-cpu accelerate numpy datasets")
        print("✅ Basic environment OK - GUI will work with limited features")
        print("✅ Basic environment OK - GUI will work with limited features")
    else:
        print("✅ Full environment check passed")
    
    return True

def launch_gui():
    """Launch the GUI application."""
    print("🚀 Launching Rails Migration Assistant GUI...")
    try:
        from rails_migration_assistant import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ GUI launch failed: {e}")
        print("💡 Try running: python rails_migration_assistant.py")
        return False
    return True

def launch_cli():
    """Launch the CLI application."""
    print("🚀 Launching Rails Migration Assistant CLI...")
    try:
        from src.analyzer.hybrid_analyzer import main as cli_main
        cli_main()
    except Exception as e:
        print(f"❌ CLI launch failed: {e}")
        return False
    return True

def analyze_project(project_path):
    """Analyze a project directly."""
    print(f"🔍 Analyzing project: {project_path}")
    
    if not os.path.exists(project_path):
        print(f"❌ Project path not found: {project_path}")
        return False
    
    try:
        from src.analyzer.hybrid_analyzer import HybridRailsAnalyzer
        
        analyzer = HybridRailsAnalyzer()
        results = analyzer.analyze_project(project_path)
        
        print(f"\n✅ Analysis complete!")
        print(f"   📁 Files analyzed: {results.get('analyzed_files', 0)}")
        print(f"   ⚠️  Issues found: {results.get('total_suggestions', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def main():
    """Main launcher function."""
    print("=" * 60)
    print("🚀 RAILS MIGRATION ASSISTANT")
    print("   Professional Rails Upgrade Tool")
    print("=" * 60)
    
    parser = argparse.ArgumentParser(
        description="Rails Migration Assistant Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py                    # Launch GUI
  python launcher.py --cli              # Launch CLI
  python launcher.py --analyze ./app    # Analyze project
  python launcher.py --check            # Check environment only
        """
    )
    
    parser.add_argument("--cli", action="store_true", 
                       help="Launch in CLI mode")
    parser.add_argument("--analyze", metavar="PATH", 
                       help="Analyze project at PATH")
    parser.add_argument("--check", action="store_true",
                       help="Check environment only")
    
    args = parser.parse_args()
    
    # Always check environment first
    if not check_environment():
        print("\n❌ Environment check failed. Please fix issues and try again.")
        return 1
    
    if args.check:
        print("\n✅ Environment check complete!")
        return 0
    
    # Launch based on arguments
    if args.analyze:
        success = analyze_project(args.analyze)
    elif args.cli:
        success = launch_cli()
    else:
        success = launch_gui()
    
    if success:
        print("\n✅ Rails Migration Assistant completed successfully!")
        return 0
    else:
        print("\n❌ Rails Migration Assistant encountered an error.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
