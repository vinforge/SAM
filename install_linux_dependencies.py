#!/usr/bin/env python3
"""
Linux Dependency Installer for SAM
==================================

Specialized installer for Linux systems (Ubuntu/Debian) that handles
common dependency installation issues.

Usage: python3 install_linux_dependencies.py
"""

import sys
import subprocess
import platform
import os

def print_header():
    """Print installer header."""
    print("=" * 60)
    print("🐧 SAM Linux Dependency Installer")
    print("=" * 60)
    print("Installing required Python packages for SAM on Linux...")
    print()

def check_system():
    """Check if running on Linux."""
    if platform.system() != "Linux":
        print("⚠️  This installer is designed for Linux systems")
        print(f"💡 Detected: {platform.system()}")
        print("💡 Please use the appropriate installer for your platform")
        return False
    
    print(f"✅ Linux system detected: {platform.platform()}")
    return True

def check_python():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        print("💡 Please upgrade Python:")
        print("   sudo apt update")
        print("   sudo apt install python3.9 python3.9-pip")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_system_packages():
    """Install system-level packages if needed."""
    print("\n🔧 Checking system packages...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip is available")
        return True
    except:
        print("❌ pip not found")
        print("💡 Installing pip...")
        
        try:
            # Try to install pip
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "python3-pip"], check=True)
            print("✅ pip installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install pip")
            print("💡 Please run manually:")
            print("   sudo apt update")
            print("   sudo apt install python3-pip")
            return False
        except FileNotFoundError:
            print("❌ sudo or apt not found")
            print("💡 Please install pip manually for your Linux distribution")
            return False

def install_python_packages():
    """Install required Python packages."""
    print("\n📦 Installing Python packages...")
    
    packages = [
        "streamlit",
        "numpy", 
        "pandas",
        "requests",
        "cryptography",
        "argon2-cffi",
        "pydantic",
        "python-dotenv",
        "plotly"
    ]
    
    # Try different installation methods
    methods = [
        # Method 1: User installation
        {
            "name": "User installation (--user)",
            "cmd": [sys.executable, "-m", "pip", "install", "--user"] + packages
        },
        # Method 2: Standard installation
        {
            "name": "Standard installation",
            "cmd": [sys.executable, "-m", "pip", "install"] + packages
        },
        # Method 3: Upgrade pip first, then install
        {
            "name": "Upgrade pip and install",
            "cmd": [sys.executable, "-m", "pip", "install", "--upgrade", "pip"] + packages
        }
    ]
    
    for method in methods:
        print(f"\n🔄 Trying: {method['name']}")
        try:
            result = subprocess.run(
                method["cmd"], 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ Installation successful!")
                return True
            else:
                print(f"⚠️  Method failed: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            print("⚠️  Installation timeout")
        except Exception as e:
            print(f"⚠️  Error: {e}")
    
    # If all methods failed
    print("\n❌ All automatic installation methods failed")
    print("💡 Please try manual installation:")
    print()
    print("# Option 1: Using pip3")
    print(f"pip3 install --user {' '.join(packages)}")
    print()
    print("# Option 2: Using python3 -m pip")
    print(f"python3 -m pip install --user {' '.join(packages)}")
    print()
    print("# Option 3: System-wide installation (requires sudo)")
    print(f"sudo python3 -m pip install {' '.join(packages)}")
    
    return False

def verify_installation():
    """Verify that packages were installed correctly."""
    print("\n🔍 Verifying installation...")
    
    packages = {
        'streamlit': 'Web interface framework',
        'numpy': 'Numerical computing',
        'pandas': 'Data manipulation', 
        'requests': 'HTTP requests',
        'cryptography': 'Encryption and security'
    }
    
    all_good = True
    
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (STILL MISSING)")
            all_good = False
    
    return all_good

def provide_next_steps(success):
    """Provide next steps based on installation result."""
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 Linux dependency installation SUCCESSFUL!")
        print("\n🚀 Next Steps:")
        print("1. Start SAM: python3 start_sam.py")
        print("2. Or run setup: python3 setup_sam.py")
        print("3. Open browser to: http://localhost:8502")
        
    else:
        print("⚠️  Linux dependency installation INCOMPLETE")
        print("\n🔧 Troubleshooting Options:")
        print()
        print("1. Try manual installation:")
        print("   pip3 install --user streamlit numpy pandas requests cryptography")
        print()
        print("2. Check Python path:")
        print("   which python3")
        print("   python3 -m pip --version")
        print()
        print("3. Install system packages:")
        print("   sudo apt install python3-dev python3-pip build-essential")
        print()
        print("4. Use virtual environment:")
        print("   python3 -m venv sam_env")
        print("   source sam_env/bin/activate")
        print("   pip install streamlit numpy pandas requests cryptography")
        print()
        print("5. Contact support with error details")

def main():
    """Main installation function."""
    print_header()
    
    # System checks
    if not check_system():
        return False
    
    if not check_python():
        return False
    
    # Install system packages
    if not install_system_packages():
        print("⚠️  System package installation failed, continuing...")
    
    # Install Python packages
    packages_installed = install_python_packages()
    
    # Verify installation
    if packages_installed:
        verification_success = verify_installation()
    else:
        verification_success = False
    
    # Provide next steps
    provide_next_steps(verification_success)
    
    return verification_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please report this error to the SAM team")
        sys.exit(1)
