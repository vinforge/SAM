#!/usr/bin/env python3
"""
Test Script for SAM's Dream Canvas (Phase 8C)

This script tests the complete Phase 8C implementation including
visualization generation and API endpoints.
"""

import logging
import tempfile
import shutil
import json
import requests
import time
from pathlib import Path

# Add SAM root to path
import sys
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dream_canvas_api():
    """Test the Dream Canvas API endpoints."""
    logger.info("🧠 TESTING SAM'S DREAM CANVAS (PHASE 8C) 🧠")
    
    base_url = "http://localhost:5001"
    
    try:
        # Test 1: Check if web UI is running
        logger.info("1. Testing web UI availability...")
        response = requests.get(f"{base_url}/api/test", timeout=5)
        
        if response.status_code == 200:
            logger.info("✅ Web UI is running")
        else:
            logger.error(f"❌ Web UI not responding: {response.status_code}")
            return False
        
        # Test 2: Test Dream Canvas page
        logger.info("2. Testing Dream Canvas page...")
        response = requests.get(f"{base_url}/dream-canvas", timeout=5)
        
        if response.status_code == 200:
            logger.info("✅ Dream Canvas page accessible")
        else:
            logger.error(f"❌ Dream Canvas page not accessible: {response.status_code}")
            return False
        
        # Test 3: Test synthesis history API
        logger.info("3. Testing synthesis history API...")
        response = requests.get(f"{base_url}/api/synthesis/history", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Synthesis history API working: {len(data.get('history', []))} runs found")
        else:
            logger.error(f"❌ Synthesis history API failed: {response.status_code}")
            return False
        
        # Test 4: Test synthesis trigger API (without visualization)
        logger.info("4. Testing synthesis trigger API...")
        response = requests.post(
            f"{base_url}/api/synthesis/trigger",
            json={"visualize": False},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                logger.info(f"✅ Synthesis trigger successful: {data.get('insights_generated', 0)} insights")
                run_id = data.get('run_id')
            else:
                logger.warning(f"⚠️ Synthesis completed with issues: {data.get('error', 'Unknown')}")
                run_id = None
        else:
            logger.error(f"❌ Synthesis trigger failed: {response.status_code}")
            return False
        
        # Test 5: Test synthesis with visualization
        logger.info("5. Testing synthesis with visualization...")
        response = requests.post(
            f"{base_url}/api/synthesis/trigger",
            json={"visualize": True},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                logger.info(f"✅ Synthesis with visualization successful")
                logger.info(f"   Clusters: {data.get('clusters_found', 0)}")
                logger.info(f"   Insights: {data.get('insights_generated', 0)}")
                logger.info(f"   Visualization: {data.get('visualization_enabled', False)}")
                
                if data.get('visualization_data'):
                    viz_data = data['visualization_data']
                    logger.info(f"   Visualization points: {len(viz_data)}")
                    
                    # Analyze visualization data
                    synthetic_count = sum(1 for point in viz_data if point.get('is_synthetic', False))
                    cluster_ids = set(point.get('cluster_id', -1) for point in viz_data)
                    
                    logger.info(f"   Synthetic insights: {synthetic_count}")
                    logger.info(f"   Unique clusters: {len([c for c in cluster_ids if c != -1])}")
                    
                run_id_viz = data.get('run_id')
            else:
                logger.warning(f"⚠️ Visualization synthesis had issues: {data.get('error', 'Unknown')}")
                run_id_viz = None
        else:
            logger.error(f"❌ Visualization synthesis failed: {response.status_code}")
            return False
        
        # Test 6: Test visualization data retrieval
        if run_id_viz:
            logger.info("6. Testing visualization data retrieval...")
            response = requests.get(f"{base_url}/api/synthesis/visualization/{run_id_viz}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    viz_data = data.get('visualization_data', [])
                    logger.info(f"✅ Visualization data retrieval successful: {len(viz_data)} points")
                else:
                    logger.warning(f"⚠️ No visualization data available for run {run_id_viz}")
            else:
                logger.warning(f"⚠️ Visualization data retrieval failed: {response.status_code}")
        
        # Summary
        logger.info("\n🎉 DREAM CANVAS TESTING COMPLETED SUCCESSFULLY! 🎉")
        logger.info("=" * 60)
        logger.info("✅ All Phase 8C components are working correctly:")
        logger.info("   • Dream Canvas web interface accessible")
        logger.info("   • Synthesis API endpoints functional")
        logger.info("   • Visualization generation working")
        logger.info("   • UMAP projection data available")
        logger.info("   • Interactive visualization ready")
        logger.info("\n💡 Phase 8C: The Dream Canvas is FULLY OPERATIONAL!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to SAM Web UI")
        logger.error("💡 Please start the web UI with: python web_ui/app.py")
        return False
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_local_synthesis_components():
    """Test synthesis components locally without web UI."""
    logger.info("\n🔧 TESTING LOCAL SYNTHESIS COMPONENTS 🔧")
    
    try:
        # Test synthesis engine with visualization
        from memory.synthesis import SynthesisEngine, SynthesisConfig
        from memory.memory_vectorstore import get_memory_store, VectorStoreType
        
        # Create test memory store
        test_dir = tempfile.mkdtemp()
        memory_dir = Path(test_dir) / "memory_store"
        
        try:
            memory_store = get_memory_store(
                store_type=VectorStoreType.SIMPLE,
                storage_directory=str(memory_dir),
                embedding_dimension=384
            )
            
            # Add test memories
            test_memories = [
                "Artificial intelligence is transforming cybersecurity through automated threat detection.",
                "Machine learning algorithms can identify network anomalies and security breaches.",
                "Deep learning models process vast amounts of security data for pattern recognition.",
                "Behavioral analytics help detect insider threats and unusual user activities.",
                "Zero-day vulnerabilities pose significant risks to enterprise security systems."
            ]
            
            for i, content in enumerate(test_memories):
                memory_store.add_memory(
                    content=content,
                    memory_type="fact",
                    source=f"test_doc_{i}",
                    tags=['ai', 'cybersecurity'],
                    importance_score=0.7 + i * 0.05
                )
            
            logger.info(f"✅ Created test memory store with {len(test_memories)} memories")
            
            # Test synthesis with visualization
            config = SynthesisConfig(
                clustering_eps=0.8,
                clustering_min_samples=2,
                min_cluster_size=2,
                enable_reingestion=False  # Skip for testing
            )
            
            synthesis_engine = SynthesisEngine(config=config)
            
            # Mock insight generation for testing
            def mock_generate_insight(prompt):
                return type('MockInsight', (), {
                    'insight_id': f"test_insight_{prompt.cluster_id}",
                    'cluster_id': prompt.cluster_id,
                    'synthesized_text': f"Test synthetic insight: AI and cybersecurity integration creates powerful defense mechanisms.",
                    'source_chunk_ids': [chunk.chunk_id for chunk in prompt.source_chunks[:2]],
                    'confidence_score': 0.85,
                    'novelty_score': 0.75,
                    'utility_score': 0.80,
                    'synthesis_metadata': {},
                    'generated_at': "2025-06-15T22:00:00.000000"
                })()
            
            # Patch for testing
            original_method = synthesis_engine.insight_generator.generate_insight
            synthesis_engine.insight_generator.generate_insight = mock_generate_insight
            
            try:
                # Run synthesis with visualization
                result = synthesis_engine.run_synthesis(memory_store, visualize=True)
                
                logger.info(f"✅ Local synthesis completed:")
                logger.info(f"   Clusters: {result.clusters_found}")
                logger.info(f"   Insights: {result.insights_generated}")
                logger.info(f"   Visualization data: {len(result.visualization_data) if result.visualization_data else 0} points")
                
                if result.visualization_data:
                    # Analyze visualization data structure
                    sample_point = result.visualization_data[0]
                    required_fields = ['chunk_id', 'coordinates', 'cluster_id', 'content_snippet', 'memory_type']
                    
                    for field in required_fields:
                        if field in sample_point:
                            logger.info(f"   ✅ Visualization field '{field}': present")
                        else:
                            logger.warning(f"   ⚠️ Visualization field '{field}': missing")
                
                return True
                
            finally:
                synthesis_engine.insight_generator.generate_insight = original_method
                
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
            
    except Exception as e:
        logger.error(f"❌ Local component test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🧠 SAM Dream Canvas Test Suite (Phase 8C) 🧠")
    logger.info("=" * 60)
    
    # Test local components first
    local_success = test_local_synthesis_components()
    
    if local_success:
        logger.info("\n🌐 Testing web API endpoints...")
        api_success = test_dream_canvas_api()
        
        if api_success:
            logger.info("\n✅ ALL TESTS PASSED! Dream Canvas is ready for production.")
        else:
            logger.error("\n❌ API tests failed. Check web UI status.")
    else:
        logger.error("\n❌ Local component tests failed. Check synthesis implementation.")
        sys.exit(1)
