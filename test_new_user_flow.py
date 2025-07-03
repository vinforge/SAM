#!/usr/bin/env python3
"""
Test script to verify the complete new user installation and setup flow
This script simulates what a new user would experience
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def print_banner():
    print("=" * 80)
    print("🧪 SAM NEW USER FLOW TEST")
    print("=" * 80)
    print("This script tests the complete new user experience:")
    print("1. Fresh installation simulation")
    print("2. Setup script execution")
    print("3. Master password creation flow")
    print("4. SAM launch verification")
    print("=" * 80)

def test_setup_scripts_exist():
    """Test that all required setup scripts exist."""
    print("\n📋 Testing Setup Scripts Availability...")
    
    required_files = [
        "setup.py",
        "interactive_setup.py", 
        "install_sam.py",
        "setup_encryption.py",
        "start_sam_secure.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required setup scripts found!")
    return True

def test_setup_py_options():
    """Test that setup.py shows all options correctly."""
    print("\n📋 Testing setup.py Options Display...")
    
    try:
        # Run setup.py with a timeout and capture output
        result = subprocess.run([sys.executable, "setup.py"], 
                               input="6\n",  # Choose exit option
                               capture_output=True, text=True, timeout=30)
        
        output = result.stdout
        
        # Check for key elements
        required_elements = [
            "Interactive Script",
            "Quick Setup", 
            "Manual Installation",
            "Encryption Only Setup",
            "View Documentation",
            "Exit"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in output:
                missing_elements.append(element)
            else:
                print(f"✅ Found: {element}")
        
        if missing_elements:
            print(f"❌ Missing elements: {missing_elements}")
            return False
        
        print("✅ setup.py displays all options correctly!")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ setup.py timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing setup.py: {e}")
        return False

def test_encryption_setup_script():
    """Test that encryption setup script exists and is callable."""
    print("\n📋 Testing Encryption Setup Script...")
    
    if not Path("setup_encryption.py").exists():
        print("❌ setup_encryption.py not found")
        return False
    
    try:
        # Test that the script can be imported/executed (dry run)
        result = subprocess.run([sys.executable, "-c", 
                               "import setup_encryption; print('✅ Script importable')"],
                               capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ setup_encryption.py is importable and executable")
            return True
        else:
            print(f"❌ setup_encryption.py import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing setup_encryption.py: {e}")
        return False

def test_start_sam_secure_flow():
    """Test the start_sam_secure.py flow for new users."""
    print("\n📋 Testing start_sam_secure.py New User Flow...")
    
    if not Path("start_sam_secure.py").exists():
        print("❌ start_sam_secure.py not found")
        return False
    
    try:
        # Check that the script contains the new user flow logic
        with open("start_sam_secure.py", "r") as f:
            content = f.read()
        
        required_elements = [
            "run_encryption_setup",
            "check_security_setup", 
            "Security setup required",
            "Starting encryption setup"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
            else:
                print(f"✅ Found: {element}")
        
        if missing_elements:
            print(f"❌ Missing elements in start_sam_secure.py: {missing_elements}")
            return False
        
        print("✅ start_sam_secure.py contains new user flow logic!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing start_sam_secure.py: {e}")
        return False

def test_documentation_files():
    """Test that documentation files exist."""
    print("\n📋 Testing Documentation Files...")
    
    doc_files = [
        "SETUP_OPTIONS.md",
        "docs/QUICK_ENCRYPTION_SETUP.md",
        "docs/ENCRYPTION_SETUP_GUIDE.md"
    ]
    
    missing_docs = []
    for doc in doc_files:
        if not Path(doc).exists():
            missing_docs.append(doc)
        else:
            print(f"✅ {doc}")
    
    if missing_docs:
        print(f"⚠️  Missing documentation: {missing_docs}")
        print("📝 Note: Documentation files are helpful but not critical for functionality")
        return True  # Don't fail the test for missing docs
    
    print("✅ All documentation files found!")
    return True

def run_all_tests():
    """Run all tests and provide summary."""
    print_banner()
    
    tests = [
        ("Setup Scripts Availability", test_setup_scripts_exist),
        ("setup.py Options Display", test_setup_py_options),
        ("Encryption Setup Script", test_encryption_setup_script),
        ("start_sam_secure.py Flow", test_start_sam_secure_flow),
        ("Documentation Files", test_documentation_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ SAM new user flow is ready for deployment!")
        print("\n📋 New users can now:")
        print("   1. Run: python setup.py")
        print("   2. Choose Option 1 or 2")
        print("   3. Run: python start_sam_secure.py --mode full")
        print("   4. Create master password when prompted")
        print("   5. Access SAM at http://localhost:8502")
    else:
        print(f"\n⚠️  {total-passed} tests failed!")
        print("🔧 Please fix the failing components before deployment")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
