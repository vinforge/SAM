#!/usr/bin/env python3
"""
Test script to verify that intelligent_web files now stay in quarantine 
after disabling automatic vetting.
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

def test_quarantine_persistence():
    """Test that files stay in quarantine after web search."""
    logger.info("🧪 TESTING QUARANTINE PERSISTENCE AFTER WEB SEARCH 🧪")
    
    try:
        # Step 1: Check current quarantine state
        quarantine_dir = Path("quarantine")
        before_files = list(quarantine_dir.glob("intelligent_web_*.json")) if quarantine_dir.exists() else []
        logger.info(f"Intelligent web files in quarantine before test: {len(before_files)}")
        
        # Step 2: Create a test intelligent_web file directly
        from secure_streamlit_app import save_intelligent_web_to_quarantine
        
        test_result = {
            'success': True,
            'tool_used': 'persistence_test_tool',
            'data': {
                'articles': [
                    {
                        'title': 'Persistence Test Article',
                        'content': 'This article tests if files stay in quarantine after the fix.',
                        'source': 'persistence-test.com',
                        'url': 'https://persistence-test.com/article'
                    }
                ]
            }
        }
        
        test_query = f"Persistence test query - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Creating test file with query: {test_query}")
        save_intelligent_web_to_quarantine(test_result, test_query)
        
        # Step 3: Check if file was created and stays in quarantine
        after_files = list(quarantine_dir.glob("intelligent_web_*.json")) if quarantine_dir.exists() else []
        logger.info(f"Intelligent web files in quarantine after test: {len(after_files)}")
        
        new_files = [f for f in after_files if f not in before_files]
        
        if new_files:
            logger.info(f"✅ NEW FILE CREATED AND PERSISTED: {new_files[0].name}")
            
            # Step 4: Test UI loading
            from secure_streamlit_app import load_quarantined_content, get_vetting_status
            
            quarantined_content = load_quarantined_content()
            intelligent_web_items = [c for c in quarantined_content if 'intelligent_web_' in c.get('filename', '')]
            
            vetting_status = get_vetting_status()
            
            logger.info(f"UI can load {len(intelligent_web_items)} intelligent web items")
            logger.info(f"Vetting status shows {vetting_status.get('quarantine_files', 0)} quarantine files")
            
            # Step 5: Wait a bit and check if file is still there (not auto-archived)
            import time
            logger.info("⏳ Waiting 5 seconds to check if file persists...")
            time.sleep(5)
            
            final_files = list(quarantine_dir.glob("intelligent_web_*.json")) if quarantine_dir.exists() else []
            logger.info(f"Intelligent web files after 5 second wait: {len(final_files)}")
            
            if len(final_files) >= len(after_files):
                logger.info("🎉 SUCCESS: Files are persisting in quarantine (not being auto-archived)")
                return True
            else:
                logger.error("❌ FAILURE: Files are still being auto-archived")
                return False
                
        else:
            logger.error("❌ FAILURE: No new file was created")
            return False
            
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run the quarantine persistence test."""
    logger.info("=" * 60)
    logger.info("🔍 QUARANTINE PERSISTENCE TEST")
    logger.info("=" * 60)
    
    success = test_quarantine_persistence()
    
    logger.info("\n" + "=" * 60)
    logger.info("🏁 TEST SUMMARY")
    logger.info("=" * 60)
    
    if success:
        logger.info("🎉 QUARANTINE PERSISTENCE TEST PASSED!")
        logger.info("Files now stay in quarantine for user review.")
    else:
        logger.info("❌ QUARANTINE PERSISTENCE TEST FAILED!")
        logger.info("Files are still being auto-archived.")

if __name__ == "__main__":
    main()
