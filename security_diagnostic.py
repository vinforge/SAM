#!/usr/bin/env python3
"""
SAM Security Diagnostic Tool
===========================

Checks security module availability and helps install missing dependencies.
Run this if you see "Security Module not available" errors.
"""

import sys
import subprocess
from pathlib import Path

def print_header():
    """Print diagnostic header."""
    print("=" * 60)
    print("🔍 SAM Security Diagnostic")
    print("=" * 60)
    print("Checking security module availability...")
    print()

def check_python_packages():
    """Check if required Python packages are installed."""
    packages = {
        'cryptography': 'Encryption and security functions',
        'argon2_cffi': 'Password hashing',
        'pydantic': 'Data validation',
        'streamlit': 'Web interface',
        'requests': 'HTTP requests'
    }
    
    print("📦 Python Package Status:")
    print("-" * 40)
    
    missing_packages = []
    
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✅ {package:<15} - {description}")
        except ImportError:
            print(f"❌ {package:<15} - {description} (MISSING)")
            missing_packages.append(package)
    
    print()
    return missing_packages

def check_security_modules():
    """Check SAM security module status."""
    print("🔐 SAM Security Module Status:")
    print("-" * 40)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from security import get_security_status
        
        status = get_security_status()
        
        for module, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"{status_icon} {module}")
        
        print()
        return status['security_ready']
        
    except Exception as e:
        print(f"❌ Could not check security status: {e}")
        print()
        return False

def install_missing_packages(packages):
    """Install missing packages."""
    if not packages:
        return True
    
    print("🔧 Installing Missing Packages:")
    print("-" * 40)
    
    # Map package import names to pip install names
    pip_names = {
        'cryptography': 'cryptography>=41.0.0',
        'argon2_cffi': 'argon2-cffi>=23.1.0', 
        'pydantic': 'pydantic>=2.0.0',
        'streamlit': 'streamlit>=1.28.0',
        'requests': 'requests>=2.25.0'
    }
    
    install_packages = [pip_names.get(pkg, pkg) for pkg in packages]
    
    try:
        print(f"Installing: {', '.join(install_packages)}")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install'
        ] + install_packages, check=True, capture_output=True, text=True)
        
        print("✅ Packages installed successfully!")
        print()
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print("stderr:", e.stderr)
        print()
        return False

def check_file_permissions():
    """Check if security files exist and are accessible."""
    print("📁 File System Status:")
    print("-" * 40)
    
    files_to_check = [
        'security/',
        'security/keystore.json',
        'security/entitlements.json',
        'secure_streamlit_app.py'
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                print(f"✅ Directory: {file_path}")
            else:
                print(f"✅ File: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_good = False
    
    print()
    return all_good

def provide_solutions():
    """Provide solutions for common issues."""
    print("💡 Solutions:")
    print("-" * 40)
    print("1. Install missing packages:")
    print("   pip install cryptography argon2-cffi pydantic streamlit requests")
    print()
    print("2. Re-run SAM setup:")
    print("   python setup_sam.py")
    print()
    print("3. Start SAM:")
    print("   python start_sam.py")
    print()
    print("4. If issues persist:")
    print("   - Check Python version (3.8+ required)")
    print("   - Try using a virtual environment")
    print("   - Contact support: vin@forge1825.net")
    print()

def main():
    """Main diagnostic function."""
    print_header()
    
    # Check Python packages
    missing_packages = check_python_packages()
    
    # Check security modules
    security_ready = check_security_modules()
    
    # Check file permissions
    files_ok = check_file_permissions()
    
    # Summary
    print("📋 Summary:")
    print("-" * 40)
    
    if not missing_packages and security_ready and files_ok:
        print("✅ All checks passed! Security should be working.")
        print("🚀 Try starting SAM: python start_sam.py")
    else:
        print("❌ Issues found:")
        if missing_packages:
            print(f"   • Missing packages: {', '.join(missing_packages)}")
        if not security_ready:
            print("   • Security modules not ready")
        if not files_ok:
            print("   • Missing security files")
        
        print()
        
        # Offer to install missing packages
        if missing_packages:
            try:
                response = input("🤔 Install missing packages automatically? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    if install_missing_packages(missing_packages):
                        print("🎉 Installation complete! Try starting SAM again.")
                    else:
                        provide_solutions()
                else:
                    provide_solutions()
            except KeyboardInterrupt:
                print("\n👋 Diagnostic cancelled")
        else:
            provide_solutions()

if __name__ == "__main__":
    main()
