#!/usr/bin/env python3
"""
Test script for Phase 8.5 CocoIndex Integration

This script tests the new CocoIndex tool integration with SAM's
intelligent web retrieval system.

Usage:
    python test_cocoindex_integration.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_cocoindex_tool():
    """Test the CocoIndex tool directly."""
    try:
        from web_retrieval.tools.cocoindex_tool import CocoIndexTool
        
        logger.info("Testing CocoIndex tool initialization...")
        
        # Test without API key (should use fallback)
        tool = CocoIndexTool(
            api_key=None,
            search_provider="duckduckgo",
            num_pages=3
        )
        
        logger.info(f"Tool initialized: {tool.cocoindex_available}")
        logger.info(f"Tool info: {tool.get_tool_info()}")
        
        # Test search
        async def test_search():
            logger.info("Testing intelligent search...")
            result = await tool.intelligent_search("artificial intelligence news")
            logger.info(f"Search result: {result}")
            return result
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_search())
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"CocoIndex tool test failed: {e}")
        return {'success': False, 'error': str(e)}

def test_query_router():
    """Test the updated query router."""
    try:
        from web_retrieval.query_router import QueryRouter
        
        logger.info("Testing updated query router...")
        
        router = QueryRouter()
        
        # Test different query types
        test_queries = [
            "latest AI news",
            "what is machine learning",
            "technology trends 2024",
            "https://example.com/article"
        ]
        
        for query in test_queries:
            routing = router.route_query(query)
            logger.info(f"Query: '{query}' -> Tool: {routing['primary_tool']}")
            logger.info(f"  Reasoning: {routing['reasoning']}")
            logger.info(f"  Confidence: {routing['confidence']}")
            logger.info(f"  Fallback: {routing['fallback_chain']}")
            print()
        
        return True
        
    except Exception as e:
        logger.error(f"Query router test failed: {e}")
        return False

def test_intelligent_web_system():
    """Test the intelligent web system with cocoindex."""
    try:
        from web_retrieval.intelligent_web_system import IntelligentWebSystem
        
        logger.info("Testing intelligent web system...")
        
        # Test configuration
        api_keys = {
            'serper': None,  # No API key for testing
            'newsapi': None
        }
        
        config = {
            'cocoindex_search_provider': 'duckduckgo',
            'cocoindex_num_pages': 3,
            'web_retrieval_provider': 'cocoindex'
        }
        
        system = IntelligentWebSystem(api_keys=api_keys, config=config)
        
        logger.info(f"System info: {system.get_system_info()}")
        
        # Test query processing
        test_query = "artificial intelligence latest developments"
        logger.info(f"Processing query: '{test_query}'")
        
        result = system.process_query(test_query)
        logger.info(f"Query result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Intelligent web system test failed: {e}")
        return {'success': False, 'error': str(e)}

def test_configuration():
    """Test the configuration management."""
    try:
        from config.config_manager import ConfigManager
        
        logger.info("Testing configuration management...")
        
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        logger.info(f"Web retrieval provider: {config.web_retrieval_provider}")
        logger.info(f"CocoIndex search provider: {config.cocoindex_search_provider}")
        logger.info(f"CocoIndex num pages: {config.cocoindex_num_pages}")
        logger.info(f"Serper API key configured: {bool(config.serper_api_key)}")
        logger.info(f"NewsAPI key configured: {bool(config.newsapi_api_key)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting Phase 8.5 CocoIndex Integration Tests")
    print("=" * 60)
    
    # Test 1: Configuration
    logger.info("📋 Test 1: Configuration Management")
    config_result = test_configuration()
    print(f"Configuration test: {'✅ PASSED' if config_result else '❌ FAILED'}")
    print()
    
    # Test 2: Query Router
    logger.info("🧭 Test 2: Query Router")
    router_result = test_query_router()
    print(f"Query router test: {'✅ PASSED' if router_result else '❌ FAILED'}")
    print()
    
    # Test 3: CocoIndex Tool
    logger.info("🔍 Test 3: CocoIndex Tool")
    tool_result = test_cocoindex_tool()
    tool_success = tool_result.get('success', False) if isinstance(tool_result, dict) else bool(tool_result)
    print(f"CocoIndex tool test: {'✅ PASSED' if tool_success else '❌ FAILED'}")
    if not tool_success and isinstance(tool_result, dict):
        print(f"  Error: {tool_result.get('error', 'Unknown error')}")
    print()
    
    # Test 4: Intelligent Web System
    logger.info("🌐 Test 4: Intelligent Web System")
    system_result = test_intelligent_web_system()
    system_success = system_result.get('success', False) if isinstance(system_result, dict) else bool(system_result)
    print(f"Intelligent web system test: {'✅ PASSED' if system_success else '❌ FAILED'}")
    if not system_success and isinstance(system_result, dict):
        print(f"  Error: {system_result.get('error', 'Unknown error')}")
    print()
    
    # Summary
    print("=" * 60)
    total_tests = 4
    passed_tests = sum([config_result, router_result, tool_success, system_success])
    
    print(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Phase 8.5 integration is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
