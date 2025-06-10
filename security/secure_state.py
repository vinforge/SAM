"""
SAM Secure Enclave - Secure State Management

Manages the application's security state including lock/unlock status,
session management, and automatic timeout handling.

Security Features:
- Secure session key management
- Automatic session timeout
- Thread-safe state management
- Comprehensive audit logging

Author: SAM Development Team
Version: 1.0.0
"""

import time
import threading
import logging
from enum import Enum
from typing import Optional, Callable
from .crypto_utils import SAMCrypto
from .key_manager import KeyManager, KeyDerivationError
from .keystore_manager import KeystoreManager, KeystoreError

# Configure logging
logger = logging.getLogger(__name__)

class ApplicationState(Enum):
    """Application security states"""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    SETUP_REQUIRED = "setup_required"
    ERROR = "error"

class SecureStateManager:
    """
    Manages SAM's security state and session lifecycle.
    
    Handles:
    - Application lock/unlock state
    - Session key management
    - Automatic timeout and locking
    - Password verification
    - Initial setup workflow
    """
    
    def __init__(self, session_timeout: int = 3600):
        """
        Initialize secure state manager.
        
        Args:
            session_timeout: Session timeout in seconds (default: 1 hour)
        """
        self.session_timeout = session_timeout
        self.state = ApplicationState.LOCKED
        self.unlock_timestamp: Optional[float] = None
        self.max_unlock_attempts = 5
        self.failed_attempts = 0
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Core security components
        self.crypto = SAMCrypto()
        self.key_manager = KeyManager()
        self.keystore_manager = KeystoreManager()
        
        # State change callbacks
        self._state_change_callbacks = []
        
        # Initialize state
        self._initialize_state()
        
        logger.info("Secure state manager initialized")
    
    def _initialize_state(self) -> None:
        """Initialize application state based on keystore existence."""
        try:
            if self.keystore_manager.is_first_run():
                self.state = ApplicationState.SETUP_REQUIRED
                logger.info("First run detected - setup required")
            else:
                self.state = ApplicationState.LOCKED
                logger.info("Existing keystore found - application locked")
        except Exception as e:
            logger.error(f"State initialization failed: {e}")
            self.state = ApplicationState.ERROR
    
    def get_state(self) -> ApplicationState:
        """
        Get current application state with timeout check.
        
        Returns:
            Current application state
        """
        with self._lock:
            # Check session timeout
            if (self.state == ApplicationState.UNLOCKED and 
                self.unlock_timestamp and 
                time.time() - self.unlock_timestamp > self.session_timeout):
                self._lock_application_internal()
                logger.info("Session timed out - application locked")
            
            return self.state
    
    def is_unlocked(self) -> bool:
        """
        Check if application is currently unlocked.
        
        Returns:
            True if unlocked, False otherwise
        """
        return self.get_state() == ApplicationState.UNLOCKED
    
    def is_setup_required(self) -> bool:
        """
        Check if initial setup is required.
        
        Returns:
            True if setup required, False otherwise
        """
        return self.get_state() == ApplicationState.SETUP_REQUIRED
    
    def setup_master_password(self, password: str) -> bool:
        """
        Initial setup: create master password and keystore.
        
        Args:
            password: Master password to set
            
        Returns:
            True if setup successful, False otherwise
        """
        with self._lock:
            if self.state != ApplicationState.SETUP_REQUIRED:
                logger.error("Setup attempted when not in setup state")
                return False
            
            try:
                # Validate password strength
                if not self._validate_password_strength(password):
                    logger.warning("Password failed strength validation")
                    return False
                
                # Generate salt
                salt = self.key_manager.generate_salt()
                
                # Derive key from password
                session_key = self.key_manager.derive_key_from_password(password, salt)
                
                # Create verifier hash
                verifier_hash = self.key_manager.create_verifier_hash(session_key)
                
                # Get KDF configuration
                kdf_config = self.key_manager.get_security_parameters()
                
                # Create keystore
                self.keystore_manager.create_keystore(salt, verifier_hash, kdf_config)
                
                # Set session key and unlock
                self.crypto.set_session_key(session_key)
                self.state = ApplicationState.UNLOCKED
                self.unlock_timestamp = time.time()
                self.failed_attempts = 0
                
                # Record successful setup
                self.keystore_manager.update_unlock_attempt(True)
                
                # Notify state change
                self._notify_state_change(ApplicationState.UNLOCKED)
                
                logger.info("Master password setup completed successfully")
                return True
                
            except (KeyDerivationError, KeystoreError) as e:
                logger.error(f"Setup failed: {e}")
                self.state = ApplicationState.ERROR
                return False
            except Exception as e:
                logger.error(f"Unexpected setup error: {e}")
                self.state = ApplicationState.ERROR
                return False
    
    def unlock_application(self, password: str) -> bool:
        """
        Unlock application with master password.
        
        Args:
            password: Master password
            
        Returns:
            True if unlock successful, False otherwise
        """
        with self._lock:
            if self.state not in [ApplicationState.LOCKED, ApplicationState.ERROR]:
                logger.warning(f"Unlock attempted in invalid state: {self.state}")
                return False
            
            # Check for too many failed attempts
            if self.failed_attempts >= self.max_unlock_attempts:
                logger.error("Too many failed unlock attempts")
                return False
            
            try:
                # Load keystore
                keystore_data = self.keystore_manager.load_keystore()
                
                # Extract salt and verifier
                salt = bytes.fromhex(keystore_data['salt'])
                stored_verifier = keystore_data['verifier_hash'].replace('sha256:', '')
                
                # Verify password
                verification_success, derived_key = self.key_manager.verify_password(
                    password, salt, stored_verifier
                )
                
                if verification_success:
                    # Set session key and unlock
                    self.crypto.set_session_key(derived_key)
                    self.state = ApplicationState.UNLOCKED
                    self.unlock_timestamp = time.time()
                    self.failed_attempts = 0
                    
                    # Record successful unlock
                    self.keystore_manager.update_unlock_attempt(True)
                    
                    # Notify state change
                    self._notify_state_change(ApplicationState.UNLOCKED)
                    
                    logger.info("Application unlocked successfully")
                    return True
                else:
                    # Failed unlock
                    self.failed_attempts += 1
                    self.keystore_manager.update_unlock_attempt(False)
                    
                    logger.warning(f"Unlock failed - attempt {self.failed_attempts}/{self.max_unlock_attempts}")
                    return False
                    
            except (KeyDerivationError, KeystoreError) as e:
                logger.error(f"Unlock failed: {e}")
                self.failed_attempts += 1
                return False
            except Exception as e:
                logger.error(f"Unexpected unlock error: {e}")
                self.failed_attempts += 1
                return False
    
    def lock_application(self) -> None:
        """
        Lock the application and clear session key.
        """
        with self._lock:
            self._lock_application_internal()
            logger.info("Application locked by user")
    
    def _lock_application_internal(self) -> None:
        """Internal method to lock application (no logging)."""
        # Clear session key from memory
        self.crypto.clear_session_key()
        
        # Update state
        self.state = ApplicationState.LOCKED
        self.unlock_timestamp = None
        
        # Notify state change
        self._notify_state_change(ApplicationState.LOCKED)
    
    def extend_session(self) -> None:
        """
        Extend the current session timeout.
        """
        with self._lock:
            if self.state == ApplicationState.UNLOCKED:
                self.unlock_timestamp = time.time()
                logger.debug("Session extended")
    
    def get_session_info(self) -> dict:
        """
        Get current session information.
        
        Returns:
            Dictionary containing session information
        """
        with self._lock:
            if self.state == ApplicationState.UNLOCKED and self.unlock_timestamp:
                time_remaining = self.session_timeout - (time.time() - self.unlock_timestamp)
                time_remaining = max(0, time_remaining)
            else:
                time_remaining = 0
            
            return {
                'state': self.state.value,
                'is_unlocked': self.is_unlocked(),
                'session_timeout': self.session_timeout,
                'time_remaining': int(time_remaining),
                'failed_attempts': self.failed_attempts,
                'max_attempts': self.max_unlock_attempts
            }
    
    def add_state_change_callback(self, callback: Callable[[ApplicationState], None]) -> None:
        """
        Add callback for state changes.
        
        Args:
            callback: Function to call when state changes
        """
        self._state_change_callbacks.append(callback)
    
    def _notify_state_change(self, new_state: ApplicationState) -> None:
        """Notify all callbacks of state change."""
        for callback in self._state_change_callbacks:
            try:
                callback(new_state)
            except Exception as e:
                logger.error(f"State change callback failed: {e}")
    
    def _validate_password_strength(self, password: str) -> bool:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            True if password meets requirements
        """
        if len(password) < 8:
            return False
        
        # Add more sophisticated password validation as needed
        return True
    
    def get_security_status(self) -> dict:
        """
        Get comprehensive security status.
        
        Returns:
            Dictionary containing security status
        """
        session_info = self.get_session_info()
        keystore_info = self.keystore_manager.get_security_info()
        kdf_params = self.key_manager.get_security_parameters()
        
        return {
            'session': session_info,
            'keystore': keystore_info,
            'kdf_parameters': kdf_params,
            'crypto_engine': {
                'is_unlocked': self.crypto.is_unlocked(),
                'algorithm': 'AES-256-GCM'
            }
        }
