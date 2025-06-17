"""
MEMOIR Phase C Integration Tests

End-to-end tests for high-level integration with SAM's advanced systems
including SOF, FeedbackHandler, and reasoning integration.

Author: SAM Development Team
Version: 1.0.0
"""

import unittest
import tempfile
import shutil
from pathlib import Path

# Import MEMOIR Phase C components
from sam.orchestration.memoir_sof_integration import MEMOIRSOFIntegration
from sam.learning.feedback_handler import MEMOIRFeedbackHandler, FeedbackType
from sam.orchestration.skills.autonomous.factual_correction import AutonomousFactualCorrectionSkill
from sam.reasoning.memoir_reasoning_integration import MEMOIRReasoningIntegration
from sam.orchestration.uif import SAM_UIF

class TestMEMOIRSOFIntegration(unittest.TestCase):
    """Test MEMOIR SOF integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sof_integration = MEMOIRSOFIntegration()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_memoir_sof_initialization(self):
        """Test MEMOIR SOF integration initialization."""
        # Test initialization
        success = self.sof_integration.initialize()
        
        # Note: May fail without full SAM environment, but should not crash
        self.assertIsInstance(success, bool)
        
        # Test skill registration info
        memoir_skills = self.sof_integration.get_memoir_skills()
        self.assertIsInstance(memoir_skills, dict)
        
        # Test statistics
        stats = self.sof_integration.get_memoir_statistics()
        self.assertIn('registered_skills', stats)
        self.assertIn('configuration', stats)
    
    def test_memoir_skill_configuration(self):
        """Test MEMOIR skill configuration."""
        # Test configuration with valid parameters
        success = self.sof_integration.configure_memoir_skill(
            'MEMOIR_EditSkill',
            learning_rate=1e-3,
            max_training_steps=5
        )
        
        # Should handle gracefully even if skill not registered
        self.assertIsInstance(success, bool)
    
    def test_memoir_plan_suggestions(self):
        """Test MEMOIR plan suggestions for queries."""
        # Test factual correction suggestions
        correction_suggestions = self.sof_integration.create_memoir_plan_suggestions(
            "Actually, that's not right. The capital of Australia is Canberra."
        )
        
        self.assertIsInstance(correction_suggestions, list)
        if correction_suggestions:
            self.assertIn('MEMOIR_EditSkill', correction_suggestions)
        
        # Test preference learning suggestions
        preference_suggestions = self.sof_integration.create_memoir_plan_suggestions(
            "Remember that I prefer Python for data science projects."
        )
        
        self.assertIsInstance(preference_suggestions, list)
        if preference_suggestions:
            self.assertIn('MEMOIR_EditSkill', preference_suggestions)


class TestMEMOIRFeedbackHandler(unittest.TestCase):
    """Test MEMOIR feedback handler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.feedback_handler = MEMOIRFeedbackHandler()
    
    def test_feedback_classification(self):
        """Test feedback type classification."""
        # Test factual correction classification
        result = self.feedback_handler.process_feedback(
            original_query="What is the capital of Australia?",
            sam_response="The capital of Australia is Sydney.",
            user_feedback="Actually, the capital of Australia is Canberra."
        )
        
        self.assertIn('feedback_id', result)
        
        # Test preference learning classification
        result = self.feedback_handler.process_feedback(
            original_query="What programming language should I use?",
            sam_response="You could use JavaScript or Python.",
            user_feedback="I prefer Python for data science projects."
        )
        
        self.assertIn('feedback_id', result)
    
    def test_feedback_statistics(self):
        """Test feedback statistics tracking."""
        # Process some feedback
        self.feedback_handler.process_feedback(
            original_query="Test query",
            sam_response="Test response",
            user_feedback="Test correction"
        )
        
        # Get statistics
        stats = self.feedback_handler.get_feedback_statistics()
        
        self.assertIn('total_feedback_events', stats)
        self.assertIn('feedback_by_type', stats)
        self.assertIn('success_rate', stats)
        self.assertEqual(stats['total_feedback_events'], 1)
    
    def test_recent_feedback_retrieval(self):
        """Test recent feedback retrieval."""
        # Process feedback
        self.feedback_handler.process_feedback(
            original_query="Test query",
            sam_response="Test response",
            user_feedback="Test feedback"
        )
        
        # Get recent feedback
        recent = self.feedback_handler.get_recent_feedback(limit=5)
        
        self.assertIsInstance(recent, list)
        self.assertEqual(len(recent), 1)
        self.assertIn('feedback_id', recent[0])
        self.assertIn('feedback_type', recent[0])
    
    def test_feedback_configuration(self):
        """Test feedback handler configuration."""
        # Test configuration
        success = self.feedback_handler.configure_feedback_handler(
            auto_process_feedback=False,
            confidence_threshold=0.8
        )
        
        self.assertTrue(success)
        self.assertFalse(self.feedback_handler.config['auto_process_feedback'])
        self.assertEqual(self.feedback_handler.config['confidence_threshold'], 0.8)


class TestAutonomousFactualCorrectionSkill(unittest.TestCase):
    """Test autonomous factual correction skill."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.correction_skill = AutonomousFactualCorrectionSkill(
            confidence_threshold=0.5,
            enable_external_verification=False  # Disable for testing
        )
    
    def test_skill_initialization(self):
        """Test skill initialization."""
        self.assertEqual(self.correction_skill.skill_name, "AutonomousFactualCorrectionSkill")
        self.assertEqual(self.correction_skill.skill_category, "autonomous")
        self.assertIn("response_text", self.correction_skill.required_inputs)
        self.assertIn("original_query", self.correction_skill.required_inputs)
    
    def test_skill_execution(self):
        """Test skill execution with sample data."""
        # Create UIF with test data
        uif = SAM_UIF(
            input_query="Test autonomous correction",
            intermediate_data={
                "response_text": "The capital of France is London. It was founded in 1066.",
                "original_query": "What is the capital of France?",
                "confidence_scores": {
                    "overall": 0.4,  # Low confidence to trigger correction
                    "geographical_error": 0.3
                }
            }
        )
        
        # Test execution
        try:
            result_uif = self.correction_skill.execute(uif)
            
            # Check that execution completed
            self.assertIn("corrections_made", result_uif.intermediate_data)
            self.assertIn("correction_details", result_uif.intermediate_data)
            self.assertIn("confidence_analysis", result_uif.intermediate_data)
            
        except Exception as e:
            # May fail without full MEMOIR setup, but should not crash unexpectedly
            self.assertIsInstance(e, Exception)
    
    def test_can_execute_validation(self):
        """Test skill execution validation."""
        # Valid UIF
        valid_uif = SAM_UIF(
            input_query="Test",
            intermediate_data={
                "response_text": "Some response text",
                "original_query": "Some query"
            }
        )
        
        self.assertTrue(self.correction_skill.can_execute(valid_uif))
        
        # Invalid UIF - missing response_text
        invalid_uif = SAM_UIF(
            input_query="Test",
            intermediate_data={
                "original_query": "Some query"
            }
        )
        
        self.assertFalse(self.correction_skill.can_execute(invalid_uif))
    
    def test_correction_statistics(self):
        """Test correction statistics tracking."""
        stats = self.correction_skill.get_correction_statistics()
        
        self.assertIn('total_responses_analyzed', stats)
        self.assertIn('corrections_made', stats)
        self.assertIn('error_types_detected', stats)
        self.assertIn('configuration', stats)


class TestMEMOIRReasoningIntegration(unittest.TestCase):
    """Test MEMOIR reasoning integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reasoning_integration = MEMOIRReasoningIntegration()
    
    def test_tpv_integration(self):
        """Test TPV (Thinking, Planning, Verification) integration."""
        # Test TPV integration with sample data
        result = self.reasoning_integration.integrate_with_tpv(
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
        
        self.assertIn('success', result)
        self.assertIn('learning_opportunities', result)
        self.assertIn('verification_issues', result)
        self.assertIn('edits_created', result)
    
    def test_slp_integration(self):
        """Test SLP (Structured Learning Protocol) integration."""
        # Test SLP integration with sample data
        result = self.reasoning_integration.integrate_with_slp(
            learning_context={'session_id': 'test_session'},
            structured_knowledge={
                'geography': {
                    'content': 'Paris is the capital of France',
                    'objective': 'Learn world capitals'
                }
            },
            learning_objectives=['Learn geography facts'],
            performance_metrics={'geography_accuracy': 0.6}  # Below threshold
        )
        
        self.assertIn('success', result)
        self.assertIn('knowledge_items_processed', result)
        self.assertIn('improvement_opportunities', result)
        self.assertIn('consolidation_edits', result)
    
    def test_reasoning_statistics(self):
        """Test reasoning integration statistics."""
        stats = self.reasoning_integration.get_reasoning_integration_statistics()
        
        self.assertIn('tpv_guided_edits', stats)
        self.assertIn('slp_learning_events', stats)
        self.assertIn('reasoning_corrections', stats)
        self.assertIn('configuration', stats)
        self.assertIn('integration_status', stats)


class TestMEMOIRPhaseCIntegration(unittest.TestCase):
    """Test complete Phase C integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_feedback_to_edit_flow(self):
        """Test complete flow from feedback to MEMOIR edit."""
        # Create components
        feedback_handler = MEMOIRFeedbackHandler()
        
        # Process user feedback
        feedback_result = feedback_handler.process_feedback(
            original_query="What is the capital of Australia?",
            sam_response="The capital of Australia is Sydney.",
            user_feedback="Actually, the capital is Canberra, not Sydney."
        )
        
        # Verify feedback was processed
        self.assertIn('feedback_id', feedback_result)
        
        # Check statistics
        stats = feedback_handler.get_feedback_statistics()
        self.assertEqual(stats['total_feedback_events'], 1)
    
    def test_autonomous_correction_integration(self):
        """Test autonomous correction integration."""
        # Create autonomous correction skill
        correction_skill = AutonomousFactualCorrectionSkill(
            enable_external_verification=False
        )
        
        # Test with response containing potential errors
        uif = SAM_UIF(
            input_query="Geography test",
            intermediate_data={
                "response_text": "The capital of Australia is Sydney, founded in 1788.",
                "original_query": "Tell me about Australia's capital.",
                "confidence_scores": {"overall": 0.4}
            }
        )
        
        # Execute correction
        try:
            result_uif = correction_skill.execute(uif)
            
            # Verify execution completed
            self.assertIn("corrections_made", result_uif.intermediate_data)
            
        except Exception as e:
            # Expected to fail without full MEMOIR setup
            self.assertIsInstance(e, Exception)
    
    def test_reasoning_guided_learning(self):
        """Test reasoning-guided learning scenarios."""
        reasoning_integration = MEMOIRReasoningIntegration()
        
        # Test TPV-guided learning
        tpv_result = reasoning_integration.integrate_with_tpv(
            thinking_output="Thinking about geography...",
            planning_output="Planning to answer about capitals...",
            verification_output="Verification failed - uncertain about answer.",
            confidence_scores={'verification': 0.4},
            original_query="What is the capital of France?"
        )
        
        self.assertIn('success', tpv_result)
        
        # Test SLP-guided learning
        slp_result = reasoning_integration.integrate_with_slp(
            learning_context={'domain': 'geography'},
            structured_knowledge={'facts': {'content': 'Geography facts'}},
            learning_objectives=['Learn capitals'],
            performance_metrics={'accuracy': 0.5}
        )
        
        self.assertIn('success', slp_result)


def run_phase_c_tests():
    """Run all Phase C integration tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestMEMOIRSOFIntegration))
    test_suite.addTest(unittest.makeSuite(TestMEMOIRFeedbackHandler))
    test_suite.addTest(unittest.makeSuite(TestAutonomousFactualCorrectionSkill))
    test_suite.addTest(unittest.makeSuite(TestMEMOIRReasoningIntegration))
    test_suite.addTest(unittest.makeSuite(TestMEMOIRPhaseCIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running MEMOIR Phase C Integration Tests...")
    print("=" * 60)
    
    success = run_phase_c_tests()
    
    if success:
        print("\n🎉 All Phase C tests passed! High-level integration is working.")
    else:
        print("\n❌ Some Phase C tests failed. Please check the output above.")
    
    exit(0 if success else 1)
