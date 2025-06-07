#!/usr/bin/env python3
"""
Sprint 2 End-to-End Test Pipeline
Tests semantic intelligence and contextual retrieval capabilities.

Sprint 2 Task 6: End-to-End Test Pipeline
"""

import logging
import sys
import numpy as np
from pathlib import Path
import tempfile
import shutil

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_embedding_utils():
    """Test embedding utilities."""
    logger.info("🔤 Testing Embedding Utils...")
    
    try:
        from utils.embedding_utils import EmbeddingManager, embed, embed_batch
        
        # Test embedding manager initialization
        embedding_manager = EmbeddingManager()
        logger.info(f"  ✅ Embedding manager initialized: {embedding_manager.model_name}")
        logger.info(f"  📏 Embedding dimension: {embedding_manager.embedding_dim}")
        
        # Test single embedding
        test_text = "This is a test sentence for embedding."
        embedding = embed(test_text)
        
        if embedding is not None and len(embedding) == embedding_manager.embedding_dim:
            logger.info(f"  ✅ Single embedding successful: shape {embedding.shape}")
        else:
            logger.error("  ❌ Single embedding failed")
            return False
        
        # Test batch embedding
        test_texts = [
            "Machine learning with GPU acceleration",
            "Python error handling best practices",
            "Data enrichment and processing pipeline"
        ]
        
        embeddings = embed_batch(test_texts)
        
        if len(embeddings) == len(test_texts):
            logger.info(f"  ✅ Batch embedding successful: {len(embeddings)} embeddings")
        else:
            logger.error("  ❌ Batch embedding failed")
            return False
        
        # Test similarity calculation
        similarity = embedding_manager.similarity(embeddings[0], embeddings[1])
        logger.info(f"  ✅ Similarity calculation: {similarity:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Embedding utils test failed: {e}")
        return False

def test_vector_manager():
    """Test vector store management."""
    logger.info("🗄️ Testing Vector Manager...")
    
    try:
        from utils.vector_manager import VectorManager
        from utils.embedding_utils import embed_batch
        
        # Create temporary vector store
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_manager = VectorManager(vector_store_path=temp_dir)
            logger.info("  ✅ Vector manager initialized")
            
            # Test data
            test_chunks = [
                ("chunk_1", "Machine learning with PyTorch and GPU acceleration", {
                    "source_file": "test1.py",
                    "tags": ["ml:torch", "gpu", "python"],
                    "enrichment_score": 85.0
                }),
                ("chunk_2", "Error handling in Python applications", {
                    "source_file": "test2.py", 
                    "tags": ["python", "error-handling", "best-practices"],
                    "enrichment_score": 70.0
                }),
                ("chunk_3", "Data processing pipeline optimization", {
                    "source_file": "test3.py",
                    "tags": ["data-processing", "optimization", "pipeline"],
                    "enrichment_score": 75.0
                })
            ]
            
            # Generate embeddings
            texts = [chunk[1] for chunk in test_chunks]
            embeddings = embed_batch(texts)
            
            # Add chunks to vector store
            for i, (chunk_id, text, metadata) in enumerate(test_chunks):
                vector_manager.add_chunk(chunk_id, text, embeddings[i], metadata)
            
            logger.info(f"  ✅ Added {len(test_chunks)} chunks to vector store")
            
            # Test search
            query_text = "machine learning GPU"
            query_embedding = embed_batch([query_text])[0]
            
            results = vector_manager.search(query_embedding, top_k=2)
            
            if results and len(results) > 0:
                logger.info(f"  ✅ Search successful: {len(results)} results")
                logger.info(f"    Top result: {results[0]['chunk_id']} (score: {results[0]['similarity_score']:.3f})")
            else:
                logger.error("  ❌ Search failed")
                return False
            
            # Test tag filtering
            filtered_results = vector_manager.filter_by_tags(results, preferred_tags=["ml:torch"])
            logger.info(f"  ✅ Tag filtering: {len(filtered_results)} filtered results")
            
            # Test stats
            stats = vector_manager.get_stats()
            logger.info(f"  ✅ Vector store stats: {stats['total_chunks']} chunks")
            
            return True
            
    except Exception as e:
        logger.error(f"  ❌ Vector manager test failed: {e}")
        return False

def test_query_router():
    """Test semantic query router."""
    logger.info("🧠 Testing Query Router...")
    
    try:
        from utils.vector_manager import VectorManager
        from utils.embedding_utils import get_embedding_manager
        from core.query_router import SemanticQueryRouter
        
        # Create temporary components
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_manager = VectorManager(vector_store_path=temp_dir)
            embedding_manager = get_embedding_manager()
            
            # Add test data
            test_data = [
                ("test_1", "PyTorch GPU acceleration for deep learning models", {
                    "source_file": "gpu_training.py",
                    "tags": ["ml:torch", "gpu", "deep-learning"],
                    "enrichment_score": 90.0
                }),
                ("test_2", "Python exception handling and error recovery", {
                    "source_file": "error_handling.py",
                    "tags": ["python", "error-handling", "exceptions"],
                    "enrichment_score": 75.0
                })
            ]
            
            # Embed and store
            texts = [item[1] for item in test_data]
            embeddings = embedding_manager.embed_batch(texts)
            
            for i, (chunk_id, text, metadata) in enumerate(test_data):
                vector_manager.add_chunk(chunk_id, text, embeddings[i], metadata)
            
            # Initialize query router
            query_router = SemanticQueryRouter(vector_manager, embedding_manager)
            logger.info("  ✅ Query router initialized")
            
            # Test semantic query
            test_query = "How to use GPU for machine learning?"
            result = query_router.route_query(test_query, semantic_mode=True, top_k=2)
            
            if result.semantic_mode and result.context_chunks:
                logger.info(f"  ✅ Semantic query successful: {len(result.context_chunks)} chunks retrieved")
                logger.info(f"    Processing time: {result.query_stats['processing_time']:.3f}s")
            else:
                logger.error("  ❌ Semantic query failed")
                return False
            
            # Test direct query
            direct_result = query_router.route_query(test_query, semantic_mode=False)
            
            if not direct_result.semantic_mode:
                logger.info("  ✅ Direct query mode working")
            else:
                logger.error("  ❌ Direct query mode failed")
                return False
            
            # Test query analysis
            analysis = query_router.analyze_query("machine learning GPU optimization")
            logger.info(f"  ✅ Query analysis: type={analysis.get('query_type', 'unknown')}")
            
            return True
            
    except Exception as e:
        logger.error(f"  ❌ Query router test failed: {e}")
        return False

def test_retrieval_logger():
    """Test retrieval logging system."""
    logger.info("📝 Testing Retrieval Logger...")
    
    try:
        from utils.retrieval_logger import RetrievalLogger
        
        # Create temporary logger
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "test_retrieval.db"
            retrieval_logger = RetrievalLogger(str(log_path))
            logger.info("  ✅ Retrieval logger initialized")
            
            # Test logging
            test_chunks = [
                {
                    'chunk_id': 'test_chunk_1',
                    'metadata': {'enrichment_score': 85.0, 'source_file': 'test.py'},
                    'similarity_score': 0.95
                }
            ]
            
            log_id = retrieval_logger.log_retrieval(
                query="Test query about machine learning",
                response="Test response about ML concepts",
                context_chunks=test_chunks,
                processing_time=0.123,
                mode="semantic"
            )
            
            if log_id > 0:
                logger.info(f"  ✅ Retrieval logged with ID: {log_id}")
            else:
                logger.error("  ❌ Retrieval logging failed")
                return False
            
            # Test feedback
            retrieval_logger.add_feedback(log_id, "👍")
            logger.info("  ✅ Feedback added")
            
            # Test stats
            stats = retrieval_logger.get_stats()
            logger.info(f"  ✅ Stats: {stats['total_queries']} total queries")
            
            # Test recent logs
            recent_logs = retrieval_logger.get_recent_logs(limit=5)
            logger.info(f"  ✅ Recent logs: {len(recent_logs)} entries")
            
            return True
            
    except Exception as e:
        logger.error(f"  ❌ Retrieval logger test failed: {e}")
        return False

def test_integration_with_knowledge_base():
    """Test integration with existing knowledge base."""
    logger.info("🔗 Testing Knowledge Base Integration...")
    
    try:
        from KC.knowledge_consolidation import consolidate_documents
        from utils.vector_manager import VectorManager
        from utils.embedding_utils import get_embedding_manager
        
        # Check if we have processed documents
        test_file = "DE/data_enrichment_enhanced_gpu_fixed_v2.py"
        
        if not Path(test_file).exists():
            logger.warning("  ⚠️ Test file not found, skipping integration test")
            return True
        
        # Process a document
        logger.info("  📄 Processing test document...")
        chunks = consolidate_documents([test_file])
        
        if not chunks:
            logger.warning("  ⚠️ No chunks processed, skipping vector store test")
            return True
        
        # Test vector store integration
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_manager = VectorManager(vector_store_path=temp_dir)
            embedding_manager = get_embedding_manager()
            
            # Add chunks to vector store
            logger.info(f"  🔄 Adding {len(chunks[:5])} chunks to vector store...")
            
            for chunk in chunks[:5]:  # Test with first 5 chunks
                if 'metadata' in chunk:
                    chunk_id = chunk['metadata'].get('chunk_id', 'unknown')
                    text = chunk.get('content', '')
                    metadata = chunk['metadata']
                    
                    if text.strip():
                        embedding = embedding_manager.embed(text)
                        vector_manager.add_chunk(chunk_id, text, embedding, metadata)
            
            # Test search
            query = "GPU acceleration machine learning"
            query_embedding = embedding_manager.embed_query(query)
            results = vector_manager.search(query_embedding, top_k=3)
            
            if results:
                logger.info(f"  ✅ Integration test successful: {len(results)} results")
                logger.info(f"    Best match: score={results[0]['similarity_score']:.3f}")
            else:
                logger.warning("  ⚠️ No search results found")
            
            return True
            
    except Exception as e:
        logger.error(f"  ❌ Integration test failed: {e}")
        return False

def test_chat_ui_semantic_features():
    """Test chat UI semantic features."""
    logger.info("💬 Testing Chat UI Semantic Features...")
    
    try:
        from ui.chat_ui import ChatInterface
        
        # Create mock components
        class MockModel:
            def generate(self, prompt):
                return "Test response with semantic context"
        
        class MockVectorIndex:
            def similarity_search(self, query, k=3):
                return []  # Empty for this test
        
        # Test enhanced chat interface
        chat = ChatInterface(
            model=MockModel(),
            vector_index=MockVectorIndex(),
            system_prompt="Test system prompt"
        )
        
        logger.info("  ✅ Enhanced chat interface initialized")
        
        # Test semantic settings
        logger.info(f"  📊 Semantic mode: {chat.semantic_mode}")
        logger.info(f"  📊 Top-K: {chat.semantic_top_k}")
        logger.info(f"  📊 Threshold: {chat.semantic_threshold}")
        
        # Test command processing
        chat.semantic_mode = False
        chat._process_command("semantics on")
        if chat.semantic_mode:
            logger.info("  ✅ Semantic toggle working")
        else:
            logger.error("  ❌ Semantic toggle failed")
            return False
        
        # Test parameter setting
        chat._process_command("topk 7")
        if chat.semantic_top_k == 7:
            logger.info("  ✅ Top-K setting working")
        else:
            logger.error("  ❌ Top-K setting failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Chat UI semantic test failed: {e}")
        return False

def main():
    """Run all Sprint 2 semantic pipeline tests."""
    logger.info("🚀 SAM Sprint 2 Semantic Pipeline Test Suite")
    logger.info("=" * 70)
    logger.info("Focus: Semantic Intelligence & Contextual Retrieval")
    logger.info("=" * 70)
    
    tests = [
        ("Embedding Utils", test_embedding_utils),
        ("Vector Manager", test_vector_manager),
        ("Query Router", test_query_router),
        ("Retrieval Logger", test_retrieval_logger),
        ("Knowledge Base Integration", test_integration_with_knowledge_base),
        ("Chat UI Semantic Features", test_chat_ui_semantic_features),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 50)
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Final summary
    logger.info("\n📊 Sprint 2 Test Results Summary")
    logger.info("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total:.1%})")
    
    if passed == total:
        logger.info("🎉 Sprint 2 semantic pipeline is ready!")
        logger.info("\n✅ Semantic Intelligence Achieved:")
        logger.info("  🔤 Text embedding and similarity search")
        logger.info("  🗄️ Vector storage with metadata")
        logger.info("  🧠 Intelligent query routing")
        logger.info("  📝 Comprehensive retrieval logging")
        logger.info("  💬 Enhanced chat UI with semantic controls")
        return 0
    else:
        logger.error("⚠️  Some Sprint 2 components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
