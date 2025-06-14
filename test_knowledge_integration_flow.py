#!/usr/bin/env python3
"""
Test the complete knowledge integration and enhanced response flow.
This tests the critical missing pieces: knowledge integration and enhanced responses.
"""

import sys
import os
import logging
import json
import requests
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_knowledge_integration_pipeline():
    """Test if approved content gets integrated into knowledge base."""
    logger.info("🧠 TESTING KNOWLEDGE INTEGRATION PIPELINE 🧠")
    
    try:
        # Step 1: Check if we have approved content to integrate
        approved_dir = Path("approved")
        if not approved_dir.exists():
            approved_dir.mkdir()
            logger.info("Created approved directory")
        
        approved_files = list(approved_dir.glob("*.json"))
        logger.info(f"Found {len(approved_files)} approved files")
        
        # Step 2: Test consolidation manager
        try:
            from knowledge_consolidation.consolidation_manager import ConsolidationManager
            manager = ConsolidationManager()
            logger.info("✅ ConsolidationManager imported successfully")
            
            # Test consolidation process
            result = manager.consolidate_approved_content()
            logger.info(f"Consolidation result: {result}")
            
            if result.get('success'):
                logger.info(f"✅ Knowledge integration successful!")
                logger.info(f"  - Total items: {result.get('total_items', 0)}")
                logger.info(f"  - Integrated: {result.get('integrated_count', 0)}")
                logger.info(f"  - Failed: {result.get('failed_count', 0)}")
                return True
            else:
                logger.error(f"❌ Knowledge integration failed: {result.get('error')}")
                return False
                
        except ImportError as e:
            logger.error(f"❌ ConsolidationManager import failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Knowledge integration test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_vetting_to_approval_flow():
    """Test the vetting → approval → integration flow."""
    logger.info("🛡️ TESTING VETTING TO APPROVAL FLOW 🛡️")
    
    try:
        # Step 1: Check if we have content in quarantine
        quarantine_dir = Path("quarantine")
        intelligent_web_files = list(quarantine_dir.glob("intelligent_web_*.json"))
        
        if not intelligent_web_files:
            logger.warning("⚠️ No intelligent_web files in quarantine to test with")
            return False
        
        # Step 2: Test vetting process
        from secure_streamlit_app import trigger_vetting_process
        logger.info("Testing vetting process...")
        
        vetting_result = trigger_vetting_process()
        logger.info(f"Vetting result: {vetting_result}")
        
        # Step 3: Check if files moved to vetted directory
        vetted_dir = Path("vetted")
        if vetted_dir.exists():
            vetted_files = list(vetted_dir.glob("*.json"))
            logger.info(f"Files in vetted directory: {len(vetted_files)}")
            
            if vetted_files:
                logger.info("✅ Content successfully moved to vetted directory")
                return True
            else:
                logger.error("❌ No files found in vetted directory after vetting")
                return False
        else:
            logger.error("❌ Vetted directory doesn't exist")
            return False
            
    except Exception as e:
        logger.error(f"❌ Vetting to approval test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_enhanced_response_generation():
    """Test if SAM provides enhanced responses after knowledge integration."""
    logger.info("🚀 TESTING ENHANCED RESPONSE GENERATION 🚀")
    
    try:
        # Step 1: Test the re-query mechanism
        test_query = "What are the latest AI developments?"
        
        logger.info(f"Testing enhanced response for: '{test_query}'")
        
        # Step 2: Call the chat API (simulating reQueryWithNewKnowledge)
        url = "http://localhost:5001/api/chat"
        response = requests.post(
            url,
            json={"message": test_query},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Chat API response received")
            logger.info(f"Response type: {data.get('type', 'normal')}")
            
            # Check if response includes web-sourced information
            response_text = data.get('response', '')
            
            # Look for indicators of enhanced knowledge
            enhancement_indicators = [
                'based on', 'according to', 'recent', 'latest', 'current',
                'sources', 'web', 'news', 'today', '2025'
            ]
            
            found_indicators = [ind for ind in enhancement_indicators if ind.lower() in response_text.lower()]
            
            if found_indicators:
                logger.info(f"✅ Enhanced response detected! Indicators: {found_indicators}")
                logger.info(f"Response preview: {response_text[:200]}...")
                return True
            else:
                logger.warning("⚠️ Response doesn't show clear enhancement indicators")
                logger.info(f"Response preview: {response_text[:200]}...")
                return False
                
        else:
            logger.error(f"❌ Chat API failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Enhanced response test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_memory_store_integration():
    """Test if new knowledge is accessible in memory store."""
    logger.info("💾 TESTING MEMORY STORE INTEGRATION 💾")
    
    try:
        # Step 1: Import memory store
        from memory.memory_vectorstore import get_memory_store, VectorStoreType
        
        memory_store = get_memory_store(
            store_type=VectorStoreType.CHROMA,
            storage_directory="memory_store",
            embedding_dimension=384
        )
        
        logger.info("✅ Memory store imported successfully")
        
        # Step 2: Check total memories
        all_memories = memory_store.get_all_memories()
        logger.info(f"Total memories in store: {len(all_memories)}")
        
        # Step 3: Search for recent web content
        test_queries = [
            "AI developments",
            "latest technology",
            "quantum computing",
            "artificial intelligence"
        ]
        
        enhanced_memories_found = False
        
        for query in test_queries:
            try:
                search_results = memory_store.search_memories(query, max_results=5)
                logger.info(f"Search '{query}': {len(search_results)} results")
                
                # Check if any results are from recent web searches
                for result in search_results:
                    source = getattr(result, 'source', '')
                    timestamp = getattr(result, 'timestamp', '')
                    
                    if 'web' in source.lower() or 'intelligent' in source.lower():
                        logger.info(f"✅ Found web-sourced memory: {source}")
                        enhanced_memories_found = True
                        
            except Exception as e:
                logger.warning(f"Search failed for '{query}': {e}")
        
        if enhanced_memories_found:
            logger.info("✅ Web-sourced content found in memory store!")
            return True
        else:
            logger.warning("⚠️ No web-sourced content found in memory store")
            return False
            
    except Exception as e:
        logger.error(f"❌ Memory store integration test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_complete_end_to_end_flow():
    """Test the complete end-to-end flow from web search to enhanced response."""
    logger.info("🔄 TESTING COMPLETE END-TO-END FLOW 🔄")
    
    try:
        # Step 1: Trigger a web search
        logger.info("Step 1: Triggering web search...")
        search_response = requests.post(
            "http://localhost:5001/api/trigger-web-search",
            json={
                "search_query": "latest breakthrough in AI technology 2025",
                "original_query": "What are the latest AI breakthroughs?"
            },
            timeout=60
        )
        
        if search_response.status_code != 200:
            logger.error(f"❌ Web search failed: {search_response.status_code}")
            return False
        
        search_data = search_response.json()
        logger.info(f"✅ Web search completed: {search_data.get('status')}")
        
        # Step 2: Wait a moment for file creation
        import time
        time.sleep(2)
        
        # Step 3: Check quarantine
        quarantine_files = list(Path("quarantine").glob("intelligent_web_*.json"))
        logger.info(f"Files in quarantine: {len(quarantine_files)}")
        
        # Step 4: Test enhanced response (simulating the frontend flow)
        logger.info("Step 4: Testing enhanced response...")
        chat_response = requests.post(
            "http://localhost:5001/api/chat",
            json={"message": "What are the latest AI breakthroughs?"},
            timeout=30
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            response_text = chat_data.get('response', '')
            
            # Check if response shows enhancement
            if any(indicator in response_text.lower() for indicator in ['recent', 'latest', 'current', '2025']):
                logger.info("✅ Enhanced response detected in end-to-end test!")
                return True
            else:
                logger.warning("⚠️ Response doesn't show clear enhancement")
                return False
        else:
            logger.error(f"❌ Chat response failed: {chat_response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ End-to-end test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all knowledge integration and enhanced response tests."""
    logger.info("=" * 80)
    logger.info("🧠 KNOWLEDGE INTEGRATION & ENHANCED RESPONSE TESTS")
    logger.info("=" * 80)
    
    tests = [
        ("Knowledge Integration Pipeline", test_knowledge_integration_pipeline),
        ("Vetting to Approval Flow", test_vetting_to_approval_flow),
        ("Enhanced Response Generation", test_enhanced_response_generation),
        ("Memory Store Integration", test_memory_store_integration),
        ("Complete End-to-End Flow", test_complete_end_to_end_flow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"TEST: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("🏁 KNOWLEDGE INTEGRATION TEST SUMMARY")
    logger.info(f"{'='*80}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    # Analysis
    if results.get("Knowledge Integration Pipeline", False):
        logger.info("✅ Knowledge integration infrastructure is working")
    else:
        logger.info("❌ Knowledge integration infrastructure needs fixes")
    
    if results.get("Enhanced Response Generation", False):
        logger.info("✅ Enhanced response generation is working")
    else:
        logger.info("❌ Enhanced response generation needs investigation")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - Complete knowledge enhancement flow working!")
    elif passed > total // 2:
        logger.info("⚠️ PARTIAL SUCCESS - Some components working, others need fixes")
    else:
        logger.info("❌ MAJOR ISSUES - Knowledge integration and enhancement flow broken")

if __name__ == "__main__":
    main()
