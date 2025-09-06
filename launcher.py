#!/usr/bin/env python3
"""
Rails Migration Assistant - Modern Launcher
A comprehensive tool for Rails application migration analysis and assistance.
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

def check_environment():
    """Check if required dependencies are available."""
    print("🔍 Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required Python packages
    required_packages = ['torch', 'transformers', 'fastapi', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check Node.js for frontend
    node_available = False
    npm_available = False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
            node_available = True
        else:
            print("⚠️  Node.js not found (frontend will not be available)")
    except FileNotFoundError:
        print("⚠️  Node.js not found (frontend will not be available)")
    
    # Check npm
    npm_commands = ["npm", "npm.cmd", "npm.exe"]
    for cmd in npm_commands:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm {result.stdout.strip()}")
                npm_available = True
                break
        except FileNotFoundError:
            continue
    
    if node_available and not npm_available:
        print("⚠️  npm not found (frontend will not be available)")
    
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("\n🚀 Starting FastAPI backend...")
    try:
        import uvicorn
        from api_bridge import app
        
        print("📡 Backend server starting on http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except ImportError as e:
        print(f"❌ Failed to start backend: {e}")
        print("Make sure FastAPI and uvicorn are installed: pip install fastapi uvicorn")
        return False
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False

def start_frontend():
    """Start the React frontend."""
    print("\n🌐 Starting React frontend...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Try to find npm command
    npm_commands = ["npm", "npm.cmd", "npm.exe"]
    npm_cmd = None
    
    for cmd in npm_commands:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            npm_cmd = cmd
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    if not npm_cmd:
        print("❌ npm command not found. Please ensure Node.js is installed and npm is in PATH")
        print("💡 You can manually run: cd frontend && npm start")
        return False
    
    print(f"✅ Using npm command: {npm_cmd}")
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run([npm_cmd, "install"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install frontend dependencies: {e}")
            return False
    
    # Start the frontend
    try:
        print("🎨 Starting React development server...")
        print(f"🌐 Frontend will be available at: http://localhost:3000")
        subprocess.run([npm_cmd, "start"], cwd=frontend_dir)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ npm command not found: {e}")
        print("💡 You can manually run: cd frontend && npm start")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    
    return True

def start_full_stack():
    """Start both backend and frontend."""
    print("\n🔄 Starting full-stack application...")
    
    # Start backend in background
    import threading
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(3)
    
    # Start frontend (blocking)
    start_frontend()

def direct_analysis(query=None, project_path=None):
    """Run direct analysis without GUI."""
    print("\n🔍 Running direct analysis...")
    
    try:
        from rails_migration_assistant import RailsMigrationAssistant
        
        assistant = RailsMigrationAssistant()
        
        if project_path:
            print(f"📁 Analyzing project: {project_path}")
            result = assistant.analyze_project(project_path)
        elif query:
            print(f"❓ Processing query: {query}")
            result = assistant.process_query(query)
        else:
            print("❓ Interactive mode - enter your query:")
            query = input("> ")
            result = assistant.process_query(query)
        
        print("\n📋 Analysis Result:")
        print("=" * 50)
        print(result)
        
    except ImportError as e:
        print(f"❌ Analysis module not available: {e}")
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Rails Migration Assistant - Modern Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py                    # Start full-stack application
  python launcher.py --backend          # Start only backend API
  python launcher.py --frontend         # Start only frontend
  python launcher.py --analyze "query"  # Direct analysis
        """
    )
    
    parser.add_argument('--backend', action='store_true', 
                       help='Start only the FastAPI backend server')
    parser.add_argument('--frontend', action='store_true', 
                       help='Start only the React frontend')
    parser.add_argument('--analyze', type=str, metavar='QUERY',
                       help='Run direct analysis with the given query')
    parser.add_argument('--project', type=str, metavar='PATH',
                       help='Analyze a specific Rails project path')
    parser.add_argument('--check', action='store_true',
                       help='Check environment and dependencies')
    
    args = parser.parse_args()
    
    print("🚀 Rails Migration Assistant - Modern Launcher")
    print("=" * 50)
    
    # Check environment first
    if args.check:
        check_environment()
        return
    
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    try:
        if args.backend:
            start_backend()
        elif args.frontend:
            start_frontend()
        elif args.analyze:
            direct_analysis(query=args.analyze, project_path=args.project)
        elif args.project:
            direct_analysis(project_path=args.project)
        else:
            # Default: start full-stack application
            start_full_stack()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
