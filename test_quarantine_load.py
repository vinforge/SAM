#!/usr/bin/env python3
"""
Test script to verify that load_quarantined_content can see the new intelligent_web files.
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

def test_load_quarantined_content():
    """Test the load_quarantined_content function."""
    logger.info("🔍 TESTING LOAD_QUARANTINED_CONTENT FUNCTION 🔍")
    
    try:
        # Import the function
        from secure_streamlit_app import load_quarantined_content
        logger.info("✅ Successfully imported load_quarantined_content")
        
        # Check quarantine directory first
        quarantine_dir = Path("quarantine")
        if quarantine_dir.exists():
            all_files = list(quarantine_dir.glob("*.json"))
            logger.info(f"Files in quarantine directory: {len(all_files)}")
            
            for f in all_files:
                logger.info(f"  - {f.name} ({f.stat().st_size} bytes)")
                if 'intelligent_web_' in f.name:
                    logger.info(f"    ✅ INTELLIGENT_WEB FILE FOUND: {f.name}")
        
        # Call the load function
        logger.info("🚀 Calling load_quarantined_content...")
        quarantined_content = load_quarantined_content()
        logger.info(f"✅ load_quarantined_content returned {len(quarantined_content)} items")
        
        # Analyze the results
        intelligent_web_items = []
        scrapy_items = []
        corrupted_items = []
        
        for i, content in enumerate(quarantined_content):
            filename = content.get('filename', 'Unknown')
            logger.info(f"Item {i+1}: {filename}")
            
            if content.get('corrupted'):
                corrupted_items.append(content)
                logger.info(f"  ❌ CORRUPTED: {content.get('error', 'Unknown error')}")
            elif 'intelligent_web_' in filename:
                intelligent_web_items.append(content)
                logger.info(f"  ✅ INTELLIGENT_WEB ITEM FOUND!")
                logger.info(f"    - Query: {content.get('query', 'NOT_FOUND')}")
                logger.info(f"    - Tool: {content.get('result', {}).get('tool_used', 'NOT_FOUND')}")
                logger.info(f"    - Timestamp: {content.get('timestamp', 'NOT_FOUND')}")
            elif 'scrapy_' in filename:
                scrapy_items.append(content)
                logger.info(f"  📜 SCRAPY ITEM")
            else:
                logger.info(f"  ❓ UNKNOWN ITEM TYPE")
        
        # Summary
        logger.info(f"\n📊 LOAD RESULTS SUMMARY:")
        logger.info(f"  - Total items loaded: {len(quarantined_content)}")
        logger.info(f"  - Intelligent web items: {len(intelligent_web_items)}")
        logger.info(f"  - Scrapy items: {len(scrapy_items)}")
        logger.info(f"  - Corrupted items: {len(corrupted_items)}")
        
        if intelligent_web_items:
            logger.info("🎉 SUCCESS: Intelligent web items are being loaded correctly!")
            return True
        else:
            logger.error("❌ FAILURE: No intelligent web items found in loaded content")
            return False
            
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_vetting_status():
    """Test the get_vetting_status function."""
    logger.info("📊 TESTING GET_VETTING_STATUS FUNCTION 📊")
    
    try:
        from secure_streamlit_app import get_vetting_status
        logger.info("✅ Successfully imported get_vetting_status")
        
        status = get_vetting_status()
        logger.info(f"✅ get_vetting_status returned: {status}")
        
        quarantine_files = status.get('quarantine_files', 0)
        logger.info(f"Quarantine files count: {quarantine_files}")
        
        if quarantine_files > 0:
            logger.info("✅ Vetting status shows quarantine files exist")
            return True
        else:
            logger.error("❌ Vetting status shows no quarantine files")
            return False
            
    except Exception as e:
        logger.error(f"❌ VETTING STATUS TEST FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("🔍 QUARANTINE LOAD TESTS STARTING")
    logger.info("=" * 60)
    
    # Test 1: Load quarantined content
    logger.info("\n" + "=" * 40)
    logger.info("TEST 1: Load Quarantined Content")
    logger.info("=" * 40)
    test1_success = test_load_quarantined_content()
    
    # Test 2: Vetting status
    logger.info("\n" + "=" * 40)
    logger.info("TEST 2: Vetting Status")
    logger.info("=" * 40)
    test2_success = test_vetting_status()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("🏁 TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Test 1 (Load Content): {'✅ PASSED' if test1_success else '❌ FAILED'}")
    logger.info(f"Test 2 (Vetting Status): {'✅ PASSED' if test2_success else '❌ FAILED'}")
    
    if test1_success and test2_success:
        logger.info("🎉 ALL TESTS PASSED - Quarantine loading is working!")
    else:
        logger.info("❌ SOME TESTS FAILED - Issues with quarantine loading")

if __name__ == "__main__":
    main()
