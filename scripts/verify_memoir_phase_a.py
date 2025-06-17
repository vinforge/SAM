#!/usr/bin/env python3
"""
MEMOIR Phase A Verification Script

Comprehensive verification that all Phase A components are implemented
correctly and meet the requirements from the implementation plan.

Usage:
    python scripts/verify_memoir_phase_a.py

Author: SAM Development Team
Version: 1.0.0
"""

import sys
import torch
import logging
from pathlib import Path

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_imports():
    """Test that all MEMOIR components can be imported."""
    print("🔍 Testing MEMOIR Component Imports...")
    
    try:
        from sam.core.model_layers import ResidualMemoryLayer, MEMOIRTransformerBlock
        print("✅ ResidualMemoryLayer and MEMOIRTransformerBlock imported successfully")
        
        from sam.core.fingerprinter import TopHashFingerprinter
        print("✅ TopHashFingerprinter imported successfully")
        
        from sam.memory.edit_mask_db import EditMaskDatabase
        print("✅ EditMaskDatabase imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_residual_memory_layer():
    """Test ResidualMemoryLayer functionality."""
    print("\n🧠 Testing ResidualMemoryLayer...")
    
    try:
        from sam.core.model_layers import ResidualMemoryLayer
        
        # Test initialization
        hidden_size = 512
        layer = ResidualMemoryLayer(hidden_size=hidden_size, max_edits=100)
        print("✅ ResidualMemoryLayer initialized successfully")
        
        # Test zero-weight initialization
        if torch.allclose(layer.edit_weights, torch.zeros_like(layer.edit_weights)):
            print("✅ Zero-weight initialization verified")
        else:
            print("❌ Zero-weight initialization failed")
            return False
        
        # Test forward pass with no effect
        batch_size, seq_len = 2, 10
        hidden_states = torch.randn(batch_size, seq_len, hidden_size)
        original_output = hidden_states.clone()
        
        # Forward pass should return zeros when no mask provided
        residual_output = layer(hidden_states)
        expected_zeros = torch.zeros_like(hidden_states)
        
        if torch.allclose(residual_output, expected_zeros):
            print("✅ No-effect forward pass verified")
        else:
            print("❌ Forward pass should return zeros with no mask")
            return False
        
        # Test edit addition
        edit_mask = torch.zeros(hidden_size)
        edit_mask[:50] = 1.0  # Activate first 50 neurons
        
        slot = layer.add_edit("test_edit", edit_mask, {"description": "test"})
        if slot == 0 and layer.edit_active[0]:
            print("✅ Edit addition verified")
        else:
            print("❌ Edit addition failed")
            return False
        
        # Test edit removal
        success = layer.remove_edit("test_edit")
        if success and not layer.edit_active[0]:
            print("✅ Edit removal verified")
        else:
            print("❌ Edit removal failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ResidualMemoryLayer test failed: {e}")
        return False

def test_top_hash_fingerprinter():
    """Test TopHashFingerprinter functionality."""
    print("\n🔍 Testing TopHashFingerprinter...")
    
    try:
        from sam.core.fingerprinter import TopHashFingerprinter
        
        # Test initialization
        hidden_size = 512
        top_k = 50
        fingerprinter = TopHashFingerprinter(
            hidden_size=hidden_size,
            top_k=top_k,
            seed=42
        )
        print("✅ TopHashFingerprinter initialized successfully")
        
        # Test permutation matrix
        if len(fingerprinter.permutation_matrix) == hidden_size:
            print("✅ Permutation matrix has correct size")
        else:
            print("❌ Permutation matrix size incorrect")
            return False
        
        # Test mask generation
        activations = torch.randn(hidden_size)
        mask = fingerprinter.generate_mask(activations)
        
        # Check mask properties
        if mask.shape == activations.shape:
            print("✅ Generated mask has correct shape")
        else:
            print("❌ Generated mask shape incorrect")
            return False
        
        if mask.sum().item() == top_k:
            print("✅ Generated mask has correct sparsity")
        else:
            print(f"❌ Generated mask sparsity incorrect: {mask.sum().item()} != {top_k}")
            return False
        
        if torch.all((mask == 0) | (mask == 1)):
            print("✅ Generated mask is binary")
        else:
            print("❌ Generated mask is not binary")
            return False
        
        # Test determinism
        mask1 = fingerprinter.generate_mask(activations, use_cache=False)
        mask2 = fingerprinter.generate_mask(activations, use_cache=False)
        
        if torch.equal(mask1, mask2):
            print("✅ Mask generation is deterministic")
        else:
            print("❌ Mask generation is not deterministic")
            return False
        
        # Test built-in determinism validation
        is_deterministic = fingerprinter.validate_determinism(activations, num_tests=5)
        if is_deterministic:
            print("✅ Built-in determinism validation passed")
        else:
            print("❌ Built-in determinism validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ TopHashFingerprinter test failed: {e}")
        return False

def test_edit_mask_database():
    """Test EditMaskDatabase functionality."""
    print("\n💾 Testing EditMaskDatabase...")
    
    try:
        from sam.memory.edit_mask_db import EditMaskDatabase
        import tempfile
        import shutil
        
        # Test initialization
        hidden_size = 512
        temp_dir = tempfile.mkdtemp()
        
        try:
            db = EditMaskDatabase(
                hidden_size=hidden_size,
                storage_dir=temp_dir
            )
            print("✅ EditMaskDatabase initialized successfully")
            
            # Test adding masks
            mask1 = torch.zeros(hidden_size)
            mask1[:50] = 1.0
            
            success = db.add("edit_1", mask1, {"description": "test edit 1"})
            if success and db.total_edits == 1:
                print("✅ Mask addition verified")
            else:
                print("❌ Mask addition failed")
                return False
            
            # Test finding exact match
            result = db.find_closest(mask1, threshold=0.9)
            if result is not None:
                edit_id, found_mask, similarity = result
                if edit_id == "edit_1" and similarity > 0.9:
                    print("✅ Exact match search verified")
                else:
                    print(f"❌ Exact match search failed: {edit_id}, {similarity}")
                    return False
            else:
                print("❌ Exact match search returned None")
                return False
            
            # Test no match with different mask
            mask2 = torch.zeros(hidden_size)
            mask2[100:150] = 1.0  # Different pattern
            
            result = db.find_closest(mask2, threshold=0.9)
            if result is None:
                print("✅ No match search verified")
            else:
                print("❌ Should not find match for different pattern")
                return False
            
            # Test mask removal
            success = db.remove("edit_1")
            if success and "edit_1" not in db.edit_metadata:
                print("✅ Mask removal verified")
            else:
                print("❌ Mask removal failed")
                return False
            
            return True
            
        finally:
            shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"❌ EditMaskDatabase test failed: {e}")
        return False

def test_memoir_transformer_block():
    """Test MEMOIRTransformerBlock functionality."""
    print("\n🔄 Testing MEMOIRTransformerBlock...")
    
    try:
        from sam.core.model_layers import MEMOIRTransformerBlock
        
        # Test initialization
        hidden_size = 512
        num_heads = 8
        intermediate_size = 2048
        
        block = MEMOIRTransformerBlock(
            hidden_size=hidden_size,
            num_attention_heads=num_heads,
            intermediate_size=intermediate_size,
            enable_memoir=True
        )
        print("✅ MEMOIRTransformerBlock initialized successfully")
        
        # Test that MEMOIR is enabled
        if block.enable_memoir and block.residual_memory is not None:
            print("✅ MEMOIR functionality enabled")
        else:
            print("❌ MEMOIR functionality not enabled")
            return False
        
        # Test forward pass
        batch_size, seq_len = 2, 10
        hidden_states = torch.randn(batch_size, seq_len, hidden_size)
        
        output, _ = block(hidden_states)
        
        if output.shape == hidden_states.shape:
            print("✅ Forward pass produces correct output shape")
        else:
            print("❌ Forward pass output shape incorrect")
            return False
        
        # Test memory operations
        edit_mask = torch.zeros(hidden_size)
        edit_mask[:50] = 1.0
        
        slot = block.add_memory_edit("test_edit", edit_mask)
        if slot is not None:
            print("✅ Memory edit addition verified")
        else:
            print("❌ Memory edit addition failed")
            return False
        
        # Test memory info
        info = block.get_memory_info()
        if info is not None and info['active_edits'] == 1:
            print("✅ Memory info retrieval verified")
        else:
            print("❌ Memory info retrieval failed")
            return False
        
        # Test memory edit removal
        success = block.remove_memory_edit("test_edit")
        if success:
            print("✅ Memory edit removal verified")
        else:
            print("❌ Memory edit removal failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ MEMOIRTransformerBlock test failed: {e}")
        return False

def test_integration():
    """Test integration between components."""
    print("\n🔗 Testing Component Integration...")
    
    try:
        from sam.core.model_layers import ResidualMemoryLayer
        from sam.core.fingerprinter import TopHashFingerprinter
        from sam.memory.edit_mask_db import EditMaskDatabase
        
        hidden_size = 512
        
        # Create components
        memory_layer = ResidualMemoryLayer(hidden_size=hidden_size)
        fingerprinter = TopHashFingerprinter(hidden_size=hidden_size, top_k=50)
        mask_db = EditMaskDatabase(hidden_size=hidden_size)
        
        print("✅ All components created successfully")
        
        # Test workflow: generate mask -> store in DB -> retrieve -> use in memory layer
        activations = torch.randn(hidden_size)
        
        # Generate mask
        edit_mask = fingerprinter.generate_mask(activations)
        print("✅ Mask generated by fingerprinter")
        
        # Store in database
        success = mask_db.add("integration_test", edit_mask)
        if not success:
            print("❌ Failed to store mask in database")
            return False
        print("✅ Mask stored in database")
        
        # Retrieve from database
        result = mask_db.find_closest(edit_mask, threshold=0.9)
        if result is None:
            print("❌ Failed to retrieve mask from database")
            return False
        
        edit_id, retrieved_mask, similarity = result
        print(f"✅ Mask retrieved from database (similarity: {similarity:.3f})")
        
        # Add to memory layer
        slot = memory_layer.add_edit(edit_id, retrieved_mask)
        print(f"✅ Edit added to memory layer (slot: {slot})")
        
        # Test forward pass with the edit
        hidden_states = torch.randn(2, 10, hidden_size)
        output = memory_layer(hidden_states, edit_mask=retrieved_mask, edit_id=edit_id)
        
        if output.shape == hidden_states.shape:
            print("✅ Integration test completed successfully")
            return True
        else:
            print("❌ Integration test failed - output shape mismatch")
            return False
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main verification function."""
    setup_logging()
    
    print("🚀 MEMOIR Phase A Verification")
    print("=" * 60)
    print("Verifying that all foundational MEMOIR components are")
    print("implemented correctly and meet the requirements.")
    print("=" * 60)
    
    tests = [
        ("Component Imports", test_imports),
        ("ResidualMemoryLayer", test_residual_memory_layer),
        ("TopHashFingerprinter", test_top_hash_fingerprinter),
        ("EditMaskDatabase", test_edit_mask_database),
        ("MEMOIRTransformerBlock", test_memoir_transformer_block),
        ("Component Integration", test_integration)
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
        print("\n🎉 Phase A verification SUCCESSFUL!")
        print("\n✅ Definition of Done for Phase A:")
        print("  • ResidualMemoryLayer implemented with zero-weight initialization")
        print("  • TopHashFingerprinter generates deterministic sparse masks")
        print("  • EditMaskDatabase provides efficient similarity search")
        print("  • All components are unit-tested and working")
        print("  • Integration between components verified")
        print("\n🚀 Ready to proceed to Phase B!")
        return 0
    else:
        print(f"\n❌ Phase A verification FAILED!")
        print(f"Please fix the {total-passed} failing test(s) before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
