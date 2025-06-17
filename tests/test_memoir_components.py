"""
Unit Tests for MEMOIR Components

Comprehensive tests for ResidualMemoryLayer, TopHashFingerprinter,
and EditMaskDatabase components.

Author: SAM Development Team
Version: 1.0.0
"""

import unittest
import torch
import numpy as np
import tempfile
import shutil
from pathlib import Path

# Import MEMOIR components
from sam.core.model_layers import ResidualMemoryLayer, MEMOIRTransformerBlock
from sam.core.fingerprinter import TopHashFingerprinter
from sam.memory.edit_mask_db import EditMaskDatabase

class TestResidualMemoryLayer(unittest.TestCase):
    """Test cases for ResidualMemoryLayer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hidden_size = 512
        self.batch_size = 2
        self.seq_len = 10
        self.layer = ResidualMemoryLayer(
            hidden_size=self.hidden_size,
            max_edits=100
        )
    
    def test_initialization(self):
        """Test layer initialization."""
        self.assertEqual(self.layer.hidden_size, self.hidden_size)
        self.assertEqual(self.layer.max_edits, 100)
        
        # Check zero initialization
        self.assertTrue(torch.allclose(self.layer.edit_weights, torch.zeros_like(self.layer.edit_weights)))
        self.assertEqual(self.layer.edit_active.sum().item(), 0)
    
    def test_forward_no_mask(self):
        """Test forward pass with no edit mask."""
        hidden_states = torch.randn(self.batch_size, self.seq_len, self.hidden_size)
        output = self.layer(hidden_states)
        
        # Should return zeros when no mask provided
        expected = torch.zeros_like(hidden_states)
        self.assertTrue(torch.allclose(output, expected))
    
    def test_forward_with_mask(self):
        """Test forward pass with edit mask."""
        hidden_states = torch.randn(self.batch_size, self.seq_len, self.hidden_size)
        edit_mask = torch.zeros(self.hidden_size)
        edit_mask[:10] = 1.0  # Activate first 10 neurons
        
        output = self.layer(hidden_states, edit_mask=edit_mask)
        
        # Output should have same shape
        self.assertEqual(output.shape, hidden_states.shape)
        
        # Should be zeros since no edits are active
        expected = torch.zeros_like(hidden_states)
        self.assertTrue(torch.allclose(output, expected))
    
    def test_add_edit(self):
        """Test adding an edit."""
        edit_mask = torch.zeros(self.hidden_size)
        edit_mask[:10] = 1.0
        
        slot = self.layer.add_edit("test_edit", edit_mask, {"description": "test"})
        
        self.assertEqual(slot, 0)  # First slot
        self.assertTrue(self.layer.edit_active[0])
        self.assertIn("test_edit", self.layer.edit_metadata)
        self.assertEqual(self.layer.total_edits_made.item(), 1)
    
    def test_remove_edit(self):
        """Test removing an edit."""
        edit_mask = torch.zeros(self.hidden_size)
        edit_mask[:10] = 1.0
        
        # Add edit
        self.layer.add_edit("test_edit", edit_mask)
        
        # Remove edit
        success = self.layer.remove_edit("test_edit")
        
        self.assertTrue(success)
        self.assertFalse(self.layer.edit_active[0])
        self.assertNotIn("test_edit", self.layer.edit_metadata)
    
    def test_get_edit_info(self):
        """Test getting edit information."""
        info = self.layer.get_edit_info()
        
        self.assertIn('total_edits_made', info)
        self.assertIn('active_edits', info)
        self.assertIn('available_slots', info)
        self.assertIn('memory_usage_mb', info)


class TestTopHashFingerprinter(unittest.TestCase):
    """Test cases for TopHashFingerprinter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hidden_size = 512
        self.top_k = 50
        self.fingerprinter = TopHashFingerprinter(
            hidden_size=self.hidden_size,
            top_k=self.top_k,
            seed=42
        )
    
    def test_initialization(self):
        """Test fingerprinter initialization."""
        self.assertEqual(self.fingerprinter.hidden_size, self.hidden_size)
        self.assertEqual(self.fingerprinter.top_k, self.top_k)
        self.assertEqual(len(self.fingerprinter.permutation_matrix), self.hidden_size)
    
    def test_generate_mask_1d(self):
        """Test mask generation with 1D input."""
        activations = torch.randn(self.hidden_size)
        mask = self.fingerprinter.generate_mask(activations)
        
        # Check mask properties
        self.assertEqual(mask.shape, activations.shape)
        self.assertEqual(mask.sum().item(), self.top_k)
        self.assertTrue(torch.all((mask == 0) | (mask == 1)))  # Binary mask
    
    def test_generate_mask_3d(self):
        """Test mask generation with 3D input."""
        batch_size, seq_len = 2, 10
        activations = torch.randn(batch_size, seq_len, self.hidden_size)
        mask = self.fingerprinter.generate_mask(activations)
        
        # Check mask properties
        self.assertEqual(mask.shape, activations.shape)
        # Each position should have top_k active neurons
        self.assertEqual(mask[0, 0, :].sum().item(), self.top_k)
    
    def test_determinism(self):
        """Test that mask generation is deterministic."""
        activations = torch.randn(self.hidden_size)
        
        mask1 = self.fingerprinter.generate_mask(activations, use_cache=False)
        mask2 = self.fingerprinter.generate_mask(activations, use_cache=False)
        
        self.assertTrue(torch.equal(mask1, mask2))
    
    def test_validate_determinism(self):
        """Test the built-in determinism validation."""
        activations = torch.randn(self.hidden_size)
        is_deterministic = self.fingerprinter.validate_determinism(activations, num_tests=5)
        
        self.assertTrue(is_deterministic)
    
    def test_analyze_mask_properties(self):
        """Test mask property analysis."""
        activations = torch.randn(self.hidden_size)
        mask = self.fingerprinter.generate_mask(activations)
        
        properties = self.fingerprinter.analyze_mask_properties(mask)
        
        self.assertIn('sparsity', properties)
        self.assertIn('density', properties)
        self.assertIn('num_active', properties)
        self.assertEqual(properties['num_active'], self.top_k)
        self.assertAlmostEqual(properties['density'], self.top_k / self.hidden_size, places=3)
    
    def test_statistics(self):
        """Test getting fingerprinter statistics."""
        # Generate a few masks
        for _ in range(5):
            activations = torch.randn(self.hidden_size)
            self.fingerprinter.generate_mask(activations)
        
        stats = self.fingerprinter.get_statistics()
        
        self.assertEqual(stats['masks_generated'], 5)
        self.assertEqual(stats['hidden_size'], self.hidden_size)
        self.assertEqual(stats['top_k'], self.top_k)


class TestEditMaskDatabase(unittest.TestCase):
    """Test cases for EditMaskDatabase."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hidden_size = 512
        self.temp_dir = tempfile.mkdtemp()
        self.db = EditMaskDatabase(
            hidden_size=self.hidden_size,
            storage_dir=self.temp_dir
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test database initialization."""
        self.assertEqual(self.db.hidden_size, self.hidden_size)
        self.assertEqual(self.db.total_edits, 0)
        self.assertEqual(len(self.db.edit_metadata), 0)
    
    def test_add_mask(self):
        """Test adding a mask to the database."""
        mask = torch.zeros(self.hidden_size)
        mask[:50] = 1.0  # Sparse mask
        
        success = self.db.add("test_edit", mask, {"description": "test"})
        
        self.assertTrue(success)
        self.assertEqual(self.db.total_edits, 1)
        self.assertIn("test_edit", self.db.edit_metadata)
    
    def test_find_closest_exact_match(self):
        """Test finding exact match."""
        mask = torch.zeros(self.hidden_size)
        mask[:50] = 1.0
        
        # Add mask
        self.db.add("test_edit", mask)
        
        # Search for exact match
        result = self.db.find_closest(mask, threshold=0.9)
        
        self.assertIsNotNone(result)
        edit_id, found_mask, similarity = result
        self.assertEqual(edit_id, "test_edit")
        self.assertGreater(similarity, 0.9)
    
    def test_find_closest_no_match(self):
        """Test finding no match when threshold is high."""
        mask1 = torch.zeros(self.hidden_size)
        mask1[:50] = 1.0
        
        mask2 = torch.zeros(self.hidden_size)
        mask2[100:150] = 1.0  # Different pattern
        
        # Add first mask
        self.db.add("test_edit", mask1)
        
        # Search with second mask (should not match with high threshold)
        result = self.db.find_closest(mask2, threshold=0.9)
        
        self.assertIsNone(result)
    
    def test_remove_mask(self):
        """Test removing a mask."""
        mask = torch.zeros(self.hidden_size)
        mask[:50] = 1.0
        
        # Add mask
        self.db.add("test_edit", mask)
        
        # Remove mask
        success = self.db.remove("test_edit")
        
        self.assertTrue(success)
        self.assertNotIn("test_edit", self.db.edit_metadata)
    
    def test_statistics(self):
        """Test getting database statistics."""
        # Add some masks
        for i in range(3):
            mask = torch.zeros(self.hidden_size)
            mask[i*10:(i+1)*10] = 1.0
            self.db.add(f"edit_{i}", mask)
        
        stats = self.db.get_statistics()
        
        self.assertEqual(stats['total_edits'], 3)
        self.assertEqual(stats['active_edits'], 3)
        self.assertEqual(stats['hidden_size'], self.hidden_size)
    
    def test_persistence(self):
        """Test saving and loading database."""
        mask = torch.zeros(self.hidden_size)
        mask[:50] = 1.0
        
        # Add mask and save
        self.db.add("test_edit", mask, {"description": "test"})
        success = self.db.save_to_disk()
        self.assertTrue(success)
        
        # Create new database and load
        new_db = EditMaskDatabase(
            hidden_size=self.hidden_size,
            storage_dir=self.temp_dir
        )
        
        # Check that data was loaded
        self.assertEqual(new_db.total_edits, 1)
        self.assertIn("test_edit", new_db.edit_metadata)


class TestMEMOIRTransformerBlock(unittest.TestCase):
    """Test cases for MEMOIRTransformerBlock."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hidden_size = 512
        self.num_heads = 8
        self.intermediate_size = 2048
        self.block = MEMOIRTransformerBlock(
            hidden_size=self.hidden_size,
            num_attention_heads=self.num_heads,
            intermediate_size=self.intermediate_size,
            enable_memoir=True
        )
    
    def test_initialization(self):
        """Test block initialization."""
        self.assertEqual(self.block.hidden_size, self.hidden_size)
        self.assertTrue(self.block.enable_memoir)
        self.assertIsNotNone(self.block.residual_memory)
    
    def test_forward_without_memoir(self):
        """Test forward pass without MEMOIR activation."""
        batch_size, seq_len = 2, 10
        hidden_states = torch.randn(batch_size, seq_len, self.hidden_size)
        
        output, _ = self.block(hidden_states)
        
        self.assertEqual(output.shape, hidden_states.shape)
    
    def test_forward_with_memoir(self):
        """Test forward pass with MEMOIR edit mask."""
        batch_size, seq_len = 2, 10
        hidden_states = torch.randn(batch_size, seq_len, self.hidden_size)
        edit_mask = torch.zeros(self.hidden_size)
        edit_mask[:50] = 1.0
        
        output, _ = self.block(hidden_states, edit_mask=edit_mask)
        
        self.assertEqual(output.shape, hidden_states.shape)
    
    def test_memory_operations(self):
        """Test memory add/remove operations."""
        edit_mask = torch.zeros(self.hidden_size)
        edit_mask[:50] = 1.0
        
        # Add edit
        slot = self.block.add_memory_edit("test_edit", edit_mask)
        self.assertIsNotNone(slot)
        
        # Get memory info
        info = self.block.get_memory_info()
        self.assertIsNotNone(info)
        self.assertEqual(info['active_edits'], 1)
        
        # Remove edit
        success = self.block.remove_memory_edit("test_edit")
        self.assertTrue(success)


def run_all_tests():
    """Run all MEMOIR component tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestResidualMemoryLayer))
    test_suite.addTest(unittest.makeSuite(TestTopHashFingerprinter))
    test_suite.addTest(unittest.makeSuite(TestEditMaskDatabase))
    test_suite.addTest(unittest.makeSuite(TestMEMOIRTransformerBlock))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running MEMOIR Component Tests...")
    print("=" * 60)
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! MEMOIR components are ready.")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
    
    exit(0 if success else 1)
