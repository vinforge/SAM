#!/usr/bin/env python3
"""
SAM Secure Launcher

Launches SAM with integrated security features.
Provides options for migration, secure mode, and legacy compatibility.

Author: SAM Development Team
Version: 1.0.0
"""

import os
import sys
import subprocess
import argparse
import time

# Suppress PyTorch/Streamlit compatibility warnings
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

def print_banner():
    """Print SAM Secure Enclave banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🧠 SAM SECURE ENCLAVE 🔒                           ║
║                     Your AI Assistant with Enterprise Security               ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        ('streamlit', 'Streamlit web framework'),
        ('flask', 'Flask web server'),
        ('chromadb', 'ChromaDB vector database'),
        ('argon2', 'Argon2 password hashing'),
        ('cryptography', 'Cryptography library')
    ]

    missing_packages = []

    for module_name, description in required_packages:
        try:
            __import__(module_name)
            print(f"  ✅ {description}")
        except ImportError:
            print(f"  ❌ {description}")
            # Map module names to pip package names
            pip_name = {
                'argon2': 'argon2-cffi'
            }.get(module_name, module_name)
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies satisfied")
    return True

def check_security_setup():
    """Check if security is already set up."""
    try:
        from security import SecureStateManager
        security_manager = SecureStateManager()
        
        if security_manager.is_setup_required():
            print("🔧 Security setup required (first run)")
            return False
        else:
            print("✅ Security already configured")
            return True
            
    except ImportError:
        print("❌ Security module not available")
        return False
    except Exception as e:
        print(f"⚠️  Security check failed: {e}")
        return False

def run_migration():
    """Run data migration to encrypted format."""
    print("\n🔄 Starting data migration to encrypted format...")
    
    try:
        # Run migration script
        result = subprocess.run([
            sys.executable, 
            "scripts/migrate_to_secure_enclave.py"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            return True
        else:
            print("❌ Migration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def launch_secure_streamlit():
    """Launch secure Streamlit application."""
    print("\n🚀 Launching SAM Secure Streamlit Application...")
    
    try:
        # Launch secure Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "secure_streamlit_app.py",
            "--server.port=8502",
            "--server.address=0.0.0.0",
            "--browser.gatherUsageStats=false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 SAM Secure Streamlit stopped by user")
    except Exception as e:
        print(f"❌ Failed to launch Secure Streamlit: {e}")

def launch_secure_web_ui():
    """Launch secure web UI."""
    print("\n🌐 Launching SAM Secure Web UI...")
    
    try:
        # Launch web UI with security
        subprocess.run([sys.executable, "web_ui/app.py"])
        
    except KeyboardInterrupt:
        print("\n👋 SAM Secure Web UI stopped by user")
    except Exception as e:
        print(f"❌ Failed to launch Secure Web UI: {e}")

def launch_memory_ui():
    """Launch memory control center."""
    print("\n🧠 Launching Memory Control Center...")
    
    try:
        # Launch memory UI
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "ui/memory_app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--browser.gatherUsageStats=false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Memory Control Center stopped by user")
    except Exception as e:
        print(f"❌ Failed to launch Memory Control Center: {e}")

def launch_full_suite():
    """Launch full SAM suite with security."""
    print("\n🚀 Launching Full SAM Secure Suite...")
    print("This will start:")
    print("  🌐 Secure Web UI (port 5001)")
    print("  🧠 Memory Control Center (port 8501)")
    print("  📱 Secure Streamlit App (port 8502)")
    
    processes = []
    
    try:
        # Launch Web UI
        print("\n🌐 Starting Secure Web UI...")
        web_process = subprocess.Popen([sys.executable, "web_ui/app.py"])
        processes.append(("Web UI", web_process))
        time.sleep(2)
        
        # Launch Memory UI
        print("🧠 Starting Memory Control Center...")
        memory_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "ui/memory_app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--browser.gatherUsageStats=false"
        ])
        processes.append(("Memory UI", memory_process))
        time.sleep(2)
        
        # Launch Secure Streamlit
        print("📱 Starting Secure Streamlit App...")
        streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "secure_streamlit_app.py",
            "--server.port=8502",
            "--server.address=0.0.0.0",
            "--browser.gatherUsageStats=false"
        ])
        processes.append(("Secure Streamlit", streamlit_process))
        
        print("\n✅ All services started successfully!")
        print("\n🌐 Access points:")
        print("  • Secure Web UI: http://localhost:5001")
        print("  • Memory Control Center: http://localhost:8501")
        print("  • Secure Streamlit App: http://localhost:8502")
        print("\n⚠️  Press Ctrl+C to stop all services")
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} stopped unexpectedly")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping all SAM services...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"  ✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"  🔪 {name} force killed")
            except Exception as e:
                print(f"  ⚠️  Error stopping {name}: {e}")
        
        print("👋 SAM Secure Suite stopped")
    
    except Exception as e:
        print(f"❌ Failed to launch full suite: {e}")
        # Cleanup
        for name, process in processes:
            try:
                process.terminate()
            except Exception:
                pass

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(description="SAM Secure Enclave Launcher")
    parser.add_argument("--mode", choices=["web", "streamlit", "memory", "full", "migrate"], 
                       default="full", help="Launch mode")
    parser.add_argument("--skip-checks", action="store_true", help="Skip dependency checks")
    parser.add_argument("--force-migration", action="store_true", help="Force data migration")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check dependencies
    if not args.skip_checks:
        if not check_dependencies():
            sys.exit(1)
    
    # Handle migration mode
    if args.mode == "migrate" or args.force_migration:
        if run_migration():
            print("\n✅ Migration completed! You can now launch SAM securely.")
        else:
            print("\n❌ Migration failed! Please check the logs.")
        return
    
    # Check security setup
    security_ready = check_security_setup()
    
    if not security_ready:
        print("\n🔧 Security setup required.")
        print("You can either:")
        print("  1. Run migration: python start_sam_secure.py --mode migrate")
        print("  2. Launch and setup during first use")
        
        response = input("\nProceed with launch? (y/N): ").strip().lower()
        if response != 'y':
            print("👋 Setup cancelled")
            return
    
    # Launch based on mode
    if args.mode == "web":
        launch_secure_web_ui()
    elif args.mode == "streamlit":
        launch_secure_streamlit()
    elif args.mode == "memory":
        launch_memory_ui()
    elif args.mode == "full":
        launch_full_suite()
    else:
        print(f"❌ Unknown mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
