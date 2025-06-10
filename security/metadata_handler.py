"""
SAM Secure Enclave - Encrypted Metadata Handler

Implements hybrid metadata encryption for ChromaDB integration.
Separates searchable metadata from sensitive encrypted content.

Security Features:
- Hybrid encryption model (searchable + encrypted fields)
- JSON-based encrypted metadata blobs
- Configurable field classification
- Backward compatibility support

Author: SAM Development Team
Version: 1.0.0
"""

import json
import logging
from typing import Dict, Any, List, Set, Optional
from .crypto_utils import SAMCrypto, SecurityError, DecryptionError

# Configure logging
logger = logging.getLogger(__name__)

class MetadataHandlerError(Exception):
    """Base exception for metadata handler errors"""
    pass

class EncryptedMetadataHandler:
    """
    Handles hybrid metadata encryption for ChromaDB storage.
    
    Separates metadata into two categories:
    1. Unencrypted: Searchable/filterable fields (source_id, timestamps, etc.)
    2. Encrypted: Sensitive content fields (text_content, source_name, etc.)
    
    The encrypted fields are stored as a single encrypted JSON blob.
    """
    
    # Fields that remain unencrypted for searching/filtering
    UNENCRYPTED_FIELDS: Set[str] = {
        # Document identification
        'source_id',           # Unique document identifier
        'document_hash',       # SHA-256 hash of original document
        'document_type',       # pdf, docx, txt, etc.
        'chunk_id',           # Unique chunk identifier
        
        # Temporal data
        'created_at',         # When chunk was created
        'processed_at',       # When chunk was processed
        'last_accessed',      # For LRU cache management
        
        # Structural data
        'chunk_index',        # Position in document (0, 1, 2...)
        'chunk_size',         # Size in characters
        'page_number',        # Source page (if applicable)
        
        # Classification
        'content_type',       # text, code, table, image_caption
        'language',           # en, es, fr, etc.
        'importance_score',   # 0.0-1.0 relevance score
        'sam_memory_type',    # SAM-specific memory type (renamed to avoid conflicts)
        
        # Security metadata
        'encryption_version', # v1.0, v1.1, etc.
        'has_encrypted_content',  # Boolean flag
        'encrypted_fields'    # List of encrypted field names
    }
    
    # Fields that are encrypted for security
    ENCRYPTED_FIELDS: Set[str] = {
        # Content data
        'text_content',       # The actual chunk text
        'content_preview',    # First 100 characters
        'section_title',      # Document section/chapter title
        'section_hierarchy',  # [chapter, section, subsection]
        
        # Source information
        'source_name',        # Original filename
        'source_path',        # Full file path
        'author',             # Document author
        'title',              # Document title
        
        # Extracted entities
        'named_entities',     # People, places, organizations
        'keywords',           # Extracted keywords
        'topics',             # Topic classifications
        
        # User annotations
        'user_notes',         # User-added notes
        'user_tags',          # User-defined tags
        'user_rating'         # User relevance rating
    }
    
    def __init__(self, crypto_manager: SAMCrypto):
        """
        Initialize metadata handler.
        
        Args:
            crypto_manager: SAMCrypto instance for encryption/decryption
        """
        self.crypto = crypto_manager
        self.encryption_version = "1.0"
        
        logger.info("Encrypted metadata handler initialized")
    
    def prepare_metadata_for_storage(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Split metadata into encrypted and unencrypted portions for storage.
        
        Args:
            metadata: Original metadata dictionary
            
        Returns:
            Processed metadata with encrypted sensitive fields
            
        Raises:
            MetadataHandlerError: If encryption fails
        """
        try:
            # Separate metadata by encryption requirement
            unencrypted_meta = {}
            sensitive_meta = {}
            
            for key, value in metadata.items():
                if key in self.UNENCRYPTED_FIELDS:
                    unencrypted_meta[key] = value
                elif key in self.ENCRYPTED_FIELDS:
                    sensitive_meta[key] = value
                else:
                    # Default: encrypt unknown fields for safety
                    logger.debug(f"Unknown field '{key}' - encrypting for safety")
                    sensitive_meta[key] = value
            
            # Encrypt sensitive metadata as a single blob
            if sensitive_meta:
                try:
                    encrypted_blob = self.crypto.encrypt_json(sensitive_meta)
                    # Convert encrypted blob to JSON string for ChromaDB compatibility
                    unencrypted_meta['encrypted_metadata'] = json.dumps(encrypted_blob)
                    unencrypted_meta['encrypted_fields'] = json.dumps(list(sensitive_meta.keys()))
                except SecurityError as e:
                    logger.error(f"Failed to encrypt metadata: {e}")
                    raise MetadataHandlerError(f"Metadata encryption failed: {e}")
            
            # Add encryption metadata
            unencrypted_meta['encryption_version'] = self.encryption_version
            unencrypted_meta['has_encrypted_content'] = bool(sensitive_meta)

            # Ensure all metadata values are ChromaDB-compatible types
            sanitized_meta = self._sanitize_metadata_for_chromadb(unencrypted_meta)

            logger.debug(f"Metadata prepared: {len(sanitized_meta)} unencrypted, {len(sensitive_meta)} encrypted fields")
            return sanitized_meta
            
        except Exception as e:
            logger.error(f"Metadata preparation failed: {e}")
            raise MetadataHandlerError(f"Failed to prepare metadata: {e}")
    
    def restore_metadata_from_storage(self, stored_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt and restore full metadata from storage format.
        
        Args:
            stored_metadata: Metadata as stored in ChromaDB
            
        Returns:
            Full metadata with decrypted sensitive fields
            
        Raises:
            MetadataHandlerError: If decryption fails
        """
        try:
            # Start with unencrypted metadata
            full_metadata = stored_metadata.copy()
            
            # Decrypt sensitive metadata if present
            if stored_metadata.get('has_encrypted_content', False) and 'encrypted_metadata' in stored_metadata:
                try:
                    # Parse JSON string back to encrypted blob
                    encrypted_blob_str = stored_metadata['encrypted_metadata']
                    encrypted_blob = json.loads(encrypted_blob_str)
                    sensitive_metadata = self.crypto.decrypt_json(encrypted_blob)

                    # Merge decrypted metadata
                    full_metadata.update(sensitive_metadata)

                    logger.debug(f"Decrypted {len(sensitive_metadata)} sensitive fields")
                    
                except (SecurityError, DecryptionError) as e:
                    # Log decryption failure but don't crash
                    logger.error(f"Failed to decrypt metadata: {e}")
                    full_metadata['decryption_error'] = str(e)
                    full_metadata['decryption_failed'] = True
                except Exception as e:
                    logger.error(f"Unexpected decryption error: {e}")
                    full_metadata['decryption_error'] = str(e)
                    full_metadata['decryption_failed'] = True
            
            # Remove encryption artifacts from final metadata
            cleanup_fields = ['encrypted_metadata', 'encrypted_fields', 'has_encrypted_content', 'encryption_version']
            for field in cleanup_fields:
                full_metadata.pop(field, None)
            
            return full_metadata
            
        except Exception as e:
            logger.error(f"Metadata restoration failed: {e}")
            raise MetadataHandlerError(f"Failed to restore metadata: {e}")
    
    def get_searchable_fields(self) -> Set[str]:
        """
        Get list of fields that can be used in ChromaDB where filters.
        
        Returns:
            Set of searchable field names
        """
        return self.UNENCRYPTED_FIELDS.copy()
    
    def get_encrypted_fields(self) -> Set[str]:
        """
        Get list of fields that are encrypted.
        
        Returns:
            Set of encrypted field names
        """
        return self.ENCRYPTED_FIELDS.copy()
    
    def is_field_searchable(self, field_name: str) -> bool:
        """
        Check if a field can be used in ChromaDB where filters.
        
        Args:
            field_name: Name of the field to check
            
        Returns:
            True if field is searchable, False if encrypted
        """
        return field_name in self.UNENCRYPTED_FIELDS
    
    def validate_filter_query(self, where_filter: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate a ChromaDB where filter for searchable fields.
        
        Args:
            where_filter: ChromaDB where filter dictionary
            
        Returns:
            Dictionary with 'valid' and 'invalid' field lists
        """
        valid_fields = []
        invalid_fields = []
        
        def check_filter_fields(filter_dict: Dict[str, Any]) -> None:
            for key, value in filter_dict.items():
                if key.startswith('$'):  # Operator like $and, $or
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                check_filter_fields(item)
                elif isinstance(value, dict):
                    # Nested filter like {"field": {"$gte": value}}
                    if self.is_field_searchable(key):
                        valid_fields.append(key)
                    else:
                        invalid_fields.append(key)
                else:
                    # Simple filter like {"field": value}
                    if self.is_field_searchable(key):
                        valid_fields.append(key)
                    else:
                        invalid_fields.append(key)
        
        check_filter_fields(where_filter)
        
        return {
            'valid': list(set(valid_fields)),
            'invalid': list(set(invalid_fields))
        }
    
    def create_searchable_filter(self, where_filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a searchable filter by removing encrypted fields.
        
        Args:
            where_filter: Original where filter
            
        Returns:
            Modified filter with only searchable fields, or None if no valid fields
        """
        validation = self.validate_filter_query(where_filter)
        
        if validation['invalid']:
            logger.warning(f"Removing encrypted fields from filter: {validation['invalid']}")
        
        # Create new filter with only valid fields
        def filter_searchable_fields(filter_dict: Dict[str, Any]) -> Dict[str, Any]:
            filtered = {}
            for key, value in filter_dict.items():
                if key.startswith('$'):  # Operator
                    if isinstance(value, list):
                        filtered_list = []
                        for item in value:
                            if isinstance(item, dict):
                                filtered_item = filter_searchable_fields(item)
                                if filtered_item:  # Only add non-empty filters
                                    filtered_list.append(filtered_item)
                        if filtered_list:
                            filtered[key] = filtered_list
                elif self.is_field_searchable(key):
                    filtered[key] = value
            return filtered
        
        searchable_filter = filter_searchable_fields(where_filter)
        return searchable_filter if searchable_filter else None
    
    def _sanitize_metadata_for_chromadb(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata to ensure ChromaDB compatibility.

        Args:
            metadata: Raw metadata dictionary

        Returns:
            Sanitized metadata with ChromaDB-compatible types
        """
        sanitized = {}

        for key, value in metadata.items():
            # Skip None values
            if value is None:
                continue

            # Ensure key is a valid string (no reserved names)
            if key.startswith('_'):
                logger.warning(f"Skipping reserved field name: {key}")
                continue

            # Convert value to ChromaDB-compatible type
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, list):
                # Convert list to JSON string for ChromaDB
                sanitized[key] = json.dumps(value)
            elif isinstance(value, dict):
                # Convert dict to JSON string for ChromaDB
                sanitized[key] = json.dumps(value)
            else:
                # Convert other types to string
                sanitized[key] = str(value)

        return sanitized

    def get_field_classification(self) -> Dict[str, List[str]]:
        """
        Get complete field classification for documentation.

        Returns:
            Dictionary with field classifications
        """
        return {
            'unencrypted_searchable': sorted(list(self.UNENCRYPTED_FIELDS)),
            'encrypted_sensitive': sorted(list(self.ENCRYPTED_FIELDS)),
            'encryption_version': self.encryption_version
        }
