"""
SAM Secure Memory Vector Store

Enhanced MemoryVectorStore with integrated encryption support.
Provides seamless transition between encrypted and unencrypted storage.

Author: SAM Development Team
Version: 1.0.0
"""

import logging
import time
from typing import Dict, List, Any, Optional
from .memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType, MemoryChunk, MemorySearchResult

logger = logging.getLogger(__name__)

class SecureMemoryVectorStore(MemoryVectorStore):
    """
    Enhanced MemoryVectorStore with encryption support.
    
    Provides backward compatibility while adding encryption capabilities.
    Automatically detects security state and routes operations accordingly.
    """
    
    def __init__(self, store_type: VectorStoreType = VectorStoreType.CHROMA,
                 storage_directory: str = "memory_store",
                 embedding_dimension: int = 384,
                 enable_encryption: bool = True,
                 security_manager=None):
        """
        Initialize secure memory vector store.

        Args:
            store_type: Type of vector store to use
            storage_directory: Directory for storing memory data
            embedding_dimension: Dimension of embedding vectors
            enable_encryption: Whether to enable encryption (default: True)
            security_manager: Optional existing security manager to use
        """
        self.encryption_enabled = enable_encryption
        self.security_manager = None
        self.encrypted_store = None
        self._encryption_available = False

        # Initialize security if enabled
        if enable_encryption:
            try:
                from security import SecureStateManager, EncryptedChromaStore

                # Use provided security manager or create new one
                if security_manager:
                    self.security_manager = security_manager
                    logger.info("🔗 Using provided security manager")
                else:
                    self.security_manager = SecureStateManager()
                    logger.info("🆕 Created new security manager")

                self._encryption_available = True

                # Initialize encrypted store if unlocked
                if self.security_manager.is_unlocked():
                    self.encrypted_store = EncryptedChromaStore(
                        collection_name="sam_secure_memory",
                        crypto_manager=self.security_manager.crypto
                    )
                    logger.info("✅ Encrypted storage initialized and ready")
                else:
                    logger.info("🔒 Encryption available but application is locked")

            except ImportError:
                logger.warning("⚠️ Security module not available - encryption disabled")
                self.encryption_enabled = False
            except Exception as e:
                logger.error(f"❌ Failed to initialize encryption: {e}")
                self.encryption_enabled = False
        
        # Initialize parent class (fallback storage)
        super().__init__(store_type, storage_directory, embedding_dimension)
        
        logger.info(f"Secure memory store initialized - Encryption: {'✅ Enabled' if self._is_encryption_active() else '❌ Disabled'}")
    
    def _is_encryption_active(self) -> bool:
        """Check if encryption is currently active."""
        return (self.encryption_enabled and 
                self._encryption_available and 
                self.security_manager and 
                self.security_manager.is_unlocked() and 
                self.encrypted_store is not None)
    
    def _ensure_encrypted_store(self) -> bool:
        """Ensure encrypted store is available and ready."""
        if not self.encryption_enabled or not self._encryption_available:
            return False
        
        if not self.security_manager:
            return False
        
        if not self.security_manager.is_unlocked():
            logger.warning("🔒 Cannot access encrypted storage - application is locked")
            return False
        
        if not self.encrypted_store:
            try:
                from security import EncryptedChromaStore
                self.encrypted_store = EncryptedChromaStore(
                    collection_name="sam_secure_memory",
                    crypto_manager=self.security_manager.crypto
                )
                logger.info("✅ Encrypted store initialized on demand")
            except Exception as e:
                logger.error(f"❌ Failed to initialize encrypted store: {e}")
                return False
        
        return True

    def activate_encryption(self) -> bool:
        """Activate encryption if security manager becomes unlocked."""
        if not self.encryption_enabled or not self._encryption_available:
            return False

        if not self.security_manager or not self.security_manager.is_unlocked():
            return False

        if self.encrypted_store is None:
            try:
                from security import EncryptedChromaStore
                self.encrypted_store = EncryptedChromaStore(
                    collection_name="sam_secure_memory",
                    crypto_manager=self.security_manager.crypto
                )
                logger.info("✅ Encryption activated - secure storage now available")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to activate encryption: {e}")
                return False

        return True

    def add_memory(self, content: str, memory_type: MemoryType, source: str,
                  tags: List[str] = None, importance_score: float = 0.5,
                  metadata: Dict[str, Any] = None) -> str:
        """
        Add memory with optional encryption.
        
        Args:
            content: Memory content
            memory_type: Type of memory
            source: Source of the memory
            tags: Optional tags
            importance_score: Importance score (0.0-1.0)
            metadata: Additional metadata
            
        Returns:
            Memory chunk ID
        """
        if self._is_encryption_active():
            return self._add_encrypted_memory(content, memory_type, source, tags, importance_score, metadata)
        else:
            # Fallback to regular storage
            logger.debug("Using fallback storage (encryption not active)")
            return super().add_memory(content, memory_type, source, tags, importance_score, metadata)
    
    def _add_encrypted_memory(self, content: str, memory_type: MemoryType, source: str,
                            tags: List[str] = None, importance_score: float = 0.5,
                            metadata: Dict[str, Any] = None) -> str:
        """Add memory to encrypted storage."""
        try:
            # Prepare metadata for encrypted storage
            encrypted_metadata = {
                'source_id': f"secure_{hash(content)%1000000:06d}",
                'document_type': self._extract_document_type(source),
                'source_name': self._extract_source_name(source),
                'sam_memory_type': memory_type.value if hasattr(memory_type, 'value') else str(memory_type),
                'importance_score': importance_score,
                'tags': tags or [],
                'source': source,
                'created_at': self._get_current_timestamp()
            }
            
            # Add original metadata
            if metadata:
                encrypted_metadata.update(metadata)
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            
            # Add to encrypted store
            chunk_id = self.encrypted_store.add_memory_chunk(
                chunk_text=content,
                metadata=encrypted_metadata,
                embedding=embedding
            )
            
            logger.debug(f"Added encrypted memory: {chunk_id}")
            return chunk_id
            
        except Exception as e:
            logger.error(f"Failed to add encrypted memory: {e}")
            # Fallback to regular storage
            return super().add_memory(content, memory_type, source, tags, importance_score, metadata)
    
    def search_memories(self, query: str, max_results: int = 5,
                       memory_types: List[MemoryType] = None,
                       tags: List[str] = None,
                       min_similarity: float = None,
                       where_filter: Optional[Dict[str, Any]] = None) -> List[MemorySearchResult]:
        """
        Search memories with optional decryption.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            memory_types: Optional filter by memory types
            tags: Optional filter by tags
            min_similarity: Minimum similarity threshold
            where_filter: Optional metadata filter
            
        Returns:
            List of memory search results
        """
        if self._is_encryption_active():
            return self._search_encrypted_memories(query, max_results, memory_types, tags, min_similarity, where_filter)
        else:
            # Fallback to regular search
            logger.debug("Using fallback search (encryption not active)")
            return super().search_memories(query, max_results, memory_types, tags, min_similarity, where_filter)
    
    def _search_encrypted_memories(self, query: str, max_results: int = 5,
                                 memory_types: List[MemoryType] = None,
                                 tags: List[str] = None,
                                 min_similarity: float = None,
                                 where_filter: Optional[Dict[str, Any]] = None) -> List[MemorySearchResult]:
        """Search encrypted memories."""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Prepare filter for encrypted store
            encrypted_filter = {}
            if memory_types:
                encrypted_filter['sam_memory_type'] = {'$in': [mt.value if hasattr(mt, 'value') else str(mt) for mt in memory_types]}
            
            if where_filter:
                encrypted_filter.update(where_filter)
            
            # Search encrypted store
            encrypted_results = self.encrypted_store.query_memories(
                query_embedding=query_embedding,
                n_results=max_results,
                where_filter=encrypted_filter if encrypted_filter else None
            )
            
            # Convert to MemorySearchResult format
            search_results = []
            for i, result in enumerate(encrypted_results):
                try:
                    # Create MemoryChunk from encrypted result
                    memory_chunk = MemoryChunk(
                        chunk_id=result['id'],
                        content=result['content'],
                        content_hash=hash(result['content']),
                        embedding=None,  # Not needed for results
                        memory_type=MemoryType(result['metadata'].get('sam_memory_type', 'conversation')),
                        source=result['metadata'].get('source', 'unknown'),
                        timestamp=result['metadata'].get('created_at', ''),
                        tags=result['metadata'].get('tags', []),
                        importance_score=result['metadata'].get('importance_score', 0.5),
                        access_count=0,
                        last_accessed=self._get_current_timestamp(),
                        metadata=result['metadata']
                    )
                    
                    # Create search result
                    search_result = MemorySearchResult(
                        chunk=memory_chunk,
                        similarity_score=1.0 - (result.get('distance', 0.0) if result.get('distance') else 0.0),
                        rank=i + 1
                    )
                    
                    # Apply additional filters
                    if tags and not any(tag in memory_chunk.tags for tag in tags):
                        continue
                    
                    if min_similarity and search_result.similarity_score < min_similarity:
                        continue
                    
                    search_results.append(search_result)
                    
                except Exception as e:
                    logger.warning(f"Failed to process encrypted search result: {e}")
                    continue
            
            logger.debug(f"Encrypted search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Encrypted search failed: {e}")
            # Fallback to regular search
            return super().search_memories(query, max_results, memory_types, tags, min_similarity, where_filter)
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security status information."""
        status = {
            'encryption_enabled': self.encryption_enabled,
            'encryption_available': self._encryption_available,
            'encryption_active': self._is_encryption_active(),
            'security_manager_initialized': self.security_manager is not None,
            'encrypted_store_ready': self.encrypted_store is not None
        }
        
        if self.security_manager:
            status.update({
                'application_state': self.security_manager.get_state().value,
                'is_unlocked': self.security_manager.is_unlocked(),
                'setup_required': self.security_manager.is_setup_required()
            })
        
        if self.encrypted_store:
            store_info = self.encrypted_store.get_collection_info()
            status.update({
                'encrypted_chunk_count': store_info.get('chunk_count', 0),
                'searchable_fields': len(store_info.get('searchable_fields', [])),
                'encrypted_fields': len(store_info.get('encrypted_fields', []))
            })
        
        return status
    
    def unlock_encryption(self, password: str) -> bool:
        """Unlock encryption with password."""
        if not self.security_manager:
            return False
        
        success = self.security_manager.unlock_application(password)
        if success:
            # Initialize encrypted store
            self._ensure_encrypted_store()
        
        return success
    
    def lock_encryption(self):
        """Lock encryption and clear sensitive data."""
        if self.security_manager:
            self.security_manager.lock_application()
        
        # Clear encrypted store reference
        self.encrypted_store = None
        logger.info("🔒 Encryption locked")
    
    def _extract_document_type(self, source: str) -> str:
        """Extract document type from source string."""
        if ':' in source:
            parts = source.split(':')
            if len(parts) > 1 and '.' in parts[1]:
                from pathlib import Path
                return Path(parts[1]).suffix.lower().replace('.', '')
        return 'unknown'
    
    def _extract_source_name(self, source: str) -> str:
        """Extract source name from source string."""
        if ':' in source:
            parts = source.split(':')
            if len(parts) > 1:
                from pathlib import Path
                return Path(parts[1]).name
        return source
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_all_memories(self) -> List[Any]:
        """Get all memories from the store."""
        try:
            all_memories = []

            # Try encrypted store first if available
            if self._is_encryption_active() and self.encrypted_store:
                try:
                    # Get all documents from encrypted ChromaDB
                    collection = self.encrypted_store.collection
                    if collection:
                        # Get all documents
                        results = collection.get()

                        if results and 'documents' in results:
                            for i, doc in enumerate(results['documents']):
                                # Create a memory-like object
                                memory_obj = type('Memory', (), {
                                    'content': doc,
                                    'source': results.get('metadatas', [{}])[i].get('source', 'unknown'),
                                    'timestamp': results.get('metadatas', [{}])[i].get('timestamp', time.time()),
                                    'memory_type': results.get('metadatas', [{}])[i].get('memory_type', 'document'),
                                    'importance_score': results.get('metadatas', [{}])[i].get('importance_score', 0.0),
                                    'tags': results.get('metadatas', [{}])[i].get('tags', []),
                                    'metadata': results.get('metadatas', [{}])[i] if i < len(results.get('metadatas', [])) else {}
                                })()
                                all_memories.append(memory_obj)

                        logger.info(f"Retrieved {len(all_memories)} memories from encrypted store")
                        return all_memories

                except Exception as e:
                    logger.warning(f"Could not get memories from encrypted store: {e}")

            # Fallback to regular store
            if hasattr(self, 'vector_store') and self.vector_store:
                try:
                    # Try to get all memories from regular vector store
                    if hasattr(self.vector_store, 'get_all_memories'):
                        all_memories = self.vector_store.get_all_memories()
                    elif hasattr(self.vector_store, 'collection'):
                        # Direct ChromaDB access
                        collection = self.vector_store.collection
                        results = collection.get()

                        if results and 'documents' in results:
                            for i, doc in enumerate(results['documents']):
                                memory_obj = type('Memory', (), {
                                    'content': doc,
                                    'source': results.get('metadatas', [{}])[i].get('source', 'unknown'),
                                    'timestamp': results.get('metadatas', [{}])[i].get('timestamp', time.time()),
                                    'memory_type': results.get('metadatas', [{}])[i].get('memory_type', 'document'),
                                    'importance_score': results.get('metadatas', [{}])[i].get('importance_score', 0.0),
                                    'tags': results.get('metadatas', [{}])[i].get('tags', []),
                                    'metadata': results.get('metadatas', [{}])[i] if i < len(results.get('metadatas', [])) else {}
                                })()
                                all_memories.append(memory_obj)

                    logger.info(f"Retrieved {len(all_memories)} memories from regular store")
                    return all_memories

                except Exception as e:
                    logger.warning(f"Could not get memories from regular store: {e}")

            return all_memories

        except Exception as e:
            logger.error(f"Error getting all memories: {e}")
            return []

# Factory function for backward compatibility
def get_secure_memory_store(store_type: VectorStoreType = VectorStoreType.CHROMA,
                           storage_directory: str = "memory_store",
                           embedding_dimension: int = 384,
                           enable_encryption: bool = True,
                           security_manager=None) -> SecureMemoryVectorStore:
    """
    Factory function to create secure memory store.

    Args:
        store_type: Type of vector store to use
        storage_directory: Directory for storing memory data
        embedding_dimension: Dimension of embedding vectors
        enable_encryption: Whether to enable encryption
        security_manager: Optional existing security manager to use

    Returns:
        SecureMemoryVectorStore instance
    """
    return SecureMemoryVectorStore(
        store_type=store_type,
        storage_directory=storage_directory,
        embedding_dimension=embedding_dimension,
        enable_encryption=enable_encryption,
        security_manager=security_manager
    )
