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
    try:
        import streamlit
        print("✅ Streamlit available")
    except ImportError:
        print("❌ Streamlit not found")
        print("💡 Installing Streamlit...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"],
                         check=True, capture_output=True)
            print("✅ Streamlit installed successfully")
        except:
            print("❌ Failed to install Streamlit")
            print("💡 Please run: pip install streamlit")
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

def start_sam():
    """Start SAM using Streamlit."""
    try:
        print("🚀 Starting SAM...")
        
        # Start SAM using streamlit run
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
        
        # Open browser
        try:
            webbrowser.open("http://localhost:8502")
        except:
            print("⚠️  Could not open browser automatically")
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
        print("• Check that secure_streamlit_app.py exists")
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
