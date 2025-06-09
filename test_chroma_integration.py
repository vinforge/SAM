#!/usr/bin/env python3
"""
Test script for SAM's enhanced Chroma integration.
Tests the new ChromaDB backend with metadata filtering and rich citations.
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

def test_chroma_integration():
    """Test the enhanced Chroma integration."""
    
    print("🧪 Testing SAM's Enhanced Chroma Integration")
    print("=" * 50)
    
    try:
        # Initialize Chroma vector store
        print("1. Initializing Chroma vector store...")
        memory_store = MemoryVectorStore(
            store_type=VectorStoreType.CHROMA,
            storage_directory="test_chroma_db",
            embedding_dimension=384
        )
        print("✅ Chroma vector store initialized")
        
        # Test adding a memory with rich metadata
        print("\n2. Adding test memory with rich metadata...")
        test_content = """
        Blue Cloak is a cybersecurity company specializing in Cyber Battle Labs (CBLs).
        They work with DoD, NASA, and Intelligence Community agencies.
        Their main platform is Keromatsu, a cyber range orchestration system.
        """
        
        chunk_id = memory_store.add_memory(
            content=test_content.strip(),
            memory_type=MemoryType.DOCUMENT,
            source="document:test_documents/blue_cloak_info.pdf:block_1",
            tags=["cybersecurity", "government", "testing"],
            importance_score=0.8,
            metadata={
                "document_id": "test_doc_001",
                "source_file": "test_documents/blue_cloak_info.pdf",
                "file_name": "blue_cloak_info.pdf",
                "block_index": 0,
                "content_type": "text",
                "page_number": 1,
                "section_title": "Company Overview"
            }
        )
        print(f"✅ Memory added with ID: {chunk_id}")
        
        # Test basic search
        print("\n3. Testing basic semantic search...")
        results = memory_store.search_memories(
            query="What is Blue Cloak?",
            max_results=5,
            min_similarity=0.1
        )
        print(f"✅ Found {len(results)} results")
        for i, result in enumerate(results):
            print(f"   {i+1}. Similarity: {result.similarity_score:.3f}")
        
        # Test filtered search (Chroma-specific feature)
        print("\n4. Testing filtered search by source...")
        filtered_results = memory_store.search_memories(
            query="cybersecurity company",
            max_results=5,
            where_filter={"source_name": "blue_cloak_info.pdf"}
        )
        print(f"✅ Filtered search found {len(filtered_results)} results")
        
        # Test filtered search by content type
        print("\n5. Testing filtered search by content type...")
        type_filtered_results = memory_store.search_memories(
            query="Blue Cloak",
            max_results=5,
            where_filter={"content_type": "text"}
        )
        print(f"✅ Content type filtered search found {len(type_filtered_results)} results")
        
        # Test confidence threshold filtering
        print("\n6. Testing confidence threshold filtering...")
        confidence_filtered_results = memory_store.search_memories(
            query="Cyber Battle Labs",
            max_results=5,
            where_filter={"confidence_score": {"$gte": 0.5}}
        )
        print(f"✅ Confidence filtered search found {len(confidence_filtered_results)} results")
        
        # Display detailed results
        if results:
            print("\n7. Detailed result analysis...")
            result = results[0]
            print(f"   Chunk ID: {result.chunk.chunk_id}")
            print(f"   Content: {result.chunk.content[:100]}...")
            print(f"   Source: {result.chunk.source}")
            print(f"   Memory Type: {result.chunk.memory_type}")
            print(f"   Similarity: {result.similarity_score:.3f}")
            print(f"   Metadata keys: {list(result.chunk.metadata.keys())}")
        
        print("\n🎉 All tests passed! Chroma integration is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ ChromaDB not available: {e}")
        print("Install with: pip install chromadb")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Test error details:")
        return False

def test_config_loading():
    """Test configuration loading."""
    print("\n🔧 Testing configuration loading...")
    
    try:
        from utils.chroma_client import load_chroma_config
        config = load_chroma_config()
        print(f"✅ Config loaded: {config}")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

if __name__ == "__main__":
    print("SAM Enhanced Chroma Integration Test")
    print("====================================")
    
    # Test configuration
    config_ok = test_config_loading()
    
    # Test Chroma integration
    chroma_ok = test_chroma_integration()
    
    # Cleanup
    print("\n🧹 Cleaning up test database...")
    try:
        import shutil
        shutil.rmtree("test_chroma_db", ignore_errors=True)
        print("✅ Test database cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"   Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   Chroma Integration: {'✅ PASS' if chroma_ok else '❌ FAIL'}")
    
    if config_ok and chroma_ok:
        print("\n🚀 SAM is ready for Chroma upgrade!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        sys.exit(1)
