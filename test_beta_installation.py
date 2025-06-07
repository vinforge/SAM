#!/usr/bin/env python3
"""
SAM Community Edition Beta - Installation Test Script
Quick test to verify the beta installation is working correctly.
"""

import os
import sys
import json
import subprocess
import importlib
from pathlib import Path

def test_python_version():
    """Test Python version compatibility."""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is too old (3.8+ required)")
        return False

def test_required_files():
    """Test that required files exist."""
    print("📁 Testing required files...")
    
    required_files = [
        "start_sam.py",
        "launch_web_ui.py", 
        "install.py",
        "requirements.txt",
        "README.md",
        "SETUP_GUIDE.md",
        "config/sam_config.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_directory_structure():
    """Test that required directories exist."""
    print("📂 Testing directory structure...")
    
    required_dirs = [
        "config",
        "logs", 
        "memory_store",
        "web_ui",
        "ui",
        "memory",
        "multimodal"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing required directories: {missing_dirs}")
        return False
    else:
        print("✅ All required directories present")
        return True

def test_configuration():
    """Test configuration file validity."""
    print("⚙️  Testing configuration...")
    
    config_path = "config/sam_config.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check required config sections
        required_sections = ["version", "model", "ui", "memory", "features"]
        missing_sections = []
        
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing config sections: {missing_sections}")
            return False
        else:
            print("✅ Configuration is valid")
            return True
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_dependencies():
    """Test that core dependencies can be imported."""
    print("📦 Testing core dependencies...")
    
    core_deps = [
        "flask",
        "streamlit", 
        "requests",
        "numpy",
        "pandas"
    ]
    
    missing_deps = []
    for dep in core_deps:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {missing_deps}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ Core dependencies available")
        return True

def test_ollama_availability():
    """Test if Ollama is available."""
    print("🤖 Testing Ollama availability...")
    
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            
            # Check if model is available
            try:
                result = subprocess.run(["ollama", "list"], 
                                      capture_output=True, text=True, timeout=10)
                if "DeepSeek-R1" in result.stdout:
                    print("✅ Required model is available")
                    return True
                else:
                    print("⚠️  Required model not found")
                    print("💡 Run: ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M")
                    return False
            except Exception:
                print("⚠️  Could not check Ollama models")
                return False
        else:
            print("❌ Ollama not found")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama not found or not responding")
        print("💡 Install from: https://ollama.ai/download")
        return False

def test_port_availability():
    """Test if required ports are available."""
    print("🌐 Testing port availability...")
    
    import socket
    
    ports_to_test = [5001, 8501]
    busy_ports = []
    
    for port in ports_to_test:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                busy_ports.append(port)
        except Exception:
            pass
        finally:
            sock.close()
    
    if busy_ports:
        print(f"⚠️  Ports in use: {busy_ports}")
        print("💡 These ports may conflict with SAM")
        return False
    else:
        print("✅ Required ports are available")
        return True

def test_launcher_scripts():
    """Test that launcher scripts exist and are executable."""
    print("🚀 Testing launcher scripts...")
    
    scripts = []
    if os.name != 'nt':  # Unix-like systems
        scripts.append("start_sam.sh")
    scripts.append("start_sam.bat")  # Windows
    
    issues = []
    for script in scripts:
        if os.path.exists(script):
            if os.name != 'nt' and script.endswith('.sh'):
                # Check if executable on Unix
                if not os.access(script, os.X_OK):
                    issues.append(f"{script} is not executable")
        else:
            issues.append(f"{script} not found")
    
    if issues:
        print(f"⚠️  Launcher script issues: {issues}")
        return False
    else:
        print("✅ Launcher scripts are ready")
        return True

def main():
    """Run all tests."""
    print("🧪 SAM Community Edition Beta - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Required Files", test_required_files),
        ("Directory Structure", test_directory_structure),
        ("Configuration", test_configuration),
        ("Dependencies", test_dependencies),
        ("Ollama Availability", test_ollama_availability),
        ("Port Availability", test_port_availability),
        ("Launcher Scripts", test_launcher_scripts),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SAM is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Start SAM: python start_sam.py")
        print("2. Open browser: http://localhost:5001")
        return True
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        print("\n💡 Common solutions:")
        print("- Run: python install.py")
        print("- Install Ollama: https://ollama.ai/download")
        print("- Check SETUP_GUIDE.md for detailed instructions")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
