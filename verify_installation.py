#!/usr/bin/env python3
"""
SAM Installation Verification Script
===================================

Comprehensive verification script to check SAM installation status
and diagnose common issues across different platforms.

Usage: python3 verify_installation.py
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def print_header():
    """Print verification header."""
    print("=" * 60)
    print("🔍 SAM Installation Verification")
    print("=" * 60)
    print("Checking SAM installation and dependencies...")
    print()

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Python Version Check:")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version_str} (Requires Python 3.8+)")
        print("💡 Please upgrade Python:")
        
        system = platform.system()
        if system == "Windows":
            print("   • Download from https://python.org")
        elif system == "Darwin":  # macOS
            print("   • Run: brew install python3")
        else:  # Linux
            print("   • Run: sudo apt install python3.9")
        
        return False
    else:
        print(f"✅ Python {version_str} (Compatible)")
        return True

def check_platform_info():
    """Display platform information."""
    print("\n🖥️  Platform Information:")
    print(f"✅ OS: {platform.system()} {platform.release()}")
    print(f"✅ Architecture: {platform.machine()}")
    print(f"✅ Python executable: {sys.executable}")

def check_dependencies():
    """Check required Python packages."""
    print("\n📦 Dependency Check:")
    
    required_packages = {
        'streamlit': 'Web interface framework',
        'numpy': 'Numerical computing (TTT system)',
        'pandas': 'Data manipulation',
        'requests': 'HTTP requests',
        'cryptography': 'Encryption and security',
        'argon2_cffi': 'Password hashing',
        'pydantic': 'Data validation',
        'plotly': 'Interactive visualizations'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            # Handle package name variations
            import_name = package
            if package == 'argon2_cffi':
                import_name = 'argon2'
            
            __import__(import_name)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (MISSING)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Install missing packages:")
        system = platform.system()
        python_cmd = "python3" if system in ["Linux", "Darwin"] else "python"
        packages_str = " ".join(missing_packages)
        print(f"   {python_cmd} -m pip install {packages_str}")
        return False
    
    return True

def check_sam_files():
    """Check SAM core files."""
    print("\n📁 SAM Files Check:")
    
    required_files = [
        'setup_sam.py',
        'start_sam.py',
        'secure_streamlit_app.py',
        'sam/orchestration/uif.py',
        'sam/orchestration/skills/reasoning/test_time_adaptation.py',
        'ui/ttt_transparency.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (MISSING)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n💡 Missing files detected. Please re-clone the repository:")
        print("   git clone https://github.com/forge-1825/SAM.git")
        return False
    
    return True

def check_sam_modules():
    """Check SAM module imports."""
    print("\n🧠 SAM Modules Check:")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        # Test core SAM imports
        from sam.orchestration.uif import SAM_UIF
        print("✅ SAM Core (UIF)")
        
        from sam.orchestration.skills.reasoning.test_time_adaptation import TestTimeAdaptationSkill
        print("✅ TTT Cognitive Priming Engine")
        
        from sam.monitoring.ttt_metrics import get_ttt_metrics_collector
        print("✅ TTT Metrics System")
        
        from ui.ttt_transparency import render_ttt_status_indicator
        print("✅ TTT UI Components")
        
        return True
        
    except ImportError as e:
        print(f"❌ SAM module import failed: {e}")
        print("💡 This may indicate missing dependencies or file corruption")
        return False

def check_setup_status():
    """Check if SAM has been set up."""
    print("\n⚙️  Setup Status Check:")
    
    setup_indicators = {
        'security/keystore.json': 'Security system',
        'logs/': 'Logging directory',
        'sam_pro_key.txt': 'SAM Pro activation key'
    }
    
    setup_complete = True
    
    for path, description in setup_indicators.items():
        if Path(path).exists():
            print(f"✅ {description}")
        else:
            print(f"⚠️  {description} (Not configured)")
            setup_complete = False
    
    if not setup_complete:
        print("\n💡 Run setup to configure SAM:")
        system = platform.system()
        python_cmd = "python3" if system in ["Linux", "Darwin"] else "python"
        print(f"   {python_cmd} setup_sam.py")
    
    return setup_complete

def run_quick_test():
    """Run a quick functionality test."""
    print("\n🧪 Quick Functionality Test:")
    
    try:
        # Test TTT skill instantiation
        sys.path.insert(0, str(Path.cwd()))
        from sam.orchestration.skills.reasoning.test_time_adaptation import TestTimeAdaptationSkill
        
        skill = TestTimeAdaptationSkill()
        print(f"✅ TTT Skill: {skill.skill_name}")
        
        # Test UIF creation
        from sam.orchestration.uif import SAM_UIF
        uif = SAM_UIF(input_query="Test query")
        print("✅ UIF Creation")
        
        # Test metrics collector
        from sam.monitoring.ttt_metrics import get_ttt_metrics_collector
        collector = get_ttt_metrics_collector()
        print("✅ Metrics Collector")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def provide_next_steps(all_checks_passed):
    """Provide next steps based on verification results."""
    print("\n" + "=" * 60)
    
    if all_checks_passed:
        print("🎉 SAM Installation Verification PASSED!")
        print("\n🚀 Next Steps:")
        
        system = platform.system()
        python_cmd = "python3" if system in ["Linux", "Darwin"] else "python"
        
        print(f"1. Start SAM: {python_cmd} start_sam.py")
        print("2. Open browser to: http://localhost:8502")
        print("3. Enter your master password and SAM Pro key")
        print("4. Start chatting with SAM!")
        
    else:
        print("⚠️  SAM Installation Verification FAILED!")
        print("\n🔧 Recommended Actions:")
        print("1. Install missing dependencies")
        print("2. Re-run setup if needed")
        print("3. Check the installation guide: https://github.com/forge-1825/SAM")
        print("4. Run this verification script again")

def main():
    """Main verification function."""
    print_header()
    
    checks = [
        ("Python Version", check_python_version),
        ("Platform Info", lambda: (check_platform_info(), True)[1]),
        ("Dependencies", check_dependencies),
        ("SAM Files", check_sam_files),
        ("SAM Modules", check_sam_modules),
        ("Setup Status", check_setup_status),
        ("Quick Test", run_quick_test)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed_checks += 1
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
    
    print(f"\n📊 Verification Results: {passed_checks}/{total_checks} checks passed")
    
    all_passed = passed_checks == total_checks
    provide_next_steps(all_passed)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
