#!/usr/bin/env python3
"""
Phase 1B Integration Testing Script
Tests TPV integration with SAM's response generation pipeline.
"""

import sys
import logging
import time
from pathlib import Path

# Add SAM to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sam_tpv_integration():
    """Test SAM-TPV integration functionality."""
    logger.info("🧪 Testing SAM-TPV Integration...")
    
    try:
        from sam.cognition.tpv import SAMTPVIntegration, UserProfile
        
        # Initialize integration
        integration = SAMTPVIntegration()
        
        if not integration.initialize():
            logger.error("❌ Integration initialization failed")
            return False
        
        logger.info("✅ SAM-TPV Integration initialized")
        
        # Test different query types
        test_cases = [
            {
                'prompt': "Analyze the economic impact of renewable energy adoption in developing countries",
                'profile': UserProfile.RESEARCHER,
                'confidence': 0.5,
                'expected_tpv': True
            },
            {
                'prompt': "What is 2 + 2?",
                'profile': UserProfile.GENERAL,
                'confidence': 0.9,
                'expected_tpv': False
            },
            {
                'prompt': "Compare machine learning algorithms for natural language processing tasks",
                'profile': UserProfile.TECHNICAL,
                'confidence': 0.6,
                'expected_tpv': True
            }
        ]
        
        passed_tests = 0
        for i, test_case in enumerate(test_cases):
            logger.info(f"\n📋 Test Case {i+1}: {test_case['prompt'][:50]}...")
            
            try:
                response = integration.generate_response_with_tpv(
                    prompt=test_case['prompt'],
                    user_profile=test_case['profile'],
                    initial_confidence=test_case['confidence']
                )
                
                # Verify response structure
                if not hasattr(response, 'content') or not response.content:
                    logger.error(f"❌ Test {i+1}: No content in response")
                    continue
                
                # Check TPV activation
                tpv_activated = response.tpv_enabled
                expected = test_case['expected_tpv']
                
                if tpv_activated == expected:
                    logger.info(f"✅ Test {i+1}: TPV activation correct ({tpv_activated})")
                    
                    # Additional checks for TPV-enabled responses
                    if tpv_activated and response.tpv_trace:
                        logger.info(f"  📊 TPV Steps: {len(response.tpv_trace.steps)}")
                        logger.info(f"  📈 Final Score: {response.tpv_trace.current_score:.3f}")
                        logger.info(f"  ⏱️ Total Time: {response.performance_metrics.get('total_time', 0):.2f}s")
                    
                    passed_tests += 1
                else:
                    logger.warning(f"⚠️ Test {i+1}: Expected TPV={expected}, got {tpv_activated}")
                
                logger.info(f"  📝 Response: {response.content[:100]}...")
                
            except Exception as e:
                logger.error(f"❌ Test {i+1} failed: {e}")
        
        logger.info(f"\n✅ Integration tests: {passed_tests}/{len(test_cases)} passed")
        
        # Test status
        status = integration.get_integration_status()
        logger.info(f"📊 Integration status: {status['tpv_activation_rate']:.1%} activation rate")
        
        return passed_tests >= len(test_cases) * 0.75  # 75% pass rate
        
    except Exception as e:
        logger.error(f"❌ SAM-TPV Integration test failed: {e}")
        return False

def test_secure_streamlit_integration():
    """Test integration with secure Streamlit app functions."""
    logger.info("🧪 Testing Secure Streamlit Integration...")
    
    try:
        # Import the secure app function
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from secure_streamlit_app import generate_secure_response
        
        # Test queries
        test_queries = [
            "Explain the principles of quantum computing",
            "What are the benefits of renewable energy?",
            "Analyze the impact of AI on healthcare systems"
        ]
        
        passed_tests = 0
        for i, query in enumerate(test_queries):
            logger.info(f"\n📋 Testing query {i+1}: {query[:50]}...")
            
            try:
                # Mock session state for testing
                import streamlit as st
                if not hasattr(st, 'session_state'):
                    # Create mock session state
                    class MockSessionState:
                        def __init__(self):
                            self.data = {}
                        
                        def get(self, key, default=None):
                            return self.data.get(key, default)
                        
                        def __setitem__(self, key, value):
                            self.data[key] = value
                        
                        def __getitem__(self, key):
                            return self.data[key]
                        
                        def __contains__(self, key):
                            return key in self.data
                    
                    st.session_state = MockSessionState()
                
                # Mock secure memory store
                class MockSecureMemoryStore:
                    def get_security_status(self):
                        return {'encrypted_chunk_count': 0}
                
                st.session_state.data['secure_memory_store'] = MockSecureMemoryStore()
                
                # Generate response
                start_time = time.time()
                response = generate_secure_response(query, force_local=True)
                end_time = time.time()
                
                if response and len(response) > 10:
                    logger.info(f"✅ Test {i+1}: Response generated ({len(response)} chars, {end_time-start_time:.2f}s)")
                    logger.info(f"  📝 Preview: {response[:100]}...")
                    
                    # Check for TPV data in session state
                    tpv_data = st.session_state.get('tpv_session_data', {})
                    if tpv_data:
                        logger.info(f"  🧠 TPV Data: {tpv_data}")
                    
                    passed_tests += 1
                else:
                    logger.error(f"❌ Test {i+1}: Invalid response")
                
            except Exception as e:
                logger.error(f"❌ Test {i+1} failed: {e}")
                import traceback
                traceback.print_exc()
        
        logger.info(f"\n✅ Streamlit integration tests: {passed_tests}/{len(test_queries)} passed")
        return passed_tests >= len(test_queries) * 0.75
        
    except Exception as e:
        logger.error(f"❌ Secure Streamlit integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_impact():
    """Test performance impact of TPV integration."""
    logger.info("🧪 Testing Performance Impact...")
    
    try:
        from sam.cognition.tpv import SAMTPVIntegration, UserProfile
        
        integration = SAMTPVIntegration()
        if not integration.initialize():
            logger.error("❌ Integration initialization failed")
            return False
        
        test_prompt = "Explain the concept of machine learning and its applications"
        
        # Test with TPV enabled
        logger.info("Testing with TPV enabled...")
        start_time = time.time()
        tpv_response = integration.generate_response_with_tpv(
            prompt=test_prompt,
            user_profile=UserProfile.TECHNICAL,
            initial_confidence=0.5  # Force TPV activation
        )
        tpv_time = time.time() - start_time
        
        # Test without TPV (standard response)
        logger.info("Testing without TPV...")
        start_time = time.time()
        standard_response = integration.generate_response_with_tpv(
            prompt=test_prompt,
            user_profile=UserProfile.GENERAL,
            initial_confidence=0.9  # Prevent TPV activation
        )
        standard_time = time.time() - start_time
        
        # Calculate overhead
        overhead = tpv_time - standard_time
        overhead_percentage = (overhead / standard_time) * 100 if standard_time > 0 else 0
        
        logger.info(f"📊 Performance Results:")
        logger.info(f"  ⚡ Standard response: {standard_time:.2f}s")
        logger.info(f"  🧠 TPV-enabled response: {tpv_time:.2f}s")
        logger.info(f"  📈 Overhead: {overhead:.2f}s ({overhead_percentage:.1f}%)")
        
        # Check if overhead is reasonable (< 50% for Phase 1)
        if overhead_percentage < 50:
            logger.info("✅ Performance overhead within acceptable range")
            return True
        else:
            logger.warning(f"⚠️ Performance overhead high: {overhead_percentage:.1f}%")
            return False
        
    except Exception as e:
        logger.error(f"❌ Performance impact test failed: {e}")
        return False

def main():
    """Run all Phase 1B integration tests."""
    logger.info("🚀 Starting Phase 1B Integration Tests")
    logger.info("=" * 60)
    
    tests = [
        ("SAM-TPV Integration", test_sam_tpv_integration),
        ("Secure Streamlit Integration", test_secure_streamlit_integration),
        ("Performance Impact", test_performance_impact)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} Test")
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 PHASE 1B INTEGRATION TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tests Passed: {passed}/{total}")
    logger.info(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 ALL PHASE 1B INTEGRATION TESTS PASSED!")
        logger.info("✅ TPV integration with SAM is working correctly")
        logger.info("✅ Ready to proceed with Phase 1C: UI & Polish")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED!")
        logger.error("Please fix issues before proceeding to Phase 1C")
        return 1

if __name__ == "__main__":
    sys.exit(main())
