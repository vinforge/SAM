"""
SAM Secure Enclave - Core Cryptographic Utilities

Implements enterprise-grade encryption using AES-256-GCM with authenticated encryption.
Provides secure data encryption/decryption for SAM's knowledge base.

Security Features:
- AES-256-GCM authenticated encryption
- Random nonce generation for each encryption
- Secure memory handling
- Comprehensive error handling

Author: SAM Development Team
Version: 1.0.0
"""

import os
import json
import secrets
import logging
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# Configure logging
logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Base exception for security-related errors"""
    pass

class EncryptionError(SecurityError):
    """Raised when encryption operations fail"""
    pass

class DecryptionError(SecurityError):
    """Raised when decryption operations fail"""
    pass

class SAMCrypto:
    """
    Core cryptographic engine for SAM Secure Enclave.
    
    Provides AES-256-GCM authenticated encryption with secure key management.
    All encryption operations use random nonces and include authentication tags
    to prevent tampering.
    """
    
    def __init__(self):
        self.session_key: Optional[bytes] = None
        self._aes_gcm: Optional[AESGCM] = None
        
    def set_session_key(self, key: bytes) -> None:
        """
        Set the session encryption key.
        
        Args:
            key: 256-bit (32-byte) encryption key
            
        Raises:
            SecurityError: If key is invalid
        """
        if not isinstance(key, bytes):
            raise SecurityError("Session key must be bytes")
        
        if len(key) != 32:
            raise SecurityError("Session key must be 256 bits (32 bytes)")
        
        self.session_key = key
        self._aes_gcm = AESGCM(key)
        logger.info("Session key set successfully")
    
    def clear_session_key(self) -> None:
        """
        Securely clear the session key from memory.
        """
        if self.session_key:
            # Overwrite key memory with random data
            self.session_key = secrets.token_bytes(32)
            self.session_key = None
        
        self._aes_gcm = None
        logger.info("Session key cleared from memory")
    
    def is_unlocked(self) -> bool:
        """
        Check if the crypto engine is unlocked (has a session key).
        
        Returns:
            True if session key is available, False otherwise
        """
        return self.session_key is not None
    
    def encrypt_data(self, plaintext: str) -> Dict[str, str]:
        """
        Encrypt plaintext data using AES-256-GCM.
        
        Args:
            plaintext: String data to encrypt
            
        Returns:
            Dictionary containing encrypted data and metadata:
            {
                'ciphertext': hex-encoded encrypted data,
                'nonce': hex-encoded nonce,
                'algorithm': 'AES-256-GCM',
                'version': '1.0'
            }
            
        Raises:
            SecurityError: If no session key is available
            EncryptionError: If encryption fails
        """
        if not self.is_unlocked():
            raise SecurityError("No session key available - application is locked")
        
        try:
            # Generate random 96-bit nonce for GCM
            nonce = os.urandom(12)
            
            # Encrypt with authenticated encryption
            ciphertext = self._aes_gcm.encrypt(nonce, plaintext.encode('utf-8'), None)
            
            return {
                'ciphertext': ciphertext.hex(),
                'nonce': nonce.hex(),
                'algorithm': 'AES-256-GCM',
                'version': '1.0'
            }
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Failed to encrypt data: {e}")
    
    def decrypt_data(self, encrypted_data: Dict[str, str]) -> str:
        """
        Decrypt data using AES-256-GCM.
        
        Args:
            encrypted_data: Dictionary containing encrypted data and metadata
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            SecurityError: If no session key is available
            DecryptionError: If decryption fails or data is tampered
        """
        if not self.is_unlocked():
            raise SecurityError("No session key available - application is locked")
        
        try:
            # Validate encrypted data format
            required_fields = ['ciphertext', 'nonce', 'algorithm']
            for field in required_fields:
                if field not in encrypted_data:
                    raise DecryptionError(f"Missing required field: {field}")
            
            # Verify algorithm
            if encrypted_data['algorithm'] != 'AES-256-GCM':
                raise DecryptionError(f"Unsupported algorithm: {encrypted_data['algorithm']}")
            
            # Extract ciphertext and nonce
            ciphertext = bytes.fromhex(encrypted_data['ciphertext'])
            nonce = bytes.fromhex(encrypted_data['nonce'])
            
            # Decrypt and authenticate
            plaintext_bytes = self._aes_gcm.decrypt(nonce, ciphertext, None)
            
            return plaintext_bytes.decode('utf-8')
            
        except InvalidTag:
            logger.error("Decryption failed: Authentication tag verification failed")
            raise DecryptionError("Data integrity check failed - data may be corrupted or tampered")
        except ValueError as e:
            logger.error(f"Decryption failed: Invalid data format - {e}")
            raise DecryptionError(f"Invalid encrypted data format: {e}")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise DecryptionError(f"Failed to decrypt data: {e}")
    
    def encrypt_json(self, data: Any) -> Dict[str, str]:
        """
        Encrypt JSON-serializable data.
        
        Args:
            data: Any JSON-serializable object
            
        Returns:
            Encrypted data dictionary
        """
        json_string = json.dumps(data, ensure_ascii=False)
        return self.encrypt_data(json_string)
    
    def decrypt_json(self, encrypted_data: Dict[str, str]) -> Any:
        """
        Decrypt and parse JSON data.
        
        Args:
            encrypted_data: Encrypted data dictionary
            
        Returns:
            Parsed JSON object
        """
        json_string = self.decrypt_data(encrypted_data)
        return json.loads(json_string)
