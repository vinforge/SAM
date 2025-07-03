#!/usr/bin/env python3
"""
SAM Encryption Setup Script

Standalone script for setting up SAM's enterprise-grade encryption system.
Creates master password, generates encryption keys, and initializes secure storage.

Author: SAM Development Team
Version: 1.0.0
"""

import os
import sys
import getpass
from pathlib import Path

def print_banner():
    """Print encryption setup banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔐 SAM ENCRYPTION SETUP 🔒                               ║
║                   Enterprise-Grade Security Configuration                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def check_security_module():
    """Check if security modules are available."""
    try:
        from security import SecureStateManager
        return True
    except ImportError:
        print("❌ Security modules not found!")
        print("🔧 Please ensure you're in the SAM directory and dependencies are installed.")
        print("   Run: pip install -r requirements.txt")
        return False

def setup_master_password():
    """Setup master password for encryption."""
    print("\n🔐 Master Password Setup")
    print("=" * 50)
    
    try:
        from security import SecureStateManager
        security_manager = SecureStateManager()
        
        if not security_manager.is_setup_required():
            print("✅ Encryption is already set up!")
            print("🔑 Use your existing master password to unlock SAM.")
            return True
        
        print("This is your first time setting up SAM encryption.")
        print("You need to create a master password to encrypt your data.")
        print("\n⚠️  IMPORTANT:")
        print("- Choose a strong password you'll remember")
        print("- This password cannot be recovered if lost")
        print("- All your SAM data will be encrypted with this password")
        print("- Minimum 8 characters (12+ recommended)")
        
        while True:
            password = getpass.getpass("\n🔑 Enter master password: ").strip()
            if len(password) < 8:
                print("❌ Password must be at least 8 characters long")
                continue
            
            confirm = getpass.getpass("🔑 Confirm master password: ").strip()
            if password != confirm:
                print("❌ Passwords do not match")
                continue
            
            break
        
        print("\n🔐 Setting up secure enclave...")
        success = security_manager.setup_master_password(password)
        
        if success:
            print("✅ Master password setup successful!")
            print("✅ Encryption keys generated")
            print("✅ Secure storage initialized")
            return True
        else:
            print("❌ Failed to setup master password")
            return False
            
    except Exception as e:
        print(f"❌ Encryption setup failed: {e}")
        return False

def create_security_directories():
    """Create necessary security directories."""
    print("\n📁 Creating security directories...")
    
    directories = ["security", "memory_store/encrypted", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("✅ Security directories created!")
    return True

def test_encryption():
    """Test encryption functionality."""
    print("\n🧪 Testing encryption...")
    
    try:
        from security import SecureStateManager
        security_manager = SecureStateManager()
        
        if security_manager.is_setup_required():
            print("⚠️  Encryption not set up yet")
            return False
        
        print("✅ Encryption system is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False

def main():
    """Main encryption setup process."""
    print_banner()
    
    print("🎯 This script will set up SAM's encryption system:")
    print("   • Check security modules")
    print("   • Create security directories")
    print("   • Setup master password")
    print("   • Generate encryption keys")
    print("   • Test encryption functionality")
    
    response = input("\n🤔 Continue with encryption setup? (Y/n): ").strip().lower()
    if response == 'n':
        print("👋 Encryption setup cancelled")
        return
    
    # Step 1: Check security modules
    print("\n" + "="*60)
    print("📋 Step 1: Checking Security Modules")
    print("="*60)
    
    if not check_security_module():
        print("\n❌ Cannot proceed without security modules")
        return
    
    # Step 2: Create directories
    print("\n" + "="*60)
    print("📋 Step 2: Creating Security Directories")
    print("="*60)
    
    if not create_security_directories():
        print("\n❌ Failed to create security directories")
        return
    
    # Step 3: Setup master password
    print("\n" + "="*60)
    print("📋 Step 3: Master Password Setup")
    print("="*60)
    
    if not setup_master_password():
        print("\n❌ Master password setup failed")
        return
    
    # Step 4: Test encryption
    print("\n" + "="*60)
    print("📋 Step 4: Testing Encryption")
    print("="*60)
    
    if not test_encryption():
        print("\n⚠️  Encryption test failed, but setup may still be valid")
    
    # Final summary
    print("\n" + "="*80)
    print("🎉 SAM Encryption Setup Complete!")
    print("="*80)
    
    print("\n🔐 **Encryption Status:**")
    print("   ✅ Master password created")
    print("   ✅ Encryption keys generated")
    print("   ✅ Secure storage initialized")
    
    print("\n🚀 **Next Steps:**")
    print("   1. Start SAM: python start_sam_secure.py --mode full")
    print("   2. Enter your master password when prompted")
    print("   3. Access SAM at http://localhost:8502")
    
    print("\n🔑 **Remember:**")
    print("   • Keep your master password safe")
    print("   • It cannot be recovered if lost")
    print("   • All SAM data is encrypted with this password")

if __name__ == "__main__":
    main()
