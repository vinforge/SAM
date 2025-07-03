#!/usr/bin/env python3
"""
SAM Interactive Setup Script

Comprehensive guided setup for new SAM users with step-by-step instructions,
dependency installation, and security configuration.

Author: SAM Development Team
Version: 1.0.0
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def print_banner():
    """Print interactive setup banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧠 SAM INTERACTIVE SETUP WIZARD 🔧                       ║
║                     Guided Installation & Configuration                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def print_step(step_num, total_steps, title):
    """Print step header."""
    print(f"\n{'='*80}")
    print(f"📋 Step {step_num}/{total_steps}: {title}")
    print('='*80)

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("⚠️  SAM requires Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible!")
    return True

def check_system_requirements():
    """Check system requirements."""
    print("\n💻 Checking system requirements...")
    
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        disk_gb = psutil.disk_usage('.').free / (1024**3)
        
        print(f"✅ Memory: {memory_gb:.1f}GB")
        print(f"✅ Disk space: {disk_gb:.1f}GB available")
        print(f"✅ Platform: {platform.system()} {platform.machine()}")
        
        if memory_gb < 4:
            print("⚠️  Warning: Less than 4GB RAM detected. SAM may run slowly.")
        if disk_gb < 2:
            print("⚠️  Warning: Less than 2GB disk space. Consider freeing up space.")
            
        return True
    except ImportError:
        print("⚠️  Could not check system requirements (psutil not available)")
        return True

def install_dependencies():
    """Install SAM dependencies."""
    print("\n📦 Installing SAM dependencies...")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found!")
        print("🔧 Creating basic requirements file...")
        
        basic_requirements = """streamlit>=1.28.0
flask>=2.3.0
sentence-transformers>=2.2.0
requests>=2.31.0
beautifulsoup4>=4.12.0
PyPDF2>=3.0.0
python-docx>=0.8.11
psutil>=5.9.0
cryptography>=41.0.0
argon2-cffi>=23.1.0
chromadb>=0.4.0
pandas>=2.0.0
numpy>=1.24.0
"""
        with open("requirements.txt", "w") as f:
            f.write(basic_requirements)
        print("✅ Basic requirements.txt created")
    
    try:
        print("  🔄 Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        print("  📥 Installing SAM dependencies...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                               check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency installation failed:")
        print(f"Error: {e.stderr if e.stderr else e.stdout}")
        print("\n🔧 Try manual installation:")
        print("   pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating SAM directories...")
    
    directories = [
        "logs", "memory_store", "security", "config", 
        "uploads", "quarantine", "approved", "archive",
        "data", "data/uploads", "data/documents"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("✅ All directories created!")
    return True

def setup_encryption():
    """Setup encryption and master password."""
    print("\n🔐 Setting up encryption...")
    print("SAM uses enterprise-grade encryption to protect your data.")
    print("You'll create a master password during first launch.")
    print("✅ Encryption will be configured on first run")
    return True

def check_ollama():
    """Check if Ollama is installed."""
    print("\n🤖 Checking Ollama installation...")
    
    try:
        result = subprocess.run(["ollama", "--version"], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama is installed!")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  Ollama not found. SAM can work without it, but AI features will be limited.")
    print("\n📥 To install Ollama:")
    print("   • Visit: https://ollama.ai/download")
    print("   • Download for your platform")
    print("   • Install and run: ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M")
    
    response = input("\nContinue without Ollama? (y/N): ").strip().lower()
    return response == 'y'

def final_setup():
    """Final setup steps."""
    print("\n🎉 Final setup...")
    
    print("✅ SAM installation completed successfully!")
    print("\n🚀 **Next Steps:**")
    print("   1. Start SAM: python start_sam_secure.py --mode full")
    print("   2. Create your master password when prompted")
    print("   3. Access SAM at http://localhost:8502")
    
    print("\n📍 **Access Points:**")
    print("   • Secure Chat: http://localhost:8502")
    print("   • Memory Center: http://localhost:8501")
    print("   • Standard Chat: http://localhost:5001")
    
    return True

def main():
    """Main interactive setup process."""
    print_banner()
    
    print("🎯 This wizard will guide you through SAM installation:")
    print("   • System requirements check")
    print("   • Dependency installation")
    print("   • Directory creation")
    print("   • Security setup")
    print("   • AI model configuration")
    
    response = input("\n🤔 Continue with interactive setup? (Y/n): ").strip().lower()
    if response == 'n':
        print("👋 Setup cancelled")
        return
    
    steps = [
        ("System Requirements", lambda: check_python_version() and check_system_requirements()),
        ("Install Dependencies", install_dependencies),
        ("Create Directories", create_directories),
        ("Setup Encryption", setup_encryption),
        ("Check AI Models", check_ollama),
        ("Final Configuration", final_setup)
    ]
    
    total_steps = len(steps)
    
    for i, (title, func) in enumerate(steps, 1):
        print_step(i, total_steps, title)
        
        if not func():
            print(f"\n❌ Step {i} failed. Please resolve the issues and try again.")
            return
        
        if i < total_steps:
            input("\nPress Enter to continue to next step...")
    
    print("\n" + "="*80)
    print("🎉 SAM Interactive Setup Complete!")
    print("="*80)
    print("SAM is ready to use! Run 'python start_sam_secure.py --mode full' to start.")

if __name__ == "__main__":
    main()
