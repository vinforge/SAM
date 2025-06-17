#!/usr/bin/env python3
"""
SAM Encryption Setup Script

This script helps new users set up AES-256-GCM encryption for SAM.
It provides a guided setup process for creating master passwords and
initializing the secure keystore.

Usage:
    python setup_encryption.py

Author: SAM Development Team
Version: 1.0.0
"""

import os
import sys
import getpass
import logging
from pathlib import Path

def setup_logging():
    """Setup basic logging for the setup process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/encryption_setup.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Check if required security dependencies are installed."""
    print("🔍 Checking security dependencies...")
    
    required_packages = [
        ('argon2', 'Argon2 password hashing'),
        ('cryptography', 'Cryptography library'),
        ('secrets', 'Secure random generation')
    ]
    
    missing_packages = []
    
    for module_name, description in required_packages:
        try:
            __import__(module_name)
            print(f"  ✅ {description}")
        except ImportError:
            print(f"  ❌ {description}")
            pip_name = 'argon2-cffi' if module_name == 'argon2' else module_name
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All security dependencies satisfied")
    return True

def validate_password(password):
    """Validate master password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    strength_score = sum([has_upper, has_lower, has_digit, has_special])
    
    if strength_score < 2:
        return False, "Password should contain uppercase, lowercase, numbers, and symbols"
    
    return True, "Password strength acceptable"

def get_master_password():
    """Get and validate master password from user."""
    print("\n🔑 Master Password Setup")
    print("=" * 50)
    print("Your master password will be used to encrypt all SAM data.")
    print("⚠️  IMPORTANT: This password cannot be recovered if lost!")
    print("\nPassword Requirements:")
    print("  • Minimum 8 characters (12+ recommended)")
    print("  • Mix of uppercase, lowercase, numbers, symbols")
    print("  • Unique password (don't reuse from other accounts)")
    
    while True:
        print("\n" + "─" * 30)
        password = getpass.getpass("Enter master password: ")
        
        if not password:
            print("❌ Password cannot be empty")
            continue
        
        is_valid, message = validate_password(password)
        if not is_valid:
            print(f"❌ {message}")
            continue
        
        confirm_password = getpass.getpass("Confirm master password: ")
        
        if password != confirm_password:
            print("❌ Passwords do not match")
            continue
        
        print(f"✅ {message}")
        return password

def setup_encryption():
    """Main encryption setup process."""
    print("🔐 SAM Encryption Setup")
    print("=" * 50)
    print("This script will help you set up enterprise-grade encryption for SAM.")
    print("All your conversations, documents, and memories will be protected.")
    
    # Check if already set up
    keystore_path = Path("security/keystore.json")
    if keystore_path.exists():
        print("\n⚠️  Encryption is already set up!")
        print(f"Keystore found at: {keystore_path}")
        
        response = input("\nDo you want to reset encryption? (This will DELETE all encrypted data) [y/N]: ")
        if response.lower() != 'y':
            print("👋 Setup cancelled")
            return False
        
        # Backup existing keystore
        backup_path = keystore_path.with_suffix('.backup')
        keystore_path.rename(backup_path)
        print(f"📦 Existing keystore backed up to: {backup_path}")
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Get master password
    password = get_master_password()
    
    # Initialize security system
    print("\n🚀 Initializing SAM Secure Enclave...")
    
    try:
        # Import security modules
        from security import SecureStateManager
        
        # Create security manager
        security_manager = SecureStateManager()
        
        # Initialize with master password
        print("  🔑 Generating encryption keys...")
        security_manager.initialize_security(password)
        
        print("  🔒 Creating secure keystore...")
        print("  ✅ Encryption setup completed successfully!")
        
        # Verify setup
        print("\n🔍 Verifying encryption setup...")
        if security_manager.is_setup_required():
            print("❌ Setup verification failed")
            return False
        
        print("✅ Encryption setup verified!")
        
        # Display success information
        print("\n" + "=" * 50)
        print("🎉 SAM Encryption Setup Complete!")
        print("=" * 50)
        print("Your SAM installation is now protected with:")
        print("  🔐 AES-256-GCM encryption")
        print("  🔑 Argon2id key derivation")
        print("  🛡️  Zero-knowledge architecture")
        print("  🏠 100% local processing")
        
        print(f"\n📁 Keystore created: {keystore_path}")
        print("📊 Security level: Enterprise Grade")
        
        print("\n🚀 Next Steps:")
        print("  1. Start SAM: python start_sam_secure.py --mode full")
        print("  2. Access SAM: http://localhost:8502")
        print("  3. Enter your master password to unlock")
        print("  4. Upload documents and start chatting securely!")
        
        print("\n⚠️  REMEMBER:")
        print("  • Keep your master password safe")
        print("  • Use a password manager to store it")
        print("  • No password recovery is possible")
        print("  • Consider encrypted backups of important data")
        
        return True
        
    except ImportError as e:
        print(f"❌ Security modules not available: {e}")
        print("Please ensure SAM is properly installed")
        return False
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        logging.error(f"Encryption setup failed: {e}")
        return False

def main():
    """Main entry point."""
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    setup_logging()
    
    try:
        success = setup_encryption()
        if success:
            print("\n✅ Encryption setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Encryption setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logging.error(f"Unexpected error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
