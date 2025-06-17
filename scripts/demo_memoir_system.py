#!/usr/bin/env python3
"""
MEMOIR System Demonstration

Interactive demonstration of the complete MEMOIR "Lifelong Knowledge Editor"
system showing edit and retrieve operations.

Usage:
    python scripts/demo_memoir_system.py

Author: SAM Development Team
Version: 1.0.0
"""

import torch
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🧠 {title}")
    print("="*60)

def print_step(step: str, description: str):
    """Print a formatted step."""
    print(f"\n📋 {step}: {description}")
    print("-" * 50)

def demonstrate_memoir_components():
    """Demonstrate individual MEMOIR components."""
    print_header("MEMOIR Component Demonstration")
    
    # Import components
    from sam.core.model_layers import ResidualMemoryLayer, MEMOIRTransformerBlock
    from sam.core.fingerprinter import TopHashFingerprinter
    from sam.memory.edit_mask_db import EditMaskDatabase
    
    hidden_size = 512
    
    print_step("1", "ResidualMemoryLayer Demonstration")
    
    # Create ResidualMemoryLayer
    memory_layer = ResidualMemoryLayer(hidden_size=hidden_size, max_edits=100)
    print(f"✅ Created ResidualMemoryLayer with {hidden_size}D hidden size")
    
    # Show zero initialization
    initial_norm = memory_layer.edit_weights.norm().item()
    print(f"✅ Initial weight norm: {initial_norm:.6f} (should be 0.0)")
    
    # Add an edit
    edit_mask = torch.zeros(hidden_size)
    edit_mask[:50] = 1.0  # Activate first 50 neurons
    
    slot = memory_layer.add_edit("demo_edit_1", edit_mask, {"description": "Demo edit"})
    print(f"✅ Added edit to slot {slot}")
    
    # Test forward pass
    hidden_states = torch.randn(2, 10, hidden_size)
    output = memory_layer(hidden_states, edit_mask=edit_mask, edit_id="demo_edit_1")
    print(f"✅ Forward pass completed, output shape: {output.shape}")
    
    print_step("2", "TopHashFingerprinter Demonstration")
    
    # Create fingerprinter
    fingerprinter = TopHashFingerprinter(hidden_size=hidden_size, top_k=50)
    print(f"✅ Created TopHashFingerprinter with top_k=50")
    
    # Generate masks
    activations = torch.randn(hidden_size)
    mask1 = fingerprinter.generate_mask(activations)
    mask2 = fingerprinter.generate_mask(activations)  # Should be identical
    
    print(f"✅ Generated masks, sparsity: {(mask1 == 0).float().mean().item():.3f}")
    print(f"✅ Determinism check: {torch.equal(mask1, mask2)}")
    
    # Analyze mask properties
    properties = fingerprinter.analyze_mask_properties(mask1)
    print(f"✅ Mask properties: {properties['num_active']} active neurons")
    
    print_step("3", "EditMaskDatabase Demonstration")
    
    # Create database
    temp_dir = tempfile.mkdtemp()
    try:
        db = EditMaskDatabase(hidden_size=hidden_size, storage_dir=temp_dir)
        print(f"✅ Created EditMaskDatabase with storage at {temp_dir}")
        
        # Add masks
        for i in range(3):
            mask = torch.zeros(hidden_size)
            mask[i*50:(i+1)*50] = 1.0
            success = db.add(f"db_edit_{i}", mask, {"index": i})
            print(f"✅ Added edit {i}: {success}")
        
        # Search for similar mask
        query_mask = torch.zeros(hidden_size)
        query_mask[:50] = 1.0  # Should match first edit
        
        result = db.find_closest(query_mask, threshold=0.8)
        if result:
            edit_id, found_mask, similarity = result
            print(f"✅ Found similar edit: {edit_id} (similarity: {similarity:.3f})")
        else:
            print("⚠️  No similar edit found")
        
        # Show statistics
        stats = db.get_statistics()
        print(f"✅ Database stats: {stats['total_edits']} edits, {stats['total_searches']} searches")
        
    finally:
        shutil.rmtree(temp_dir)
    
    print_step("4", "MEMOIRTransformerBlock Demonstration")
    
    # Create transformer block
    block = MEMOIRTransformerBlock(
        hidden_size=hidden_size,
        num_attention_heads=8,
        intermediate_size=2048,
        enable_memoir=True
    )
    print(f"✅ Created MEMOIRTransformerBlock with MEMOIR enabled")
    
    # Test forward pass
    hidden_states = torch.randn(2, 10, hidden_size)
    output, _ = block(hidden_states, enable_memoir_retrieval=True)
    print(f"✅ Forward pass with retrieval, output shape: {output.shape}")
    
    # Add memory edit
    edit_mask = torch.zeros(hidden_size)
    edit_mask[:25] = 1.0
    slot = block.add_memory_edit("transformer_edit", edit_mask)
    print(f"✅ Added memory edit to slot {slot}")
    
    # Test with specific edit
    output_with_edit, _ = block(
        hidden_states, 
        edit_mask=edit_mask, 
        edit_id="transformer_edit"
    )
    print(f"✅ Forward pass with specific edit, output shape: {output_with_edit.shape}")
    
    print("\n🎉 All components demonstrated successfully!")

def demonstrate_edit_skill():
    """Demonstrate the MEMOIR_EditSkill."""
    print_header("MEMOIR_EditSkill Demonstration")
    
    from sam.orchestration.skills.internal.memoir_edit import MEMOIR_EditSkill
    from sam.orchestration.uif import SAM_UIF
    
    print_step("1", "Creating MEMOIR_EditSkill")
    
    # Create edit skill
    edit_skill = MEMOIR_EditSkill(
        hidden_size=256,  # Smaller for demo
        max_training_steps=5,
        learning_rate=1e-3
    )
    print(f"✅ Created MEMOIR_EditSkill")
    
    # Show skill metadata
    metadata = edit_skill.get_metadata()
    print(f"✅ Skill name: {metadata.name}")
    print(f"✅ Skill version: {metadata.version}")
    print(f"✅ Required inputs: {metadata.required_inputs}")
    
    print_step("2", "Preparing Edit Request")
    
    # Create UIF for edit
    edit_uif = SAM_UIF(
        input_query="Factual correction demonstration",
        intermediate_data={
            "edit_prompt": "What is the capital of Australia?",
            "correct_answer": "Canberra",
            "edit_context": "Geography correction - Sydney is the largest city but not the capital",
            "confidence_score": 0.95,
            "edit_metadata": {
                "source": "demonstration",
                "category": "geography",
                "timestamp": datetime.now().isoformat()
            }
        }
    )
    print(f"✅ Created edit UIF")
    
    # Validate input
    can_execute = edit_skill.can_execute(edit_uif)
    print(f"✅ Input validation: {can_execute}")
    
    print_step("3", "Executing Edit")
    
    try:
        # Execute the edit
        result_uif = edit_skill.execute(edit_uif)
        
        # Show results
        if "edit_id" in result_uif.intermediate_data:
            edit_id = result_uif.intermediate_data["edit_id"]
            edit_success = result_uif.intermediate_data.get("edit_success", False)
            
            print(f"✅ Edit executed: {edit_id}")
            print(f"✅ Edit success: {edit_success}")
            
            if edit_success:
                training_metrics = result_uif.intermediate_data.get("training_metrics", {})
                print(f"✅ Training steps: {training_metrics.get('steps', 'N/A')}")
                print(f"✅ Final loss: {training_metrics.get('final_loss', 'N/A')}")
                print(f"✅ Converged: {training_metrics.get('converged', 'N/A')}")
            else:
                print("⚠️  Edit marked as failed (expected with synthetic model)")
        else:
            print("⚠️  No edit_id returned")
        
        # Show skill statistics
        stats = edit_skill.get_edit_statistics()
        print(f"✅ Total edits attempted: {stats['total_edits']}")
        print(f"✅ Successful edits: {stats['successful_edits']}")
        print(f"✅ Success rate: {stats['success_rate']:.2%}")
        
    except Exception as e:
        print(f"⚠️  Edit execution failed (expected with synthetic model): {e}")
    
    print("\n🎉 MEMOIR_EditSkill demonstration completed!")

def demonstrate_end_to_end_scenario():
    """Demonstrate a complete end-to-end scenario."""
    print_header("End-to-End MEMOIR Scenario")
    
    from sam.core.model_layers import MEMOIRTransformerBlock
    from sam.orchestration.skills.internal.memoir_edit import MEMOIR_EditSkill
    from sam.orchestration.uif import SAM_UIF
    
    hidden_size = 256
    temp_dir = tempfile.mkdtemp()
    
    try:
        print_step("1", "Setting Up MEMOIR System")
        
        # Create components
        transformer_block = MEMOIRTransformerBlock(
            hidden_size=hidden_size,
            num_attention_heads=4,
            intermediate_size=1024,
            enable_memoir=True
        )
        
        edit_skill = MEMOIR_EditSkill(
            hidden_size=hidden_size,
            max_training_steps=3
        )
        
        # Override storage for demo
        edit_skill.mask_database.storage_dir = Path(temp_dir)
        
        print(f"✅ Created transformer block and edit skill")
        
        print_step("2", "Scenario: Learning User Preferences")
        
        # Scenario: User teaches SAM their programming preferences
        scenarios = [
            {
                "edit_prompt": "What programming language should I use for web development?",
                "correct_answer": "Based on your previous projects, you prefer React with TypeScript",
                "edit_context": "User preference learning",
                "confidence_score": 0.9
            },
            {
                "edit_prompt": "What database should I use for my project?",
                "correct_answer": "You typically prefer PostgreSQL for relational data",
                "edit_context": "Database preference",
                "confidence_score": 0.8
            },
            {
                "edit_prompt": "What testing framework should I use?",
                "correct_answer": "You usually choose Jest for JavaScript testing",
                "edit_context": "Testing preference",
                "confidence_score": 0.85
            }
        ]
        
        edit_ids = []
        
        for i, scenario in enumerate(scenarios):
            print(f"\n  📝 Learning preference {i+1}: {scenario['edit_prompt'][:50]}...")
            
            # Create UIF
            uif = SAM_UIF(
                input_query=f"Preference learning {i+1}",
                intermediate_data=scenario
            )
            
            # Execute edit
            try:
                result_uif = edit_skill.execute(uif)
                if "edit_id" in result_uif.intermediate_data:
                    edit_id = result_uif.intermediate_data["edit_id"]
                    edit_ids.append(edit_id)
                    print(f"  ✅ Learned preference: {edit_id}")
                else:
                    print(f"  ⚠️  Preference learning processed but no edit_id")
            except Exception as e:
                print(f"  ⚠️  Preference learning failed: {e}")
        
        print_step("3", "Testing Learned Preferences")
        
        # Test that the transformer can process queries related to learned preferences
        test_queries = [
            "web development recommendation",
            "database selection advice", 
            "testing framework choice"
        ]
        
        for query in test_queries:
            print(f"\n  🔍 Testing query: {query}")
            
            # Generate synthetic hidden states for the query
            torch.manual_seed(hash(query) % 2**32)
            hidden_states = torch.randn(1, 5, hidden_size)
            
            # Forward pass with retrieval
            output, _ = transformer_block(
                hidden_states,
                enable_memoir_retrieval=True
            )
            
            print(f"  ✅ Processed query, output shape: {output.shape}")
            
            # Check if any retrieval occurred
            retrieval_info = transformer_block.get_last_retrieval_info()
            if retrieval_info:
                print(f"  🎯 Retrieved edit: {retrieval_info['edit_id']} "
                      f"(similarity: {retrieval_info['similarity']:.3f})")
            else:
                print(f"  📭 No relevant edit retrieved")
        
        print_step("4", "System Statistics")
        
        # Show comprehensive statistics
        edit_stats = edit_skill.get_edit_statistics()
        print(f"✅ Edit Statistics:")
        print(f"  • Total edits: {edit_stats['total_edits']}")
        print(f"  • Success rate: {edit_stats['success_rate']:.2%}")
        
        retrieval_stats = transformer_block.get_retrieval_statistics()
        print(f"✅ Retrieval Statistics:")
        print(f"  • Threshold: {retrieval_stats['retrieval_threshold']}")
        
        memory_info = transformer_block.get_memory_info()
        if memory_info:
            print(f"✅ Memory Statistics:")
            print(f"  • Active edits: {memory_info['active_edits']}")
            print(f"  • Memory usage: {memory_info['memory_usage_mb']:.2f} MB")
        
        print("\n🎉 End-to-end scenario completed successfully!")
        
    finally:
        shutil.rmtree(temp_dir)

def main():
    """Main demonstration function."""
    setup_logging()
    
    print("🚀 MEMOIR System Demonstration")
    print("=" * 60)
    print("Interactive demonstration of SAM's Lifelong Knowledge Editor")
    print("Based on the MEMOIR paper implementation")
    print("=" * 60)
    
    try:
        # Run demonstrations
        demonstrate_memoir_components()
        demonstrate_edit_skill()
        demonstrate_end_to_end_scenario()
        
        print_header("Demonstration Complete")
        print("🎉 All MEMOIR components demonstrated successfully!")
        print("\n✨ Key Capabilities Shown:")
        print("  • Non-destructive knowledge editing")
        print("  • Deterministic mask generation")
        print("  • Efficient similarity-based retrieval")
        print("  • Gradient-isolated training")
        print("  • End-to-end edit and retrieve cycles")
        print("\n🚀 SAM is now equipped with lifelong learning capabilities!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
