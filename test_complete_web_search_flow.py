#!/usr/bin/env python3
"""
Test the complete web search flow from chat escalation to vetting page display.
This tests the exact flow that should happen when users click "Yes, Search Online".
"""

import sys
import os
import logging
import requests
import json
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

def test_web_search_api_endpoint():
    """Test the /api/trigger-web-search endpoint directly."""
    logger.info("🧪 TESTING WEB SEARCH API ENDPOINT 🧪")
    
    try:
        # Test data that mimics frontend request
        test_data = {
            "search_query": "latest AI developments 2025",
            "original_query": "What are the latest AI developments?"
        }
        
        # Call the API endpoint
        url = "http://localhost:5001/api/trigger-web-search"
        logger.info(f"Calling: {url}")
        logger.info(f"Data: {test_data}")
        
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ API call successful!")
            logger.info(f"Response status: {data.get('status')}")
            logger.info(f"Tool used: {data.get('tool_used')}")
            logger.info(f"Content count: {data.get('content_count')}")
            logger.info(f"Message: {data.get('message', '')[:100]}...")
            
            return True, data
        else:
            logger.error(f"❌ API call failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        return False, None

def test_quarantine_file_creation():
    """Test if quarantine files are created after web search."""
    logger.info("📁 TESTING QUARANTINE FILE CREATION 📁")
    
    try:
        quarantine_dir = Path("quarantine")
        
        # List files before
        before_files = list(quarantine_dir.glob("intelligent_web_*.json")) if quarantine_dir.exists() else []
        logger.info(f"Files before test: {len(before_files)}")
        
        # Trigger web search
        success, response_data = test_web_search_api_endpoint()
        
        if not success:
            logger.error("❌ Web search failed, cannot test file creation")
            return False
        
        # List files after
        after_files = list(quarantine_dir.glob("intelligent_web_*.json")) if quarantine_dir.exists() else []
        logger.info(f"Files after test: {len(after_files)}")
        
        # Check for new files
        new_files = [f for f in after_files if f not in before_files]
        
        if new_files:
            logger.info(f"✅ NEW FILES CREATED: {len(new_files)}")
            for f in new_files:
                logger.info(f"  - {f.name} ({f.stat().st_size} bytes)")
            return True
        else:
            logger.error("❌ NO NEW FILES CREATED")
            return False
            
    except Exception as e:
        logger.error(f"❌ File creation test failed: {e}")
        return False

def test_vetting_page_integration():
    """Test if vetting page can load the new quarantine content."""
    logger.info("🛡️ TESTING VETTING PAGE INTEGRATION 🛡️")
    
    try:
        # Import vetting functions
        from secure_streamlit_app import load_quarantined_content, get_vetting_status
        
        # Load quarantined content
        quarantined_content = load_quarantined_content()
        logger.info(f"Loaded quarantined content: {len(quarantined_content)} items")
        
        # Check for intelligent_web items
        intelligent_web_items = [c for c in quarantined_content if 'intelligent_web_' in c.get('filename', '')]
        logger.info(f"Intelligent web items: {len(intelligent_web_items)}")
        
        # Get vetting status
        vetting_status = get_vetting_status()
        logger.info(f"Vetting status: {vetting_status}")
        
        # Check if we have content to vet
        if intelligent_web_items and vetting_status.get('quarantine_files', 0) > 0:
            logger.info("✅ VETTING PAGE INTEGRATION WORKING!")
            
            # Show details of latest item
            if intelligent_web_items:
                latest_item = intelligent_web_items[-1]
                logger.info(f"Latest item details:")
                logger.info(f"  - Filename: {latest_item.get('filename')}")
                logger.info(f"  - Query: {latest_item.get('query', 'N/A')}")
                logger.info(f"  - Tool: {latest_item.get('result', {}).get('tool_used', 'N/A')}")
                logger.info(f"  - Size: {latest_item.get('file_size', 'N/A')} bytes")
            
            return True
        else:
            logger.error("❌ VETTING PAGE INTEGRATION BROKEN")
            logger.error(f"Intelligent web items: {len(intelligent_web_items)}")
            logger.error(f"Quarantine files: {vetting_status.get('quarantine_files', 0)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Vetting integration test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_security_statistics():
    """Test if security statistics are calculated correctly."""
    logger.info("📊 TESTING SECURITY STATISTICS 📊")
    
    try:
        from secure_streamlit_app import calculate_security_overview
        
        # Calculate security overview
        security_overview = calculate_security_overview()
        logger.info(f"Security overview: {security_overview}")
        
        # Check if statistics are meaningful
        if security_overview and isinstance(security_overview, dict):
            logger.info("✅ SECURITY STATISTICS CALCULATED!")
            logger.info(f"  - Critical risks: {security_overview.get('critical_risks', 'N/A')}")
            logger.info(f"  - High risks: {security_overview.get('high_risks', 'N/A')}")
            logger.info(f"  - Avg credibility: {security_overview.get('avg_credibility', 'N/A')}")
            logger.info(f"  - Avg purity: {security_overview.get('avg_purity', 'N/A')}")
            return True
        else:
            logger.error("❌ SECURITY STATISTICS BROKEN")
            return False
            
    except Exception as e:
        logger.error(f"❌ Security statistics test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run complete web search flow test."""
    logger.info("=" * 80)
    logger.info("🔍 COMPLETE WEB SEARCH FLOW TEST")
    logger.info("=" * 80)
    
    # Test sequence
    tests = [
        ("API Endpoint", test_web_search_api_endpoint),
        ("File Creation", test_quarantine_file_creation),
        ("Vetting Integration", test_vetting_page_integration),
        ("Security Statistics", test_security_statistics)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*40}")
        logger.info(f"TEST: {test_name}")
        logger.info(f"{'='*40}")
        
        try:
            if test_name == "File Creation":
                # Skip file creation test if API test failed
                if not results.get("API Endpoint", False):
                    logger.warning("⏭️ Skipping file creation test - API test failed")
                    results[test_name] = False
                    continue
            
            result = test_func()
            results[test_name] = result
            
        except Exception as e:
            logger.error(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("🏁 TEST SUMMARY")
    logger.info(f"{'='*80}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - WEB SEARCH FLOW IS WORKING!")
        logger.info("Users should now see web search results in the vetting page.")
    elif passed > 0:
        logger.info("⚠️ PARTIAL SUCCESS - Some components working, others need fixes")
    else:
        logger.info("❌ ALL TESTS FAILED - Major issues with web search flow")
    
    # Specific guidance
    if not results.get("API Endpoint", False):
        logger.info("\n🔧 NEXT STEPS: Fix web search API endpoint")
    elif not results.get("File Creation", False):
        logger.info("\n🔧 NEXT STEPS: Fix quarantine file creation")
    elif not results.get("Vetting Integration", False):
        logger.info("\n🔧 NEXT STEPS: Fix vetting page integration")
    elif not results.get("Security Statistics", False):
        logger.info("\n🔧 NEXT STEPS: Fix security statistics calculation")

if __name__ == "__main__":
    main()
