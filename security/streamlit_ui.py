"""
SAM Secure Enclave - Streamlit UI Components

Provides secure UI components for password entry, application unlock,
and security status display in Streamlit.

Security Features:
- Secure password input with masking
- Session state management
- Security status dashboard
- Key ceremony workflow

Author: SAM Development Team
Version: 1.0.0
"""

import streamlit as st
import time
from typing import Optional, Callable
from .secure_state import SecureStateManager, ApplicationState

class SAMSecurityUI:
    """
    Streamlit UI components for SAM security features.
    
    Provides a complete security interface including:
    - Initial setup workflow
    - Password unlock interface
    - Security status dashboard
    - Session management
    """
    
    def __init__(self, state_manager: SecureStateManager):
        """
        Initialize security UI.
        
        Args:
            state_manager: SecureStateManager instance
        """
        self.state_manager = state_manager
        
        # Initialize session state
        if 'security_initialized' not in st.session_state:
            st.session_state.security_initialized = True
            st.session_state.unlock_attempts = 0
            st.session_state.last_unlock_attempt = None
    
    def render_security_interface(self) -> bool:
        """
        Render the main security interface based on current state.
        
        Returns:
            True if application is unlocked, False if locked/setup required
        """
        current_state = self.state_manager.get_state()
        
        if current_state == ApplicationState.SETUP_REQUIRED:
            return self._render_setup_interface()
        elif current_state == ApplicationState.LOCKED:
            return self._render_unlock_interface()
        elif current_state == ApplicationState.UNLOCKED:
            self._render_security_status()
            return True
        else:  # ERROR state
            self._render_error_interface()
            return False
    
    def _render_setup_interface(self) -> bool:
        """Render initial setup interface."""
        st.markdown("# 🔐 SAM Secure Enclave Setup")
        st.markdown("---")
        
        st.markdown("""
        ### Welcome to SAM's Secure Enclave
        
        This is your first time running SAM with security enabled. You need to create a **Master Password** 
        that will protect all your data with enterprise-grade encryption.
        
        #### 🔒 What happens next:
        - Your password will be used to derive a 256-bit encryption key
        - All your documents and memories will be encrypted with AES-256-GCM
        - Your password is never stored - only a secure hash for verification
        - You'll need this password every time you start SAM
        
        #### ⚠️ Important Security Notes:
        - **Choose a strong password** - it protects all your data
        - **Remember your password** - it cannot be recovered if lost
        - **Keep it secure** - anyone with this password can access your data
        """)
        
        st.markdown("---")
        
        with st.form("setup_form"):
            st.markdown("### 🔑 Create Master Password")
            
            password = st.text_input(
                "Master Password",
                type="password",
                placeholder="Enter a strong master password...",
                help="Minimum 8 characters. Use a mix of letters, numbers, and symbols."
            )
            
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your master password...",
                help="Must match the password above."
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                setup_button = st.form_submit_button(
                    "🚀 Initialize SAM Secure Enclave",
                    use_container_width=True
                )
        
        if setup_button:
            if not password:
                st.error("❌ Please enter a password")
                return False
            
            if len(password) < 8:
                st.error("❌ Password must be at least 8 characters long")
                return False
            
            if password != confirm_password:
                st.error("❌ Passwords do not match")
                return False
            
            # Show progress
            with st.spinner("🔐 Initializing secure enclave..."):
                success = self.state_manager.setup_master_password(password)
            
            if success:
                st.success("✅ SAM Secure Enclave initialized successfully!")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to initialize secure enclave. Please try again.")
        
        return False
    
    def _render_unlock_interface(self) -> bool:
        """Render unlock interface."""
        st.markdown("# 🔒 SAM is Locked")
        st.markdown("---")
        
        session_info = self.state_manager.get_session_info()
        
        # Show security status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔐 Status", "LOCKED", delta="Secure")
        with col2:
            st.metric("🔑 Failed Attempts", session_info['failed_attempts'], 
                     delta=f"Max: {session_info['max_attempts']}")
        with col3:
            st.metric("🛡️ Security Level", "Enterprise", delta="AES-256")
        
        st.markdown("---")
        
        # Check for too many attempts
        if session_info['failed_attempts'] >= session_info['max_attempts']:
            st.error(f"🚫 Too many failed attempts ({session_info['failed_attempts']}/{session_info['max_attempts']})")
            st.markdown("Please restart the application to try again.")
            return False
        
        with st.form("unlock_form"):
            st.markdown("### 🔓 Enter Master Password")
            
            password = st.text_input(
                "Master Password",
                type="password",
                placeholder="Enter your master password...",
                help="The password you created during initial setup."
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                unlock_button = st.form_submit_button(
                    "🔓 Unlock SAM",
                    use_container_width=True
                )
        
        if unlock_button:
            if not password:
                st.error("❌ Please enter your password")
                return False
            
            # Show progress
            with st.spinner("🔐 Verifying password..."):
                success = self.state_manager.unlock_application(password)
            
            if success:
                st.success("✅ SAM unlocked successfully!")
                st.session_state.unlock_attempts = 0
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")
                st.session_state.unlock_attempts += 1
                st.session_state.last_unlock_attempt = time.time()
        
        return False
    
    def _render_security_status(self) -> None:
        """Render security status for unlocked state."""
        # Compact security status in sidebar
        with st.sidebar:
            st.markdown("### 🔐 Security Status")
            
            session_info = self.state_manager.get_session_info()
            
            # Status indicator
            st.success("🔓 UNLOCKED")
            
            # Session time remaining
            time_remaining = session_info['time_remaining']
            if time_remaining > 0:
                minutes = time_remaining // 60
                seconds = time_remaining % 60
                st.info(f"⏱️ Session: {minutes}m {seconds}s")
            else:
                st.warning("⏱️ Session expired")
            
            # Lock button
            if st.button("🔒 Lock SAM", use_container_width=True, key="security_lock_button"):
                self.state_manager.lock_application()
                st.rerun()

            # Extend session button
            if st.button("⏱️ Extend Session", use_container_width=True, key="security_extend_session_button"):
                self.state_manager.extend_session()
                st.success("Session extended!")
                time.sleep(1)
                st.rerun()
    
    def _render_error_interface(self) -> bool:
        """Render error interface."""
        st.error("🚨 Security System Error")
        st.markdown("""
        There was an error with the security system. This could be due to:
        - Corrupted keystore file
        - File permission issues
        - System configuration problems

        Please check the logs and restart the application.
        """)

        # Debug information
        with st.expander("🔧 Debug Information", expanded=False):
            try:
                current_state = self.state_manager.get_state()
                st.write(f"**Current State:** {current_state}")

                session_info = self.state_manager.get_session_info()
                st.write("**Session Info:**")
                st.json(session_info)

                # Check keystore
                import os
                keystore_path = "security/keystore.json"
                if os.path.exists(keystore_path):
                    st.write(f"**Keystore exists:** ✅ {keystore_path}")
                    stat = os.stat(keystore_path)
                    st.write(f"**Keystore size:** {stat.st_size} bytes")
                    st.write(f"**Keystore permissions:** {oct(stat.st_mode)[-3:]}")
                else:
                    st.write(f"**Keystore exists:** ❌ {keystore_path}")

            except Exception as e:
                st.write(f"**Debug Error:** {e}")
                import traceback
                st.code(traceback.format_exc())

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Initialization", key="security_retry_init_button"):
                st.rerun()

        with col2:
            if st.button("🔧 Reset Security System", key="security_reset_button"):
                st.warning("⚠️ This will delete all encrypted data!")
                if st.button("⚠️ Confirm Reset", key="security_reset_confirm"):
                    try:
                        # Reset security system
                        import shutil
                        from pathlib import Path

                        # Remove keystore
                        keystore_path = Path("security/keystore.json")
                        if keystore_path.exists():
                            keystore_path.unlink()

                        # Remove encrypted data directories
                        for dir_name in ["memory_store", "chroma_db", "sam_secure_memory"]:
                            dir_path = Path(dir_name)
                            if dir_path.exists():
                                shutil.rmtree(dir_path)

                        st.success("✅ Security system reset! Please refresh the page.")

                    except Exception as e:
                        st.error(f"❌ Reset failed: {e}")

        return False
    
    def render_security_dashboard(self) -> None:
        """Render detailed security dashboard."""
        if not self.state_manager.is_unlocked():
            st.warning("🔒 Security dashboard requires unlocked state")
            return
        
        st.markdown("# 🛡️ SAM Security Dashboard")
        st.markdown("---")
        
        # Get comprehensive security status
        security_status = self.state_manager.get_security_status()
        
        # Session Information
        st.markdown("### 📊 Session Information")
        col1, col2, col3, col4 = st.columns(4)
        
        session = security_status['session']
        with col1:
            st.metric("Status", "🔓 UNLOCKED")
        with col2:
            st.metric("Time Remaining", f"{session['time_remaining']}s")
        with col3:
            st.metric("Session Timeout", f"{session['session_timeout']}s")
        with col4:
            st.metric("Failed Attempts", session['failed_attempts'])
        
        # Keystore Information
        st.markdown("### 🗄️ Keystore Information")
        keystore = security_status['keystore']
        
        col1, col2 = st.columns(2)
        with col1:
            st.json({
                "Version": keystore.get('version', 'Unknown'),
                "Created": keystore.get('created_at', 'Unknown'),
                "Algorithm": keystore.get('kdf_algorithm', 'Unknown'),
                "Installation ID": keystore.get('installation_id', 'Unknown')[:8] + "..."
            })
        
        with col2:
            st.json({
                "Unlock Attempts": keystore.get('unlock_attempt_count', 0),
                "Last Attempt": keystore.get('last_unlock_attempt', 'Never'),
                "Last Success": keystore.get('last_successful_unlock', 'Never')
            })
        
        # Cryptographic Parameters
        st.markdown("### 🔐 Cryptographic Parameters")
        kdf = security_status['kdf_parameters']
        crypto = security_status['crypto_engine']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Key Derivation (Argon2id)**")
            st.json({
                "Time Cost": kdf['time_cost'],
                "Memory Cost": f"{kdf['memory_mb']} MB",
                "Parallelism": kdf['parallelism'],
                "Security Level": kdf['estimated_security_level']
            })
        
        with col2:
            st.markdown("**Encryption (AES-256-GCM)**")
            st.json({
                "Algorithm": crypto['algorithm'],
                "Key Length": "256 bits",
                "Mode": "Galois/Counter Mode",
                "Authentication": "Built-in"
            })

def create_security_ui(state_manager: SecureStateManager) -> SAMSecurityUI:
    """
    Factory function to create SAM security UI.
    
    Args:
        state_manager: SecureStateManager instance
        
    Returns:
        SAMSecurityUI instance
    """
    return SAMSecurityUI(state_manager)
