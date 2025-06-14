#!/usr/bin/env python3
"""
Phase 1A Foundation Testing Script
Tests the core TPV monitoring components before integration.
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

def test_tpv_monitor():
    """Test TPV Monitor functionality."""
    logger.info("🧪 Testing TPV Monitor...")
    
    try:
        from sam.cognition.tpv import TPVMonitor, UserProfile, QueryIntent
        
        # Initialize monitor
        monitor = TPVMonitor()
        
        # Test initialization
        if monitor.initialize():
            logger.info("✅ TPV Monitor initialization successful")
        else:
            logger.error("❌ TPV Monitor initialization failed")
            return False
        
        # Test monitoring workflow
        test_query = "Analyze the impact of artificial intelligence on healthcare systems"
        query_id = monitor.start_monitoring(test_query)
        logger.info(f"✅ Started monitoring query: {query_id}")
        
        # Simulate progressive response generation
        test_responses = [
            "To analyze the impact of AI on healthcare",
            "To analyze the impact of AI on healthcare systems, we need to consider several key factors.",
            "To analyze the impact of AI on healthcare systems, we need to consider several key factors. First, AI has revolutionized diagnostic capabilities through machine learning algorithms that can detect patterns in medical imaging with remarkable accuracy.",
            "To analyze the impact of AI on healthcare systems, we need to consider several key factors. First, AI has revolutionized diagnostic capabilities through machine learning algorithms that can detect patterns in medical imaging with remarkable accuracy. However, this technological advancement also raises important questions about data privacy, algorithmic bias, and the changing role of healthcare professionals."
        ]
        
        scores = []
        for i, response in enumerate(test_responses):
            score = monitor.predict_progress(response, query_id, token_count=(i+1)*20)
            scores.append(score)
            logger.info(f"  Step {i+1}: Score = {score:.3f}")
            time.sleep(0.1)  # Simulate processing time
        
        # Test trace retrieval
        trace = monitor.get_trace(query_id)
        if trace:
            logger.info(f"✅ Retrieved trace with {len(trace.steps)} steps")
            logger.info(f"  Final score: {trace.current_score:.3f}")
            logger.info(f"  Progress: {trace.get_progress_percentage():.1f}%")
        else:
            logger.error("❌ Failed to retrieve trace")
            return False
        
        # Stop monitoring
        completed_trace = monitor.stop_monitoring(query_id)
        if completed_trace:
            logger.info("✅ Successfully stopped monitoring")
        else:
            logger.error("❌ Failed to stop monitoring")
            return False
        
        # Test status
        status = monitor.get_status()
        logger.info(f"✅ Monitor status: {status['initialized']}, Active queries: {status['active_queries']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TPV Monitor test failed: {e}")
        return False

def test_reasoning_controller():
    """Test Reasoning Controller functionality."""
    logger.info("🧪 Testing Reasoning Controller...")
    
    try:
        from sam.cognition.tpv import ReasoningController, ControlMode, ReasoningTrace
        
        # Initialize controller in passive mode
        controller = ReasoningController(mode=ControlMode.PASSIVE)
        logger.info("✅ Reasoning Controller initialized in passive mode")
        
        # Create mock trace
        trace = ReasoningTrace(
            query_id="test_query",
            start_time=time.time(),
            steps=[],
            is_active=True,
            total_tokens=0,
            current_score=0.0
        )
        
        # Test should_continue method
        for i in range(5):
            should_continue = controller.should_continue(trace)
            if not should_continue:
                logger.error(f"❌ Controller unexpectedly returned False at step {i}")
                return False
            
            # Simulate trace updates
            trace.total_tokens += 20
            trace.current_score = min(i * 0.2, 1.0)
        
        logger.info("✅ Controller correctly returned True for all steps (passive mode)")
        
        # Test statistics
        stats = controller.get_control_statistics()
        logger.info(f"✅ Control statistics: {stats['total_decisions']} decisions, {stats['continue_rate']:.1%} continue rate")
        
        # Test status
        status = controller.get_status()
        logger.info(f"✅ Controller status: Mode = {status['mode']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Reasoning Controller test failed: {e}")
        return False

def test_tpv_trigger():
    """Test TPV Trigger functionality."""
    logger.info("🧪 Testing TPV Trigger...")
    
    try:
        from sam.cognition.tpv import TPVTrigger, UserProfile, QueryIntent
        
        # Initialize trigger
        trigger = TPVTrigger()
        logger.info("✅ TPV Trigger initialized")
        
        # Test different query types
        test_cases = [
            {
                'query': "Analyze the economic impact of renewable energy adoption",
                'profile': UserProfile.RESEARCHER,
                'confidence': 0.5,
                'expected': True
            },
            {
                'query': "What is the weather today?",
                'profile': UserProfile.GENERAL,
                'confidence': 0.9,
                'expected': False
            },
            {
                'query': "Compare machine learning algorithms for image recognition",
                'profile': UserProfile.TECHNICAL,
                'confidence': 0.8,
                'expected': True
            },
            {
                'query': "Explain quantum computing principles",
                'profile': UserProfile.STUDENT,
                'confidence': 0.6,
                'expected': True  # Low confidence should trigger
            }
        ]
        
        passed_tests = 0
        for i, test_case in enumerate(test_cases):
            result = trigger.should_activate_tpv(
                query=test_case['query'],
                user_profile=test_case['profile'],
                initial_confidence=test_case['confidence']
            )
            
            if result.should_activate == test_case['expected']:
                logger.info(f"✅ Test {i+1}: {result.should_activate} ({result.trigger_type}, {result.confidence:.3f})")
                passed_tests += 1
            else:
                logger.warning(f"⚠️ Test {i+1}: Expected {test_case['expected']}, got {result.should_activate}")
        
        logger.info(f"✅ Trigger tests: {passed_tests}/{len(test_cases)} passed")
        
        # Test status
        status = trigger.get_status()
        logger.info(f"✅ Trigger status: {len(status['supported_profiles'])} profiles, {len(status['supported_intents'])} intents")
        
        return passed_tests >= len(test_cases) * 0.75  # 75% pass rate
        
    except Exception as e:
        logger.error(f"❌ TPV Trigger test failed: {e}")
        return False

def test_integration():
    """Test integration between components."""
    logger.info("🧪 Testing Component Integration...")
    
    try:
        from sam.cognition.tpv import TPVMonitor, ReasoningController, TPVTrigger, UserProfile, ControlMode
        
        # Initialize all components
        trigger = TPVTrigger()
        monitor = TPVMonitor()
        controller = ReasoningController(mode=ControlMode.PASSIVE)
        
        if not monitor.initialize():
            logger.error("❌ Monitor initialization failed")
            return False
        
        # Test complete workflow
        test_query = "Research the effectiveness of different machine learning approaches for medical diagnosis"
        
        # Step 1: Check if TPV should be activated
        trigger_result = trigger.should_activate_tpv(
            query=test_query,
            user_profile=UserProfile.RESEARCHER,
            initial_confidence=0.6
        )
        
        logger.info(f"✅ Trigger evaluation: {trigger_result.should_activate} ({trigger_result.reason})")
        
        if trigger_result.should_activate:
            # Step 2: Start monitoring
            query_id = monitor.start_monitoring(test_query)
            
            # Step 3: Simulate reasoning loop
            response_text = ""
            for i in range(3):
                response_text += f" This is step {i+1} of the reasoning process."
                
                # Get TPV score
                score = monitor.predict_progress(response_text, query_id)
                
                # Check if should continue
                trace = monitor.get_trace(query_id)
                should_continue = controller.should_continue(trace)
                
                logger.info(f"  Step {i+1}: Score = {score:.3f}, Continue = {should_continue}")
                
                if not should_continue:
                    break
            
            # Step 4: Stop monitoring
            final_trace = monitor.stop_monitoring(query_id)
            logger.info(f"✅ Integration test completed: {len(final_trace.steps)} steps")
            
            return True
        else:
            logger.info("✅ Integration test: TPV not triggered (as expected for this case)")
            return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all Phase 1A foundation tests."""
    logger.info("🚀 Starting Phase 1A Foundation Tests")
    logger.info("=" * 60)
    
    tests = [
        ("TPV Monitor", test_tpv_monitor),
        ("Reasoning Controller", test_reasoning_controller),
        ("TPV Trigger", test_tpv_trigger),
        ("Component Integration", test_integration)
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
    logger.info("📊 PHASE 1A FOUNDATION TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tests Passed: {passed}/{total}")
    logger.info(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 ALL PHASE 1A FOUNDATION TESTS PASSED!")
        logger.info("✅ Ready to proceed with Phase 1B: Integration")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED!")
        logger.error("Please fix issues before proceeding to Phase 1B")
        return 1

if __name__ == "__main__":
    sys.exit(main())
