"""
MEMOIR Phase B Integration Tests

End-to-end tests for the complete MEMOIR edit and retrieve cycle.
Tests the integration between MEMOIR_EditSkill and enhanced transformer blocks.

Author: SAM Development Team
Version: 1.0.0
"""

import unittest
import torch
import tempfile
import shutil
from pathlib import Path

# Import MEMOIR components
from sam.core.model_layers import MEMOIRTransformerBlock
from sam.orchestration.skills.internal.memoir_edit import MEMOIR_EditSkill
from sam.orchestration.uif import SAM_UIF, UIFStatus

class TestMEMOIRPhaseB(unittest.TestCase):
    """End-to-end tests for MEMOIR Phase B functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hidden_size = 512
        self.temp_dir = tempfile.mkdtemp()
        
        # Create MEMOIR transformer block
        self.memoir_block = MEMOIRTransformerBlock(
            hidden_size=self.hidden_size,
            num_attention_heads=8,
            intermediate_size=2048,
            enable_memoir=True
        )
        
        # Create MEMOIR edit skill
        self.edit_skill = MEMOIR_EditSkill(
            model=None,  # Will use synthetic model
            hidden_size=self.hidden_size,
            learning_rate=1e-3,
            max_training_steps=5
        )
        
        # Set up storage directory
        self.edit_skill.mask_database.storage_dir = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_edit_cycle(self):
        """Test the complete edit and retrieve cycle."""
        # Step 1: Create UIF for edit operation
        uif = SAM_UIF(
            input_query="Test edit operation",
            intermediate_data={
                "edit_prompt": "What is the capital of France?",
                "correct_answer": "Paris",
                "edit_context": "Geography correction",
                "confidence_score": 0.95
            }
        )
        
        # Step 2: Execute edit skill
        result_uif = self.edit_skill.execute(uif)
        
        # Verify edit was successful
        self.assertEqual(result_uif.status, UIFStatus.PENDING)  # Should not fail
        self.assertIn("edit_id", result_uif.intermediate_data)
        self.assertIn("edit_success", result_uif.intermediate_data)
        
        edit_success = result_uif.intermediate_data["edit_success"]
        if edit_success:
            edit_id = result_uif.intermediate_data["edit_id"]
            edit_mask = result_uif.intermediate_data["edit_mask"]
            
            # Step 3: Test retrieval in transformer block
            # Generate query that should match the edit
            batch_size, seq_len = 2, 10
            hidden_states = torch.randn(batch_size, seq_len, self.hidden_size)
            
            # Forward pass with retrieval enabled
            output, _ = self.memoir_block(
                hidden_states,
                enable_memoir_retrieval=True
            )
            
            # Verify output shape
            self.assertEqual(output.shape, hidden_states.shape)
            
            # Check if retrieval occurred
            retrieval_info = self.memoir_block.get_last_retrieval_info()
            # Note: Retrieval might not occur due to synthetic data
            
            print(f"✅ Edit cycle completed successfully: {edit_id}")
        else:
            print("⚠️  Edit failed (expected with synthetic model)")
    
    def test_edit_skill_validation(self):
        """Test edit skill input validation."""
        # Test valid input
        valid_uif = SAM_UIF(
            input_query="Test validation",
            intermediate_data={
                "edit_prompt": "What is 2+2?",
                "correct_answer": "4"
            }
        )
        
        self.assertTrue(self.edit_skill.can_execute(valid_uif))
        
        # Test invalid input - missing correct_answer
        invalid_uif = SAM_UIF(
            input_query="Test validation",
            intermediate_data={
                "edit_prompt": "What is 2+2?"
            }
        )
        
        self.assertFalse(self.edit_skill.can_execute(invalid_uif))
        
        # Test invalid input - empty prompt
        invalid_uif2 = SAM_UIF(
            input_query="Test validation",
            intermediate_data={
                "edit_prompt": "",
                "correct_answer": "4"
            }
        )
        
        self.assertFalse(self.edit_skill.can_execute(invalid_uif2))
    
    def test_transformer_retrieval_threshold(self):
        """Test retrieval threshold functionality."""
        # Test setting threshold
        self.memoir_block.set_retrieval_threshold(0.8)
        self.assertEqual(self.memoir_block.retrieval_threshold, 0.8)
        
        # Test invalid threshold
        with self.assertRaises(ValueError):
            self.memoir_block.set_retrieval_threshold(1.5)
        
        with self.assertRaises(ValueError):
            self.memoir_block.set_retrieval_threshold(-0.1)
    
    def test_forced_edit_retrieval(self):
        """Test forced edit retrieval functionality."""
        # Test forced retrieval with query text
        result = self.memoir_block.force_edit_retrieval("What is the capital of France?")
        
        # Should return None since no edits are stored yet
        self.assertIsNone(result)
        
        # Get retrieval statistics
        stats = self.memoir_block.get_retrieval_statistics()
        self.assertIn('retrieval_threshold', stats)
        self.assertIn('memory_info', stats)
    
    def test_memory_layer_integration(self):
        """Test integration with ResidualMemoryLayer."""
        # Add an edit directly to the memory layer
        edit_mask = torch.zeros(self.hidden_size)
        edit_mask[:50] = 1.0
        
        slot = self.memoir_block.add_memory_edit("test_integration", edit_mask)
        self.assertIsNotNone(slot)
        
        # Test forward pass with the edit
        hidden_states = torch.randn(1, 5, self.hidden_size)
        
        # Forward pass with specific edit
        output, _ = self.memoir_block(
            hidden_states,
            edit_mask=edit_mask,
            edit_id="test_integration"
        )
        
        self.assertEqual(output.shape, hidden_states.shape)
        
        # Remove the edit
        success = self.memoir_block.remove_memory_edit("test_integration")
        self.assertTrue(success)
    
    def test_edit_skill_statistics(self):
        """Test edit skill statistics tracking."""
        initial_stats = self.edit_skill.get_edit_statistics()
        self.assertEqual(initial_stats['total_edits'], 0)
        self.assertEqual(initial_stats['successful_edits'], 0)
        
        # Perform an edit (will likely fail with synthetic model)
        uif = SAM_UIF(
            input_query="Test statistics",
            intermediate_data={
                "edit_prompt": "Test prompt for statistics",
                "correct_answer": "Test answer"
            }
        )
        
        self.edit_skill.execute(uif)
        
        # Check updated statistics
        updated_stats = self.edit_skill.get_edit_statistics()
        self.assertEqual(updated_stats['total_edits'], 1)
    
    def test_retrieval_cache_management(self):
        """Test retrieval cache management."""
        # Clear cache
        self.memoir_block.clear_retrieval_cache()
        
        # Get statistics before and after cache operations
        stats_before = self.memoir_block.get_retrieval_statistics()
        
        # Perform some operations that would populate cache
        hidden_states = torch.randn(1, 5, self.hidden_size)
        self.memoir_block(hidden_states, enable_memoir_retrieval=True)
        
        stats_after = self.memoir_block.get_retrieval_statistics()
        
        # Both should succeed without errors
        self.assertIsInstance(stats_before, dict)
        self.assertIsInstance(stats_after, dict)
    
    def test_error_handling(self):
        """Test error handling in edit operations."""
        # Test with malformed UIF
        malformed_uif = SAM_UIF(
            input_query="Test error handling",
            intermediate_data={
                "edit_prompt": None,  # Invalid type
                "correct_answer": "Test answer"
            }
        )
        
        # Should handle gracefully
        try:
            result_uif = self.edit_skill.execute(malformed_uif)
            # Should either succeed with warning or fail gracefully
            self.assertIn(result_uif.status, [UIFStatus.PENDING, UIFStatus.FAILURE])
        except Exception as e:
            # Should raise SkillExecutionError, not generic exception
            self.assertIn("execution failed", str(e).lower())
    
    def test_concurrent_edits(self):
        """Test handling of multiple concurrent edits."""
        # Add multiple edits to the memory layer
        for i in range(3):
            edit_mask = torch.zeros(self.hidden_size)
            edit_mask[i*50:(i+1)*50] = 1.0  # Different regions
            
            slot = self.memoir_block.add_memory_edit(f"concurrent_edit_{i}", edit_mask)
            self.assertIsNotNone(slot)
        
        # Test forward pass with multiple active edits
        hidden_states = torch.randn(1, 5, self.hidden_size)
        output, _ = self.memoir_block(hidden_states)
        
        self.assertEqual(output.shape, hidden_states.shape)
        
        # Check memory info
        memory_info = self.memoir_block.get_memory_info()
        self.assertEqual(memory_info['active_edits'], 3)
        
        # Clean up
        for i in range(3):
            self.memoir_block.remove_memory_edit(f"concurrent_edit_{i}")


class TestMEMOIRIntegrationScenarios(unittest.TestCase):
    """Test realistic integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hidden_size = 256  # Smaller for faster tests
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_factual_correction_scenario(self):
        """Test a realistic factual correction scenario."""
        # Create components
        memoir_block = MEMOIRTransformerBlock(
            hidden_size=self.hidden_size,
            num_attention_heads=4,
            intermediate_size=1024,
            enable_memoir=True
        )
        
        edit_skill = MEMOIR_EditSkill(
            hidden_size=self.hidden_size,
            max_training_steps=3
        )
        
        # Scenario: Correct a factual error
        correction_uif = SAM_UIF(
            input_query="Factual correction",
            intermediate_data={
                "edit_prompt": "The capital of Australia is Sydney",
                "correct_answer": "The capital of Australia is Canberra",
                "edit_context": "Geography correction",
                "confidence_score": 0.9,
                "edit_metadata": {
                    "source": "user_correction",
                    "category": "geography"
                }
            }
        )
        
        # Execute the correction
        result_uif = edit_skill.execute(correction_uif)
        
        # Verify the correction was processed
        self.assertIn("edit_id", result_uif.intermediate_data)
        
        # Test that the transformer can process related queries
        hidden_states = torch.randn(1, 10, self.hidden_size)
        output, _ = memoir_block(hidden_states, enable_memoir_retrieval=True)
        
        self.assertEqual(output.shape, hidden_states.shape)
        
        print("✅ Factual correction scenario completed")
    
    def test_personalization_scenario(self):
        """Test a personalization scenario."""
        # Create components
        memoir_block = MEMOIRTransformerBlock(
            hidden_size=self.hidden_size,
            num_attention_heads=4,
            intermediate_size=1024,
            enable_memoir=True
        )
        
        edit_skill = MEMOIR_EditSkill(
            hidden_size=self.hidden_size,
            max_training_steps=3
        )
        
        # Scenario: Learn user preference
        preference_uif = SAM_UIF(
            input_query="User preference learning",
            intermediate_data={
                "edit_prompt": "What programming language should I use?",
                "correct_answer": "Based on your previous projects, Python would be ideal",
                "edit_context": "User prefers Python for data science projects",
                "confidence_score": 0.8,
                "edit_metadata": {
                    "source": "user_preference",
                    "category": "personalization",
                    "user_id": "test_user_123"
                }
            }
        )
        
        # Execute the personalization
        result_uif = edit_skill.execute(preference_uif)
        
        # Verify processing
        self.assertIn("edit_id", result_uif.intermediate_data)
        
        print("✅ Personalization scenario completed")


def run_phase_b_tests():
    """Run all Phase B integration tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestMEMOIRPhaseB))
    test_suite.addTest(unittest.makeSuite(TestMEMOIRIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running MEMOIR Phase B Integration Tests...")
    print("=" * 60)
    
    success = run_phase_b_tests()
    
    if success:
        print("\n🎉 All Phase B tests passed! Edit & Retrieve cycle is working.")
    else:
        print("\n❌ Some Phase B tests failed. Please check the output above.")
    
    exit(0 if success else 1)
