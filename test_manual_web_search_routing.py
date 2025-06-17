#!/usr/bin/env python3
"""
Test Manual Web Search Intelligent Routing

This script tests whether SAM's Manual Web Search is properly using
the intelligent routing system instead of falling back to RSS-only mode.
"""

import logging
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_intelligent_web_system():
    """Test the intelligent web system initialization and routing."""
    try:
        logger.info("🧪 Testing Intelligent Web System...")
        
        # Test 1: Import and initialize
        from web_retrieval.intelligent_web_system import IntelligentWebSystem
        from web_retrieval.config import load_web_config
        
        # Load configuration
        web_config = load_web_config()
        logger.info(f"✅ Web config loaded: {web_config}")
        
        # Initialize with empty API keys (should fall back to DuckDuckGo)
        api_keys = {
            'serper': None,
            'newsapi': None
        }
        
        # Create intelligent web system
        intelligent_system = IntelligentWebSystem(api_keys=api_keys, config=web_config)
        logger.info("✅ Intelligent Web System initialized")
        
        # Test 2: Query routing
        test_query = "latest artificial intelligence developments"
        logger.info(f"🔍 Testing query routing for: '{test_query}'")
        
        # Get routing decision
        routing_decision = intelligent_system.router.route_query(test_query)
        logger.info(f"📋 Routing decision: {routing_decision}")
        
        # Test 3: Process query
        logger.info("🚀 Processing query through intelligent system...")
        result = intelligent_system.process_query(test_query)
        
        logger.info(f"📊 Result summary:")
        logger.info(f"  - Success: {result.get('success', False)}")
        logger.info(f"  - Tool used: {result.get('tool_used', 'unknown')}")
        logger.info(f"  - Error: {result.get('error', 'none')}")
        
        if result.get('success'):
            data = result.get('data', {})
            logger.info(f"  - Data keys: {list(data.keys())}")
            
            # Check content
            if 'chunks' in data:
                logger.info(f"  - Chunks found: {len(data['chunks'])}")
            elif 'articles' in data:
                logger.info(f"  - Articles found: {len(data['articles'])}")
            elif 'search_results' in data:
                logger.info(f"  - Search results found: {len(data['search_results'])}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Intelligent web system test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def test_cocoindex_availability():
    """Test if CocoIndex is available and working."""
    try:
        logger.info("🧪 Testing CocoIndex availability...")
        
        from web_retrieval.tools.cocoindex_tool import CocoIndexTool
        
        # Initialize CocoIndex tool
        cocoindex_tool = CocoIndexTool(
            api_key=None,  # No API key - should fall back to DuckDuckGo
            search_provider="duckduckgo",
            num_pages=3
        )
        
        logger.info(f"✅ CocoIndex tool initialized")
        logger.info(f"  - Available: {cocoindex_tool.cocoindex_available}")
        logger.info(f"  - Search provider: {cocoindex_tool.search_provider}")
        
        # Get tool info
        tool_info = cocoindex_tool.get_tool_info()
        logger.info(f"📋 Tool info: {tool_info}")
        
        return cocoindex_tool.cocoindex_available
        
    except Exception as e:
        logger.error(f"❌ CocoIndex test failed: {e}")
        return False

def test_manual_web_search_function():
    """Test the actual manual web search function from secure_streamlit_app.py."""
    try:
        logger.info("🧪 Testing Manual Web Search function...")
        
        # Import the function
        sys.path.insert(0, str(project_root))
        from secure_streamlit_app import perform_secure_web_search
        
        # Test query
        test_query = "current technology trends 2024"
        logger.info(f"🔍 Testing manual web search for: '{test_query}'")
        
        # Perform search
        result = perform_secure_web_search(test_query)
        
        logger.info(f"📊 Manual web search result:")
        logger.info(f"  - Success: {result.get('success', False)}")
        logger.info(f"  - Method: {result.get('method', 'unknown')}")
        logger.info(f"  - Tool used: {result.get('tool_used', 'unknown')}")
        logger.info(f"  - Error: {result.get('error', 'none')}")
        
        if result.get('success'):
            logger.info(f"  - Response length: {len(result.get('response', ''))}")
            logger.info(f"  - Sources count: {len(result.get('sources', []))}")
        
        # Check if it's using intelligent routing or falling back to RSS
        if result.get('method') == 'intelligent_web_system':
            logger.info("✅ Manual Web Search is using intelligent routing!")
        elif result.get('method') == 'rss_fallback':
            logger.warning("⚠️ Manual Web Search is falling back to RSS-only mode")
        else:
            logger.warning(f"⚠️ Manual Web Search using unknown method: {result.get('method')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Manual web search test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def main():
    """Run all tests to verify Manual Web Search intelligent routing."""
    logger.info("🚀 Starting Manual Web Search Routing Tests")
    logger.info("=" * 60)
    
    # Test 1: CocoIndex availability
    logger.info("\n📋 Test 1: CocoIndex Availability")
    cocoindex_available = test_cocoindex_availability()
    
    # Test 2: Intelligent Web System
    logger.info("\n📋 Test 2: Intelligent Web System")
    intelligent_result = test_intelligent_web_system()
    
    # Test 3: Manual Web Search Function
    logger.info("\n📋 Test 3: Manual Web Search Function")
    manual_search_result = test_manual_web_search_function()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    logger.info(f"CocoIndex Available: {'✅ Yes' if cocoindex_available else '❌ No'}")
    logger.info(f"Intelligent System: {'✅ Working' if intelligent_result and intelligent_result.get('success') else '❌ Failed'}")
    logger.info(f"Manual Web Search: {'✅ Working' if manual_search_result and manual_search_result.get('success') else '❌ Failed'}")
    
    if manual_search_result:
        method = manual_search_result.get('method', 'unknown')
        tool_used = manual_search_result.get('tool_used', 'unknown')
        
        if method == 'intelligent_web_system':
            logger.info(f"🎯 RESULT: Manual Web Search IS using intelligent routing with {tool_used}")
        else:
            logger.info(f"⚠️ RESULT: Manual Web Search is NOT using intelligent routing (method: {method})")
    
    logger.info("\n🏁 Test completed!")

if __name__ == "__main__":
    main()
