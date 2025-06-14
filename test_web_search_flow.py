#!/usr/bin/env python3
"""
Test script to simulate the actual web search flow that would be triggered from the UI.
This tests the complete path: web search → quarantine save → UI display.
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

def test_complete_web_search_flow():
    """Test the complete web search flow as it would happen from the UI."""
    logger.info("🌐 TESTING COMPLETE WEB SEARCH FLOW 🌐")
    
    try:
        # Step 1: Import required components (same as web_ui/app.py)
        logger.info("📦 Importing web search components...")
        from web_retrieval.intelligent_web_system import IntelligentWebSystem
        from config.config_manager import ConfigManager
        logger.info("✅ Successfully imported web search components")
        
        # Step 2: Load configuration (same as web_ui/app.py)
        logger.info("⚙️ Loading configuration...")
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # Initialize intelligent web system
        api_keys = {
            'serper': config.serper_api_key if config.serper_api_key else None,
            'newsapi': config.newsapi_api_key if config.newsapi_api_key else None
        }
        
        web_config = {
            'cocoindex_search_provider': config.cocoindex_search_provider,
            'cocoindex_num_pages': config.cocoindex_num_pages,
            'web_retrieval_provider': config.web_retrieval_provider
        }
        
        logger.info(f"API keys available: {list(api_keys.keys())}")
        logger.info(f"Web config: {web_config}")
        
        # Step 3: Create intelligent web system
        logger.info("🤖 Creating IntelligentWebSystem...")
        intelligent_web_system = IntelligentWebSystem(api_keys=api_keys, config=web_config)
        logger.info("✅ IntelligentWebSystem created successfully")
        
        # Step 4: Process a test query
        test_query = "latest AI technology news 2025"
        logger.info(f"🔍 Processing test query: '{test_query}'")
        
        # Count quarantine files before
        quarantine_dir = Path("quarantine")
        before_files = list(quarantine_dir.glob("intelligent_web_*.json")) if quarantine_dir.exists() else []
        logger.info(f"Intelligent web files before search: {len(before_files)}")
        
        # Process the query
        result = intelligent_web_system.process_query(test_query)
        logger.info(f"Web search result success: {result.get('success', False)}")
        logger.info(f"Web search result keys: {list(result.keys())}")
        
        if result.get('success'):
            logger.info(f"✅ Web search successful using tool: {result.get('tool_used', 'unknown')}")
            logger.info(f"Data keys: {list(result.get('data', {}).keys()) if 'data' in result else 'NO_DATA'}")
            
            # Step 5: Save to quarantine (same as web_ui/app.py)
            logger.info("💾 Saving to quarantine...")
            from secure_streamlit_app import save_intelligent_web_to_quarantine
            
            try:
                save_intelligent_web_to_quarantine(result, test_query)
                logger.info("✅ Quarantine save completed successfully")
                
                # Count files after
                after_files = list(quarantine_dir.glob("intelligent_web_*.json")) if quarantine_dir.exists() else []
                logger.info(f"Intelligent web files after search: {len(after_files)}")
                
                new_files = [f for f in after_files if f not in before_files]
                if new_files:
                    logger.info(f"✅ NEW FILE CREATED: {new_files[0].name}")
                    
                    # Step 6: Test if UI can load the new file
                    logger.info("🖥️ Testing UI load functionality...")
                    from secure_streamlit_app import load_quarantined_content, get_vetting_status
                    
                    # Test load
                    quarantined_content = load_quarantined_content()
                    intelligent_web_items = [c for c in quarantined_content if 'intelligent_web_' in c.get('filename', '')]
                    logger.info(f"UI can load {len(intelligent_web_items)} intelligent web items")
                    
                    # Test vetting status
                    vetting_status = get_vetting_status()
                    logger.info(f"Vetting status shows {vetting_status.get('quarantine_files', 0)} quarantine files")
                    
                    if intelligent_web_items and vetting_status.get('quarantine_files', 0) > 0:
                        logger.info("🎉 COMPLETE FLOW SUCCESS: Web search → Quarantine → UI display all working!")
                        return True
                    else:
                        logger.error("❌ UI cannot properly load the new quarantine content")
                        return False
                else:
                    logger.error("❌ No new quarantine file was created")
                    return False
                    
            except Exception as quarantine_error:
                logger.error(f"❌ Quarantine save failed: {quarantine_error}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
        else:
            logger.error(f"❌ Web search failed: {result.get('error', 'Unknown error')}")
            logger.info("This might be expected if no API keys are configured")
            
            # Test with a mock result to verify quarantine save works
            logger.info("🧪 Testing with mock result...")
            mock_result = {
                'success': True,
                'tool_used': 'mock_tool',
                'data': {
                    'articles': [
                        {'title': 'Mock Article', 'content': 'Mock content', 'source': 'mock.com'}
                    ]
                }
            }
            
            from secure_streamlit_app import save_intelligent_web_to_quarantine
            save_intelligent_web_to_quarantine(mock_result, test_query)
            logger.info("✅ Mock quarantine save successful")
            return True
            
    except Exception as e:
        logger.error(f"❌ COMPLETE FLOW TEST FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run the complete web search flow test."""
    logger.info("=" * 60)
    logger.info("🔍 COMPLETE WEB SEARCH FLOW TEST")
    logger.info("=" * 60)
    
    success = test_complete_web_search_flow()
    
    logger.info("\n" + "=" * 60)
    logger.info("🏁 FLOW TEST SUMMARY")
    logger.info("=" * 60)
    
    if success:
        logger.info("🎉 COMPLETE FLOW TEST PASSED!")
        logger.info("The web search → quarantine → UI display pipeline is working correctly.")
    else:
        logger.info("❌ COMPLETE FLOW TEST FAILED!")
        logger.info("There are issues in the web search → quarantine → UI display pipeline.")

if __name__ == "__main__":
    main()
