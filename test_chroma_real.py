#!/usr/bin/env python3
"""
Test ChromaDB with real SAM configuration.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chroma_real():
    """Test ChromaDB with real configuration."""
    
    print("🧪 Testing ChromaDB with Real Configuration")
    print("=" * 50)
    
    try:
        # Initialize Chroma vector store
        print("1. Initializing Chroma vector store...")
        memory_store = MemoryVectorStore(
            store_type=VectorStoreType.CHROMA,
            storage_directory="test_real_chroma",
            embedding_dimension=384
        )
        print(f"✅ Vector store initialized: {memory_store.store_type}")
        
        # Test adding a memory with simple metadata (no lists)
        print("\n2. Adding test memory with simple metadata...")
        test_content = "Blue Cloak specializes in cybersecurity and Cyber Battle Labs."
        
        chunk_id = memory_store.add_memory(
            content=test_content,
            memory_type=MemoryType.DOCUMENT,
            source="document:test.pdf:block_1",
            tags=["cybersecurity", "testing"],  # This will be converted to string
            importance_score=0.8,
            metadata={
                "document_id": "test_001",
                "source_file": "test.pdf",
                "file_name": "test.pdf",
                "block_index": 0,
                "content_type": "text"
            }
        )
        print(f"✅ Memory added: {chunk_id}")
        
        # Test search
        print("\n3. Testing search...")
        results = memory_store.search_memories(
            query="What is Blue Cloak?",
            max_results=5
        )
        print(f"✅ Found {len(results)} results")
        
        if results:
            result = results[0]
            print(f"   Similarity: {result.similarity_score:.3f}")
            print(f"   Content: {result.chunk.content[:50]}...")
        
        # Test with filter if using Chroma
        if memory_store.store_type == VectorStoreType.CHROMA:
            print("\n4. Testing filtered search...")
            filtered_results = memory_store.search_memories(
                query="cybersecurity",
                max_results=5,
                where_filter={"content_type": "text"}
            )
            print(f"✅ Filtered search found {len(filtered_results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Test error details:")
        return False

if __name__ == "__main__":
    success = test_chroma_real()
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    try:
        import shutil
        shutil.rmtree("test_real_chroma", ignore_errors=True)
        print("✅ Cleanup complete")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    
    if success:
        print("\n🎉 ChromaDB integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ ChromaDB integration test failed!")
        sys.exit(1)
