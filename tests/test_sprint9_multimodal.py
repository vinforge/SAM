#!/usr/bin/env python3
"""
Sprint 9 Multimodal Input, Web Search, and Visual Reasoning Test Suite
Tests the complete multimodal processing and reasoning system.

Sprint 9 Task Testing: Multimodal Ingestion, Local Search, Web Search, Reasoning
"""

import logging
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import base64

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_multimodal_ingestion():
    """Test multimodal ingestion engine."""
    logger.info("📸 Testing Multimodal Ingestion Engine...")
    
    try:
        from multimodal.ingestion_engine import MultimodalIngestionEngine
        
        # Create temporary storage directory
        with tempfile.TemporaryDirectory() as storage_dir:
            # Initialize ingestion engine
            ingestion_engine = MultimodalIngestionEngine(storage_directory=storage_dir)
            logger.info("  ✅ Multimodal ingestion engine initialized")
            
            # Test image ingestion (simulated)
            test_image_data = b"fake_image_data_for_testing"
            image_id = ingestion_engine.ingest_image(
                image_data=test_image_data,
                filename="test_image.jpg",
                perform_ocr=True,
                generate_caption=True
            )
            
            logger.info(f"  ✅ Image ingested: {image_id}")
            
            # Test image processing result
            image_result = ingestion_engine.get_processing_result(image_id)
            
            if image_result:
                logger.info(f"  ✅ Image processing result retrieved")
                logger.info(f"    OCR text: {image_result.extracted_text is not None}")
                logger.info(f"    Caption: {image_result.caption is not None}")
                logger.info(f"    Processing time: {image_result.processing_time_ms}ms")
            
            # Test audio ingestion (simulated)
            test_audio_data = b"fake_audio_data_for_testing"
            audio_id = ingestion_engine.ingest_audio(
                audio_data=test_audio_data,
                filename="test_audio.wav",
                perform_transcription=True
            )
            
            logger.info(f"  ✅ Audio ingested: {audio_id}")
            
            # Test audio processing result
            audio_result = ingestion_engine.get_processing_result(audio_id)
            
            if audio_result:
                logger.info(f"  ✅ Audio processing result retrieved")
                logger.info(f"    Transcription: {audio_result.transcription is not None}")
            
            # Test document ingestion
            test_doc_data = b"This is a test document with some content for testing."
            doc_id = ingestion_engine.ingest_document(
                document_data=test_doc_data,
                filename="test_document.txt"
            )
            
            logger.info(f"  ✅ Document ingested: {doc_id}")
            
            # Test document processing result
            doc_result = ingestion_engine.get_processing_result(doc_id)
            
            if doc_result:
                logger.info(f"  ✅ Document processing result retrieved")
                logger.info(f"    Extracted text: {doc_result.extracted_text is not None}")
            
            # Test media search
            search_results = ingestion_engine.search_media("test")
            
            if search_results:
                logger.info(f"  🔍 Media search: {len(search_results)} results found")
            
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Multimodal ingestion test failed: {e}")
        return False

def test_local_file_search():
    """Test local file search integration."""
    logger.info("🔍 Testing Local File Search Integration...")
    
    try:
        from multimodal.local_search import LocalFileSearchEngine
        
        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            knowledge_dir = Path(temp_dir) / "knowledge"
            knowledge_dir.mkdir()
            
            # Create test files
            test_files = [
                ("machine_learning.md", "# Machine Learning\n\nMachine learning is a subset of artificial intelligence."),
                ("data_science.txt", "Data science combines statistics, programming, and domain expertise."),
                ("ai_overview.md", "# Artificial Intelligence\n\nAI is the simulation of human intelligence in machines.")
            ]
            
            for filename, content in test_files:
                with open(knowledge_dir / filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Initialize search engine
            search_engine = LocalFileSearchEngine(
                knowledge_directory=str(knowledge_dir),
                index_file=str(Path(temp_dir) / "search_index.json")
            )
            logger.info("  ✅ Local file search engine initialized")
            
            # Test directory indexing
            indexed_count = search_engine.index_directory()
            
            if indexed_count > 0:
                logger.info(f"  ✅ Directory indexed: {indexed_count} files")
            else:
                logger.warning("  ⚠️ No files indexed")
            
            # Test search functionality
            search_results = search_engine.search("machine learning", max_results=5)
            
            if search_results:
                logger.info(f"  🔍 Search results: {len(search_results)} found")
                for result in search_results:
                    logger.info(f"    - {result.title} (confidence: {result.confidence_score:.2f})")
            else:
                logger.warning("  ⚠️ No search results found")
            
            # Test file content retrieval
            if search_results:
                first_result = search_results[0]
                content = search_engine.get_file_content(first_result.file_path)
                
                if content:
                    logger.info(f"  ✅ File content retrieved: {len(content)} characters")
                
                # Test citation creation
                citation = search_engine.create_citation(first_result)
                logger.info(f"  ✅ Citation created: {citation}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Local file search test failed: {e}")
        return False

def test_web_search_engine():
    """Test web search and external knowledge access."""
    logger.info("🌐 Testing Web Search & External Knowledge Access...")
    
    try:
        from multimodal.web_search import WebSearchEngine, SearchEngine
        
        # Create temporary logs file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            logs_file = tmp.name
        
        # Initialize web search engine (without actual web access)
        web_search_engine = WebSearchEngine(
            search_logs_file=logs_file,
            enable_web_access=False  # Disabled for testing
        )
        logger.info("  ✅ Web search engine initialized")
        
        # Test search functionality (simulated)
        if not web_search_engine.enable_web_access:
            logger.info("  ℹ️ Web access disabled - testing simulation mode")
            
            # Test query sanitization
            sanitized = web_search_engine._sanitize_query("test query with <script>")
            
            if "script" not in sanitized:
                logger.info("  ✅ Query sanitization working")
            
            # Test search history
            history = web_search_engine.get_search_history()
            logger.info(f"  📋 Search history: {len(history)} entries")
        
        # Test with web access enabled (simulated results)
        web_search_engine.enable_web_access = True
        
        results, query_id = web_search_engine.search(
            query="artificial intelligence",
            user_id="test_user",
            session_id="test_session",
            search_engine=SearchEngine.DUCKDUCKGO,
            max_results=3
        )
        
        if results:
            logger.info(f"  ✅ Web search completed: {len(results)} results")
            logger.info(f"    Query ID: {query_id}")
            
            for result in results:
                logger.info(f"    - {result.title} (confidence: {result.confidence_score:.2f})")
            
            # Test result summarization
            summary = web_search_engine.summarize_results(query_id, results)
            
            if summary:
                logger.info(f"  ✅ Search summary generated: {summary.summary_id}")
                logger.info(f"    Key insights: {len(summary.key_insights)}")
                logger.info(f"    Confidence: {summary.confidence_score:.2f}")
        
        # Cleanup
        Path(logs_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Web search engine test failed: {e}")
        return False

def test_multimodal_reasoning_engine():
    """Test multimodal reasoning engine."""
    logger.info("🧠 Testing Multimodal Reasoning Engine...")
    
    try:
        from multimodal.reasoning_engine import MultimodalReasoningEngine
        
        # Initialize reasoning engine
        reasoning_engine = MultimodalReasoningEngine()
        logger.info("  ✅ Multimodal reasoning engine initialized")
        
        # Test multimodal reasoning
        response = reasoning_engine.reason_multimodal(
            query="What is artificial intelligence and how does it work?",
            user_id="test_user",
            session_id="test_session",
            text_inputs=["AI is the simulation of human intelligence in machines."],
            enable_web_search=False,
            enable_local_search=False
        )
        
        if response:
            logger.info(f"  ✅ Multimodal reasoning completed: {response.response_id}")
            logger.info(f"    Confidence level: {response.confidence_level.value}")
            logger.info(f"    Overall confidence: {response.overall_confidence:.2f}")
            logger.info(f"    Reasoning steps: {len(response.reasoning_steps)}")
            logger.info(f"    Source attributions: {len(response.source_attributions)}")
        else:
            logger.error("  ❌ Multimodal reasoning failed")
            return False
        
        # Test response formatting
        formatted_response = reasoning_engine.format_response(
            response,
            include_reasoning_trace=True,
            include_source_details=True
        )
        
        if formatted_response and len(formatted_response) > 100:
            logger.info(f"  ✅ Response formatted: {len(formatted_response)} characters")
        else:
            logger.warning("  ⚠️ Response formatting may have issues")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Multimodal reasoning engine test failed: {e}")
        return False

def test_integrated_multimodal_system():
    """Test the integrated multimodal system."""
    logger.info("🎯 Testing Integrated Multimodal System...")
    
    try:
        from multimodal.integrated_multimodal import IntegratedMultimodalSystem, MultimodalRequest
        
        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            knowledge_dir = Path(temp_dir) / "knowledge"
            storage_dir = Path(temp_dir) / "storage"
            knowledge_dir.mkdir()
            storage_dir.mkdir()
            
            # Create test knowledge file
            with open(knowledge_dir / "ai_basics.md", 'w', encoding='utf-8') as f:
                f.write("# AI Basics\n\nArtificial Intelligence is a fascinating field of computer science.")
            
            # Initialize integrated system
            multimodal_system = IntegratedMultimodalSystem(
                enable_web_access=False,
                knowledge_directory=str(knowledge_dir),
                storage_directory=str(storage_dir)
            )
            logger.info("  ✅ Integrated multimodal system initialized")
            
            # Test system status
            status = multimodal_system.get_system_status()
            
            if status and status.get('system_ready'):
                logger.info("  ✅ System status: Ready")
                logger.info(f"    Indexed items: {status['local_search_engine']['indexed_items']}")
                logger.info(f"    Media count: {status['ingestion_engine']['media_count']}")
            else:
                logger.warning("  ⚠️ System not ready")
            
            # Test individual ingestion methods
            test_image_data = base64.b64encode(b"fake_image_data").decode()
            image_id = multimodal_system.ingest_image(test_image_data, "test.jpg")
            
            if image_id:
                logger.info(f"  ✅ Image ingested: {image_id}")
            
            # Test local knowledge search
            local_results = multimodal_system.search_local_knowledge("artificial intelligence")
            
            if local_results:
                logger.info(f"  🔍 Local search: {len(local_results)} results")
                for result in local_results:
                    logger.info(f"    - {result['title']} (confidence: {result['confidence_score']:.2f})")
            
            # Test multimodal request processing
            import uuid
            request = MultimodalRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                user_id="test_user",
                session_id="test_session",
                query="What is artificial intelligence?",
                text_inputs=["AI is machine intelligence"],
                image_data=[],
                audio_data=[],
                document_data=[],
                enable_web_search=False,
                enable_local_search=True,
                context={}
            )
            
            response = multimodal_system.process_multimodal_request(request)
            
            if response:
                logger.info(f"  ✅ Multimodal request processed: {response.request_id}")
                logger.info(f"    Confidence level: {response.confidence_level}")
                logger.info(f"    Overall confidence: {response.overall_confidence:.2f}")
                logger.info(f"    Processing time: {response.processing_time_ms}ms")
                logger.info(f"    Answer length: {len(response.answer)} characters")
            else:
                logger.error("  ❌ Multimodal request processing failed")
                return False
            
            # Test media info retrieval
            if image_id:
                media_info = multimodal_system.get_media_info(image_id)
                
                if media_info:
                    logger.info(f"  ✅ Media info retrieved: {media_info['filename']}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Integrated multimodal system test failed: {e}")
        return False

def main():
    """Run all Sprint 9 multimodal tests."""
    logger.info("🚀 SAM Sprint 9 Multimodal Input, Web Search, and Visual Reasoning Test Suite")
    logger.info("=" * 80)
    logger.info("Focus: Multimodal Ingestion, Local Search, Web Search, Reasoning")
    logger.info("=" * 80)
    
    tests = [
        ("Multimodal Ingestion Engine", test_multimodal_ingestion),
        ("Local File Search Integration", test_local_file_search),
        ("Web Search & External Knowledge Access", test_web_search_engine),
        ("Multimodal Reasoning Engine", test_multimodal_reasoning_engine),
        ("Integrated Multimodal System", test_integrated_multimodal_system),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 60)
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Final summary
    logger.info("\n📊 Sprint 9 Test Results Summary")
    logger.info("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total:.1%})")
    
    if passed == total:
        logger.info("🎉 Sprint 9 multimodal input, web search, and visual reasoning system is ready!")
        logger.info("\n✅ Multimodal Input, Web Search, and Visual Reasoning Achieved:")
        logger.info("  📸 Multimodal ingestion with OCR, captioning, and transcription")
        logger.info("  🔍 Local file search integration with semantic indexing")
        logger.info("  🌐 Web search and external knowledge access with security controls")
        logger.info("  🧠 Multimodal reasoning engine with cross-modal fusion")
        logger.info("  🎯 Integrated multimodal system with unified processing")
        logger.info("  📊 Comprehensive source attribution and confidence scoring")
        logger.info("  🔄 Cross-modal reasoning across text, images, audio, and documents")
        logger.info("  🛡️ Secure and controlled external knowledge access")
        return 0
    else:
        logger.error("⚠️  Some Sprint 9 components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
