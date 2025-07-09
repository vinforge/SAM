#!/usr/bin/env python3
"""
SAM Main Launcher
================

Streamlined launcher for SAM with first-time setup detection.
Automatically guides new users through setup and launches SAM.

Usage: python start_sam.py
"""

import os
import sys
import time
import subprocess
import webbrowser
import json
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def print_header():
    """Print SAM startup header."""
    print("=" * 60)
    print("🚀 SAM - Starting Up")
    print("=" * 60)
    print("Welcome to SAM - The world's most advanced AI system")
    print("with human-like introspection and self-improvement!")
    print("=" * 60)
    print()

def check_first_time_setup():
    """Check if this is a first-time user and handle setup."""
    try:
        from utils.first_time_setup import get_first_time_setup_manager
        setup_manager = get_first_time_setup_manager()

        if setup_manager.is_first_time_user():
            print("🎯 First-time setup detected!")
            print()

            # Show setup progress
            progress = setup_manager.get_setup_progress()
            next_step = progress['next_step']

            print(f"📋 Setup Progress: {progress['completed_steps']}/{progress['total_steps']} steps complete")
            print()

            if next_step == 'master_password':
                print("🔐 Next: Create your master password for secure encryption")
                print("💡 This password protects all your SAM data and conversations")
            elif next_step == 'sam_pro_activation':
                print("🔑 Next: Activate your SAM Pro features")
                sam_pro_key = setup_manager.get_sam_pro_key()
                if sam_pro_key:
                    print(f"💎 Your SAM Pro Key: {sam_pro_key}")
                    print("💡 Enter this key in SAM to unlock all premium features")
            elif next_step == 'onboarding':
                print("🎓 Next: Complete the quick onboarding tour")
                print("💡 Learn about SAM's powerful features and capabilities")

            print()
            print("🌐 SAM will open in your browser with the setup wizard")
            print("📱 Follow the on-screen instructions to complete setup")
            print()

            return True
        else:
            print("✅ Setup complete - launching SAM...")
            print()
            return False

    except ImportError as e:
        print(f"⚠️  Missing dependencies: {e}")
        print("🔧 Run security diagnostic: python security_diagnostic.py")
        print("🚀 Continuing with SAM launch...")
        print()
        return False
    except Exception as e:
        print(f"⚠️  Could not check setup status: {e}")
        print("🚀 Continuing with SAM launch...")
        print()
        return False

def check_dependencies():
    """Check if required dependencies are available."""
    import platform

    missing_packages = []

    # Check essential packages
    essential_packages = {
        'streamlit': 'streamlit',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'requests': 'requests',
        'cryptography': 'cryptography'
    }

    print("🔍 Checking dependencies...")
    for package_name, package_spec in essential_packages.items():
        try:
            __import__(package_name)
            print(f"✅ {package_name} available")
        except ImportError:
            print(f"❌ {package_name} not found")
            missing_packages.append(package_spec)

    # Install missing packages if any
    if missing_packages:
        print(f"\n💡 Installing {len(missing_packages)} missing packages...")

        # Determine the correct Python command
        system = platform.system()
        python_cmd = sys.executable

        # Try multiple installation methods
        installation_success = False

        # Method 1: Direct pip install
        try:
            print("🔄 Attempting installation...")
            result = subprocess.run([
                python_cmd, "-m", "pip", "install", "--user"
            ] + missing_packages,
            capture_output=True, text=True, timeout=180)

            if result.returncode == 0:
                print("✅ Packages installed successfully!")
                installation_success = True
            else:
                print(f"⚠️  Installation had issues: {result.stderr}")

        except subprocess.TimeoutExpired:
            print("⚠️  Installation timeout")
        except Exception as e:
            print(f"⚠️  Installation error: {e}")

        # Method 2: Try without --user flag
        if not installation_success:
            try:
                print("🔄 Trying alternative installation method...")
                result = subprocess.run([
                    python_cmd, "-m", "pip", "install"
                ] + missing_packages,
                capture_output=True, text=True, timeout=180)

                if result.returncode == 0:
                    print("✅ Packages installed successfully!")
                    installation_success = True
                else:
                    print(f"⚠️  Alternative installation failed: {result.stderr}")

            except Exception as e:
                print(f"⚠️  Alternative installation error: {e}")

        # If automatic installation failed, provide manual instructions
        if not installation_success:
            print("\n❌ Automatic installation failed")
            print("📋 Please install dependencies manually:")
            print()

            if system == "Linux":
                print("🐧 For Linux (Ubuntu/Debian):")
                print("   sudo apt update")
                print("   sudo apt install python3-pip")
                print(f"   python3 -m pip install --user {' '.join(missing_packages)}")
                print("   # Or try: pip3 install --user " + ' '.join(missing_packages))
            elif system == "Darwin":  # macOS
                print("🍎 For macOS:")
                print(f"   python3 -m pip install --user {' '.join(missing_packages)}")
                print("   # Or try: pip3 install --user " + ' '.join(missing_packages))
            else:  # Windows
                print("🪟 For Windows:")
                print(f"   python -m pip install {' '.join(missing_packages)}")
                print("   # Or try: pip install " + ' '.join(missing_packages))

            print()
            print("💡 After manual installation, run this script again:")
            print(f"   {python_cmd} start_sam.py")
            print()
            return False

        # Re-check packages after installation
        print("\n🔍 Verifying installation...")
        still_missing = []
        for package_name in missing_packages:
            try:
                __import__(package_name)
                print(f"✅ {package_name} now available")
            except ImportError:
                print(f"❌ {package_name} still missing")
                still_missing.append(package_name)

        if still_missing:
            print(f"\n⚠️  Some packages still missing: {', '.join(still_missing)}")
            print("💡 Please install them manually and try again")
            return False

    # Check security dependencies
    try:
        from security import is_security_available
        if is_security_available():
            print("✅ Security modules available")
        else:
            print("⚠️  Security modules have missing dependencies")
            print("💡 Run diagnostic: python security_diagnostic.py")
    except ImportError:
        print("⚠️  Security modules not available")
        print("💡 Run diagnostic: python security_diagnostic.py")

    return True

def is_first_time_user():
    """Check if this is a first-time user who needs setup."""
    try:
        # Check for security setup
        from security import SecureStateManager
        security_manager = SecureStateManager()

        # If security setup is required, this is a first-time user
        if security_manager.is_setup_required():
            return True

    except ImportError:
        pass
    except Exception:
        pass

    # Check setup status file
    try:
        setup_file = Path("setup_status.json")
        if setup_file.exists():
            with open(setup_file, 'r') as f:
                status = json.load(f)

            # Check if master password is created
            if status.get('master_password_created', False):
                return False

    except Exception:
        pass

    # Check for keystore file
    keystore_file = Path("security/keystore.json")
    if keystore_file.exists():
        return False

    # If no indicators of setup, assume first-time user
    return True

def start_sam():
    """Start SAM using Streamlit."""
    try:
        # Check if this is a first-time user
        if is_first_time_user():
            print("🎯 First-time user detected!")
            print("🚀 Starting SAM Welcome & Setup page...")

            # Start welcome setup page
            cmd = [
                sys.executable, "-m", "streamlit", "run", "welcome_setup.py",
                "--server.port", "8503",
                "--server.address", "localhost",
                "--browser.gatherUsageStats", "false",
                "--server.headless", "true"
            ]

            print("🌐 Opening SAM Welcome page in your browser...")
            print("📱 Setup page: http://localhost:8503")
            print("📋 After setup, access SAM at: http://localhost:8502")

        else:
            print("✅ Existing user detected")
            print("🚀 Starting SAM main interface...")

            # Start main SAM interface
            cmd = [
                sys.executable, "-m", "streamlit", "run", "secure_streamlit_app.py",
                "--server.port", "8502",
                "--server.address", "localhost",
                "--browser.gatherUsageStats", "false",
                "--server.headless", "true"
            ]

            print("🌐 Opening SAM in your browser...")
            print("📱 Access SAM at: http://localhost:8502")

        print()
        print("🛑 Press Ctrl+C to stop SAM")
        print("=" * 60)
        print()

        # Start the process
        process = subprocess.Popen(cmd)
        
        # Wait a moment for startup
        time.sleep(3)

        # Open browser to appropriate URL
        try:
            if is_first_time_user():
                webbrowser.open("http://localhost:8503")
            else:
                webbrowser.open("http://localhost:8502")
        except:
            print("⚠️  Could not open browser automatically")
            if is_first_time_user():
                print("🌐 Please open: http://localhost:8503")
            else:
                print("🌐 Please open: http://localhost:8502")
        
        # Wait for the process
        process.wait()
        
        return True
        
    except KeyboardInterrupt:
        print("\n👋 SAM stopped by user")
        try:
            process.terminate()
        except:
            pass
        return True
    except Exception as e:
        print(f"❌ Error starting SAM: {e}")
        print()
        print("🔧 Troubleshooting:")
        print("• Make sure you're in the SAM directory")
        print("• Try: pip install streamlit")
        print("• Check that secure_streamlit_app.py and welcome_setup.py exist")
        print("💡 Manual start options:")
        print("  First-time: streamlit run welcome_setup.py --server.port 8503")
        print("  Existing: streamlit run secure_streamlit_app.py --server.port 8502")
        return False

def main():
    """Main launcher function."""
    try:
        # Print header
        print_header()
        
        # Check dependencies
        if not check_dependencies():
            return 1
        
        # Check for first-time setup
        is_first_time = check_first_time_setup()
        
        # Start SAM
        if start_sam():
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled by user")
        return 0
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        print("💡 Please report this issue to: vin@forge1825.net")
        return 1

if __name__ == "__main__":
    sys.exit(main())
