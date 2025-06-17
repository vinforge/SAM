#!/usr/bin/env python3
"""
SAM Interactive Setup Script

This script provides a guided, interactive setup process for new SAM users.
It handles dependency installation, encryption setup, and initial configuration.

Usage:
    python setup_sam.py

Author: SAM Development Team
Version: 1.0.0
"""

import os
import sys
import time
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Display the SAM setup banner."""
    print("\n" + "=" * 70)
    print("🚀 SAM: Secure AI Memory - Interactive Setup")
    print("=" * 70)
    print("Welcome to SAM! This script will guide you through the setup process.")
    print("SAM is the FIRST AI system with human-like conceptual understanding")
    print("and enterprise-grade security.")
    print("=" * 70)

def print_section(title):
    """Print a section header."""
    print(f"\n{'─' * 50}")
    print(f"📋 {title}")
    print("─" * 50)

def get_user_choice(prompt, options, default=None):
    """Get user choice from a list of options."""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        marker = " (recommended)" if i == 1 else ""
        print(f"  {i}. {option}{marker}")
    
    if default:
        print(f"\nPress Enter for default ({default})")
    
    while True:
        try:
            choice = input("\nEnter your choice: ").strip()
            if not choice and default:
                return default
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num
            else:
                print(f"❌ Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("❌ Please enter a valid number")

def check_python_version():
    """Check if Python version is compatible."""
    print_section("System Requirements Check")
    
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ SAM requires Python 3.8 or higher")
        print("Please upgrade Python and try again")
        return False
    
    if version.minor < 11:
        print("⚠️  Python 3.11+ recommended for optimal performance")
    else:
        print("✅ Python version is optimal")
    
    return True

def check_system_resources():
    """Check system resources."""
    import psutil
    
    # Check RAM
    ram_gb = psutil.virtual_memory().total / (1024**3)
    print(f"💾 Available RAM: {ram_gb:.1f} GB")
    
    if ram_gb < 8:
        print("⚠️  SAM recommends 8GB+ RAM for optimal performance")
    else:
        print("✅ RAM is sufficient")
    
    # Check disk space
    disk_free = psutil.disk_usage('.').free / (1024**3)
    print(f"💽 Free disk space: {disk_free:.1f} GB")
    
    if disk_free < 5:
        print("⚠️  SAM requires 5GB+ free disk space")
        return False
    else:
        print("✅ Disk space is sufficient")
    
    return True

def install_dependencies():
    """Install required dependencies."""
    print_section("Dependency Installation")
    
    print("📦 Installing SAM dependencies...")
    print("This may take a few minutes...")
    
    # Core dependencies
    core_deps = [
        "streamlit>=1.28.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "argon2-cffi>=23.0.0",
        "cryptography>=41.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "PyPDF2>=3.0.0",
        "python-docx>=0.8.11",
        "psutil>=5.9.0"
    ]
    
    try:
        for dep in core_deps:
            print(f"  Installing {dep.split('>=')[0]}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
        
        print("✅ Core dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_ollama():
    """Guide user through Ollama setup."""
    print_section("AI Model Setup (Ollama)")
    
    print("🤖 SAM uses Ollama for local AI processing")
    print("This ensures complete privacy - no data leaves your computer")
    
    # Check if Ollama is installed
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        print(f"✅ Ollama is installed: {result.stdout.strip()}")
        
        # Check if model is available
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "DeepSeek-R1" in result.stdout:
            print("✅ SAM's AI model is already downloaded")
            return True
        else:
            print("📥 Downloading SAM's AI model...")
            print("This is a one-time download (~4GB)")
            
            choice = get_user_choice(
                "Download the AI model now?",
                ["Yes, download now", "Skip for now (manual setup required)"],
                1
            )
            
            if choice == 1:
                try:
                    subprocess.run([
                        "ollama", "pull", 
                        "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M"
                    ], check=True)
                    print("✅ AI model downloaded successfully")
                    return True
                except subprocess.CalledProcessError:
                    print("❌ Failed to download model")
                    return False
            else:
                print("⚠️  You'll need to download the model manually later")
                return True
                
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("\n📖 Installation instructions:")
        
        system = platform.system().lower()
        if system == "darwin":  # macOS
            print("  • Visit: https://ollama.ai/download")
            print("  • Download Ollama for macOS")
            print("  • Install and restart this setup")
        elif system == "linux":
            print("  • Run: curl -fsSL https://ollama.ai/install.sh | sh")
            print("  • Or visit: https://ollama.ai/download")
        elif system == "windows":
            print("  • Visit: https://ollama.ai/download")
            print("  • Download Ollama for Windows")
            print("  • Install and restart this setup")
        
        return False

def setup_encryption():
    """Setup encryption for SAM."""
    print_section("Security Setup")
    
    print("🔐 SAM uses enterprise-grade AES-256-GCM encryption")
    print("All your conversations and documents will be protected")
    
    choice = get_user_choice(
        "How would you like to set up encryption?",
        [
            "Interactive setup (guided process)",
            "Use default security settings",
            "Skip encryption (not recommended)"
        ],
        1
    )
    
    if choice == 1:
        # Interactive encryption setup
        try:
            from setup_encryption import setup_encryption
            return setup_encryption()
        except ImportError:
            print("❌ Encryption setup module not found")
            return False
    
    elif choice == 2:
        # Default security settings
        print("🔑 Setting up default encryption...")
        try:
            from security import SecureStateManager
            import getpass
            
            password = getpass.getpass("Enter master password: ")
            confirm = getpass.getpass("Confirm master password: ")
            
            if password != confirm:
                print("❌ Passwords do not match")
                return False
            
            security_manager = SecureStateManager()
            security_manager.initialize_security(password)
            print("✅ Encryption setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Encryption setup failed: {e}")
            return False
    
    else:
        print("⚠️  Skipping encryption - your data will not be protected")
        return True

def create_config():
    """Create SAM configuration."""
    print_section("Configuration Setup")
    
    print("⚙️  Creating SAM configuration...")
    
    # Create config directory
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Basic configuration
    config = {
        "version": "1.0.0-beta",
        "model": {
            "provider": "ollama",
            "model_name": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
            "api_url": "http://localhost:11434"
        },
        "ui": {
            "chat_port": 5001,
            "memory_ui_port": 8501,
            "secure_port": 8502,
            "host": "0.0.0.0",
            "auto_open_browser": True
        },
        "memory": {
            "max_memories": 10000,
            "backend": "chroma",
            "storage_dir": "memory_store"
        },
        "features": {
            "show_thoughts": True,
            "document_upload": True,
            "memory_management": True,
            "web_search": True,
            "dream_canvas": True
        },
        "security": {
            "encryption_enabled": True,
            "session_timeout": 3600,
            "max_unlock_attempts": 5
        }
    }
    
    # Port configuration
    choice = get_user_choice(
        "Configure network ports:",
        [
            "Use default ports (5001, 8501, 8502)",
            "Customize ports"
        ],
        1
    )
    
    if choice == 2:
        try:
            chat_port = int(input("Chat interface port [5001]: ") or "5001")
            memory_port = int(input("Memory center port [8501]: ") or "8501")
            secure_port = int(input("Secure chat port [8502]: ") or "8502")
            
            config["ui"]["chat_port"] = chat_port
            config["ui"]["memory_ui_port"] = memory_port
            config["ui"]["secure_port"] = secure_port
        except ValueError:
            print("❌ Invalid port number, using defaults")
    
    # Save configuration
    import json
    with open(config_dir / "sam_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration created successfully")
    return True

def setup_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    directories = [
        "logs",
        "memory_store", 
        "security",
        "uploads",
        "quarantine",
        "approved",
        "archive"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    return True

def final_setup():
    """Final setup steps and verification."""
    print_section("Final Setup")
    
    print("🔍 Verifying installation...")
    
    # Check critical files
    critical_files = [
        "config/sam_config.json",
        "start_sam_secure.py",
        "secure_streamlit_app.py"
    ]
    
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Missing!")
            return False
    
    print("✅ Installation verification complete")
    return True

def show_completion():
    """Show completion message and next steps."""
    print("\n" + "=" * 70)
    print("🎉 SAM Setup Complete!")
    print("=" * 70)
    
    print("\n🚀 Your SAM installation is ready!")
    print("\n📍 Access Points:")
    print("  • Secure Chat (Recommended): http://localhost:8502")
    print("  • Memory Center: http://localhost:8501") 
    print("  • Standard Chat: http://localhost:5001")
    
    print("\n🔑 Starting SAM:")
    print("  python start_sam_secure.py --mode full")
    
    print("\n📖 Documentation:")
    print("  • Quick Start: docs/QUICK_ENCRYPTION_SETUP.md")
    print("  • Full Guide: docs/ENCRYPTION_SETUP_GUIDE.md")
    print("  • Main README: docs/README.md")
    
    print("\n🎯 Next Steps:")
    print("  1. Start SAM with the command above")
    print("  2. Enter your master password")
    print("  3. Upload some documents")
    print("  4. Start chatting with your secure AI!")
    
    print("\n⚠️  Remember:")
    print("  • Keep your master password safe")
    print("  • All processing happens locally")
    print("  • Your data never leaves your computer")
    
    print("\n" + "=" * 70)

def main():
    """Main interactive setup process."""
    try:
        print_banner()
        
        # System checks
        if not check_python_version():
            return False
        
        if not check_system_resources():
            return False
        
        # Installation steps
        steps = [
            ("Installing Dependencies", install_dependencies),
            ("Setting up AI Model", setup_ollama),
            ("Configuring Security", setup_encryption),
            ("Creating Configuration", create_config),
            ("Setting up Directories", setup_directories),
            ("Final Verification", final_setup)
        ]
        
        for step_name, step_func in steps:
            print_section(step_name)
            if not step_func():
                print(f"❌ {step_name} failed!")
                return False
            time.sleep(1)  # Brief pause between steps
        
        show_completion()
        return True
        
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
