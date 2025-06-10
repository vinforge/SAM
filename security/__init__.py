"""
SAM Secure Enclave - Security Module

This module provides enterprise-grade cryptographic security for SAM,
implementing zero-knowledge encryption for all sensitive user data.

Phase 1: Master Key & Encrypted Knowledge Base
- Key derivation using Argon2id
- AES-256-GCM authenticated encryption
- Secure session management
- Hybrid metadata encryption for ChromaDB

Author: SAM Development Team
Version: 1.0.0
Security Level: Enterprise Grade
"""

from .crypto_utils import SAMCrypto, SecurityError
from .key_manager import KeyManager, KeyDerivationError
from .keystore_manager import KeystoreManager, KeystoreError
from .secure_state import SecureStateManager, ApplicationState
from .metadata_handler import EncryptedMetadataHandler
from .encrypted_chroma_store import EncryptedChromaStore
from .streamlit_ui import SAMSecurityUI, create_security_ui

__version__ = "1.0.0"
__security_level__ = "enterprise"

# Security module exports
__all__ = [
    'SAMCrypto',
    'KeyManager',
    'KeystoreManager',
    'SecureStateManager',
    'EncryptedMetadataHandler',
    'EncryptedChromaStore',
    'SAMSecurityUI',
    'create_security_ui',
    'ApplicationState',
    'SecurityError',
    'KeyDerivationError',
    'KeystoreError'
]

# Security configuration constants
SECURITY_CONFIG = {
    'argon2': {
        'time_cost': 3,
        'memory_cost': 65536,  # 64MB
        'parallelism': 4,
        'salt_length': 16,
        'hash_length': 32
    },
    'aes_gcm': {
        'key_length': 32,      # 256-bit
        'nonce_length': 12,    # 96-bit for GCM
        'tag_length': 16       # 128-bit authentication tag
    },
    'session': {
        'timeout_seconds': 3600,  # 1 hour
        'auto_lock_enabled': True,
        'max_unlock_attempts': 5
    }
}
