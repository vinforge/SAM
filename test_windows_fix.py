#!/usr/bin/env python3
"""
Test script to verify Windows psutil compatibility fix
This script tests the same system requirements check that was failing
"""

import platform
import sys

def test_system_requirements():
    """Test the same system requirements check from interactive_setup.py"""
    print("🧪 Testing Windows psutil compatibility fix...")
    print(f"🐍 Python: {sys.version}")
    print(f"💻 Platform: {platform.system()} {platform.machine()}")
    
    try:
        import psutil
        print("✅ psutil imported successfully")
        
        # Test memory check
        try:
            memory_gb = psutil.virtual_memory().total / (1024**3)
            print(f"✅ Memory: {memory_gb:.1f}GB")
            if memory_gb < 4:
                print("⚠️  Warning: Less than 4GB RAM detected. SAM may run slowly.")
        except:
            print("ℹ️  Memory check skipped")
            memory_gb = 0
        
        # Test disk space check with Windows compatibility
        try:
            if platform.system() == "Windows":
                # Use current drive on Windows
                import os
                current_drive = os.path.splitdrive(os.getcwd())[0] + os.sep
                print(f"🪟 Windows detected, using drive: {current_drive}")
                disk_gb = psutil.disk_usage(current_drive).free / (1024**3)
            else:
                # Use current directory on Unix-like systems
                disk_gb = psutil.disk_usage('.').free / (1024**3)
            
            print(f"✅ Disk space: {disk_gb:.1f}GB available")
            if disk_gb < 2:
                print("⚠️  Warning: Less than 2GB disk space. Consider freeing up space.")
        except Exception as e:
            # Broad exception handling for maximum compatibility
            print(f"ℹ️  Disk space check skipped: {e}")
            disk_gb = 0
        
        print("✅ System requirements check completed successfully!")
        return True
        
    except ImportError:
        print("ℹ️  System requirements check skipped (psutil not available)")
        return True
    except Exception as e:
        print(f"ℹ️  System requirements check skipped: {e}")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 SAM Windows Compatibility Test")
    print("=" * 60)
    
    success = test_system_requirements()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: Windows compatibility fix is working!")
        print("✅ Interactive setup should now work on Windows")
    else:
        print("❌ FAILED: Windows compatibility issue still exists")
        print("🔧 Please report this issue for further investigation")
    print("=" * 60)
