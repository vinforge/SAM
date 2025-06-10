"""
SAM Secure Enclave - Encrypted ChromaDB Store

Provides encrypted storage for SAM's knowledge base using ChromaDB with
application-layer encryption for sensitive content and metadata.

Security Features:
- Hybrid metadata encryption (searchable + encrypted fields)
- AES-256-GCM encryption for document content
- Plaintext embeddings for vector similarity search
- Secure query filtering and result decryption

Author: SAM Development Team
Version: 1.0.0
"""

import json
import uuid
import logging
from typing import List, Dict, Any, Optional, Union
import chromadb

from .crypto_utils import SAMCrypto, SecurityError
from .metadata_handler import EncryptedMetadataHandler, MetadataHandlerError

# Configure logging
logger = logging.getLogger(__name__)

class EncryptedChromaStoreError(Exception):
    """Base exception for encrypted ChromaDB store errors"""
    pass

class EncryptedChromaStore:
    """
    Encrypted ChromaDB store for SAM's knowledge base.
    
    Provides transparent encryption/decryption of document content and metadata
    while maintaining vector search capabilities through plaintext embeddings.
    """
    
    def __init__(self, collection_name: str, crypto_manager: SAMCrypto, 
                 chroma_client: Optional[chromadb.Client] = None):
        """
        Initialize encrypted ChromaDB store.
        
        Args:
            collection_name: Name of the ChromaDB collection
            crypto_manager: SAMCrypto instance for encryption/decryption
            chroma_client: Optional ChromaDB client (creates default if None)
        """
        self.collection_name = collection_name
        self.crypto = crypto_manager
        self.metadata_handler = EncryptedMetadataHandler(crypto_manager)
        
        # Initialize ChromaDB client
        if chroma_client is None:
            self.client = chromadb.PersistentClient(path="./chroma_db")
        else:
            self.client = chroma_client
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"encryption_enabled": True, "version": "1.0"}
        )
        
        logger.info(f"Encrypted ChromaDB store initialized: {collection_name}")
    
    def add_memory_chunk(self, chunk_text: str, metadata: Dict[str, Any], 
                        embedding: List[float], chunk_id: Optional[str] = None) -> str:
        """
        Add an encrypted memory chunk to the store.
        
        Args:
            chunk_text: The text content to encrypt and store
            metadata: Metadata dictionary (will be split into encrypted/unencrypted)
            embedding: Vector embedding for similarity search (stored as plaintext)
            chunk_id: Optional chunk ID (generates UUID if None)
            
        Returns:
            The chunk ID that was used
            
        Raises:
            EncryptedChromaStoreError: If storage fails
        """
        if not self.crypto.is_unlocked():
            raise EncryptedChromaStoreError("Cannot add chunks - application is locked")
        
        try:
            # Generate chunk ID if not provided
            if chunk_id is None:
                chunk_id = str(uuid.uuid4())
            
            # Add chunk_id to metadata
            metadata = metadata.copy()
            metadata['chunk_id'] = chunk_id
            
            # Encrypt the main content
            encrypted_content = self.crypto.encrypt_data(chunk_text)
            
            # Process metadata (split encrypted/unencrypted)
            processed_metadata = self.metadata_handler.prepare_metadata_for_storage(metadata)
            
            # Store in ChromaDB
            self.collection.add(
                documents=[json.dumps(encrypted_content)],  # Encrypted content as JSON string
                embeddings=[embedding],                      # Plaintext embedding for search
                metadatas=[processed_metadata],             # Hybrid metadata
                ids=[chunk_id]
            )
            
            logger.debug(f"Added encrypted chunk: {chunk_id}")
            return chunk_id
            
        except (SecurityError, MetadataHandlerError) as e:
            logger.error(f"Failed to add encrypted chunk: {e}")
            raise EncryptedChromaStoreError(f"Failed to add chunk: {e}")
        except Exception as e:
            logger.error(f"Unexpected error adding chunk: {e}")
            raise EncryptedChromaStoreError(f"Unexpected error: {e}")
    
    def add_memory_chunks(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple encrypted memory chunks in batch.
        
        Args:
            chunks: List of chunk dictionaries with keys:
                   - 'text': chunk text content
                   - 'metadata': metadata dictionary
                   - 'embedding': vector embedding
                   - 'id': optional chunk ID
                   
        Returns:
            List of chunk IDs that were used
        """
        if not self.crypto.is_unlocked():
            raise EncryptedChromaStoreError("Cannot add chunks - application is locked")
        
        try:
            chunk_ids = []
            documents = []
            embeddings = []
            metadatas = []
            
            for chunk in chunks:
                # Generate chunk ID if not provided
                chunk_id = chunk.get('id', str(uuid.uuid4()))
                chunk_ids.append(chunk_id)
                
                # Add chunk_id to metadata
                metadata = chunk['metadata'].copy()
                metadata['chunk_id'] = chunk_id
                
                # Encrypt content
                encrypted_content = self.crypto.encrypt_data(chunk['text'])
                documents.append(json.dumps(encrypted_content))
                
                # Process metadata
                processed_metadata = self.metadata_handler.prepare_metadata_for_storage(metadata)
                metadatas.append(processed_metadata)
                
                # Add embedding
                embeddings.append(chunk['embedding'])
            
            # Batch add to ChromaDB
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            logger.info(f"Added {len(chunk_ids)} encrypted chunks in batch")
            return chunk_ids
            
        except (SecurityError, MetadataHandlerError) as e:
            logger.error(f"Failed to add encrypted chunks: {e}")
            raise EncryptedChromaStoreError(f"Failed to add chunks: {e}")
        except Exception as e:
            logger.error(f"Unexpected error adding chunks: {e}")
            raise EncryptedChromaStoreError(f"Unexpected error: {e}")
    
    def query_memories(self, query_embedding: List[float], n_results: int = 5,
                      where_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query and decrypt memory chunks.
        
        Args:
            query_embedding: Vector embedding for similarity search
            n_results: Number of results to return
            where_filter: Optional filter (only works on unencrypted fields)
            
        Returns:
            List of decrypted memory chunks with metadata
            
        Raises:
            EncryptedChromaStoreError: If query fails
        """
        if not self.crypto.is_unlocked():
            raise EncryptedChromaStoreError("Cannot query memories - application is locked")
        
        try:
            # Validate and clean the where filter
            if where_filter:
                searchable_filter = self.metadata_handler.create_searchable_filter(where_filter)
                if not searchable_filter:
                    logger.warning("All filter fields are encrypted - performing unfiltered search")
                    where_filter = None
                else:
                    where_filter = searchable_filter
            
            # Query ChromaDB (only unencrypted metadata can be filtered)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )
            
            # Decrypt results
            decrypted_results = []
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    try:
                        # Decrypt content
                        encrypted_content = json.loads(doc)
                        decrypted_text = self.crypto.decrypt_data(encrypted_content)
                        
                        # Decrypt metadata
                        stored_metadata = results['metadatas'][0][i]
                        full_metadata = self.metadata_handler.restore_metadata_from_storage(stored_metadata)
                        
                        # Create result object
                        result = {
                            'content': decrypted_text,
                            'metadata': full_metadata,
                            'id': results['ids'][0][i],
                            'distance': results['distances'][0][i] if 'distances' in results else None
                        }
                        
                        decrypted_results.append(result)
                        
                    except Exception as e:
                        logger.error(f"Failed to decrypt result {i}: {e}")
                        # Add error result instead of failing completely
                        decrypted_results.append({
                            'content': '[DECRYPTION_FAILED]',
                            'metadata': {'decryption_error': str(e)},
                            'id': results['ids'][0][i] if 'ids' in results else f'error_{i}',
                            'distance': results['distances'][0][i] if 'distances' in results else None
                        })
            
            logger.debug(f"Query returned {len(decrypted_results)} decrypted results")
            return decrypted_results
            
        except Exception as e:
            logger.error(f"Memory query failed: {e}")
            raise EncryptedChromaStoreError(f"Query failed: {e}")
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific chunk by ID.
        
        Args:
            chunk_id: The chunk ID to retrieve
            
        Returns:
            Decrypted chunk data or None if not found
        """
        if not self.crypto.is_unlocked():
            raise EncryptedChromaStoreError("Cannot get chunk - application is locked")
        
        try:
            results = self.collection.get(ids=[chunk_id])
            
            if not results['documents'] or not results['documents'][0]:
                return None
            
            # Decrypt the single result
            encrypted_content = json.loads(results['documents'][0])
            decrypted_text = self.crypto.decrypt_data(encrypted_content)
            
            stored_metadata = results['metadatas'][0]
            full_metadata = self.metadata_handler.restore_metadata_from_storage(stored_metadata)
            
            return {
                'content': decrypted_text,
                'metadata': full_metadata,
                'id': chunk_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get chunk {chunk_id}: {e}")
            raise EncryptedChromaStoreError(f"Failed to get chunk: {e}")
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a chunk by ID.
        
        Args:
            chunk_id: The chunk ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            self.collection.delete(ids=[chunk_id])
            logger.debug(f"Deleted chunk: {chunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete chunk {chunk_id}: {e}")
            return False
    
    def count_chunks(self) -> int:
        """
        Get the total number of chunks in the store.
        
        Returns:
            Number of chunks
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to count chunks: {e}")
            return 0
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the encrypted collection.
        
        Returns:
            Dictionary with collection information
        """
        try:
            count = self.count_chunks()
            searchable_fields = list(self.metadata_handler.get_searchable_fields())
            encrypted_fields = list(self.metadata_handler.get_encrypted_fields())
            
            return {
                'collection_name': self.collection_name,
                'chunk_count': count,
                'encryption_enabled': True,
                'encryption_version': '1.0',
                'searchable_fields': searchable_fields,
                'encrypted_fields': encrypted_fields,
                'is_unlocked': self.crypto.is_unlocked()
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {'error': str(e)}
