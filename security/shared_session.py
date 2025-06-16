"""
SAM Secure Enclave - Shared Session Management

Manages shared session state across multiple SAM processes (ports 8501, 8502, 5001).
This enables cross-port authentication where unlocking at one port grants access to all.

Security Features:
- File-based session state sharing
- Automatic session timeout
- Thread-safe operations
- Secure session token management

Author: SAM Development Team
Version: 1.0.0
"""

import json
import time
import threading
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

class SharedSessionManager:
    """
    Manages shared session state across multiple SAM processes.
    
    This allows authentication at port 8502 to grant access to port 8501
    and other SAM interfaces.
    """
    
    def __init__(self, session_timeout: int = 3600):
        """
        Initialize shared session manager.
        
        Args:
            session_timeout: Session timeout in seconds (default: 1 hour)
        """
        self.session_timeout = session_timeout
        self.session_file = Path("security") / "shared_session.json"
        self._lock = threading.RLock()
        
        # Ensure security directory exists
        self.session_file.parent.mkdir(exist_ok=True)
        
        logger.info("Shared session manager initialized")
    
    def create_session(self, user_id: str = "sam_user") -> str:
        """
        Create a new shared session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session token
        """
        with self._lock:
            try:
                # Generate session token
                session_token = self._generate_session_token()
                
                # Create session data
                session_data = {
                    "session_token": session_token,
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "last_activity": datetime.utcnow().isoformat() + "Z",
                    "expires_at": (datetime.utcnow() + timedelta(seconds=self.session_timeout)).isoformat() + "Z",
                    "is_active": True,
                    "ports_accessed": [],
                    "metadata": {
                        "session_timeout": self.session_timeout,
                        "created_by": "SAM Secure Enclave"
                    }
                }
                
                # Write session file
                self._write_session_file(session_data)
                
                logger.info(f"Shared session created: {session_token[:8]}...")
                return session_token
                
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                raise
    
    def validate_session(self, session_token: Optional[str] = None) -> bool:
        """
        Validate if there's an active session.
        
        Args:
            session_token: Optional specific session token to validate
            
        Returns:
            True if session is valid, False otherwise
        """
        with self._lock:
            try:
                session_data = self._read_session_file()
                
                if not session_data:
                    return False
                
                # Check if session is active
                if not session_data.get("is_active", False):
                    return False
                
                # Check specific token if provided
                if session_token and session_data.get("session_token") != session_token:
                    return False
                
                # Check expiration
                expires_at = datetime.fromisoformat(session_data["expires_at"].replace("Z", "+00:00"))
                if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
                    # Session expired - invalidate it
                    self.invalidate_session()
                    logger.info("Session expired and invalidated")
                    return False
                
                # Update last activity
                self._update_last_activity()
                
                return True
                
            except Exception as e:
                logger.error(f"Session validation failed: {e}")
                return False
    
    def extend_session(self) -> bool:
        """
        Extend the current session timeout.
        
        Returns:
            True if session was extended, False otherwise
        """
        with self._lock:
            try:
                session_data = self._read_session_file()
                
                if not session_data or not session_data.get("is_active", False):
                    return False
                
                # Extend expiration
                new_expires_at = (datetime.utcnow() + timedelta(seconds=self.session_timeout)).isoformat() + "Z"
                session_data["expires_at"] = new_expires_at
                session_data["last_activity"] = datetime.utcnow().isoformat() + "Z"
                
                self._write_session_file(session_data)
                
                logger.debug("Session extended")
                return True
                
            except Exception as e:
                logger.error(f"Failed to extend session: {e}")
                return False
    
    def invalidate_session(self) -> None:
        """Invalidate the current session."""
        with self._lock:
            try:
                if self.session_file.exists():
                    self.session_file.unlink()
                    logger.info("Shared session invalidated")
            except Exception as e:
                logger.error(f"Failed to invalidate session: {e}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information.
        
        Returns:
            Dictionary containing session information
        """
        with self._lock:
            try:
                session_data = self._read_session_file()
                
                if not session_data:
                    return {
                        "is_active": False,
                        "session_exists": False
                    }
                
                # Calculate time remaining
                expires_at = datetime.fromisoformat(session_data["expires_at"].replace("Z", "+00:00"))
                time_remaining = (expires_at - datetime.utcnow().replace(tzinfo=expires_at.tzinfo)).total_seconds()
                time_remaining = max(0, time_remaining)
                
                return {
                    "is_active": session_data.get("is_active", False),
                    "session_exists": True,
                    "user_id": session_data.get("user_id"),
                    "created_at": session_data.get("created_at"),
                    "last_activity": session_data.get("last_activity"),
                    "time_remaining": int(time_remaining),
                    "session_timeout": session_data.get("metadata", {}).get("session_timeout", self.session_timeout),
                    "ports_accessed": session_data.get("ports_accessed", [])
                }
                
            except Exception as e:
                logger.error(f"Failed to get session info: {e}")
                return {
                    "is_active": False,
                    "session_exists": False,
                    "error": str(e)
                }
    
    def register_port_access(self, port: int) -> None:
        """
        Register that a specific port has been accessed.
        
        Args:
            port: Port number that was accessed
        """
        with self._lock:
            try:
                session_data = self._read_session_file()
                
                if session_data and session_data.get("is_active", False):
                    ports_accessed = session_data.get("ports_accessed", [])
                    if port not in ports_accessed:
                        ports_accessed.append(port)
                        session_data["ports_accessed"] = ports_accessed
                        session_data["last_activity"] = datetime.utcnow().isoformat() + "Z"
                        
                        self._write_session_file(session_data)
                        logger.debug(f"Registered access to port {port}")
                
            except Exception as e:
                logger.error(f"Failed to register port access: {e}")
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token."""
        # Combine timestamp, random UUID, and additional entropy
        timestamp = str(time.time())
        random_id = str(uuid.uuid4())
        entropy = str(uuid.uuid4())
        
        # Create hash
        token_data = f"{timestamp}:{random_id}:{entropy}"
        session_token = hashlib.sha256(token_data.encode()).hexdigest()
        
        return session_token
    
    def _read_session_file(self) -> Optional[Dict[str, Any]]:
        """Read session data from file."""
        try:
            if not self.session_file.exists():
                return None
            
            with open(self.session_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to read session file: {e}")
            return None
    
    def _write_session_file(self, session_data: Dict[str, Any]) -> None:
        """Write session data to file."""
        try:
            # Write to temporary file first
            temp_file = self.session_file.with_suffix('.tmp')
            
            with open(temp_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            # Atomic move
            temp_file.replace(self.session_file)
            
            # Set secure permissions (Unix only)
            if hasattr(os, 'chmod'):
                os.chmod(self.session_file, 0o600)
                
        except Exception as e:
            logger.error(f"Failed to write session file: {e}")
            raise
    
    def _update_last_activity(self) -> None:
        """Update last activity timestamp."""
        try:
            session_data = self._read_session_file()
            
            if session_data:
                session_data["last_activity"] = datetime.utcnow().isoformat() + "Z"
                self._write_session_file(session_data)
                
        except Exception as e:
            logger.error(f"Failed to update last activity: {e}")

# Global shared session manager instance
_shared_session_manager = None

def get_shared_session_manager() -> SharedSessionManager:
    """Get the global shared session manager instance."""
    global _shared_session_manager
    
    if _shared_session_manager is None:
        _shared_session_manager = SharedSessionManager()
    
    return _shared_session_manager
