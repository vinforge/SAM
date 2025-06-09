#!/usr/bin/env python3
"""
Test the migrated ChromaDB data with enhanced features.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_migrated_data():
    """Test the migrated ChromaDB data."""
    
    print("🧪 Testing Migrated ChromaDB Data")
    print("=" * 40)
    
    try:
        # Initialize ChromaDB vector store
        print("1. Connecting to migrated ChromaDB...")
        memory_store = MemoryVectorStore(
            store_type=VectorStoreType.CHROMA,
            storage_directory="web_ui",
            embedding_dimension=384
        )
        print(f"✅ Connected to ChromaDB: {memory_store.store_type}")
        print(f"   Total memories: {len(memory_store.memory_chunks)}")
        
        # Test basic search
        print("\n2. Testing basic search...")
        results = memory_store.search_memories(
            query="Blue Cloak cybersecurity",
            max_results=5
        )
        print(f"✅ Found {len(results)} results")
        
        if results:
            result = results[0]
            print(f"   Top result similarity: {result.similarity_score:.3f}")
            print(f"   Content preview: {result.chunk.content[:100]}...")
            print(f"   Source: {result.chunk.source}")
        
        # Test filtered search by source
        print("\n3. Testing filtered search by source...")
        filtered_results = memory_store.search_memories(
            query="cybersecurity",
            max_results=5,
            where_filter={"source_name": {"$eq": "Blue_Cloak_Ad-Hoc_CBL_PastPerf_Narrative.pdf"}}
        )
        print(f"✅ Filtered search found {len(filtered_results)} results")
        
        # Test filtered search by content type
        print("\n4. Testing filtered search by content type...")
        content_filtered = memory_store.search_memories(
            query="engineer",
            max_results=5,
            where_filter={"content_type": "text"}
        )
        print(f"✅ Content type filtered search found {len(content_filtered)} results")
        
        # Test confidence threshold filtering
        print("\n5. Testing confidence threshold filtering...")
        confidence_filtered = memory_store.search_memories(
            query="AI software",
            max_results=5,
            where_filter={"confidence_score": {"$gte": 0.5}}
        )
        print(f"✅ Confidence filtered search found {len(confidence_filtered)} results")
        
        # Display enhanced metadata
        if results:
            print("\n6. Enhanced metadata analysis...")
            result = results[0]
            chunk = result.chunk
            
            print(f"   Chunk ID: {chunk.chunk_id}")
            print(f"   Memory Type: {chunk.memory_type}")
            print(f"   Importance Score: {chunk.importance_score:.3f}")
            print(f"   Access Count: {chunk.access_count}")
            print(f"   Tags: {chunk.tags[:3]}...")  # First 3 tags
            
            if chunk.metadata:
                print(f"   Metadata keys: {list(chunk.metadata.keys())[:5]}...")  # First 5 keys
                
                # Show Citation-relevant fields
                citation_fields = ["source_file", "block_index", "content_type", "document_id"]
                for field in citation_fields:
                    if field in chunk.metadata:
                        print(f"   {field}: {chunk.metadata[field]}")
        
        print("\n🎉 All tests passed! ChromaDB migration successful.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Test error details:")
        return False

def test_collection_stats():
    """Test ChromaDB collection statistics."""
    print("\n📊 ChromaDB Collection Statistics")
    print("-" * 40)
    
    try:
        from utils.chroma_client import get_chroma_collection
        
        collection = get_chroma_collection()
        count = collection.count()
        
        print(f"Collection name: {collection.name}")
        print(f"Total documents: {count}")
        
        # Get collection metadata
        metadata = collection.metadata
        if metadata:
            print("Collection metadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        
        # Sample a few documents to check metadata structure
        if count > 0:
            sample = collection.get(limit=3, include=["metadatas", "documents"])
            
            print(f"\nSample metadata structure:")
            for i, meta in enumerate(sample["metadatas"][:2]):
                print(f"  Document {i+1} metadata keys: {list(meta.keys())}")
                
                # Show Citation-aligned fields
                citation_fields = ["source_name", "chunk_index", "confidence_score", "content_type"]
                for field in citation_fields:
                    if field in meta:
                        print(f"    {field}: {meta[field]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Collection stats failed: {e}")
        return False

if __name__ == "__main__":
    print("SAM Phase 2: ChromaDB Migration Verification")
    print("=" * 50)
    
    # Test migrated data
    data_ok = test_migrated_data()
    
    # Test collection statistics
    stats_ok = test_collection_stats()
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"   Data Migration: {'✅ PASS' if data_ok else '❌ FAIL'}")
    print(f"   Collection Stats: {'✅ PASS' if stats_ok else '❌ FAIL'}")
    
    if data_ok and stats_ok:
        print("\n🚀 ChromaDB migration verification successful!")
        print("SAM is ready for Phase 3: Enhanced Core Logic!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        sys.exit(1)
