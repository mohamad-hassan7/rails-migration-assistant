#!/usr/bin/env python3
"""
Complete System Test for Rails Migration Assistant
This script tests both API and Local LLM modes of the Rails migration assistance system.
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description, expect_success=True):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {description}")
    print(f"📝 Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 or not expect_success:
            print("✅ SUCCESS")
            if result.stdout:
                print(f"📤 Output:\n{result.stdout}")
        else:
            print("❌ FAILED")
            if result.stderr:
                print(f"🚨 Error:\n{result.stderr}")
            if result.stdout:
                print(f"📤 Output:\n{result.stdout}")
                
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏱️ TIMEOUT: Command took too long")
        return False
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return False

def main():
    """Run comprehensive system tests."""
    print("🚀 Rails Migration Assistant - Complete System Test")
    print(f"📅 Started at: {datetime.now()}")
    print("="*80)
    
    # Change to project directory
    project_dir = r"c:\Users\Mohammed Hassan\Zewail\SummerInternship\Skolera\BE_Migration\demo"
    os.chdir(project_dir)
    
    # Activate virtual environment
    venv_activate = r".venv\Scripts\Activate.ps1"
    
    results = []
    
    # Test 1: CLI with Gemini API (quick test)
    test1 = run_command(
        f'{venv_activate}; python rails_upgrade_suggestions.py "Rails 7 routing changes" --max-results 2',
        "CLI with Gemini API - Routing Changes",
        expect_success=True
    )
    results.append(("CLI Gemini API", test1))
    
    # Test 2: CLI with Local LLM (may take longer due to model loading)
    test2 = run_command(
        f'{venv_activate}; python rails_upgrade_suggestions.py "update ActiveRecord models for Rails 7" --local --max-results 2',
        "CLI with Local LLM - ActiveRecord Updates",
        expect_success=True
    )
    results.append(("CLI Local LLM", test2))
    
    # Test 3: Check GUI can start (just initialization, no interaction)
    test3 = run_command(
        f'{venv_activate}; python -c "from rails_upgrade_gui import RailsUpgradeGUI; gui = RailsUpgradeGUI(); print(\'GUI initialized successfully\')"',
        "GUI Initialization Test",
        expect_success=True
    )
    results.append(("GUI Initialization", test3))
    
    # Test 4: Test retriever directly
    test4 = run_command(
        f'{venv_activate}; python -c "from src.retriever.retriever import RailsDocsRetriever; r = RailsDocsRetriever(); results = r.search(\'Rails upgrade\', max_results=3); print(f\'Retrieved {{len(results)}} results\')"',
        "Documentation Retriever Test",
        expect_success=True
    )
    results.append(("Documentation Retriever", test4))
    
    # Test 5: Test agent runner
    test5 = run_command(
        f'{venv_activate}; python -c "from src.analyzer.agent_runner import RailsUpgradeAnalyzer; analyzer = RailsUpgradeAnalyzer(); print(\'Analyzer initialized successfully\')"',
        "Agent Runner Initialization Test",
        expect_success=True
    )
    results.append(("Agent Runner", test5))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Total Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is fully operational.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the output above for details.")
    
    print(f"\n📅 Completed at: {datetime.now()}")
    print("="*80)

if __name__ == "__main__":
    main()
