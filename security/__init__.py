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

# Core security components (always available)
from .secure_state_manager import SecureStateManager, SecurityState
from .crypto_utils import CryptoManager
from .keystore_manager import KeystoreManager

# Conditionally import components that require external dependencies
try:
    from .encrypted_chroma_store import EncryptedChromaStore
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False
    EncryptedChromaStore = None

try:
    from .security_ui import create_security_ui
    _UI_AVAILABLE = True
except ImportError:
    _UI_AVAILABLE = False
    create_security_ui = None

# Base exports (always available)
__all__ = [
    'SecureStateManager',
    'SecurityState',
    'CryptoManager',
    'KeystoreManager'
]

# Add optional components if available
if _CHROMA_AVAILABLE:
    __all__.append('EncryptedChromaStore')

if _UI_AVAILABLE:
    __all__.append('create_security_ui')
