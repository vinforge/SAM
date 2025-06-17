#!/usr/bin/env python3
"""
Debug script to test web search functionality and identify the RSS fallback issue.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_rss_feeds():
    """Test RSS feed connectivity."""
    import requests
    
    rss_urls = [
        "http://rss.cnn.com/rss/cnn_latest.rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.bbci.co.uk/news/rss.xml"
    ]
    
    logger.info("🔍 Testing RSS feed connectivity...")
    
    for url in rss_urls:
        try:
            logger.info(f"Testing: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            logger.info(f"✅ {url}: Status {response.status_code}, Content-Length: {len(response.content)}")
            
            # Check if it's valid XML
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(response.content)
                items = root.findall('.//item')
                logger.info(f"   📰 Found {len(items)} news items")
            except ET.ParseError as e:
                logger.error(f"   ❌ XML parsing failed: {e}")
                
        except Exception as e:
            logger.error(f"❌ {url}: Failed - {e}")

def test_intelligent_web_system():
    """Test the intelligent web system."""
    try:
        logger.info("🤖 Testing Intelligent Web System...")
        
        from web_retrieval.intelligent_web_system import IntelligentWebSystem
        from config.config_manager import ConfigManager
        
        # Load configuration
        config_manager = ConfigManager()
        web_config = config_manager.get_web_retrieval_config()
        
        # Create system
        web_system = IntelligentWebSystem(web_config)
        
        # Test query
        test_query = "latest technology news"
        logger.info(f"Testing query: '{test_query}'")
        
        result = web_system.process_query(test_query)
        
        logger.info(f"Result success: {result.get('success', False)}")
        logger.info(f"Result error: {result.get('error', 'None')}")
        
        if result.get('success'):
            logger.info("✅ Intelligent Web System working")
        else:
            logger.error(f"❌ Intelligent Web System failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Intelligent Web System test failed: {e}")

def test_manual_web_search():
    """Test the manual web search function directly."""
    try:
        logger.info("🔍 Testing Manual Web Search Function...")
        
        # Import the function from secure_streamlit_app
        from secure_streamlit_app import perform_secure_web_search
        
        test_query = "latest AI developments"
        logger.info(f"Testing query: '{test_query}'")
        
        result = perform_secure_web_search(test_query)
        
        logger.info(f"Search result success: {result.get('success', False)}")
        logger.info(f"Search result error: {result.get('error', 'None')}")
        logger.info(f"Search result method: {result.get('method', 'Unknown')}")
        
        if result.get('success'):
            logger.info("✅ Manual web search working")
            logger.info(f"Response length: {len(result.get('response', ''))}")
        else:
            logger.error(f"❌ Manual web search failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Manual web search test failed: {e}")

def test_simple_rss_fetch():
    """Test simple RSS fetch function."""
    try:
        logger.info("📡 Testing Simple RSS Fetch...")
        
        from secure_streamlit_app import fetch_rss_content
        
        test_url = "http://rss.cnn.com/rss/cnn_latest.rss"
        logger.info(f"Testing RSS URL: {test_url}")
        
        result = fetch_rss_content(test_url)
        
        logger.info(f"RSS fetch success: {result.get('success', False)}")
        logger.info(f"RSS fetch error: {result.get('error', 'None')}")
        
        if result.get('success'):
            content = result.get('content', '')
            logger.info(f"✅ RSS fetch working - Content length: {len(content)}")
            logger.info(f"Content preview: {content[:200]}...")
        else:
            logger.error(f"❌ RSS fetch failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ RSS fetch test failed: {e}")

def main():
    """Run all web search tests."""
    logger.info("🚀 Starting Web Search Debug Tests")
    logger.info("=" * 60)
    
    # Test 1: RSS feed connectivity
    test_rss_feeds()
    logger.info("-" * 40)
    
    # Test 2: Simple RSS fetch function
    test_simple_rss_fetch()
    logger.info("-" * 40)
    
    # Test 3: Intelligent web system
    test_intelligent_web_system()
    logger.info("-" * 40)
    
    # Test 4: Manual web search function
    test_manual_web_search()
    logger.info("-" * 40)
    
    logger.info("🎯 Web Search Debug Tests Complete")

if __name__ == '__main__':
    main()
