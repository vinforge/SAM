#!/usr/bin/env python3
"""
SAM Welcome & First-Time Setup Page
==================================

Dedicated first-time setup page that bypasses browser caching issues.
This ensures all new users get the proper welcome experience regardless
of browser cache state.

Usage: python -m streamlit run welcome_setup.py --server.port 8503
"""

import streamlit as st
import sys
import json
import uuid
import hashlib
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main welcome and setup application."""
    
    # Configure page
    st.set_page_config(
        page_title="Welcome to SAM!",
        page_icon="🚀",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for welcome page
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .setup-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .step-number {
        background: #4CAF50;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if setup is already complete
    if is_setup_complete():
        show_setup_complete_page()
        return
    
    # Show welcome and setup page
    show_welcome_setup_page()

def is_setup_complete():
    """Check if SAM setup is already complete."""
    try:
        # Check for security setup
        from security import SecureStateManager
        security_manager = SecureStateManager()
        
        # If security is already configured, setup is complete
        if not security_manager.is_setup_required():
            return True
            
    except ImportError:
        pass
    except Exception:
        pass
    
    # Check setup status file
    try:
        setup_file = Path("setup_status.json")
        if setup_file.exists():
            with open(setup_file, 'r') as f:
                status = json.load(f)
            
            # Check if master password is created
            if status.get('master_password_created', False):
                return True
                
    except Exception:
        pass
    
    return False

def show_setup_complete_page():
    """Show page for users who have already completed setup."""
    
    st.markdown('<h1 class="main-header">🎉 Welcome Back to SAM!</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your setup is already complete</p>', unsafe_allow_html=True)
    
    st.success("✅ **Setup Complete!** Your SAM installation is ready to use.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🚀 Access SAM")
        
        if st.button("🧠 Open SAM Chat Interface", type="primary", use_container_width=True):
            st.markdown("""
            <script>
            window.open('http://localhost:8502', '_blank');
            </script>
            """, unsafe_allow_html=True)
            st.info("Opening SAM in a new tab...")
        
        st.markdown("---")
        
        st.markdown("### 📋 Quick Access")
        st.markdown("• **Main Chat**: http://localhost:8502")
        st.markdown("• **Memory Center**: Access via main chat interface")
        st.markdown("• **Dream Canvas**: Available in Memory Center")
        
        st.markdown("---")
        
        if st.button("🔄 Re-run Setup (Advanced)", use_container_width=True):
            if st.checkbox("I understand this will reset my SAM configuration"):
                reset_setup()
                st.rerun()

def show_welcome_setup_page():
    """Show the main welcome and setup page."""
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Welcome to SAM!</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Let\'s get you set up in just a few steps</p>', unsafe_allow_html=True)
    
    # Welcome container
    st.markdown("""
    <div class="setup-container">
        <h2>🧠 SAM - Synthetic Autonomous Mind</h2>
        <p>You're about to experience the world's most advanced AI system with:</p>
        <ul>
            <li>🔒 <strong>Enterprise-grade security</strong> with zero-knowledge encryption</li>
            <li>🧠 <strong>Human-like reasoning</strong> with Test-Time Training</li>
            <li>🎨 <strong>Dream Canvas</strong> for cognitive visualization</li>
            <li>🔬 <strong>Automated research</strong> discovery and analysis</li>
            <li>📚 <strong>Lifelong learning</strong> with encrypted memory</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Setup steps
    st.markdown("### 📋 Setup Steps")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown('<div class="step-number">1</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("**Create Master Password** - Secures all your data with military-grade encryption")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<div class="step-number">2</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("**Activate SAM Pro** - Unlock advanced features like Dream Canvas and TPV")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<div class="step-number">3</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("**Start Chatting** - Begin your journey with SAM's revolutionary AI")
    
    st.markdown("---")
    
    # Master password setup
    st.markdown("### 🔐 Step 1: Create Your Master Password")
    st.info("💡 **Important**: This password encrypts all your data. Choose something secure that you'll remember!")
    
    with st.form("master_password_form"):
        password = st.text_input("Master Password", type="password", help="Minimum 8 characters recommended")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        # Password strength indicator
        if password:
            strength = check_password_strength(password)
            if strength == "Strong":
                st.success(f"✅ Password strength: {strength}")
            elif strength == "Medium":
                st.warning(f"⚠️ Password strength: {strength}")
            else:
                st.error(f"❌ Password strength: {strength}")
        
        submitted = st.form_submit_button("🔐 Create Master Password", type="primary")
        
        if submitted:
            if not password:
                st.error("❌ Please enter a password")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            else:
                # Create master password
                with st.spinner("🔐 Setting up encryption..."):
                    success = create_master_password(password)
                    
                if success:
                    st.success("✅ Master password created successfully!")
                    
                    # Generate SAM Pro key
                    sam_pro_key = generate_sam_pro_key()
                    
                    # Update setup status
                    update_setup_status({
                        'master_password_created': True,
                        'sam_pro_key': sam_pro_key,
                        'setup_timestamp': datetime.now().isoformat()
                    })
                    
                    # Show success and next steps
                    show_setup_success(sam_pro_key)
                else:
                    st.error("❌ Failed to create master password. Please try again.")

def check_password_strength(password):
    """Check password strength."""
    if len(password) < 6:
        return "Weak"
    elif len(password) < 10:
        return "Medium"
    else:
        return "Strong"

def create_master_password(password):
    """Create master password and initialize security."""
    try:
        from security import SecureStateManager
        security_manager = SecureStateManager()
        
        # Initialize security with the password
        success = security_manager.initialize_security(password)
        return success
        
    except ImportError:
        # Security module not available, create basic setup
        try:
            # Create a basic keystore file to indicate setup completion
            keystore_dir = Path("security")
            keystore_dir.mkdir(exist_ok=True)
            
            keystore_file = keystore_dir / "keystore.json"
            keystore_data = {
                "initialized": True,
                "created_at": datetime.now().isoformat(),
                "password_hash": hashlib.sha256(password.encode()).hexdigest()
            }
            
            with open(keystore_file, 'w') as f:
                json.dump(keystore_data, f, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"Setup error: {e}")
            return False
            
    except Exception as e:
        st.error(f"Security initialization error: {e}")
        return False

def generate_sam_pro_key():
    """Generate a SAM Pro activation key."""
    return str(uuid.uuid4())

def update_setup_status(status_update):
    """Update setup status file."""
    try:
        setup_file = Path("setup_status.json")
        
        # Load existing status
        if setup_file.exists():
            with open(setup_file, 'r') as f:
                status = json.load(f)
        else:
            status = {}
        
        # Update with new status
        status.update(status_update)
        
        # Save updated status
        with open(setup_file, 'w') as f:
            json.dump(status, f, indent=2)
            
        # Also save SAM Pro key to separate file for compatibility
        if 'sam_pro_key' in status_update:
            key_file = Path("sam_pro_key.txt")
            with open(key_file, 'w') as f:
                f.write(status_update['sam_pro_key'])
                
    except Exception as e:
        st.error(f"Failed to update setup status: {e}")

def show_setup_success(sam_pro_key):
    """Show setup success page with next steps."""
    
    st.balloons()
    
    st.markdown("---")
    st.markdown("### 🎉 Setup Complete!")
    
    # SAM Pro key display
    st.markdown("### 🔑 Your SAM Pro Activation Key")
    st.code(sam_pro_key, language=None)
    st.warning("💾 **Important**: Save this key! You'll need it to access SAM Pro features.")
    
    # Next steps
    st.markdown("### 🚀 Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧠 Open SAM Chat", type="primary", use_container_width=True):
            st.markdown("""
            <script>
            window.open('http://localhost:8502', '_blank');
            </script>
            """, unsafe_allow_html=True)
            st.success("Opening SAM in a new tab...")
    
    with col2:
        if st.button("📋 Copy Activation Key", use_container_width=True):
            st.code(sam_pro_key)
            st.info("Key displayed above - copy and save it!")
    
    st.markdown("---")
    
    st.markdown("### 📚 What's Next?")
    st.markdown("""
    1. **Open SAM Chat** using the button above
    2. **Enter your master password** when prompted
    3. **Enter your SAM Pro key** to unlock advanced features
    4. **Start chatting** with SAM and explore its capabilities!
    
    **Pro Features Unlocked:**
    - 🎨 **Dream Canvas** - Interactive memory visualization
    - 🧠 **TPV Active Reasoning** - Advanced reasoning control
    - 🧠 **Test-Time Training** - Cognitive adaptation
    - 📁 **Cognitive Automation** - Bulk document processing
    - 🔬 **Advanced Analytics** - Comprehensive insights
    """)

def reset_setup():
    """Reset setup status (advanced users only)."""
    try:
        # Remove setup files
        files_to_remove = [
            "setup_status.json",
            "sam_pro_key.txt",
            "security/keystore.json"
        ]
        
        for file_path in files_to_remove:
            path = Path(file_path)
            if path.exists():
                path.unlink()
        
        st.success("✅ Setup reset complete. Please refresh the page.")
        
    except Exception as e:
        st.error(f"Failed to reset setup: {e}")

if __name__ == "__main__":
    main()
