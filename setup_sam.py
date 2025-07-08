#!/usr/bin/env python3
"""
SAM Master Setup Script
======================

One-command setup for SAM - The world's most advanced AI system.
This script handles everything: dependencies, configuration, and launch.

Usage:
    python setup_sam.py

Author: SAM Development Team
Version: 2.0.0
"""

import sys
import os
import subprocess
import platform
import json
import uuid
import time
from pathlib import Path
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header():
    """Print welcome header."""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 70)
    print("🚀 SAM MASTER SETUP")
    print("=" * 70)
    print("Welcome to SAM - The world's most advanced AI system with")
    print("human-like introspection and self-improvement capabilities!")
    print("=" * 70)
    print(f"{Colors.END}")
    print()

def print_step(step_num, total_steps, description):
    """Print step progress."""
    print(f"{Colors.BLUE}{Colors.BOLD}[{step_num}/{total_steps}] {description}...{Colors.END}")

def print_success(message):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_warning(message):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_error(message):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    """Print info message."""
    print(f"{Colors.CYAN}💡 {message}{Colors.END}")

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required. Current: {version.major}.{version.minor}.{version.micro}")
        print_info("Please upgrade Python and try again:")
        print_info("• Windows: Download from python.org")
        print_info("• macOS: brew install python3")
        print_info("• Linux: sudo apt install python3.8")
        return False

    print_success(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_system_requirements():
    """Check system requirements."""
    print_step(1, 8, "Checking system requirements")

    # Check Python version
    if not check_python_version():
        return False

    # Check available disk space
    try:
        import shutil
        free_space = shutil.disk_usage('.').free / (1024**3)  # GB
        if free_space < 1:
            print_warning(f"Low disk space: {free_space:.1f}GB available (1GB+ recommended)")
        else:
            print_success(f"Disk space: {free_space:.1f}GB available")
    except:
        print_warning("Could not check disk space")

    # Check platform
    system = platform.system()
    print_success(f"Platform: {system} {platform.release()}")

    return True

def install_dependencies():
    """Install required dependencies."""
    print_step(2, 8, "Installing dependencies")

    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      capture_output=True, check=True)
        print_success("pip is available")
    except:
        print_error("pip not found. Please install pip and try again.")
        return False

    # Install requirements
    try:
        print_info("Installing Streamlit (this may take a moment)...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "streamlit>=1.28.0", "requests>=2.25.0"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print_success("Core dependencies installed successfully")
        else:
            print_warning("Some dependencies may have failed to install")
            print_info("Continuing with setup...")
    except subprocess.TimeoutExpired:
        print_warning("Installation taking longer than expected, continuing...")
    except Exception as e:
        print_warning(f"Dependency installation issue: {e}")
        print_info("Continuing with setup...")

    return True

def create_directory_structure():
    """Create necessary directories."""
    print_step(3, 8, "Creating directory structure")

    directories = [
        "security",
        "logs",
        "data",
        "cache",
        "sam/discovery/distillation/data"
    ]

    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {directory}")
        except Exception as e:
            print_warning(f"Could not create {directory}: {e}")

    return True

def initialize_security_system():
    """Initialize security and key system."""
    print_step(4, 8, "Initializing security system")

    try:
        # Create keystore
        keystore_file = Path("security/keystore.json")
        if not keystore_file.exists():
            keystore = {}
            with open(keystore_file, 'w') as f:
                json.dump(keystore, f, indent=2)
            print_success("Created keystore.json")

        # Create entitlements
        entitlements_file = Path("security/entitlements.json")
        if not entitlements_file.exists():
            entitlements = {
                "sam_pro_keys": {},
                "feature_flags": {
                    "tpv_active_reasoning": True,
                    "enhanced_slp_learning": True,
                    "memoir_lifelong_learning": True,
                    "dream_canvas": True,
                    "cognitive_distillation": True,
                    "cognitive_automation": True
                }
            }
            with open(entitlements_file, 'w') as f:
                json.dump(entitlements, f, indent=2)
            print_success("Created entitlements.json")

        return True

    except Exception as e:
        print_error(f"Security initialization failed: {e}")
        return False

def generate_sam_pro_key():
    """Generate SAM Pro activation key."""
    print_step(5, 8, "Generating SAM Pro activation key")

    try:
        # Generate key
        activation_key = str(uuid.uuid4())

        # Add to keystore
        keystore_file = Path("security/keystore.json")
        with open(keystore_file, 'r') as f:
            keystore = json.load(f)

        keystore[activation_key] = {
            'email': 'setup@sam.local',
            'created_date': datetime.now().isoformat(),
            'key_type': 'sam_pro_free',
            'status': 'active',
            'source': 'master_setup'
        }

        with open(keystore_file, 'w') as f:
            json.dump(keystore, f, indent=2)

        print_success("SAM Pro key generated and registered")
        return activation_key

    except Exception as e:
        print_error(f"Key generation failed: {e}")
        return None

def initialize_databases():
    """Initialize SAM databases."""
    print_step(6, 8, "Initializing databases")

    try:
        # Create basic database structure for cognitive distillation
        db_dir = Path("sam/discovery/distillation/data")
        db_dir.mkdir(parents=True, exist_ok=True)

        # Create empty database files that will be initialized by SAM
        db_files = [
            "cognitive_principles.db",
            "successful_interactions.db",
            "distillation_runs.db"
        ]

        for db_file in db_files:
            db_path = db_dir / db_file
            if not db_path.exists():
                # Create empty file - SAM will initialize the schema
                db_path.touch()
                print_success(f"Created database: {db_file}")

        return True

    except Exception as e:
        print_warning(f"Database initialization issue: {e}")
        print_info("SAM will create databases on first run")
        return True

def validate_installation():
    """Validate that SAM components are working."""
    print_step(7, 8, "Validating installation")

    validation_results = []

    # Check critical files
    critical_files = [
        "secure_streamlit_app.py",
        "security/keystore.json",
        "security/entitlements.json"
    ]

    for file_path in critical_files:
        if Path(file_path).exists():
            validation_results.append(f"✅ {file_path}")
        else:
            validation_results.append(f"❌ {file_path}")

    # Test imports
    try:
        import streamlit
        validation_results.append("✅ Streamlit import")
    except ImportError:
        validation_results.append("❌ Streamlit import")

    # Display results
    for result in validation_results:
        print(f"  {result}")

    success_count = sum(1 for r in validation_results if r.startswith("✅"))
    total_count = len(validation_results)

    if success_count >= total_count - 1:  # Allow one failure
        print_success(f"Validation passed: {success_count}/{total_count}")
        return True
    else:
        print_warning(f"Validation issues: {success_count}/{total_count}")
        print_info("SAM may still work, but some features might be limited")
        return True

def create_launch_script():
    """Create convenient launch script."""
    print_step(8, 8, "Creating launch script")

    try:
        launch_script = '''#!/usr/bin/env python3
"""
SAM Launch Script
================

Convenient script to start SAM with proper error handling.
"""

import subprocess
import sys
import webbrowser
import time

def main():
    print("🚀 Starting SAM...")

    try:
        # Start SAM
        process = subprocess.Popen([
            sys.executable, "secure_streamlit_app.py"
        ])

        # Wait a moment for startup
        time.sleep(3)

        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open("http://localhost:8502")

        print("✅ SAM is running!")
        print("📱 Access SAM at: http://localhost:8502")
        print("🛑 Press Ctrl+C to stop SAM")

        # Wait for process
        process.wait()

    except KeyboardInterrupt:
        print("\\n👋 Stopping SAM...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error starting SAM: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

        with open("start_sam_simple.py", 'w') as f:
            f.write(launch_script)

        # Make executable on Unix systems
        if platform.system() != "Windows":
            os.chmod("start_sam.py", 0o755)

        print_success("Created start_sam_simple.py launch script")
        return True

    except Exception as e:
        print_warning(f"Could not create launch script: {e}")
        return False

def main():
    """Main setup function."""
    print_header()

    # Track setup progress
    setup_start_time = time.time()

    try:
        # Step 1: System requirements
        if not check_system_requirements():
            return 1

        # Step 2: Dependencies
        if not install_dependencies():
            print_error("Dependency installation failed")
            return 1

        # Step 3: Directory structure
        if not create_directory_structure():
            print_error("Directory creation failed")
            return 1

        # Step 4: Security system
        if not initialize_security_system():
            print_error("Security initialization failed")
            return 1

        # Step 5: SAM Pro key
        activation_key = generate_sam_pro_key()
        if not activation_key:
            print_error("Key generation failed")
            return 1

        # Step 6: Databases
        if not initialize_databases():
            print_warning("Database initialization had issues")

        # Step 7: Validation
        if not validate_installation():
            print_warning("Validation had issues")

        # Step 8: Launch script
        create_launch_script()

        # Success!
        setup_time = time.time() - setup_start_time

        print()
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 SAM SETUP COMPLETE! 🎉{Colors.END}")
        print(f"{Colors.GREEN}Setup completed in {setup_time:.1f} seconds{Colors.END}")
        print()

        # Display key
        print(f"{Colors.CYAN}{Colors.BOLD}🔑 Your SAM Pro Activation Key:{Colors.END}")
        print("=" * 60)
        print(f"{Colors.YELLOW}{Colors.BOLD}   {activation_key}{Colors.END}")
        print("=" * 60)
        print()

        # Next steps
        print(f"{Colors.BLUE}{Colors.BOLD}🚀 Ready to Start SAM!{Colors.END}")
        print()
        print("📋 Next Steps:")
        print("1. Start SAM:")
        print(f"   {Colors.CYAN}python start_sam_simple.py{Colors.END}")
        print("   OR")
        print(f"   {Colors.CYAN}python secure_streamlit_app.py{Colors.END}")
        print("   OR")
        print(f"   {Colors.CYAN}python start_sam.py{Colors.END} (Advanced launcher)")
        print()
        print("2. Open your browser and go to:")
        print(f"   {Colors.CYAN}http://localhost:8502{Colors.END}")
        print()
        print("3. Enter your activation key when prompted")
        print()
        print("4. Enjoy SAM Pro features:")
        print("   • 🧠 Cognitive Distillation Engine")
        print("   • 🧠 TPV Active Reasoning Control")
        print("   • 📚 MEMOIR Lifelong Learning")
        print("   • 🎨 Dream Canvas Visualization")
        print("   • 🤖 Cognitive Automation")
        print("   • 📊 Advanced Analytics")
        print()
        print(f"{Colors.GREEN}💾 Important: Save your activation key!{Colors.END}")
        print(f"{Colors.CYAN}❓ Questions? Contact: vin@forge1825.net{Colors.END}")
        print()
        print(f"{Colors.BOLD}🌟 Welcome to the future of AI! 🚀🧠{Colors.END}")

        return 0

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Setup cancelled by user{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}❌ Setup failed: {e}{Colors.END}")
        print(f"{Colors.CYAN}💡 Please report this issue to: vin@forge1825.net{Colors.END}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
