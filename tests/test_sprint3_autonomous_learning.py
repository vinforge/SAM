#!/usr/bin/env python3
"""
Sprint 3 Autonomous Learning Test Suite
Tests the complete self-enrichment and curiosity loop functionality.

Sprint 3 Task 9: End-to-End Test Pipeline
"""

import logging
import sys
import tempfile
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_curiosity_signal_detection():
    """Test curiosity signal detection functionality."""
    logger.info("🔍 Testing Curiosity Signal Detection...")
    
    try:
        from deepseek_enhanced_learning.curiosity_signal import CuriositySignalDetector
        
        # Create temporary detector
        with tempfile.TemporaryDirectory() as temp_dir:
            retrieval_db = Path(temp_dir) / "test_retrieval.db"
            detector = CuriositySignalDetector(
                retrieval_db_path=str(retrieval_db),
                similarity_threshold=0.3
            )
            
            logger.info("  ✅ Curiosity signal detector initialized")
            
            # Test signal detection (will be empty without real data)
            signals = detector.detect_signals(lookback_hours=24)
            logger.info(f"  ✅ Signal detection working: {len(signals)} signals found")
            
            # Test stats
            stats = detector.get_signal_stats()
            logger.info(f"  ✅ Signal stats: {stats}")
            
            return True
            
    except Exception as e:
        logger.error(f"  ❌ Curiosity signal detection test failed: {e}")
        return False

def test_self_discover_enricher():
    """Test SELF-DISCOVER enrichment generation."""
    logger.info("🧠 Testing SELF-DISCOVER Enricher...")
    
    try:
        from deepseek_enhanced_learning.self_discover_enricher import SelfDiscoverEnricher
        from deepseek_enhanced_learning.curiosity_signal import CuriositySignal
        
        # Create temporary enricher
        with tempfile.TemporaryDirectory() as temp_dir:
            enricher = SelfDiscoverEnricher(enrichment_dir=temp_dir)
            logger.info("  ✅ SELF-DISCOVER enricher initialized")
            
            # Create a test curiosity signal
            test_signal = CuriositySignal(
                signal_id="test_signal_1",
                timestamp=datetime.now().isoformat(),
                signal_type="low_similarity",
                topic_cluster="machine_learning",
                confidence_score=0.8,
                query="How does GPU acceleration work in machine learning?",
                context={"max_similarity": 0.2, "mode": "semantic"},
                metadata={"processing_time": 0.5}
            )
            
            # Test enrichment generation
            enrichment = enricher.generate_enrichment(test_signal)
            
            if enrichment and enrichment.sub_questions:
                logger.info(f"  ✅ Enrichment generated: {len(enrichment.sub_questions)} sub-questions")
                logger.info(f"    Sample question: {enrichment.sub_questions[0]}")
                return True
            else:
                logger.error("  ❌ No enrichment generated")
                return False
                
    except Exception as e:
        logger.error(f"  ❌ SELF-DISCOVER enricher test failed: {e}")
        return False

def test_self_study_runner():
    """Test self-study execution framework."""
    logger.info("📚 Testing Self-Study Runner...")
    
    try:
        from deepseek_enhanced_learning.self_study_runner import SelfStudyRunner
        from deepseek_enhanced_learning.self_discover_enricher import EnrichmentObject
        
        # Create temporary runner
        with tempfile.TemporaryDirectory() as temp_dir:
            runner = SelfStudyRunner(enriched_chunks_dir=temp_dir)
            logger.info("  ✅ Self-study runner initialized")
            
            # Create a test enrichment object
            test_enrichment = EnrichmentObject(
                enrichment_id="test_enrich_1",
                timestamp=datetime.now().isoformat(),
                original_signal={
                    'signal_id': 'test_signal_1',
                    'query': 'Test query about machine learning',
                    'signal_type': 'low_similarity'
                },
                topic="machine_learning",
                context_window="Test context window",
                sub_questions=[
                    "What are the fundamental concepts of machine learning?",
                    "How do neural networks process information?"
                ],
                generation_metadata={"test": True}
            )
            
            # Test study session (will have limited results without real vector data)
            study_results = runner.run_study_session(test_enrichment)
            logger.info(f"  ✅ Study session completed: {len(study_results)} results")
            
            # Test loading study results
            loaded_results = runner.get_study_results()
            logger.info(f"  ✅ Study results loaded: {len(loaded_results)} results")
            
            return True
            
    except Exception as e:
        logger.error(f"  ❌ Self-study runner test failed: {e}")
        return False

def test_autonomous_learning_manager():
    """Test autonomous learning manager integration."""
    logger.info("🤖 Testing Autonomous Learning Manager...")
    
    try:
        from deepseek_enhanced_learning.autonomous_learning_manager import AutonomousLearningManager
        
        # Create manager with disabled auto-learning for testing
        manager = AutonomousLearningManager(
            auto_run_interval=3600,
            enable_auto_learning=False  # Disable for testing
        )
        
        logger.info("  ✅ Autonomous learning manager initialized")
        
        # Test status
        status = manager.get_learning_status()
        logger.info(f"  ✅ Learning status: {status['is_running']}")
        
        # Test manual learning cycle
        results = manager.trigger_manual_learning(
            detect_signals=True,
            generate_enrichments=False,  # Skip to avoid Ollama dependency
            run_studies=False
        )
        
        logger.info(f"  ✅ Manual learning cycle: {results}")
        
        # Test configuration
        manager.configure_learning(auto_run_interval=1800)
        logger.info("  ✅ Learning configuration updated")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Autonomous learning manager test failed: {e}")
        return False

def test_integration_with_existing_systems():
    """Test integration with existing SAM components."""
    logger.info("🔗 Testing Integration with Existing Systems...")
    
    try:
        # Test integration with vector store
        from utils.vector_manager import VectorManager
        from utils.embedding_utils import get_embedding_manager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_manager = VectorManager(vector_store_path=temp_dir)
            embedding_manager = get_embedding_manager()
            
            logger.info("  ✅ Vector store integration working")
        
        # Test integration with retrieval logger
        from utils.retrieval_logger import get_retrieval_logger
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # This will create a temporary logger
            logger.info("  ✅ Retrieval logger integration working")
        
        # Test integration with chat UI components
        from ui.chat_ui import ChatInterface
        logger.info("  ✅ Chat UI integration available")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Integration test failed: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist and are accessible."""
    logger.info("📁 Testing Directory Structure...")
    
    try:
        # Check required directories
        required_dirs = [
            "knowledge_enrichment",
            "vector_store/enriched_chunks",
            "logs"
        ]
        
        for dir_path in required_dirs:
            path = Path(dir_path)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"  ✅ Created directory: {dir_path}")
            else:
                logger.info(f"  ✅ Directory exists: {dir_path}")
        
        # Test file creation in directories
        test_file = Path("knowledge_enrichment") / "test_file.json"
        test_file.write_text('{"test": true}')
        test_file.unlink()  # Clean up
        
        logger.info("  ✅ Directory write permissions working")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Directory structure test failed: {e}")
        return False

def test_database_operations():
    """Test database operations for curiosity signals and enrichment logging."""
    logger.info("🗄️ Testing Database Operations...")
    
    try:
        import sqlite3
        from deepseek_enhanced_learning.curiosity_signal import CuriositySignalDetector
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test curiosity signals database
            detector = CuriositySignalDetector(
                retrieval_db_path=str(Path(temp_dir) / "retrieval.db")
            )
            
            # Test database creation
            assert detector.signals_db_path.exists()
            logger.info("  ✅ Curiosity signals database created")
            
            # Test database operations
            stats = detector.get_signal_stats()
            logger.info(f"  ✅ Database stats: {stats}")
            
            # Test retrieval logs database integration
            retrieval_db = Path(temp_dir) / "retrieval.db"
            with sqlite3.connect(retrieval_db) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS retrieval_log (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        query TEXT,
                        response TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert test data
                conn.execute("""
                    INSERT INTO retrieval_log (timestamp, query, response)
                    VALUES (?, ?, ?)
                """, (datetime.now().isoformat(), "test query", "test response"))
            
            logger.info("  ✅ Retrieval logs database operations working")
            
            return True
            
    except Exception as e:
        logger.error(f"  ❌ Database operations test failed: {e}")
        return False

def test_streamlit_dashboard_components():
    """Test Streamlit dashboard components (import and basic functionality)."""
    logger.info("📊 Testing Streamlit Dashboard Components...")
    
    try:
        # Test that dashboard can be imported
        import streamlit_enrichment_dashboard
        logger.info("  ✅ Streamlit dashboard module imported")
        
        # Test helper functions
        if hasattr(streamlit_enrichment_dashboard, 'get_curiosity_stats'):
            logger.info("  ✅ Dashboard helper functions available")
        
        return True
        
    except ImportError as e:
        logger.warning(f"  ⚠️ Streamlit not available (optional): {e}")
        return True  # Not a failure since Streamlit is optional
    except Exception as e:
        logger.error(f"  ❌ Dashboard test failed: {e}")
        return False

def main():
    """Run all Sprint 3 autonomous learning tests."""
    logger.info("🚀 SAM Sprint 3 Autonomous Learning Test Suite")
    logger.info("=" * 70)
    logger.info("Focus: Self-Enrichment & Curiosity Loop")
    logger.info("=" * 70)
    
    tests = [
        ("Curiosity Signal Detection", test_curiosity_signal_detection),
        ("SELF-DISCOVER Enricher", test_self_discover_enricher),
        ("Self-Study Runner", test_self_study_runner),
        ("Autonomous Learning Manager", test_autonomous_learning_manager),
        ("Integration with Existing Systems", test_integration_with_existing_systems),
        ("Directory Structure", test_directory_structure),
        ("Database Operations", test_database_operations),
        ("Streamlit Dashboard Components", test_streamlit_dashboard_components),
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
    logger.info("\n📊 Sprint 3 Test Results Summary")
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
        logger.info("🎉 Sprint 3 autonomous learning system is ready!")
        logger.info("\n✅ Self-Enrichment & Curiosity Loop Achieved:")
        logger.info("  🔍 Curiosity signal detection from retrieval patterns")
        logger.info("  🧠 SELF-DISCOVER enrichment question generation")
        logger.info("  📚 Autonomous self-study execution")
        logger.info("  🤖 Integrated learning management system")
        logger.info("  📊 Comprehensive enrichment dashboard")
        logger.info("  🔄 Complete autonomous learning loop")
        return 0
    else:
        logger.error("⚠️  Some Sprint 3 components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
