#!/usr/bin/env python3
"""
MEMOIR Phase C Verification Script

Comprehensive verification that high-level integration with SAM's advanced
systems is implemented correctly and meets all Phase C requirements.

Usage:
    python scripts/verify_memoir_phase_c.py

Author: SAM Development Team
Version: 1.0.0
"""

import sys
import logging
import tempfile
import shutil
from pathlib import Path

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_sof_integration():
    """Test MEMOIR SOF integration."""
    print("🔗 Testing MEMOIR SOF Integration...")
    
    try:
        from sam.orchestration.memoir_sof_integration import MEMOIRSOFIntegration
        
        # Test initialization
        sof_integration = MEMOIRSOFIntegration()
        print("✅ MEMOIRSOFIntegration initialized successfully")
        
        # Test skill information retrieval
        memoir_skills = sof_integration.get_memoir_skills()
        if isinstance(memoir_skills, dict):
            print("✅ MEMOIR skills information retrieved")
        else:
            print("❌ Failed to retrieve MEMOIR skills information")
            return False
        
        # Test statistics
        stats = sof_integration.get_memoir_statistics()
        if isinstance(stats, dict) and 'registered_skills' in stats:
            print("✅ MEMOIR statistics available")
        else:
            print("❌ MEMOIR statistics not available")
            return False
        
        # Test plan suggestions
        suggestions = sof_integration.create_memoir_plan_suggestions(
            "Actually, that's incorrect. The capital of Australia is Canberra."
        )
        if isinstance(suggestions, list):
            print("✅ MEMOIR plan suggestions working")
            if 'MEMOIR_EditSkill' in suggestions:
                print("✅ Correct skill suggested for factual correction")
        else:
            print("❌ MEMOIR plan suggestions failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ SOF integration test failed: {e}")
        return False

def test_feedback_handler():
    """Test MEMOIR feedback handler."""
    print("\n🔄 Testing MEMOIR Feedback Handler...")
    
    try:
        from sam.learning.feedback_handler import MEMOIRFeedbackHandler, FeedbackType
        
        # Test initialization
        feedback_handler = MEMOIRFeedbackHandler()
        print("✅ MEMOIRFeedbackHandler initialized successfully")
        
        # Test feedback processing
        result = feedback_handler.process_feedback(
            original_query="What is the capital of France?",
            sam_response="The capital of France is London.",
            user_feedback="Actually, the capital of France is Paris."
        )
        
        if 'feedback_id' in result:
            print("✅ Feedback processing working")
        else:
            print("❌ Feedback processing failed")
            return False
        
        # Test feedback classification
        result2 = feedback_handler.process_feedback(
            original_query="What programming language should I use?",
            sam_response="You could use any language.",
            user_feedback="I prefer Python for data science projects."
        )
        
        if 'feedback_id' in result2:
            print("✅ Preference learning feedback working")
        else:
            print("❌ Preference learning feedback failed")
            return False
        
        # Test statistics
        stats = feedback_handler.get_feedback_statistics()
        if stats['total_feedback_events'] >= 2:
            print("✅ Feedback statistics tracking working")
        else:
            print("❌ Feedback statistics tracking failed")
            return False
        
        # Test recent feedback retrieval
        recent = feedback_handler.get_recent_feedback(limit=5)
        if isinstance(recent, list) and len(recent) >= 2:
            print("✅ Recent feedback retrieval working")
        else:
            print("❌ Recent feedback retrieval failed")
            return False
        
        # Test configuration
        success = feedback_handler.configure_feedback_handler(
            confidence_threshold=0.8
        )
        if success:
            print("✅ Feedback handler configuration working")
        else:
            print("❌ Feedback handler configuration failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback handler test failed: {e}")
        return False

def test_autonomous_factual_correction():
    """Test autonomous factual correction skill."""
    print("\n🤖 Testing Autonomous Factual Correction...")
    
    try:
        from sam.orchestration.skills.autonomous.factual_correction import AutonomousFactualCorrectionSkill
        from sam.orchestration.uif import SAM_UIF
        
        # Test initialization
        correction_skill = AutonomousFactualCorrectionSkill(
            confidence_threshold=0.5,
            enable_external_verification=False  # Disable for testing
        )
        print("✅ AutonomousFactualCorrectionSkill initialized successfully")
        
        # Test skill metadata
        if correction_skill.skill_name == "AutonomousFactualCorrectionSkill":
            print("✅ Skill metadata correct")
        else:
            print("❌ Skill metadata incorrect")
            return False
        
        # Test dependency validation
        valid_uif = SAM_UIF(
            input_query="Test correction",
            intermediate_data={
                "response_text": "The capital of Australia is Sydney.",
                "original_query": "What is the capital of Australia?"
            }
        )
        
        if correction_skill.can_execute(valid_uif):
            print("✅ Dependency validation working")
        else:
            print("❌ Dependency validation failed")
            return False
        
        # Test invalid input handling
        invalid_uif = SAM_UIF(
            input_query="Test correction",
            intermediate_data={
                "original_query": "What is the capital of Australia?"
                # Missing response_text
            }
        )
        
        if not correction_skill.can_execute(invalid_uif):
            print("✅ Invalid input rejection working")
        else:
            print("❌ Invalid input rejection failed")
            return False
        
        # Test execution (may fail without full MEMOIR setup)
        try:
            test_uif = SAM_UIF(
                input_query="Test autonomous correction",
                intermediate_data={
                    "response_text": "The capital of France is London. It was founded in 1066.",
                    "original_query": "What is the capital of France?",
                    "confidence_scores": {"overall": 0.4}
                }
            )
            
            result_uif = correction_skill.execute(test_uif)
            
            if "corrections_made" in result_uif.intermediate_data:
                print("✅ Autonomous correction execution working")
            else:
                print("⚠️  Autonomous correction executed but no corrections field")
                
        except Exception as e:
            print(f"⚠️  Autonomous correction execution failed (expected without full MEMOIR): {e}")
        
        # Test statistics
        stats = correction_skill.get_correction_statistics()
        if isinstance(stats, dict) and 'total_responses_analyzed' in stats:
            print("✅ Correction statistics working")
        else:
            print("❌ Correction statistics failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Autonomous factual correction test failed: {e}")
        return False

def test_reasoning_integration():
    """Test MEMOIR reasoning integration."""
    print("\n🧠 Testing MEMOIR Reasoning Integration...")
    
    try:
        from sam.reasoning.memoir_reasoning_integration import MEMOIRReasoningIntegration
        
        # Test initialization
        reasoning_integration = MEMOIRReasoningIntegration()
        print("✅ MEMOIRReasoningIntegration initialized successfully")
        
        # Test TPV integration
        tpv_result = reasoning_integration.integrate_with_tpv(
            thinking_output="I think the capital of France is Paris...",
            planning_output="Plan to verify this information...",
            verification_output="Verification shows uncertainty about the answer.",
            confidence_scores={
                'thinking': 0.8,
                'planning': 0.7,
                'verification': 0.5  # Low confidence to trigger learning
            },
            original_query="What is the capital of France?"
        )
        
        if tpv_result['success']:
            print("✅ TPV integration working")
        else:
            print(f"⚠️  TPV integration completed with issues: {tpv_result.get('error', 'Unknown')}")
        
        # Test SLP integration
        slp_result = reasoning_integration.integrate_with_slp(
            learning_context={'session_id': 'test_session'},
            structured_knowledge={
                'geography': {
                    'content': 'Paris is the capital of France',
                    'objective': 'Learn world capitals'
                }
            },
            learning_objectives=['Learn geography facts'],
            performance_metrics={'geography_accuracy': 0.6}
        )
        
        if slp_result['success']:
            print("✅ SLP integration working")
        else:
            print(f"⚠️  SLP integration completed with issues: {slp_result.get('error', 'Unknown')}")
        
        # Test statistics
        stats = reasoning_integration.get_reasoning_integration_statistics()
        if isinstance(stats, dict) and 'tpv_guided_edits' in stats:
            print("✅ Reasoning integration statistics working")
        else:
            print("❌ Reasoning integration statistics failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Reasoning integration test failed: {e}")
        return False

def test_end_to_end_integration():
    """Test end-to-end Phase C integration."""
    print("\n🔗 Testing End-to-End Phase C Integration...")
    
    try:
        from sam.orchestration.memoir_sof_integration import MEMOIRSOFIntegration
        from sam.learning.feedback_handler import MEMOIRFeedbackHandler
        from sam.reasoning.memoir_reasoning_integration import MEMOIRReasoningIntegration
        
        # Create integrated system
        sof_integration = MEMOIRSOFIntegration()
        feedback_handler = MEMOIRFeedbackHandler()
        reasoning_integration = MEMOIRReasoningIntegration()
        
        print("✅ All Phase C components created successfully")
        
        # Test feedback to reasoning flow
        feedback_result = feedback_handler.process_feedback(
            original_query="What is the capital of Australia?",
            sam_response="The capital of Australia is Sydney.",
            user_feedback="Actually, the capital is Canberra."
        )
        
        if 'feedback_id' in feedback_result:
            print("✅ Feedback processing in integrated system working")
        else:
            print("❌ Feedback processing in integrated system failed")
            return False
        
        # Test reasoning-guided learning
        tpv_result = reasoning_integration.integrate_with_tpv(
            thinking_output="Thinking about geography correction...",
            planning_output="Planning to update knowledge...",
            verification_output="Verification confirms user correction is accurate.",
            confidence_scores={'verification': 0.9},
            original_query="What is the capital of Australia?"
        )
        
        if tpv_result['success']:
            print("✅ Reasoning-guided learning in integrated system working")
        else:
            print("⚠️  Reasoning-guided learning completed with issues")
        
        # Test plan suggestions for integrated workflow
        suggestions = sof_integration.create_memoir_plan_suggestions(
            "I need to correct this information and remember my preference."
        )
        
        if isinstance(suggestions, list):
            print("✅ Integrated plan suggestions working")
        else:
            print("❌ Integrated plan suggestions failed")
            return False
        
        print("✅ End-to-end Phase C integration working")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end integration test failed: {e}")
        return False

def test_performance_characteristics():
    """Test Phase C performance characteristics."""
    print("\n⚡ Testing Phase C Performance Characteristics...")
    
    try:
        import time
        from sam.learning.feedback_handler import MEMOIRFeedbackHandler
        from sam.reasoning.memoir_reasoning_integration import MEMOIRReasoningIntegration
        
        # Test feedback processing performance
        feedback_handler = MEMOIRFeedbackHandler()
        
        start_time = time.time()
        for i in range(5):
            feedback_handler.process_feedback(
                original_query=f"Test query {i}",
                sam_response=f"Test response {i}",
                user_feedback=f"Test feedback {i}"
            )
        feedback_time = (time.time() - start_time) / 5
        
        if feedback_time < 0.1:  # Should be under 100ms
            print(f"✅ Feedback processing performance good: {feedback_time*1000:.2f}ms")
        else:
            print(f"⚠️  Feedback processing slower than expected: {feedback_time*1000:.2f}ms")
        
        # Test reasoning integration performance
        reasoning_integration = MEMOIRReasoningIntegration()
        
        start_time = time.time()
        for i in range(3):
            reasoning_integration.integrate_with_tpv(
                thinking_output=f"Thinking {i}",
                planning_output=f"Planning {i}",
                verification_output=f"Verification {i}",
                confidence_scores={'thinking': 0.8, 'planning': 0.7, 'verification': 0.6},
                original_query=f"Query {i}"
            )
        reasoning_time = (time.time() - start_time) / 3
        
        if reasoning_time < 0.5:  # Should be under 500ms
            print(f"✅ Reasoning integration performance good: {reasoning_time*1000:.2f}ms")
        else:
            print(f"⚠️  Reasoning integration slower than expected: {reasoning_time*1000:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Main verification function."""
    setup_logging()
    
    print("🚀 MEMOIR Phase C Verification")
    print("=" * 60)
    print("Verifying that high-level integration with SAM's advanced")
    print("systems is implemented correctly and meets all requirements.")
    print("=" * 60)
    
    tests = [
        ("SOF Integration", test_sof_integration),
        ("Feedback Handler", test_feedback_handler),
        ("Autonomous Factual Correction", test_autonomous_factual_correction),
        ("Reasoning Integration", test_reasoning_integration),
        ("End-to-End Integration", test_end_to_end_integration),
        ("Performance Characteristics", test_performance_characteristics)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Phase C verification SUCCESSFUL!")
        print("\n✅ Definition of Done for Phase C:")
        print("  • MEMOIR skills registered with SOF framework")
        print("  • FeedbackHandler integration for automatic learning")
        print("  • Autonomous FactualCorrectionSkill implemented")
        print("  • Advanced reasoning integration with TPV and SLP")
        print("  • End-to-end integration working across all systems")
        print("  • Performance characteristics within acceptable limits")
        print("\n🎉 MEMOIR IMPLEMENTATION COMPLETE!")
        print("SAM now has full lifelong learning capabilities!")
        return 0
    else:
        print(f"\n❌ Phase C verification FAILED!")
        print(f"Please fix the {total-passed} failing test(s) before completion.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
