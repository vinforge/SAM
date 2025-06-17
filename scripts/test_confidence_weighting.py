#!/usr/bin/env python3
"""
Test Script for PINN-Inspired Confidence-Based Weighting

Tests the confidence-based skill weighting system integrated with the Loss Balancer.
Validates dynamic execution order optimization, resource allocation, and adaptive weighting.

Usage:
    python scripts/test_confidence_weighting.py

Author: SAM Development Team
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add SAM to path
sys.path.append(str(Path(__file__).parent.parent))

from sam.orchestration.confidence_weighting import (
    ConfidenceWeighting, SkillCategory, WeightingResult
)
from sam.orchestration.loss_balancer import LossBalancer

def test_confidence_adjustment():
    """Test confidence-based weight adjustment."""
    print("🧪 Testing confidence-based weight adjustment...")
    
    weighting = ConfidenceWeighting()
    
    test_plan = [
        "MemoryRetrievalSkill",
        "ConflictDetectorSkill", 
        "ContentVettingSkill",
        "ResponseGenerationSkill"
    ]
    
    # Test high confidence scenario
    high_conf_result = weighting.calculate_weighted_plan(
        original_plan=test_plan,
        current_confidence=0.9,
        executed_skills=[],
        query_complexity="medium"
    )
    
    print(f"  High confidence (0.9):")
    print(f"    Original plan: {test_plan}")
    print(f"    Weighted plan: {high_conf_result.weighted_plan}")
    print(f"    Execution order: {high_conf_result.execution_order}")
    print(f"    Confidence impact: {high_conf_result.confidence_impact:.3f}")
    
    # Test low confidence scenario
    low_conf_result = weighting.calculate_weighted_plan(
        original_plan=test_plan,
        current_confidence=0.3,
        executed_skills=[],
        query_complexity="medium"
    )
    
    print(f"  Low confidence (0.3):")
    print(f"    Original plan: {test_plan}")
    print(f"    Weighted plan: {low_conf_result.weighted_plan}")
    print(f"    Execution order: {low_conf_result.execution_order}")
    print(f"    Confidence impact: {low_conf_result.confidence_impact:.3f}")
    
    # Validate that confidence affects weighting
    assert high_conf_result.confidence_impact != low_conf_result.confidence_impact
    assert len(high_conf_result.weighted_plan) == len(test_plan)
    assert len(low_conf_result.weighted_plan) == len(test_plan)
    
    print("  ✅ Confidence-based weight adjustment successful")

def test_execution_order_optimization():
    """Test dynamic execution order optimization."""
    print("\n🧪 Testing execution order optimization...")
    
    weighting = ConfidenceWeighting(enable_dynamic_reordering=True)
    
    test_plan = [
        "ResponseGenerationSkill",  # Usually last
        "MemoryRetrievalSkill",     # Usually first
        "ConflictDetectorSkill",    # Middle
        "CalculatorTool"            # Tool
    ]
    
    result = weighting.calculate_weighted_plan(
        original_plan=test_plan,
        current_confidence=0.5,
        executed_skills=[],
        query_complexity="medium"
    )
    
    print(f"  Original plan: {test_plan}")
    print(f"  Optimized order: {result.execution_order}")
    
    # Validate that ResponseGenerationSkill moved to end
    assert result.execution_order[-1] == "ResponseGenerationSkill"
    
    # Validate that MemoryRetrievalSkill is prioritized
    memory_index = result.execution_order.index("MemoryRetrievalSkill")
    response_index = result.execution_order.index("ResponseGenerationSkill")
    assert memory_index < response_index
    
    print("  ✅ Execution order optimization successful")

def test_resource_allocation():
    """Test resource allocation based on weights."""
    print("\n🧪 Testing resource allocation...")
    
    weighting = ConfidenceWeighting()
    
    test_plan = [
        "MemoryRetrievalSkill",
        "ConflictDetectorSkill",
        "ResponseGenerationSkill"
    ]
    
    result = weighting.calculate_weighted_plan(
        original_plan=test_plan,
        current_confidence=0.8,
        executed_skills=[],
        query_complexity="complex"
    )
    
    print(f"  Resource allocation:")
    total_allocation = 0.0
    for skill, allocation in result.resource_allocation.items():
        print(f"    {skill}: {allocation:.3f}")
        total_allocation += allocation
    
    print(f"  Total allocation: {total_allocation:.3f}")
    
    # Validate resource allocation
    assert abs(total_allocation - 1.0) < 0.001  # Should sum to 1.0
    assert all(0.0 <= alloc <= 1.0 for alloc in result.resource_allocation.values())
    
    print("  ✅ Resource allocation successful")

def test_query_complexity_impact():
    """Test impact of query complexity on weighting."""
    print("\n🧪 Testing query complexity impact...")
    
    weighting = ConfidenceWeighting()
    
    test_plan = [
        "MemoryRetrievalSkill",
        "ImplicitKnowledgeSkill",
        "CalculatorTool",
        "ResponseGenerationSkill"
    ]
    
    # Test simple query
    simple_result = weighting.calculate_weighted_plan(
        original_plan=test_plan,
        current_confidence=0.6,
        executed_skills=[],
        query_complexity="simple"
    )
    
    # Test complex query
    complex_result = weighting.calculate_weighted_plan(
        original_plan=test_plan,
        current_confidence=0.6,
        executed_skills=[],
        query_complexity="complex"
    )
    
    print(f"  Simple query weights:")
    for skill, weight in simple_result.skill_weights.items():
        print(f"    {skill}: {weight:.3f}")
    
    print(f"  Complex query weights:")
    for skill, weight in complex_result.skill_weights.items():
        print(f"    {skill}: {weight:.3f}")
    
    # Validate that complexity affects weights
    implicit_simple = simple_result.skill_weights.get("ImplicitKnowledgeSkill", 0.5)
    implicit_complex = complex_result.skill_weights.get("ImplicitKnowledgeSkill", 0.5)
    
    # Complex queries should give higher weight to synthesis skills
    assert implicit_complex >= implicit_simple
    
    print("  ✅ Query complexity impact successful")

def test_weight_adaptation():
    """Test adaptive weight adjustment based on performance."""
    print("\n🧪 Testing weight adaptation...")
    
    weighting = ConfidenceWeighting()
    
    # Get initial sensitivity
    initial_sensitivity = weighting.skill_weights["ConflictDetectorSkill"].confidence_sensitivity
    print(f"  Initial sensitivity: {initial_sensitivity:.3f}")
    
    # Simulate high accuracy performance
    weighting.adapt_weights(
        skill_name="ConflictDetectorSkill",
        performance_score=0.9,
        confidence_accuracy=0.85
    )
    
    # Check if sensitivity increased
    adapted_sensitivity = weighting.skill_weights["ConflictDetectorSkill"].confidence_sensitivity
    print(f"  Adapted sensitivity: {adapted_sensitivity:.3f}")
    
    # Should increase sensitivity for high accuracy
    assert adapted_sensitivity >= initial_sensitivity
    
    # Simulate low accuracy performance
    weighting.adapt_weights(
        skill_name="ConflictDetectorSkill",
        performance_score=0.6,
        confidence_accuracy=0.4
    )
    
    final_sensitivity = weighting.skill_weights["ConflictDetectorSkill"].confidence_sensitivity
    print(f"  Final sensitivity: {final_sensitivity:.3f}")
    
    # Should decrease sensitivity for low accuracy
    assert final_sensitivity <= adapted_sensitivity
    
    print("  ✅ Weight adaptation successful")

def test_integration_with_loss_balancer():
    """Test integration with Loss Balancer."""
    print("\n🧪 Testing integration with Loss Balancer...")
    
    balancer = LossBalancer(enable_confidence_weighting=True)
    
    test_plan = [
        "MemoryRetrievalSkill",
        "ConflictDetectorSkill",
        "ContentVettingSkill",
        "ResponseGenerationSkill"
    ]
    
    # Allocate effort with confidence weighting
    allocation = balancer.allocate_effort(
        plan=test_plan,
        initial_confidence=0.7,
        query_complexity="medium"
    )
    
    print(f"  Original plan: {test_plan}")
    print(f"  Optimized plan: {getattr(allocation, 'optimized_plan', 'Not available')}")
    print(f"  Effort allocations:")
    
    for skill, config in allocation.skill_efforts.items():
        print(f"    {skill}: {config.effort_level.value}")
    
    # Validate integration
    assert hasattr(allocation, 'optimized_plan')
    assert len(allocation.skill_efforts) == len(test_plan)
    
    # Get statistics including confidence weighting
    stats = balancer.get_effort_statistics()
    print(f"  Statistics include confidence weighting: {'confidence_weighting' in stats}")
    
    if 'confidence_weighting' in stats:
        cw_stats = stats['confidence_weighting']
        print(f"    Dynamic reordering: {cw_stats.get('dynamic_reordering', False)}")
        print(f"    Confidence threshold: {cw_stats.get('confidence_threshold', 0.0)}")
    
    print("  ✅ Integration with Loss Balancer successful")

def test_skill_categories():
    """Test skill category-based weighting."""
    print("\n🧪 Testing skill category-based weighting...")
    
    weighting = ConfidenceWeighting()
    
    # Test different skill categories
    category_skills = {
        SkillCategory.RETRIEVAL: ["MemoryRetrievalSkill"],
        SkillCategory.ANALYSIS: ["ConflictDetectorSkill"],
        SkillCategory.SYNTHESIS: ["ImplicitKnowledgeSkill"],
        SkillCategory.VALIDATION: ["ContentVettingSkill"],
        SkillCategory.TOOLS: ["CalculatorTool"],
        SkillCategory.GENERATION: ["ResponseGenerationSkill"]
    }
    
    for category, skills in category_skills.items():
        for skill in skills:
            if skill in weighting.skill_weights:
                config = weighting.skill_weights[skill]
                print(f"  {skill}: {category.value} (priority: {config.execution_priority})")
                assert config.category == category
    
    print("  ✅ Skill category-based weighting successful")

def main():
    """Run all confidence weighting tests."""
    print("🚀 PINN-Inspired Confidence-Based Weighting Test Suite")
    print("=" * 60)
    
    try:
        # Test core functionality
        test_confidence_adjustment()
        test_execution_order_optimization()
        test_resource_allocation()
        test_query_complexity_impact()
        test_weight_adaptation()
        test_integration_with_loss_balancer()
        test_skill_categories()
        
        print("\n🎉 All confidence weighting tests passed!")
        print("✅ Phase B Component 3: Confidence-Based Weighting - VALIDATED")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
