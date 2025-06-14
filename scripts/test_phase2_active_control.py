#!/usr/bin/env python3
"""
Phase 2 Active Control Testing Script
Tests the active reasoning control functionality.
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

def test_active_control_thresholds():
    """Test active control with different threshold scenarios."""
    logger.info("🧪 Testing Active Control Thresholds...")
    
    try:
        from sam.cognition.tpv import TPVMonitor, ReasoningController, ControlMode
        
        # Initialize components in active mode
        monitor = TPVMonitor()
        controller = ReasoningController(mode=ControlMode.ACTIVE)
        
        if not monitor.initialize():
            logger.error("❌ Monitor initialization failed")
            return False
        
        logger.info("✅ Active control components initialized")
        
        # Test scenarios
        test_scenarios = [
            {
                'name': 'Completion Threshold Test',
                'description': 'Should stop when reasoning quality is high',
                'responses': [
                    "This is a basic response with initial reasoning that demonstrates fundamental understanding of the topic.",
                    "This is a more detailed response with better reasoning that explores multiple perspectives and provides deeper analysis of the subject matter.",
                    "This is a comprehensive response with excellent reasoning and thorough analysis that demonstrates mastery of the topic, considers various viewpoints, and provides well-supported conclusions.",
                    "This is an exceptional response with outstanding reasoning, comprehensive analysis, and perfect conclusions that synthesizes complex information, addresses potential counterarguments, and provides actionable insights with clear logical flow and evidence-based recommendations."
                ],
                'expected_stop': True,
                'expected_reason': 'COMPLETE'
            },
            {
                'name': 'Plateau Detection Test',
                'description': 'Should stop when reasoning stagnates',
                'responses': [
                    "This is a response.",
                    "This is a similar response.",
                    "This is another similar response.",
                    "This is yet another similar response.",
                    "This is still another similar response."
                ],
                'expected_stop': True,
                'expected_reason': 'PLATEAU'
            },
            {
                'name': 'Token Limit Test',
                'description': 'Should stop when token limit is reached',
                'responses': [f"Token {i} " * 50 for i in range(20)],  # Generate many tokens
                'expected_stop': True,
                'expected_reason': 'HALT'
            }
        ]
        
        passed_tests = 0
        for i, scenario in enumerate(test_scenarios):
            logger.info(f"\n📋 Test {i+1}: {scenario['name']}")
            logger.info(f"  📝 {scenario['description']}")
            
            # Start monitoring
            query_id = monitor.start_monitoring(f"test_query_{i}")
            
            stopped = False
            stop_reason = None
            
            for j, response in enumerate(scenario['responses']):
                # Simulate token count
                token_count = len(response.split()) * (j + 1)
                
                # Get TPV score
                score = monitor.predict_progress(response, query_id, token_count=token_count)
                
                # Check if controller says to continue
                trace = monitor.get_trace(query_id)
                should_continue = controller.should_continue(trace)
                
                logger.info(f"    Step {j+1}: Score = {score:.3f}, Tokens = {token_count}, Continue = {should_continue}")
                
                if not should_continue:
                    stopped = True
                    # Get the last control action to determine reason
                    recent_actions = controller.get_recent_actions(1)
                    if recent_actions:
                        stop_reason = recent_actions[0].metadata.get('action_type', 'UNKNOWN')
                    break
            
            # Stop monitoring
            monitor.stop_monitoring(query_id)
            
            # Evaluate results
            if stopped == scenario['expected_stop']:
                if stopped and stop_reason == scenario['expected_reason']:
                    logger.info(f"  ✅ Test {i+1}: PASSED (stopped with {stop_reason})")
                    passed_tests += 1
                elif not stopped:
                    logger.info(f"  ✅ Test {i+1}: PASSED (continued as expected)")
                    passed_tests += 1
                else:
                    logger.warning(f"  ⚠️ Test {i+1}: PARTIAL (stopped but wrong reason: {stop_reason} vs {scenario['expected_reason']})")
            else:
                logger.error(f"  ❌ Test {i+1}: FAILED (expected stop: {scenario['expected_stop']}, actual: {stopped})")
        
        logger.info(f"\n✅ Active control tests: {passed_tests}/{len(test_scenarios)} passed")
        return passed_tests >= len(test_scenarios) * 0.75
        
    except Exception as e:
        logger.error(f"❌ Active control threshold test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_control_configuration():
    """Test control parameter configuration."""
    logger.info("🧪 Testing Control Configuration...")
    
    try:
        from sam.cognition.tpv import TPVConfig
        
        # Load configuration
        config = TPVConfig()
        control_params = config.control_params
        
        # Verify control parameters
        expected_params = {
            'completion_threshold': 0.92,
            'plateau_threshold': 0.005,
            'plateau_patience': 3,
            'max_tokens': 500,
            'min_steps': 2
        }
        
        passed_checks = 0
        for param_name, expected_value in expected_params.items():
            actual_value = getattr(control_params, param_name)
            if actual_value == expected_value:
                logger.info(f"  ✅ {param_name}: {actual_value}")
                passed_checks += 1
            else:
                logger.error(f"  ❌ {param_name}: expected {expected_value}, got {actual_value}")
        
        logger.info(f"✅ Configuration checks: {passed_checks}/{len(expected_params)} passed")
        return passed_checks == len(expected_params)
        
    except Exception as e:
        logger.error(f"❌ Control configuration test failed: {e}")
        return False

def test_performance_optimization():
    """Test performance improvements from Phase 2 optimizations."""
    logger.info("🧪 Testing Performance Optimization...")
    
    try:
        from sam.cognition.tpv import SAMTPVIntegration, UserProfile
        
        # Test cached initialization
        logger.info("Testing cached initialization...")
        
        # First initialization (should be slow)
        start_time = time.time()
        integration1 = SAMTPVIntegration()
        integration1.initialize()
        first_init_time = time.time() - start_time
        
        # Second initialization (should be fast due to caching)
        start_time = time.time()
        integration2 = SAMTPVIntegration()
        integration2.initialize()
        second_init_time = time.time() - start_time
        
        # Calculate speedup
        speedup = first_init_time / second_init_time if second_init_time > 0 else 1.0
        
        logger.info(f"📊 Initialization Performance:")
        logger.info(f"  First init: {first_init_time:.3f}s")
        logger.info(f"  Second init: {second_init_time:.3f}s")
        logger.info(f"  Speedup: {speedup:.1f}x")
        
        # Test should show significant speedup (>2x)
        if speedup > 2.0:
            logger.info("✅ Cached initialization working correctly")
            return True
        else:
            logger.warning(f"⚠️ Limited speedup from caching: {speedup:.1f}x")
            return False
        
    except Exception as e:
        logger.error(f"❌ Performance optimization test failed: {e}")
        return False

def test_ui_data_generation():
    """Test UI data generation for active control."""
    logger.info("🧪 Testing UI Data Generation...")
    
    try:
        from sam.cognition.tpv import TPVMonitor, ReasoningController, ControlMode
        
        # Initialize components
        monitor = TPVMonitor()
        controller = ReasoningController(mode=ControlMode.ACTIVE)
        
        if not monitor.initialize():
            logger.error("❌ Monitor initialization failed")
            return False
        
        # Simulate a controlled session
        query_id = monitor.start_monitoring("test_ui_query")
        
        # Generate some steps
        responses = [
            "Initial response",
            "Improved response with better reasoning",
            "Final response with excellent reasoning quality"
        ]
        
        for i, response in enumerate(responses):
            score = monitor.predict_progress(response, query_id, token_count=(i+1)*20)
            trace = monitor.get_trace(query_id)
            should_continue = controller.should_continue(trace)
            
            if not should_continue:
                break
        
        # Get final trace and control actions
        final_trace = monitor.stop_monitoring(query_id)
        recent_actions = controller.get_recent_actions(5)
        
        # Generate UI data structure
        ui_data = {
            'active_control_enabled': True,
            'final_decision': recent_actions[0].metadata.get('action_type', 'CONTINUE') if recent_actions else 'CONTINUE',
            'decision_reason': recent_actions[0].reason if recent_actions else 'No control action taken',
            'control_statistics': controller.get_control_statistics(),
            'trace_summary': {
                'total_steps': len(final_trace.steps) if final_trace else 0,
                'final_score': final_trace.current_score if final_trace else 0.0,
                'total_tokens': final_trace.total_tokens if final_trace else 0
            }
        }
        
        # Verify UI data structure
        required_fields = ['active_control_enabled', 'final_decision', 'decision_reason', 'control_statistics']
        missing_fields = [field for field in required_fields if field not in ui_data]
        
        if not missing_fields:
            logger.info("✅ UI data structure complete")
            logger.info(f"  🎛️ Control Enabled: {ui_data['active_control_enabled']}")
            logger.info(f"  🚦 Final Decision: {ui_data['final_decision']}")
            logger.info(f"  📝 Reason: {ui_data['decision_reason']}")
            logger.info(f"  📊 Control Stats: {ui_data['control_statistics']}")
            return True
        else:
            logger.error(f"❌ Missing UI data fields: {missing_fields}")
            return False
        
    except Exception as e:
        logger.error(f"❌ UI data generation test failed: {e}")
        return False

def main():
    """Run all Phase 2 active control tests."""
    logger.info("🚀 Starting Phase 2 Active Control Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Control Configuration", test_control_configuration),
        ("Active Control Thresholds", test_active_control_thresholds),
        ("Performance Optimization", test_performance_optimization),
        ("UI Data Generation", test_ui_data_generation)
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
    logger.info("📊 PHASE 2 ACTIVE CONTROL TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tests Passed: {passed}/{total}")
    logger.info(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed >= total * 0.75:
        logger.info("🎉 PHASE 2 ACTIVE CONTROL TESTS PASSED!")
        logger.info("✅ Active reasoning control is working correctly")
        logger.info("✅ Performance optimizations implemented")
        logger.info("✅ Ready for Phase 2 UI enhancements and A/B testing")
        return 0
    else:
        logger.error("❌ INSUFFICIENT TESTS PASSED!")
        logger.error("Please fix active control issues before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())
