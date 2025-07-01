#!/usr/bin/env python3
"""
SAM Security Recovery Tool

Helps recover access to SAM when the master password is unknown or
the keystore has been accidentally overwritten.

Author: SAM Development Team
Version: 1.0.0
"""

import sys
import getpass
import json
from pathlib import Path
from datetime import datetime

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def analyze_current_keystore():
    """Analyze the current keystore situation."""
    print_section("SAM Security Recovery Tool")
    
    keystore_path = Path("security/keystore.json")
    
    if not keystore_path.exists():
        print("❌ No keystore found. Security system needs to be set up.")
        return None
    
    try:
        with open(keystore_path, 'r') as f:
            keystore_data = json.load(f)
        
        metadata = keystore_data.get('metadata', {})
        
        print("📋 **Current Keystore Analysis:**")
        print(f"   • Created: {metadata.get('created_at', 'Unknown')}")
        print(f"   • Installation ID: {metadata.get('installation_id', 'Unknown')}")
        print(f"   • Version: {metadata.get('version', 'Unknown')}")
        print(f"   • Access Count: {metadata.get('access_count', 0)}")
        print(f"   • Last Accessed: {metadata.get('last_accessed', 'Never')}")
        
        # Check if this looks like the test keystore I created
        created_at = metadata.get('created_at', '')
        if '2025-06-20T11:12:18' in created_at:
            print("\n⚠️  **DETECTED:** This appears to be the test keystore created during implementation.")
            print("   The test password was: **TestPassword123!**")
            return "TestPassword123!"
        else:
            print("\n✅ This appears to be your original keystore.")
            return "original"
            
    except Exception as e:
        print(f"❌ Error reading keystore: {e}")
        return None

def test_password(password: str) -> bool:
    """Test if a password works with the current keystore."""
    try:
        from security import SecureStateManager
        
        # Create a temporary state manager to test
        state_manager = SecureStateManager()
        
        # Try to unlock with the password
        success = state_manager.unlock_application(password)
        
        if success:
            # Lock it again to clean up
            state_manager.lock_application()
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error testing password: {e}")
        return False

def backup_current_keystore():
    """Backup the current keystore before making changes."""
    keystore_path = Path("security/keystore.json")
    if not keystore_path.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(f"security/keystore_backup_{timestamp}.json")
    
    try:
        import shutil
        shutil.copy2(keystore_path, backup_path)
        print(f"✅ Keystore backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def reset_security_system():
    """Reset the security system for fresh setup."""
    keystore_path = Path("security/keystore.json")
    
    if keystore_path.exists():
        # Backup first
        backup_path = backup_current_keystore()
        if not backup_path:
            print("❌ Cannot proceed without backup")
            return False
        
        # Remove current keystore
        keystore_path.unlink()
        print("✅ Current keystore removed")
    
    print("✅ Security system reset. You can now run setup_encryption.py to create a new password.")
    return True

def main():
    """Main recovery process."""
    print("🔐 SAM Security Recovery Tool")
    print("This tool helps you regain access to SAM when you don't know the master password.")
    
    # Analyze current situation
    detected_password = analyze_current_keystore()
    
    if detected_password is None:
        print("\n❌ No keystore found. Please run: python setup_encryption.py")
        return
    
    print_subsection("Recovery Options")
    
    if detected_password == "TestPassword123!":
        print("🎯 **GOOD NEWS:** I can help you access SAM right now!")
        print()
        print("**Option 1: Use Test Password (Immediate Access)**")
        print("   • Password: TestPassword123!")
        print("   • You can access SAM immediately")
        print("   • Change password later through SAM interface")
        print()
        print("**Option 2: Reset and Create New Password**")
        print("   • Removes current keystore")
        print("   • You set up your own password")
        print("   • Requires running setup again")
        
        print("\n" + "─" * 40)
        choice = input("Choose option (1 for test password, 2 for reset, q to quit): ").strip().lower()
        
        if choice == '1':
            print("\n✅ **Using Test Password**")
            print("   Password: **TestPassword123!**")
            print()
            print("🚀 **Next Steps:**")
            print("   1. Start SAM: python start_sam_secure.py --mode full")
            print("   2. Enter password: TestPassword123!")
            print("   3. Access SAM normally")
            print("   4. (Optional) Change password through SAM settings")
            
            # Test the password to confirm
            print("\n🧪 Testing password...")
            if test_password("TestPassword123!"):
                print("✅ Password confirmed working!")
            else:
                print("❌ Password test failed - there may be an issue")
            
        elif choice == '2':
            print("\n⚠️  **Resetting Security System**")
            confirm = input("This will remove the current keystore. Continue? [y/N]: ").strip().lower()
            
            if confirm == 'y':
                if reset_security_system():
                    print("\n🚀 **Next Steps:**")
                    print("   1. Run: python setup_encryption.py")
                    print("   2. Create your own master password")
                    print("   3. Start SAM normally")
                else:
                    print("❌ Reset failed")
            else:
                print("👋 Reset cancelled")
        
        elif choice == 'q':
            print("👋 Exiting recovery tool")
        
        else:
            print("❌ Invalid choice")
    
    elif detected_password == "original":
        print("🤔 **This appears to be your original keystore.**")
        print("   I don't know your original password.")
        print()
        print("**Option 1: Try Your Password**")
        print("   • Enter your original master password")
        print("   • If it works, you're all set!")
        print()
        print("**Option 2: Reset Security System**")
        print("   • Remove current keystore (with backup)")
        print("   • Set up new password")
        
        print("\n" + "─" * 40)
        choice = input("Choose option (1 to try password, 2 to reset, q to quit): ").strip().lower()
        
        if choice == '1':
            print("\n🔑 **Password Test**")
            password = getpass.getpass("Enter your master password: ")
            
            if password:
                print("🧪 Testing password...")
                if test_password(password):
                    print("✅ **SUCCESS!** Your password works!")
                    print("\n🚀 **Next Steps:**")
                    print("   1. Start SAM: python start_sam_secure.py --mode full")
                    print("   2. Enter your password")
                    print("   3. Access SAM normally")
                else:
                    print("❌ **Password incorrect or system error**")
                    print("\nYou can:")
                    print("   • Try again with a different password")
                    print("   • Reset the security system (Option 2)")
            else:
                print("❌ No password entered")
        
        elif choice == '2':
            print("\n⚠️  **Resetting Security System**")
            print("This will backup and remove the current keystore.")
            confirm = input("Continue? [y/N]: ").strip().lower()
            
            if confirm == 'y':
                if reset_security_system():
                    print("\n🚀 **Next Steps:**")
                    print("   1. Run: python setup_encryption.py")
                    print("   2. Create your new master password")
                    print("   3. Start SAM normally")
                else:
                    print("❌ Reset failed")
            else:
                print("👋 Reset cancelled")
        
        elif choice == 'q':
            print("👋 Exiting recovery tool")
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Recovery cancelled by user")
    except Exception as e:
        print(f"\n❌ Recovery tool error: {e}")
        print("Please check the logs or contact support.")
