"""
SAM Secure Enclave - Keystore Management

Manages secure storage of cryptographic metadata including salts and verifier hashes.
Implements secure file handling with proper permissions and audit trails.

Security Features:
- Secure file permissions (600 - owner read/write only)
- JSON-based keystore format with versioning
- Audit trail for security monitoring
- Cross-platform compatibility

Author: SAM Development Team
Version: 1.0.0
"""

import json
import os
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class KeystoreError(Exception):
    """Base exception for keystore-related errors"""
    pass

class KeystoreNotFoundError(KeystoreError):
    """Raised when keystore file is not found"""
    pass

class KeystoreCorruptedError(KeystoreError):
    """Raised when keystore file is corrupted or invalid"""
    pass

class KeystoreManager:
    """
    Manages the secure keystore file for SAM's cryptographic metadata.
    
    The keystore contains:
    - Salt for key derivation
    - Verifier hash for password verification
    - Security configuration parameters
    - Audit trail metadata
    
    The keystore file is stored with restricted permissions and never contains
    the actual encryption key.
    """
    
    KEYSTORE_VERSION = "1.0"
    DEFAULT_KEYSTORE_PATH = "security/keystore.json"
    
    def __init__(self, keystore_path: Optional[str] = None):
        """
        Initialize keystore manager.
        
        Args:
            keystore_path: Path to keystore file (default: security/keystore.json)
        """
        self.keystore_path = Path(keystore_path or self.DEFAULT_KEYSTORE_PATH)
        
        # Ensure security directory exists
        self.keystore_path.parent.mkdir(exist_ok=True, mode=0o700)
        
        logger.info(f"Keystore manager initialized: {self.keystore_path}")
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run (no keystore exists).
        
        Returns:
            True if keystore doesn't exist, False otherwise
        """
        exists = self.keystore_path.exists()
        logger.info(f"First run check: keystore exists = {exists}")
        return not exists
    
    def create_keystore(self, salt: bytes, verifier_hash: str, 
                       kdf_config: Optional[Dict[str, Any]] = None) -> None:
        """
        Create a new keystore with the provided cryptographic metadata.
        
        Args:
            salt: Random salt used for key derivation
            verifier_hash: SHA-256 hash of the derived key
            kdf_config: Key derivation function configuration
            
        Raises:
            KeystoreError: If keystore creation fails
        """
        if self.keystore_path.exists():
            raise KeystoreError("Keystore already exists - cannot overwrite")
        
        try:
            # Default KDF configuration
            if kdf_config is None:
                kdf_config = {
                    "algorithm": "argon2id",
                    "time_cost": 3,
                    "memory_cost": 65536,
                    "parallelism": 4,
                    "salt_length": 16,
                    "hash_length": 32
                }
            
            # Create keystore data structure
            keystore_data = {
                "version": self.KEYSTORE_VERSION,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "kdf_config": kdf_config,
                "salt": salt.hex(),
                "verifier_hash": f"sha256:{verifier_hash}",
                "metadata": {
                    "installation_id": str(uuid.uuid4()),
                    "first_setup_completed": True,
                    "last_unlock_attempt": None,
                    "unlock_attempt_count": 0,
                    "created_by": "SAM Secure Enclave v1.0"
                }
            }
            
            # Write keystore with atomic operation
            temp_path = self.keystore_path.with_suffix('.tmp')
            
            with open(temp_path, 'w') as f:
                json.dump(keystore_data, f, indent=2)
            
            # Atomic move to final location
            temp_path.replace(self.keystore_path)
            
            # Set secure file permissions (Unix/Linux/macOS)
            if os.name != 'nt':  # Not Windows
                os.chmod(self.keystore_path, 0o600)
            
            logger.info("Keystore created successfully")
            
        except Exception as e:
            # Clean up temporary file if it exists
            temp_path = self.keystore_path.with_suffix('.tmp')
            if temp_path.exists():
                temp_path.unlink()
            
            logger.error(f"Failed to create keystore: {e}")
            raise KeystoreError(f"Keystore creation failed: {e}")
    
    def load_keystore(self) -> Dict[str, Any]:
        """
        Load and validate keystore data.
        
        Returns:
            Dictionary containing keystore data
            
        Raises:
            KeystoreNotFoundError: If keystore file doesn't exist
            KeystoreCorruptedError: If keystore is invalid or corrupted
        """
        if not self.keystore_path.exists():
            raise KeystoreNotFoundError("Keystore file not found")
        
        try:
            with open(self.keystore_path, 'r') as f:
                keystore_data = json.load(f)
            
            # Validate keystore structure
            self._validate_keystore(keystore_data)
            
            logger.info("Keystore loaded successfully")
            return keystore_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Keystore JSON parsing failed: {e}")
            raise KeystoreCorruptedError(f"Keystore file is corrupted: {e}")
        except Exception as e:
            logger.error(f"Failed to load keystore: {e}")
            raise KeystoreError(f"Keystore loading failed: {e}")
    
    def _validate_keystore(self, keystore_data: Dict[str, Any]) -> None:
        """
        Validate keystore data structure and content.
        
        Args:
            keystore_data: Keystore data to validate
            
        Raises:
            KeystoreCorruptedError: If keystore is invalid
        """
        required_fields = ['version', 'salt', 'verifier_hash', 'kdf_config']
        
        for field in required_fields:
            if field not in keystore_data:
                raise KeystoreCorruptedError(f"Missing required field: {field}")
        
        # Validate version
        if keystore_data['version'] != self.KEYSTORE_VERSION:
            logger.warning(f"Keystore version mismatch: {keystore_data['version']} != {self.KEYSTORE_VERSION}")
        
        # Validate salt format
        try:
            salt_bytes = bytes.fromhex(keystore_data['salt'])
            if len(salt_bytes) != 16:  # 128-bit salt
                raise KeystoreCorruptedError("Invalid salt length")
        except ValueError:
            raise KeystoreCorruptedError("Invalid salt format")
        
        # Validate verifier hash format
        verifier = keystore_data['verifier_hash']
        if not verifier.startswith('sha256:') or len(verifier) != 71:  # 'sha256:' + 64 hex chars
            raise KeystoreCorruptedError("Invalid verifier hash format")
        
        logger.info("Keystore validation passed")
    
    def update_unlock_attempt(self, success: bool) -> None:
        """
        Update unlock attempt metadata.
        
        Args:
            success: Whether the unlock attempt was successful
            
        Raises:
            KeystoreError: If update fails
        """
        try:
            keystore_data = self.load_keystore()
            
            # Update metadata
            keystore_data["metadata"]["last_unlock_attempt"] = datetime.utcnow().isoformat() + "Z"
            keystore_data["metadata"]["unlock_attempt_count"] = keystore_data["metadata"].get("unlock_attempt_count", 0) + 1
            
            if success:
                keystore_data["metadata"]["last_successful_unlock"] = datetime.utcnow().isoformat() + "Z"
            
            # Write updated keystore
            temp_path = self.keystore_path.with_suffix('.tmp')
            
            with open(temp_path, 'w') as f:
                json.dump(keystore_data, f, indent=2)
            
            temp_path.replace(self.keystore_path)
            
            # Restore file permissions
            if os.name != 'nt':
                os.chmod(self.keystore_path, 0o600)
            
            logger.info(f"Unlock attempt recorded: success={success}")
            
        except Exception as e:
            logger.error(f"Failed to update unlock attempt: {e}")
            raise KeystoreError(f"Unlock attempt update failed: {e}")
    
    def get_security_info(self) -> Dict[str, Any]:
        """
        Get security information from keystore.
        
        Returns:
            Dictionary containing security information
        """
        try:
            keystore_data = self.load_keystore()
            
            return {
                'version': keystore_data['version'],
                'created_at': keystore_data['created_at'],
                'kdf_algorithm': keystore_data['kdf_config']['algorithm'],
                'installation_id': keystore_data['metadata']['installation_id'],
                'unlock_attempt_count': keystore_data['metadata'].get('unlock_attempt_count', 0),
                'last_unlock_attempt': keystore_data['metadata'].get('last_unlock_attempt'),
                'last_successful_unlock': keystore_data['metadata'].get('last_successful_unlock')
            }
            
        except Exception as e:
            logger.error(f"Failed to get security info: {e}")
            return {'error': str(e)}
    
    def backup_keystore(self, backup_path: str) -> None:
        """
        Create a backup of the keystore.
        
        Args:
            backup_path: Path for backup file
            
        Raises:
            KeystoreError: If backup fails
        """
        try:
            if not self.keystore_path.exists():
                raise KeystoreNotFoundError("No keystore to backup")
            
            backup_path_obj = Path(backup_path)
            backup_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy keystore to backup location
            import shutil
            shutil.copy2(self.keystore_path, backup_path_obj)
            
            # Set secure permissions on backup
            if os.name != 'nt':
                os.chmod(backup_path_obj, 0o600)
            
            logger.info(f"Keystore backed up to: {backup_path}")
            
        except Exception as e:
            logger.error(f"Keystore backup failed: {e}")
            raise KeystoreError(f"Backup failed: {e}")
