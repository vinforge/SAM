#!/usr/bin/env python3
"""
Test script to perform a real web search and verify it stays in quarantine.
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_real_web_search():
    """Test a real web search with the fixed quarantine system."""
    logger.info("🌐 TESTING REAL WEB SEARCH WITH FIXED QUARANTINE 🌐")
    
    try:
        # Step 1: Import web search components
        from web_retrieval.intelligent_web_system import IntelligentWebSystem
        from config.config_manager import ConfigManager
        logger.info("✅ Successfully imported web search components")
        
        # Step 2: Load configuration
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        api_keys = {
            'serper': config.serper_api_key if config.serper_api_key else None,
            'newsapi': config.newsapi_api_key if config.newsapi_api_key else None
        }
        
        web_config = {
            'cocoindex_search_provider': config.cocoindex_search_provider,
            'cocoindex_num_pages': config.cocoindex_num_pages,
            'web_retrieval_provider': config.web_retrieval_provider
        }
        
        logger.info(f"API keys available: {[k for k, v in api_keys.items() if v]}")
        
        # Step 3: Create intelligent web system
        intelligent_web_system = IntelligentWebSystem(api_keys=api_keys, config=web_config)
        
        # Step 4: Check quarantine before search
        quarantine_dir = Path("quarantine")
        before_files = list(quarantine_dir.glob("intelligent_web_*.json")) if quarantine_dir.exists() else []
        logger.info(f"Intelligent web files before search: {len(before_files)}")
        
        # Step 5: Perform web search
        test_query = "latest breakthrough in quantum computing 2025"
        logger.info(f"🔍 Searching for: '{test_query}'")
        
        result = intelligent_web_system.process_query(test_query)
        
        if result.get('success'):
            logger.info(f"✅ Web search successful using: {result.get('tool_used')}")
            
            # Step 6: Save to quarantine (simulating the web_ui/app.py flow)
            from secure_streamlit_app import save_intelligent_web_to_quarantine
            save_intelligent_web_to_quarantine(result, test_query)
            logger.info("✅ Content saved to quarantine")
            
            # Step 7: Verify file persists (no auto-archiving)
            after_files = list(quarantine_dir.glob("intelligent_web_*.json")) if quarantine_dir.exists() else []
            logger.info(f"Intelligent web files after search: {len(after_files)}")
            
            new_files = [f for f in after_files if f not in before_files]
            if new_files:
                logger.info(f"✅ NEW FILE CREATED: {new_files[0].name}")
                
                # Step 8: Test UI can load it
                from secure_streamlit_app import load_quarantined_content
                quarantined_content = load_quarantined_content()
                intelligent_web_items = [c for c in quarantined_content if 'intelligent_web_' in c.get('filename', '')]
                
                logger.info(f"✅ UI can now load {len(intelligent_web_items)} intelligent web items")
                
                # Show details of the new content
                for item in intelligent_web_items:
                    if item['filename'] == new_files[0].name:
                        logger.info(f"📄 New content details:")
                        logger.info(f"  - Query: {item.get('query', 'N/A')}")
                        logger.info(f"  - Tool: {item.get('result', {}).get('tool_used', 'N/A')}")
                        logger.info(f"  - Articles: {len(item.get('result', {}).get('data', {}).get('articles', []))}")
                        logger.info(f"  - File size: {item.get('file_size', 'N/A')} bytes")
                
                logger.info("🎉 SUCCESS: Real web search → quarantine → UI display working!")
                return True
            else:
                logger.error("❌ No new file was created")
                return False
        else:
            logger.warning(f"⚠️ Web search failed: {result.get('error', 'Unknown error')}")
            logger.info("This might be expected if no API keys are configured")
            return False
            
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run the real web search test."""
    logger.info("=" * 60)
    logger.info("🔍 REAL WEB SEARCH TEST WITH FIXED QUARANTINE")
    logger.info("=" * 60)
    
    success = test_real_web_search()
    
    logger.info("\n" + "=" * 60)
    logger.info("🏁 TEST SUMMARY")
    logger.info("=" * 60)
    
    if success:
        logger.info("🎉 REAL WEB SEARCH TEST PASSED!")
        logger.info("Web search results now stay in quarantine for user review.")
        logger.info("Check the Content Vetting page in the UI to see the new content.")
    else:
        logger.info("❌ REAL WEB SEARCH TEST FAILED!")
        logger.info("Check API keys or network connectivity.")

if __name__ == "__main__":
    main()
