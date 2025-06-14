#!/usr/bin/env python3
"""
Debug script to test quarantine save functionality independently.
This helps isolate whether the issue is in the save function itself or the web search flow.
"""

import sys
import os
import logging
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

def test_quarantine_save_direct():
    """Test the quarantine save function directly."""
    logger.info("🧪 STARTING DIRECT QUARANTINE SAVE TEST 🧪")
    
    try:
        # Import the function
        from secure_streamlit_app import save_intelligent_web_to_quarantine
        logger.info("✅ Successfully imported save_intelligent_web_to_quarantine")
        
        # Create test data that mimics real web search results
        test_result = {
            'success': True,
            'tool_used': 'debug_test_tool',
            'data': {
                'articles': [
                    {
                        'title': 'Debug Test Article 1',
                        'content': 'This is test content for debugging the quarantine save functionality.',
                        'source': 'debug-test.com',
                        'url': 'https://debug-test.com/article1'
                    },
                    {
                        'title': 'Debug Test Article 2', 
                        'content': 'Another test article to verify multiple articles are saved correctly.',
                        'source': 'debug-test2.com',
                        'url': 'https://debug-test2.com/article2'
                    }
                ]
            },
            'metadata': {
                'query_time': datetime.now().isoformat(),
                'test_run': True
            }
        }
        
        test_query = f"Debug test query - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Test query: {test_query}")
        logger.info(f"Test result structure: {list(test_result.keys())}")
        
        # Check quarantine directory before
        quarantine_dir = Path("quarantine")
        before_files = list(quarantine_dir.glob("*.json")) if quarantine_dir.exists() else []
        logger.info(f"Files in quarantine before test: {len(before_files)}")
        
        # Call the save function
        logger.info("🚀 Calling save_intelligent_web_to_quarantine...")
        save_intelligent_web_to_quarantine(test_result, test_query)
        logger.info("✅ save_intelligent_web_to_quarantine completed without exception")
        
        # Check quarantine directory after
        after_files = list(quarantine_dir.glob("*.json")) if quarantine_dir.exists() else []
        logger.info(f"Files in quarantine after test: {len(after_files)}")
        
        # Find new files
        new_files = [f for f in after_files if f not in before_files]
        logger.info(f"New files created: {len(new_files)}")
        
        for new_file in new_files:
            logger.info(f"  ✅ Created: {new_file.name} ({new_file.stat().st_size} bytes)")
            
            # Verify file content
            try:
                import json
                with open(new_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"  ✅ File content verified, keys: {list(data.keys())}")
                logger.info(f"  ✅ Query in file: {data.get('query', 'NOT_FOUND')}")
                logger.info(f"  ✅ Tool used: {data.get('result', {}).get('tool_used', 'NOT_FOUND')}")
            except Exception as verify_error:
                logger.error(f"  ❌ File verification failed: {verify_error}")
        
        if new_files:
            logger.info("🎉 QUARANTINE SAVE TEST SUCCESSFUL! 🎉")
            return True
        else:
            logger.error("❌ QUARANTINE SAVE TEST FAILED - NO NEW FILES CREATED")
            return False
            
    except Exception as e:
        logger.error(f"❌ QUARANTINE SAVE TEST FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_web_search_flow():
    """Test the complete web search flow."""
    logger.info("🌐 STARTING WEB SEARCH FLOW TEST 🌐")
    
    try:
        # Import web search components
        from web_retrieval.intelligent_web_system import IntelligentWebSystem
        from web_retrieval.config import load_web_config
        logger.info("✅ Successfully imported web search components")
        
        # Load configuration
        web_config = load_web_config()
        api_keys = {}  # Empty for testing
        
        # Create system
        intelligent_web_system = IntelligentWebSystem(api_keys=api_keys, config=web_config)
        logger.info("✅ Created IntelligentWebSystem instance")
        
        # Test query
        test_query = "latest technology news test"
        logger.info(f"Testing query: {test_query}")
        
        # Process query
        result = intelligent_web_system.process_query(test_query)
        logger.info(f"Web search result success: {result.get('success', False)}")
        logger.info(f"Web search result keys: {list(result.keys())}")
        
        if result.get('success'):
            logger.info("✅ Web search successful - testing quarantine save...")
            
            # Test the save
            from secure_streamlit_app import save_intelligent_web_to_quarantine
            save_intelligent_web_to_quarantine(result, test_query)
            logger.info("✅ Quarantine save completed!")
            
            return True
        else:
            logger.error(f"❌ Web search failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ WEB SEARCH FLOW TEST FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all debug tests."""
    logger.info("=" * 60)
    logger.info("🔍 QUARANTINE SAVE DEBUG TESTS STARTING")
    logger.info("=" * 60)
    
    # Test 1: Direct quarantine save
    logger.info("\n" + "=" * 40)
    logger.info("TEST 1: Direct Quarantine Save")
    logger.info("=" * 40)
    test1_success = test_quarantine_save_direct()
    
    # Test 2: Web search flow
    logger.info("\n" + "=" * 40)
    logger.info("TEST 2: Web Search Flow")
    logger.info("=" * 40)
    test2_success = test_web_search_flow()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("🏁 DEBUG TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Test 1 (Direct Save): {'✅ PASSED' if test1_success else '❌ FAILED'}")
    logger.info(f"Test 2 (Web Search Flow): {'✅ PASSED' if test2_success else '❌ FAILED'}")
    
    if test1_success and test2_success:
        logger.info("🎉 ALL TESTS PASSED - Quarantine save functionality is working!")
    elif test1_success:
        logger.info("⚠️ Direct save works, but web search flow has issues")
    elif test2_success:
        logger.info("⚠️ Web search works, but direct save has issues")
    else:
        logger.info("❌ BOTH TESTS FAILED - Major issue with quarantine save functionality")

if __name__ == "__main__":
    main()
