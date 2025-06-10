"""
SAM Secure Enclave - Key Management

Implements secure key derivation using Argon2id for password-based encryption.
Provides enterprise-grade protection against brute force and timing attacks.

Security Features:
- Argon2id key derivation (winner of Password Hashing Competition)
- Configurable memory/time costs for future hardware scaling
- Secure random salt generation
- Timing attack protection

Author: SAM Development Team
Version: 1.0.0
"""

import secrets
import hashlib
import logging
from typing import Tuple
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from argon2.exceptions import VerifyMismatchError, HashingError

# Configure logging
logger = logging.getLogger(__name__)

class KeyDerivationError(Exception):
    """Raised when key derivation operations fail"""
    pass

class KeyManager:
    """
    Manages cryptographic key derivation and verification for SAM.
    
    Uses Argon2id with enterprise-grade parameters to derive encryption keys
    from user passwords. Provides protection against GPU/ASIC attacks and
    timing attacks.
    """
    
    # Enterprise-grade Argon2 parameters
    ARGON2_TIME_COST = 3        # 3 iterations
    ARGON2_MEMORY_COST = 65536  # 64MB memory usage
    ARGON2_PARALLELISM = 4      # 4 parallel threads
    ARGON2_HASH_LENGTH = 32     # 256-bit output
    ARGON2_SALT_LENGTH = 16     # 128-bit salt
    
    def __init__(self):
        self.password_hasher = PasswordHasher(
            time_cost=self.ARGON2_TIME_COST,
            memory_cost=self.ARGON2_MEMORY_COST,
            parallelism=self.ARGON2_PARALLELISM,
            hash_len=self.ARGON2_HASH_LENGTH,
            salt_len=self.ARGON2_SALT_LENGTH
        )
    
    def generate_salt(self) -> bytes:
        """
        Generate a cryptographically secure random salt.
        
        Returns:
            128-bit (16-byte) random salt
        """
        return secrets.token_bytes(self.ARGON2_SALT_LENGTH)
    
    def derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """
        Derive a 256-bit encryption key from a password using Argon2id.
        
        Args:
            password: User's master password
            salt: 128-bit random salt
            
        Returns:
            256-bit (32-byte) encryption key
            
        Raises:
            KeyDerivationError: If key derivation fails
        """
        if not isinstance(password, str):
            raise KeyDerivationError("Password must be a string")
        
        if not isinstance(salt, bytes):
            raise KeyDerivationError("Salt must be bytes")
        
        if len(salt) != self.ARGON2_SALT_LENGTH:
            raise KeyDerivationError(f"Salt must be {self.ARGON2_SALT_LENGTH} bytes")
        
        if len(password) == 0:
            raise KeyDerivationError("Password cannot be empty")
        
        try:
            # Derive key using Argon2id
            derived_key = hash_secret_raw(
                secret=password.encode('utf-8'),
                salt=salt,
                time_cost=self.ARGON2_TIME_COST,
                memory_cost=self.ARGON2_MEMORY_COST,
                parallelism=self.ARGON2_PARALLELISM,
                hash_len=self.ARGON2_HASH_LENGTH,
                type=Type.ID  # Argon2id (hybrid of Argon2i and Argon2d)
            )
            
            logger.info("Key derivation completed successfully")
            return derived_key
            
        except HashingError as e:
            logger.error(f"Argon2 hashing failed: {e}")
            raise KeyDerivationError(f"Key derivation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during key derivation: {e}")
            raise KeyDerivationError(f"Unexpected key derivation error: {e}")
    
    def create_verifier_hash(self, derived_key: bytes) -> str:
        """
        Create a verifier hash from a derived key for password verification.
        
        Args:
            derived_key: 256-bit derived encryption key
            
        Returns:
            SHA-256 hash of the derived key (hex-encoded)
            
        Raises:
            KeyDerivationError: If hash creation fails
        """
        if not isinstance(derived_key, bytes):
            raise KeyDerivationError("Derived key must be bytes")
        
        if len(derived_key) != self.ARGON2_HASH_LENGTH:
            raise KeyDerivationError(f"Derived key must be {self.ARGON2_HASH_LENGTH} bytes")
        
        try:
            verifier_hash = hashlib.sha256(derived_key).hexdigest()
            logger.info("Verifier hash created successfully")
            return verifier_hash
            
        except Exception as e:
            logger.error(f"Failed to create verifier hash: {e}")
            raise KeyDerivationError(f"Verifier hash creation failed: {e}")
    
    def verify_password(self, password: str, salt: bytes, stored_verifier: str) -> Tuple[bool, bytes]:
        """
        Verify a password against a stored verifier hash.
        
        Args:
            password: User-provided password
            salt: Stored salt used for key derivation
            stored_verifier: Stored verifier hash (hex-encoded)
            
        Returns:
            Tuple of (verification_success, derived_key)
            - verification_success: True if password is correct
            - derived_key: The derived encryption key (if verification succeeds)
            
        Raises:
            KeyDerivationError: If verification process fails
        """
        try:
            # Derive key from provided password
            derived_key = self.derive_key_from_password(password, salt)
            
            # Create verifier hash from derived key
            computed_verifier = self.create_verifier_hash(derived_key)
            
            # Compare verifier hashes (constant-time comparison)
            verification_success = secrets.compare_digest(computed_verifier, stored_verifier)
            
            if verification_success:
                logger.info("Password verification successful")
                return True, derived_key
            else:
                logger.warning("Password verification failed")
                # Return dummy key for failed verification (security measure)
                dummy_key = secrets.token_bytes(32)
                return False, dummy_key
                
        except KeyDerivationError:
            # Re-raise key derivation errors
            raise
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            raise KeyDerivationError(f"Password verification failed: {e}")
    
    def estimate_derivation_time(self, password: str = "test_password") -> float:
        """
        Estimate key derivation time for performance monitoring.
        
        Args:
            password: Test password (default: "test_password")
            
        Returns:
            Estimated derivation time in seconds
        """
        import time
        
        try:
            salt = self.generate_salt()
            start_time = time.time()
            self.derive_key_from_password(password, salt)
            end_time = time.time()
            
            derivation_time = end_time - start_time
            logger.info(f"Key derivation time: {derivation_time:.3f} seconds")
            return derivation_time
            
        except Exception as e:
            logger.error(f"Failed to estimate derivation time: {e}")
            return 0.0
    
    def get_security_parameters(self) -> dict:
        """
        Get current Argon2 security parameters.
        
        Returns:
            Dictionary containing security parameters
        """
        return {
            'algorithm': 'Argon2id',
            'time_cost': self.ARGON2_TIME_COST,
            'memory_cost': self.ARGON2_MEMORY_COST,
            'memory_mb': self.ARGON2_MEMORY_COST // 1024,
            'parallelism': self.ARGON2_PARALLELISM,
            'hash_length': self.ARGON2_HASH_LENGTH,
            'salt_length': self.ARGON2_SALT_LENGTH,
            'estimated_security_level': '128-bit equivalent'
        }
