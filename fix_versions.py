#!/usr/bin/env python3
"""
SAM Version Consistency Fix
===========================

This script fixes version mismatches that can cause issues like:
- "tuple' object has no attribute 'split'" errors
- Different behavior on different machines
- Inconsistent SAM responses

It ensures all installations use the same tested package versions.

Usage: python fix_versions.py
"""

import sys
import subprocess
import platform

def print_header():
    """Print fix header."""
    print("=" * 60)
    print("🔧 SAM Version Consistency Fix")
    print("=" * 60)
    print("Fixing package versions for consistent SAM behavior...")
    print()

def check_current_versions():
    """Check current package versions."""
    print("🔍 Checking current package versions...")
    
    packages_to_check = {
        'streamlit': 'Web interface framework',
        'numpy': 'Numerical computing',
        'pandas': 'Data manipulation',
        'requests': 'HTTP requests',
        'cryptography': 'Security and encryption'
    }
    
    current_versions = {}
    
    for package, description in packages_to_check.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'Unknown')
            print(f"📦 {package}: {version} - {description}")
            current_versions[package] = version
        except ImportError:
            print(f"❌ {package}: Not installed - {description}")
            current_versions[package] = None
    
    return current_versions

def fix_streamlit_version():
    """Fix Streamlit to the working version."""
    print("\n🎯 Fixing Streamlit version (main cause of tuple.split() errors)...")
    
    target_version = "1.42.0"
    
    try:
        # Uninstall current streamlit
        print("🔄 Uninstalling current Streamlit...")
        subprocess.run([
            sys.executable, "-m", "pip", "uninstall", "streamlit", "-y"
        ], capture_output=True, check=True)
        
        # Install specific working version
        print(f"🔄 Installing Streamlit {target_version}...")
        install_cmd = [sys.executable, "-m", "pip", "install"]

        # Add --only-binary=all on Windows to prevent compilation issues
        if platform.system() == "Windows":
            install_cmd.append("--only-binary=all")
            print("💡 Using pre-built package for Windows compatibility...")

        install_cmd.append(f"streamlit=={target_version}")
        subprocess.run(install_cmd, capture_output=True, check=True, timeout=120)
        
        print(f"✅ Streamlit fixed to version {target_version}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fix Streamlit: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Streamlit installation timeout")
        return False
    except Exception as e:
        print(f"❌ Unexpected error fixing Streamlit: {e}")
        return False

def install_from_requirements():
    """Install all packages from requirements.txt."""
    print("\n📋 Installing from requirements.txt for full version consistency...")
    
    try:
        # Check if requirements.txt exists
        from pathlib import Path
        requirements_file = Path("requirements.txt")
        
        if not requirements_file.exists():
            print("⚠️  requirements.txt not found, using manual package list")
            return install_manual_packages()
        
        # Install from requirements.txt
        print("🔄 Installing from requirements.txt...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ All packages installed from requirements.txt")
            return True
        else:
            print(f"⚠️  Requirements.txt installation had issues: {result.stderr[:200]}...")
            print("💡 Trying manual package installation...")
            return install_manual_packages()
            
    except subprocess.TimeoutExpired:
        print("⚠️  Requirements.txt installation timeout")
        return install_manual_packages()
    except Exception as e:
        print(f"⚠️  Error with requirements.txt: {e}")
        return install_manual_packages()

def install_manual_packages():
    """Install packages manually with pinned versions."""
    print("\n🔧 Installing packages manually with pinned versions...")
    
    # Version-pinned packages for consistency
    packages = [
        "streamlit==1.42.0",
        "numpy>=1.21.0,<2.0.0",
        "pandas>=1.3.0,<3.0.0", 
        "requests>=2.25.0,<3.0.0",
        "cryptography>=41.0.0,<43.0.0",
        "argon2-cffi>=23.1.0,<24.0.0",
        "pydantic>=2.0.0,<3.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "plotly>=5.0.0,<6.0.0"
    ]
    
    success_count = 0
    
    for package in packages:
        try:
            print(f"🔄 Installing {package}...")
            install_cmd = [sys.executable, "-m", "pip", "install"]

            # Add --only-binary=all on Windows to prevent compilation issues
            if platform.system() == "Windows":
                install_cmd.append("--only-binary=all")

            install_cmd.append(package)
            subprocess.run(install_cmd, capture_output=True, check=True, timeout=60)
            
            print(f"✅ {package} installed")
            success_count += 1
            
        except subprocess.CalledProcessError:
            print(f"⚠️  {package} failed")
        except subprocess.TimeoutExpired:
            print(f"⚠️  {package} timeout")
        except Exception as e:
            print(f"⚠️  {package} error: {e}")
    
    print(f"\n📊 Manual installation: {success_count}/{len(packages)} packages installed")
    return success_count >= 5  # At least essential packages

def verify_fix():
    """Verify that the fix worked."""
    print("\n🔍 Verifying version fix...")
    
    try:
        import streamlit
        streamlit_version = streamlit.__version__
        
        if streamlit_version == "1.42.0":
            print(f"✅ Streamlit version: {streamlit_version} (CORRECT)")
            return True
        else:
            print(f"⚠️  Streamlit version: {streamlit_version} (Should be 1.42.0)")
            return False
            
    except ImportError:
        print("❌ Streamlit not available after fix")
        return False
    except Exception as e:
        print(f"❌ Error verifying fix: {e}")
        return False

def provide_next_steps(success):
    """Provide next steps based on fix results."""
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 Version fix SUCCESSFUL!")
        print("\n🚀 Next Steps:")
        print("1. Restart SAM: python start_sam.py")
        print("2. Test with a simple question: 'Tell me a joke'")
        print("3. Should work consistently across all machines now")
        print("\n💡 The tuple.split() error should be resolved!")
        
    else:
        print("⚠️  Version fix INCOMPLETE")
        print("\n🔧 Manual Steps Required:")
        print("1. Uninstall streamlit: pip uninstall streamlit")
        print("2. Install specific version: pip install streamlit==1.42.0")
        print("3. Verify: python -c \"import streamlit; print(streamlit.__version__)\"")
        print("4. Should show: 1.42.0")

def main():
    """Main fix function."""
    print_header()
    
    # Check current versions
    current_versions = check_current_versions()
    
    # Fix Streamlit specifically (main culprit)
    streamlit_fixed = fix_streamlit_version()
    
    # Install all packages from requirements for consistency
    all_packages_fixed = install_from_requirements()
    
    # Verify the fix
    verification_success = verify_fix()
    
    # Overall success
    overall_success = streamlit_fixed and verification_success
    
    # Provide next steps
    provide_next_steps(overall_success)
    
    return overall_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Fix cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please try manual Streamlit downgrade:")
        print("   pip uninstall streamlit")
        print("   pip install streamlit==1.42.0")
        sys.exit(1)
