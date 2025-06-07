"""
Persistent Vector Store for SAM Long-Term Memory
Supports FAISS, Chroma, and other vector databases for memory persistence.

Sprint 11 Task 3: Persistent Vector Store
"""

import logging
import json
import uuid
import hashlib
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pickle

logger = logging.getLogger(__name__)

class VectorStoreType(Enum):
    """Supported vector store types."""
    FAISS = "faiss"
    CHROMA = "chroma"
    SIMPLE = "simple"
    DISABLED = "disabled"

class MemoryType(Enum):
    """Types of memories that can be stored."""
    DOCUMENT = "document"
    CONVERSATION = "conversation"
    REASONING = "reasoning"
    INSIGHT = "insight"
    FACT = "fact"
    PROCEDURE = "procedure"

@dataclass
class MemoryChunk:
    """A chunk of memory with vector embedding and metadata."""
    chunk_id: str
    content: str
    content_hash: str
    embedding: Optional[List[float]]
    memory_type: MemoryType
    source: str
    timestamp: str
    tags: List[str]
    importance_score: float
    access_count: int
    last_accessed: str
    metadata: Dict[str, Any]

@dataclass
class MemorySearchResult:
    """Result from memory search."""
    chunk: MemoryChunk
    similarity_score: float
    rank: int

class MemoryVectorStore:
    """
    Persistent vector store for SAM's long-term memory.
    """
    
    def __init__(self, store_type: VectorStoreType = VectorStoreType.SIMPLE,
                 storage_directory: str = "memory_store",
                 embedding_dimension: int = 384):
        """
        Initialize the memory vector store.
        
        Args:
            store_type: Type of vector store to use
            storage_directory: Directory for storing memory data
            embedding_dimension: Dimension of embedding vectors
        """
        self.store_type = store_type
        self.storage_dir = Path(storage_directory)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_dimension = embedding_dimension
        
        # Storage
        self.memory_chunks: Dict[str, MemoryChunk] = {}
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.chunk_ids: List[str] = []
        
        # Vector store instances
        self.faiss_index = None
        self.chroma_client = None
        
        # Configuration
        self.config = {
            'max_memory_chunks': 10000,
            'similarity_threshold': 0.1,  # Lower threshold for better recall
            'auto_cleanup_enabled': True,
            'cleanup_threshold_days': 90,
            'importance_decay_rate': 0.95,
            'max_search_results': 10
        }
        
        # Initialize vector store
        self._initialize_vector_store()
        
        # Load existing memories
        self._load_memories()
        
        logger.info(f"Memory vector store initialized: {store_type.value} with {len(self.memory_chunks)} memories")
    
    def add_memory(self, content: str, memory_type: MemoryType, source: str,
                  tags: List[str] = None, importance_score: float = 0.5,
                  metadata: Dict[str, Any] = None) -> str:
        """
        Add a new memory to the vector store.
        
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
        try:
            chunk_id = f"mem_{uuid.uuid4().hex[:12]}"
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Check for duplicate content
            for existing_chunk in self.memory_chunks.values():
                if existing_chunk.content_hash == content_hash:
                    logger.debug(f"Duplicate memory content detected, updating existing: {existing_chunk.chunk_id}")
                    return self._update_memory_access(existing_chunk.chunk_id)
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            
            # Create memory chunk
            memory_chunk = MemoryChunk(
                chunk_id=chunk_id,
                content=content,
                content_hash=content_hash,
                embedding=embedding,
                memory_type=memory_type,
                source=source,
                timestamp=datetime.now().isoformat(),
                tags=tags or [],
                importance_score=importance_score,
                access_count=0,
                last_accessed=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            # Add to storage
            self.memory_chunks[chunk_id] = memory_chunk
            
            # Add to vector index
            self._add_to_vector_index(chunk_id, embedding)
            
            # Save to disk
            self._save_memory_chunk(memory_chunk)
            
            logger.info(f"Added memory: {chunk_id} ({memory_type.value})")
            return chunk_id
            
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            raise
    
    def search_memories(self, query: str, max_results: int = 5,
                       memory_types: List[MemoryType] = None,
                       tags: List[str] = None,
                       min_similarity: float = None) -> List[MemorySearchResult]:
        """
        Search for relevant memories.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            memory_types: Optional filter by memory types
            tags: Optional filter by tags
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of memory search results
        """
        try:
            if not query.strip():
                return []
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Search vector index
            similar_chunks = self._search_vector_index(query_embedding, max_results * 2)
            
            # Filter and rank results
            results = []
            min_sim = min_similarity or self.config['similarity_threshold']
            
            for chunk_id, similarity in similar_chunks:
                chunk = self.memory_chunks.get(chunk_id)
                if not chunk:
                    continue
                
                # Apply filters
                if memory_types and chunk.memory_type not in memory_types:
                    continue
                
                if tags and not any(tag in chunk.tags for tag in tags):
                    continue
                
                if similarity < min_sim:
                    continue
                
                # Update access tracking
                self._update_memory_access(chunk_id)
                
                # Create search result
                result = MemorySearchResult(
                    chunk=chunk,
                    similarity_score=similarity,
                    rank=len(results) + 1
                )
                
                results.append(result)
                
                if len(results) >= max_results:
                    break
            
            logger.info(f"Memory search: '{query[:50]}...' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def get_memory(self, chunk_id: str) -> Optional[MemoryChunk]:
        """Get a specific memory by ID."""
        chunk = self.memory_chunks.get(chunk_id)
        if chunk:
            self._update_memory_access(chunk_id)
        return chunk

    def get_all_memories(self) -> List[MemoryChunk]:
        """
        Get all memories from the store.

        Returns:
            List of all memory chunks
        """
        try:
            all_memories = list(self.memory_chunks.values())
            logger.info(f"Retrieved {len(all_memories)} total memories")
            return all_memories

        except Exception as e:
            logger.error(f"Error getting all memories: {e}")
            return []

    def update_memory(self, chunk_id: str, content: str = None, tags: List[str] = None,
                     importance_score: float = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Update an existing memory.
        
        Args:
            chunk_id: Memory chunk ID
            content: New content (optional)
            tags: New tags (optional)
            importance_score: New importance score (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if successful
        """
        try:
            chunk = self.memory_chunks.get(chunk_id)
            if not chunk:
                logger.error(f"Memory not found: {chunk_id}")
                return False
            
            # Update fields
            if content is not None:
                chunk.content = content
                chunk.content_hash = hashlib.sha256(content.encode()).hexdigest()
                chunk.embedding = self._generate_embedding(content)
                # Update vector index
                self._update_vector_index(chunk_id, chunk.embedding)
            
            if tags is not None:
                chunk.tags = tags
            
            if importance_score is not None:
                chunk.importance_score = importance_score
            
            if metadata is not None:
                chunk.metadata.update(metadata)
            
            # Save updated chunk
            self._save_memory_chunk(chunk)
            
            logger.info(f"Updated memory: {chunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating memory {chunk_id}: {e}")
            return False
    
    def delete_memory(self, chunk_id: str) -> bool:
        """
        Delete a memory from the store.
        
        Args:
            chunk_id: Memory chunk ID
            
        Returns:
            True if successful
        """
        try:
            if chunk_id not in self.memory_chunks:
                logger.error(f"Memory not found: {chunk_id}")
                return False
            
            # Remove from memory
            del self.memory_chunks[chunk_id]
            
            # Remove from vector index
            self._remove_from_vector_index(chunk_id)
            
            # Remove file
            chunk_file = self.storage_dir / f"{chunk_id}.json"
            chunk_file.unlink(missing_ok=True)
            
            logger.info(f"Deleted memory: {chunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting memory {chunk_id}: {e}")
            return False
    
    def clear_memories(self, memory_types: List[MemoryType] = None,
                      older_than_days: int = None) -> int:
        """
        Clear memories based on criteria.
        
        Args:
            memory_types: Optional filter by memory types
            older_than_days: Optional age filter
            
        Returns:
            Number of memories cleared
        """
        try:
            from datetime import timedelta
            
            chunks_to_delete = []
            cutoff_date = None
            
            if older_than_days:
                cutoff_date = datetime.now() - timedelta(days=older_than_days)
            
            for chunk_id, chunk in self.memory_chunks.items():
                # Apply filters
                if memory_types and chunk.memory_type not in memory_types:
                    continue
                
                if cutoff_date:
                    chunk_date = datetime.fromisoformat(chunk.timestamp)
                    if chunk_date > cutoff_date:
                        continue
                
                chunks_to_delete.append(chunk_id)
            
            # Delete chunks
            deleted_count = 0
            for chunk_id in chunks_to_delete:
                if self.delete_memory(chunk_id):
                    deleted_count += 1
            
            logger.info(f"Cleared {deleted_count} memories")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing memories: {e}")
            return 0
    
    def export_memories(self, export_file: str) -> bool:
        """
        Export memories to a file.
        
        Args:
            export_file: Path to export file
            
        Returns:
            True if successful
        """
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'store_type': self.store_type.value,
                'embedding_dimension': self.embedding_dimension,
                'memory_count': len(self.memory_chunks),
                'memories': [asdict(chunk) for chunk in self.memory_chunks.values()]
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(self.memory_chunks)} memories to {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting memories: {e}")
            return False
    
    def import_memories(self, import_file: str) -> int:
        """
        Import memories from a file.
        
        Args:
            import_file: Path to import file
            
        Returns:
            Number of memories imported
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            
            for memory_data in import_data.get('memories', []):
                try:
                    # Reconstruct memory chunk
                    chunk = MemoryChunk(
                        chunk_id=memory_data['chunk_id'],
                        content=memory_data['content'],
                        content_hash=memory_data['content_hash'],
                        embedding=memory_data['embedding'],
                        memory_type=MemoryType(memory_data['memory_type']),
                        source=memory_data['source'],
                        timestamp=memory_data['timestamp'],
                        tags=memory_data['tags'],
                        importance_score=memory_data['importance_score'],
                        access_count=memory_data['access_count'],
                        last_accessed=memory_data['last_accessed'],
                        metadata=memory_data['metadata']
                    )
                    
                    # Add to storage
                    self.memory_chunks[chunk.chunk_id] = chunk
                    
                    # Add to vector index
                    if chunk.embedding:
                        self._add_to_vector_index(chunk.chunk_id, chunk.embedding)
                    
                    imported_count += 1
                    
                except Exception as e:
                    logger.error(f"Error importing memory chunk: {e}")
            
            logger.info(f"Imported {imported_count} memories from {import_file}")
            return imported_count
            
        except Exception as e:
            logger.error(f"Error importing memories: {e}")
            return 0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        try:
            stats = {
                'total_memories': len(self.memory_chunks),
                'store_type': self.store_type.value,
                'embedding_dimension': self.embedding_dimension,
                'storage_directory': str(self.storage_dir),
                'memory_types': {},
                'total_size_mb': 0,
                'oldest_memory': None,
                'newest_memory': None,
                'most_accessed': None
            }
            
            # Calculate type distribution
            for chunk in self.memory_chunks.values():
                mem_type = chunk.memory_type.value
                stats['memory_types'][mem_type] = stats['memory_types'].get(mem_type, 0) + 1
            
            # Calculate storage size
            for file_path in self.storage_dir.glob("*.json"):
                stats['total_size_mb'] += file_path.stat().st_size / (1024 * 1024)
            
            # Find oldest and newest
            if self.memory_chunks:
                sorted_by_time = sorted(self.memory_chunks.values(), key=lambda c: c.timestamp)
                stats['oldest_memory'] = sorted_by_time[0].timestamp
                stats['newest_memory'] = sorted_by_time[-1].timestamp
                
                # Most accessed
                most_accessed = max(self.memory_chunks.values(), key=lambda c: c.access_count)
                stats['most_accessed'] = {
                    'chunk_id': most_accessed.chunk_id,
                    'access_count': most_accessed.access_count,
                    'content_preview': most_accessed.content[:100]
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {'error': str(e)}
    
    def _initialize_vector_store(self):
        """Initialize the vector store backend."""
        try:
            if self.store_type == VectorStoreType.FAISS:
                self._initialize_faiss()
            elif self.store_type == VectorStoreType.CHROMA:
                self._initialize_chroma()
            elif self.store_type == VectorStoreType.SIMPLE:
                self._initialize_simple()
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            # Fallback to simple store
            self.store_type = VectorStoreType.SIMPLE
            self._initialize_simple()
    
    def _initialize_faiss(self):
        """Initialize FAISS vector store."""
        try:
            import faiss
            
            # Create FAISS index
            self.faiss_index = faiss.IndexFlatIP(self.embedding_dimension)
            
            # Load existing index if available
            index_file = self.storage_dir / "faiss_index.bin"
            if index_file.exists():
                self.faiss_index = faiss.read_index(str(index_file))
                logger.info("Loaded existing FAISS index")
            
        except ImportError:
            logger.warning("FAISS not available, falling back to simple store")
            self.store_type = VectorStoreType.SIMPLE
            self._initialize_simple()
        except Exception as e:
            logger.error(f"Error initializing FAISS: {e}")
            self.store_type = VectorStoreType.SIMPLE
            self._initialize_simple()
    
    def _initialize_chroma(self):
        """Initialize Chroma vector store."""
        try:
            import chromadb
            
            # Create Chroma client
            self.chroma_client = chromadb.PersistentClient(path=str(self.storage_dir / "chroma"))
            
            # Get or create collection
            self.chroma_collection = self.chroma_client.get_or_create_collection(
                name="sam_memories",
                metadata={"description": "SAM long-term memory store"}
            )
            
            logger.info("Initialized Chroma vector store")
            
        except ImportError:
            logger.warning("Chroma not available, falling back to simple store")
            self.store_type = VectorStoreType.SIMPLE
            self._initialize_simple()
        except Exception as e:
            logger.error(f"Error initializing Chroma: {e}")
            self.store_type = VectorStoreType.SIMPLE
            self._initialize_simple()
    
    def _initialize_simple(self):
        """Initialize simple in-memory vector store."""
        self.embeddings_matrix = None
        self.chunk_ids = []
        logger.info("Initialized simple vector store")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using proper embedding model."""
        try:
            # Use the proper embedding manager for consistent embeddings
            from utils.embedding_utils import get_embedding_manager

            embedding_manager = get_embedding_manager()
            embedding = embedding_manager.embed_query(text)

            # Convert to list if numpy array
            if hasattr(embedding, 'tolist'):
                embedding = embedding.tolist()

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Fallback to simple hash-based embedding
            import hashlib

            # Create a deterministic embedding based on text content
            text_hash = hashlib.sha256(text.encode()).hexdigest()

            # Convert hash to embedding vector
            embedding = []
            for i in range(0, min(len(text_hash), self.embedding_dimension * 8), 8):
                hex_chunk = text_hash[i:i+8]
                # Convert hex to float between -1 and 1
                int_val = int(hex_chunk, 16) if hex_chunk else 0
                float_val = (int_val / (16**8)) * 2 - 1
                embedding.append(float_val)

            # Pad or truncate to desired dimension
            while len(embedding) < self.embedding_dimension:
                embedding.append(0.0)

            embedding = embedding[:self.embedding_dimension]

            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = [x / norm for x in embedding]

            return embedding
    
    def _add_to_vector_index(self, chunk_id: str, embedding: List[float]):
        """Add embedding to vector index."""
        try:
            if self.store_type == VectorStoreType.FAISS and self.faiss_index:
                embedding_array = np.array([embedding], dtype=np.float32)
                self.faiss_index.add(embedding_array)
                self.chunk_ids.append(chunk_id)
                
                # Save index
                index_file = self.storage_dir / "faiss_index.bin"
                import faiss
                faiss.write_index(self.faiss_index, str(index_file))
                
            elif self.store_type == VectorStoreType.CHROMA and self.chroma_client:
                self.chroma_collection.add(
                    embeddings=[embedding],
                    documents=[self.memory_chunks[chunk_id].content],
                    ids=[chunk_id]
                )
                
            elif self.store_type == VectorStoreType.SIMPLE:
                if self.embeddings_matrix is None:
                    self.embeddings_matrix = np.array([embedding])
                    self.chunk_ids = [chunk_id]
                else:
                    self.embeddings_matrix = np.vstack([self.embeddings_matrix, embedding])
                    self.chunk_ids.append(chunk_id)
            
        except Exception as e:
            logger.error(f"Error adding to vector index: {e}")
    
    def _search_vector_index(self, query_embedding: List[float], max_results: int) -> List[Tuple[str, float]]:
        """Search vector index for similar embeddings."""
        try:
            results = []
            
            if self.store_type == VectorStoreType.FAISS and self.faiss_index:
                query_array = np.array([query_embedding], dtype=np.float32)
                scores, indices = self.faiss_index.search(query_array, min(max_results, len(self.chunk_ids)))
                
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(self.chunk_ids):
                        results.append((self.chunk_ids[idx], float(score)))
                        
            elif self.store_type == VectorStoreType.CHROMA and self.chroma_client:
                chroma_results = self.chroma_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=max_results
                )
                
                for chunk_id, distance in zip(chroma_results['ids'][0], chroma_results['distances'][0]):
                    similarity = 1.0 - distance  # Convert distance to similarity
                    results.append((chunk_id, similarity))
                    
            elif self.store_type == VectorStoreType.SIMPLE and self.embeddings_matrix is not None:
                query_array = np.array(query_embedding)
                similarities = np.dot(self.embeddings_matrix, query_array)
                
                # Get top results
                top_indices = np.argsort(similarities)[::-1][:max_results]
                
                for idx in top_indices:
                    if idx < len(self.chunk_ids):
                        results.append((self.chunk_ids[idx], float(similarities[idx])))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector index: {e}")
            return []
    
    def _update_memory_access(self, chunk_id: str) -> str:
        """Update memory access tracking."""
        try:
            chunk = self.memory_chunks.get(chunk_id)
            if chunk:
                chunk.access_count += 1
                chunk.last_accessed = datetime.now().isoformat()
                self._save_memory_chunk(chunk)
            return chunk_id
            
        except Exception as e:
            logger.error(f"Error updating memory access: {e}")
            return chunk_id
    
    def _save_memory_chunk(self, chunk: MemoryChunk):
        """Save memory chunk to disk."""
        try:
            chunk_file = self.storage_dir / f"{chunk.chunk_id}.json"

            # Convert chunk to dict and handle enum serialization
            chunk_dict = asdict(chunk)
            chunk_dict['memory_type'] = chunk.memory_type.value  # Convert enum to string

            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk_dict, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error saving memory chunk: {e}")
    
    def _load_memories(self):
        """Load existing memories from disk."""
        try:
            loaded_count = 0
            
            for chunk_file in self.storage_dir.glob("mem_*.json"):
                try:
                    with open(chunk_file, 'r', encoding='utf-8') as f:
                        chunk_data = json.load(f)
                    
                    chunk = MemoryChunk(
                        chunk_id=chunk_data['chunk_id'],
                        content=chunk_data['content'],
                        content_hash=chunk_data['content_hash'],
                        embedding=chunk_data['embedding'],
                        memory_type=MemoryType(chunk_data['memory_type']),
                        source=chunk_data['source'],
                        timestamp=chunk_data['timestamp'],
                        tags=chunk_data['tags'],
                        importance_score=chunk_data['importance_score'],
                        access_count=chunk_data['access_count'],
                        last_accessed=chunk_data['last_accessed'],
                        metadata=chunk_data['metadata']
                    )
                    
                    self.memory_chunks[chunk.chunk_id] = chunk
                    
                    # Add to vector index
                    if chunk.embedding:
                        self._add_to_vector_index(chunk.chunk_id, chunk.embedding)
                    
                    loaded_count += 1
                    
                except Exception as e:
                    logger.error(f"Error loading memory chunk {chunk_file}: {e}")
            
            logger.info(f"Loaded {loaded_count} existing memories")
            
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
    
    def _update_vector_index(self, chunk_id: str, embedding: List[float]):
        """Update embedding in vector index."""
        # For simplicity, remove and re-add
        self._remove_from_vector_index(chunk_id)
        self._add_to_vector_index(chunk_id, embedding)
    
    def _remove_from_vector_index(self, chunk_id: str):
        """Remove embedding from vector index."""
        try:
            if chunk_id in self.chunk_ids:
                idx = self.chunk_ids.index(chunk_id)
                self.chunk_ids.pop(idx)
                
                if self.store_type == VectorStoreType.SIMPLE and self.embeddings_matrix is not None:
                    self.embeddings_matrix = np.delete(self.embeddings_matrix, idx, axis=0)
                    
                # For FAISS and Chroma, we would need to rebuild the index
                # This is a simplified implementation
                
        except Exception as e:
            logger.error(f"Error removing from vector index: {e}")

# Global memory vector store instance
_memory_store = None

def get_memory_store(store_type: VectorStoreType = VectorStoreType.SIMPLE,
                    storage_directory: str = "memory_store",
                    embedding_dimension: int = 384) -> MemoryVectorStore:
    """Get or create a global memory vector store instance."""
    global _memory_store
    
    if _memory_store is None:
        _memory_store = MemoryVectorStore(
            store_type=store_type,
            storage_directory=storage_directory,
            embedding_dimension=embedding_dimension
        )
    
    return _memory_store
