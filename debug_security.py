#!/usr/bin/env python3
"""
Security System Diagnostic Tool
Helps troubleshoot security system issues
"""

import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_security_system():
    """Test the security system components."""
    print("🔧 SAM Security System Diagnostic")
    print("=" * 50)
    
    # Test 1: Check if security module can be imported
    print("\n1. Testing Security Module Import...")
    try:
        from security import SecureStateManager
        print("✅ Security module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import security module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing security module: {e}")
        return False
    
    # Test 2: Check keystore file
    print("\n2. Testing Keystore File...")
    keystore_path = Path("security/keystore.json")
    if keystore_path.exists():
        print(f"✅ Keystore file exists: {keystore_path}")
        try:
            import json
            with open(keystore_path, 'r') as f:
                keystore_data = json.load(f)
            print(f"✅ Keystore file is valid JSON")
            print(f"   Version: {keystore_data.get('version', 'unknown')}")
            print(f"   Created: {keystore_data.get('created_at', 'unknown')}")
            print(f"   Setup completed: {keystore_data.get('metadata', {}).get('first_setup_completed', False)}")
        except Exception as e:
            print(f"❌ Keystore file is corrupted: {e}")
            return False
    else:
        print(f"❌ Keystore file not found: {keystore_path}")
        return False
    
    # Test 3: Initialize Security Manager
    print("\n3. Testing Security Manager Initialization...")
    try:
        security_manager = SecureStateManager()
        print("✅ Security manager created successfully")
        
        # Check state
        state = security_manager.get_state()
        print(f"   Current state: {state}")
        print(f"   Is unlocked: {security_manager.is_unlocked()}")
        print(f"   Setup required: {security_manager.is_setup_required()}")
        
    except Exception as e:
        print(f"❌ Failed to initialize security manager: {e}")
        import traceback
        print(f"   Error details: {traceback.format_exc()}")
        return False
    
    # Test 4: Test Keystore Manager
    print("\n4. Testing Keystore Manager...")
    try:
        from security.keystore_manager import KeystoreManager
        keystore_manager = KeystoreManager()
        print("✅ Keystore manager created successfully")
        
        # Test validation
        is_valid = keystore_manager.validate_keystore()
        print(f"   Keystore validation: {'✅ PASS' if is_valid else '❌ FAIL'}")
        
    except Exception as e:
        print(f"❌ Failed to test keystore manager: {e}")
        import traceback
        print(f"   Error details: {traceback.format_exc()}")
        return False
    
    # Test 5: Test Crypto Utils
    print("\n5. Testing Crypto Utils...")
    try:
        from security.crypto_utils import CryptoManager
        print("✅ Crypto utils imported successfully")
        
        # Test basic crypto operations
        crypto = CryptoManager()
        test_data = "Hello, World!"
        
        # This should fail without a session key, which is expected
        try:
            encrypted = crypto.encrypt(test_data)
            print("⚠️ Crypto encryption worked without session key (unexpected)")
        except Exception:
            print("✅ Crypto properly requires session key")
        
    except Exception as e:
        print(f"❌ Failed to test crypto utils: {e}")
        import traceback
        print(f"   Error details: {traceback.format_exc()}")
        return False
    
    print("\n🎉 All security system tests passed!")
    print("\n💡 If you're still seeing errors, try:")
    print("   1. Restart the Streamlit application")
    print("   2. Clear browser cache and cookies")
    print("   3. Check file permissions on security/ directory")
    print("   4. Try unlocking with your password again")
    
    return True

def reset_security_system():
    """Reset the security system (WARNING: This will delete all encrypted data!)"""
    print("\n⚠️ SECURITY SYSTEM RESET")
    print("=" * 30)
    print("This will DELETE all encrypted data and reset the security system!")
    print("You will need to set up a new password and re-upload all documents.")
    
    confirm = input("\nType 'RESET' to confirm: ")
    if confirm != "RESET":
        print("❌ Reset cancelled")
        return False
    
    try:
        # Remove keystore
        keystore_path = Path("security/keystore.json")
        if keystore_path.exists():
            keystore_path.unlink()
            print("✅ Keystore file removed")
        
        # Remove encrypted data
        encrypted_dirs = [
            Path("memory_store"),
            Path("chroma_db"),
            Path("sam_secure_memory")
        ]
        
        for dir_path in encrypted_dirs:
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path)
                print(f"✅ Removed encrypted directory: {dir_path}")
        
        print("\n🎉 Security system reset complete!")
        print("   Restart the application to set up a new password.")
        return True
        
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return False

def main():
    """Main diagnostic function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_security_system()
    else:
        test_security_system()

if __name__ == "__main__":
    main()
