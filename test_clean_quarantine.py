#!/usr/bin/env python3
"""
Test script to verify quarantine is now clean after removing old scrapy files.
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

def test_clean_quarantine():
    """Test that quarantine is now clean."""
    logger.info("🧹 TESTING CLEAN QUARANTINE STATUS 🧹")
    
    try:
        # Test the load function
        from secure_streamlit_app import load_quarantined_content, get_vetting_status
        
        # Load quarantined content
        quarantined_content = load_quarantined_content()
        logger.info(f"Quarantined content items loaded: {len(quarantined_content)}")
        
        # Check for different types
        intelligent_web_items = [c for c in quarantined_content if 'intelligent_web_' in c.get('filename', '')]
        scrapy_items = [c for c in quarantined_content if 'scrapy_search_' in c.get('filename', '')]
        corrupted_items = [c for c in quarantined_content if c.get('corrupted', False)]
        
        logger.info(f"  - Intelligent web items: {len(intelligent_web_items)}")
        logger.info(f"  - Scrapy search items: {len(scrapy_items)}")
        logger.info(f"  - Corrupted items: {len(corrupted_items)}")
        
        # List any remaining files
        if quarantined_content:
            logger.info("Remaining files:")
            for item in quarantined_content:
                logger.info(f"  - {item.get('filename', 'Unknown')}")
        else:
            logger.info("✅ No content files in quarantine")
        
        # Test vetting status
        vetting_status = get_vetting_status()
        logger.info(f"Vetting status: {vetting_status}")
        
        # Check if quarantine is truly clean
        if len(quarantined_content) == 0:
            logger.info("🎉 SUCCESS: Quarantine is completely clean!")
            return True
        else:
            logger.warning(f"⚠️ Quarantine still has {len(quarantined_content)} items")
            return False
            
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run the clean quarantine test."""
    logger.info("=" * 60)
    logger.info("🔍 CLEAN QUARANTINE TEST")
    logger.info("=" * 60)
    
    success = test_clean_quarantine()
    
    logger.info("\n" + "=" * 60)
    logger.info("🏁 TEST SUMMARY")
    logger.info("=" * 60)
    
    if success:
        logger.info("🎉 QUARANTINE IS CLEAN!")
        logger.info("The 'Content Awaiting Analysis' section should now be empty.")
    else:
        logger.info("❌ QUARANTINE STILL HAS CONTENT!")
        logger.info("Additional cleanup may be needed.")

if __name__ == "__main__":
    main()
