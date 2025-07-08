#!/usr/bin/env python3
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
        print("\n👋 Stopping SAM...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error starting SAM: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
