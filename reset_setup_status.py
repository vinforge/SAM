#!/usr/bin/env python3
"""
Reset Setup Status for Testing
==============================

This script resets the setup status to simulate a fresh installation
for testing the first-time user detection logic.

Usage: python reset_setup_status.py
"""

import sys
import json
from pathlib import Path

def reset_setup_status():
    """Reset setup status to simulate fresh installation."""
    print("=" * 60)
    print("🔄 Resetting Setup Status")
    print("=" * 60)
    print("This will reset SAM to first-time user state for testing...")
    print()
    
    # Files that indicate completed setup
    files_to_remove = [
        "setup_status.json",  # Welcome page completion status
    ]
    
    # Files to modify (not remove completely)
    files_to_modify = [
        "security/keystore.json",  # Remove password_hash to simulate technical-only setup
    ]
    
    # Files to keep (technical setup from setup_sam.py)
    files_to_keep = [
        "sam_pro_key.txt",  # Keep SAM Pro key from setup_sam.py
        "security/entitlements.json",  # Keep entitlements
    ]
    
    removed_count = 0
    modified_count = 0
    
    # Remove welcome page completion indicators
    for file_path in files_to_remove:
        path = Path(file_path)
        if path.exists():
            try:
                path.unlink()
                print(f"🗑️  Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Could not remove {file_path}: {e}")
        else:
            print(f"📝 Not found: {file_path}")
    
    # Modify keystore to remove password_hash (simulate technical setup only)
    keystore_file = Path("security/keystore.json")
    if keystore_file.exists():
        try:
            with open(keystore_file, 'r') as f:
                keystore_data = json.load(f)
            
            # Remove password_hash to simulate technical setup without welcome page
            if 'password_hash' in keystore_data:
                del keystore_data['password_hash']
                keystore_data['note'] = 'Technical setup only - no welcome page completion'
                
                with open(keystore_file, 'w') as f:
                    json.dump(keystore_data, f, indent=2)
                
                print(f"🔧 Modified: {keystore_file} (removed password_hash)")
                modified_count += 1
            else:
                print(f"📝 No password_hash in: {keystore_file}")
                
        except Exception as e:
            print(f"❌ Could not modify {keystore_file}: {e}")
    else:
        print(f"📝 Not found: {keystore_file}")
    
    # Show what we're keeping
    print(f"\n📋 Keeping technical setup files:")
    for file_path in files_to_keep:
        path = Path(file_path)
        if path.exists():
            print(f"✅ Kept: {file_path}")
        else:
            print(f"📝 Not found: {file_path}")
    
    print(f"\n📊 Reset Summary:")
    print(f"   • Files removed: {removed_count}")
    print(f"   • Files modified: {modified_count}")
    print(f"   • Technical setup preserved")
    
    print(f"\n🎯 Result:")
    print(f"   • setup_sam.py completion: ✅ Preserved")
    print(f"   • Welcome page completion: ❌ Reset")
    print(f"   • Next start_sam.py should open: localhost:8503")
    
    return True

def show_current_status():
    """Show current setup status."""
    print("\n🔍 Current Setup Status:")
    
    status_files = {
        "setup_status.json": "Welcome page completion",
        "security/keystore.json": "Security setup",
        "sam_pro_key.txt": "SAM Pro key (technical setup)",
        "security/entitlements.json": "Entitlements (technical setup)"
    }
    
    for file_path, description in status_files.items():
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path} - {description}")
            
            # Show relevant content
            if file_path == "setup_status.json":
                try:
                    with open(path, 'r') as f:
                        content = json.load(f)
                    master_pwd = content.get('master_password_created', False)
                    print(f"      📄 master_password_created: {master_pwd}")
                except:
                    print(f"      ⚠️  Could not read content")
                    
            elif file_path == "security/keystore.json":
                try:
                    with open(path, 'r') as f:
                        content = json.load(f)
                    has_password = 'password_hash' in content
                    print(f"      📄 has_password_hash: {has_password}")
                except:
                    print(f"      ⚠️  Could not read content")
                    
        else:
            print(f"   ❌ {file_path} - {description} (Missing)")

def main():
    """Main reset function."""
    print("🚀 Setup Status Reset Tool\n")
    
    # Show current status
    show_current_status()
    
    # Ask for confirmation
    print("\n" + "=" * 40)
    response = input("Reset setup status to first-time user? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print()
        success = reset_setup_status()
        
        if success:
            print("\n✅ Reset complete!")
            print("\n🧪 Test the detection:")
            print("   python test_first_time_detection.py")
            print("\n🚀 Test the routing:")
            print("   python start_sam.py")
            print("   (Should open localhost:8503)")
        else:
            print("\n❌ Reset failed!")
    else:
        print("\n🚫 Reset cancelled")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Reset cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Make sure you're in the SAM directory")
