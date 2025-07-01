"""
SAM Security Module

Provides enterprise-grade security features for SAM including:
- AES-256-GCM authenticated encryption
- Argon2id key derivation
- Secure keystore management
- Session management with automatic timeout
- Security UI components

Author: SAM Development Team
Version: 2.0.0
"""

from .secure_state_manager import SecureStateManager, SecurityState
from .security_ui import create_security_ui
from .crypto_utils import CryptoManager
from .keystore_manager import KeystoreManager
from .encrypted_chroma_store import EncryptedChromaStore

__all__ = [
    'SecureStateManager',
    'SecurityState',
    'create_security_ui',
    'CryptoManager',
    'KeystoreManager',
    'EncryptedChromaStore'
]
