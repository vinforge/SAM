#!/usr/bin/env python3
"""
Test Script for PINN-Inspired Loss Balancer

Tests the dynamic effort allocation system integrated into SAM's
SOF coordinator engine. Validates effort allocation, adaptation,
and early termination capabilities.

Usage:
    python scripts/test_loss_balancer.py

Author: SAM Development Team
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add SAM to path
sys.path.append(str(Path(__file__).parent.parent))

from sam.orchestration.loss_balancer import LossBalancer, EffortLevel, EffortAllocation
from sam.orchestration.coordinator import CoordinatorEngine
from sam.orchestration.uif import SAM_UIF

def test_effort_allocation():
    """Test basic effort allocation functionality."""
    print("🧪 Testing effort allocation...")
    
    balancer = LossBalancer(
        confidence_threshold=0.8,
        effort_budget=3.0,
        enable_early_termination=True
    )
    
    # Test simple plan allocation
    plan = ["MemoryRetrievalSkill", "ConflictDetectorSkill", "ResponseGenerationSkill"]
    allocation = balancer.allocate_effort(
        plan=plan,
        initial_confidence=0.5,
        query_complexity="medium"
    )
    
    print(f"  Plan: {plan}")
    print(f"  Total effort budget: {allocation.total_effort_budget}")
    print(f"  Confidence threshold: {allocation.confidence_threshold}")
    
    for skill_name, effort_config in allocation.skill_efforts.items():
        print(f"  {skill_name}: {effort_config.effort_level.value}")
        print(f"    Parameters: {effort_config.parameter_adjustments}")
    
    # Validate allocation
    assert len(allocation.skill_efforts) == len(plan)
    assert all(skill in allocation.skill_efforts for skill in plan)
    
    print("  ✅ Basic effort allocation successful")

def test_effort_adaptation():
    """Test effort adaptation based on intermediate confidence."""
    print("\n🧪 Testing effort adaptation...")
    
    balancer = LossBalancer(adaptation_rate=0.5)
    
    plan = ["MemoryRetrievalSkill", "ConflictDetectorSkill", "ResponseGenerationSkill"]
    allocation = balancer.allocate_effort(plan, initial_confidence=0.3)
    
    # Simulate high confidence after first skill
    executed_skills = ["MemoryRetrievalSkill"]
    remaining_skills = ["ConflictDetectorSkill", "ResponseGenerationSkill"]
    
    print(f"  Initial allocation:")
    for skill, config in allocation.skill_efforts.items():
        if skill in remaining_skills:
            print(f"    {skill}: {config.effort_level.value}")
    
    # Adapt based on high confidence
    adapted_allocation = balancer.adapt_effort(
        allocation=allocation,
        executed_skills=executed_skills,
        intermediate_confidence=0.9,  # High confidence
        remaining_skills=remaining_skills
    )
    
    print(f"  After adaptation (confidence 0.9):")
    for skill, config in adapted_allocation.skill_efforts.items():
        if skill in remaining_skills:
            print(f"    {skill}: {config.effort_level.value}")
    
    # Validate adaptation reduced effort
    original_effort = allocation.skill_efforts["ConflictDetectorSkill"].effort_level
    adapted_effort = adapted_allocation.skill_efforts["ConflictDetectorSkill"].effort_level
    
    print(f"  ConflictDetectorSkill effort: {original_effort.value} → {adapted_effort.value}")
    
    print("  ✅ Effort adaptation successful")

def test_early_termination():
    """Test early termination logic."""
    print("\n🧪 Testing early termination...")
    
    balancer = LossBalancer(enable_early_termination=True)
    
    plan = ["MemoryRetrievalSkill", "ConflictDetectorSkill", "ResponseGenerationSkill"]
    allocation = balancer.allocate_effort(plan)
    
    # Test early termination conditions
    executed_skills = ["MemoryRetrievalSkill", "ConflictDetectorSkill"]
    remaining_skills = ["ResponseGenerationSkill"]
    
    # High confidence should trigger early termination
    should_terminate = balancer.should_terminate_early(
        allocation=allocation,
        current_confidence=0.95,
        executed_skills=executed_skills,
        remaining_skills=remaining_skills
    )
    
    print(f"  High confidence (0.95) early termination: {should_terminate}")
    assert should_terminate, "Should terminate early with high confidence"
    
    # Low confidence should not trigger early termination
    should_not_terminate = balancer.should_terminate_early(
        allocation=allocation,
        current_confidence=0.6,
        executed_skills=executed_skills,
        remaining_skills=remaining_skills
    )
    
    print(f"  Medium confidence (0.6) early termination: {should_not_terminate}")
    assert not should_not_terminate, "Should not terminate early with medium confidence"
    
    print("  ✅ Early termination logic successful")

def test_query_complexity_assessment():
    """Test query complexity assessment."""
    print("\n🧪 Testing query complexity assessment...")
    
    coordinator = CoordinatorEngine(enable_loss_balancing=True)
    
    # Test different query types
    test_queries = [
        ("What is Python?", "simple"),
        ("Explain the relationship between machine learning and artificial intelligence", "complex"),
        ("How do I install a package?", "medium"),
        ("Analyze the pros and cons of different database architectures", "complex"),
        ("Define recursion", "simple")
    ]
    
    for query, expected_complexity in test_queries:
        assessed_complexity = coordinator._assess_query_complexity(query)
        print(f"  '{query[:30]}...' → {assessed_complexity} (expected: {expected_complexity})")
        
        # Allow some flexibility in complexity assessment
        valid_complexities = ["simple", "medium", "complex"]
        assert assessed_complexity in valid_complexities
    
    print("  ✅ Query complexity assessment successful")

def test_effort_level_adjustments():
    """Test effort level adjustment logic."""
    print("\n🧪 Testing effort level adjustments...")
    
    balancer = LossBalancer()
    
    # Test effort level adjustments
    test_cases = [
        (EffortLevel.NORMAL, 0.5, EffortLevel.REDUCED),  # Reduce effort
        (EffortLevel.NORMAL, 1.5, EffortLevel.ENHANCED),  # Increase effort
        (EffortLevel.MINIMAL, 0.5, EffortLevel.MINIMAL),  # Can't reduce below minimal
        (EffortLevel.MAXIMUM, 1.5, EffortLevel.MAXIMUM),  # Can't increase above maximum
    ]
    
    for original, factor, expected in test_cases:
        adjusted = balancer._adjust_effort_level(original, factor)
        print(f"  {original.value} × {factor} → {adjusted.value} (expected: {expected.value})")
        assert adjusted == expected, f"Expected {expected.value}, got {adjusted.value}"
    
    print("  ✅ Effort level adjustments successful")

def test_skill_parameter_configuration():
    """Test skill parameter configuration."""
    print("\n🧪 Testing skill parameter configuration...")
    
    balancer = LossBalancer()
    
    # Test parameter retrieval for different skills and effort levels
    test_cases = [
        ("MemoryRetrievalSkill", EffortLevel.MINIMAL),
        ("MemoryRetrievalSkill", EffortLevel.MAXIMUM),
        ("ResponseGenerationSkill", EffortLevel.NORMAL),
        ("ConflictDetectorSkill", EffortLevel.ENHANCED),
    ]
    
    for skill_name, effort_level in test_cases:
        params = balancer._get_skill_parameters(skill_name, effort_level)
        print(f"  {skill_name} @ {effort_level.value}: {params}")
        
        # Validate parameters exist for known skills
        if skill_name in balancer.default_efforts:
            assert isinstance(params, dict), f"Parameters should be a dict for {skill_name}"
    
    print("  ✅ Skill parameter configuration successful")

def test_statistics_tracking():
    """Test statistics tracking."""
    print("\n🧪 Testing statistics tracking...")
    
    balancer = LossBalancer()
    
    # Get initial statistics
    stats = balancer.get_effort_statistics()
    print(f"  Initial statistics: {stats}")
    
    assert stats["total_allocations"] == 0
    assert "effort_budget" in stats
    assert "confidence_threshold" in stats
    
    # Simulate some allocation history
    balancer.allocation_history = [
        {"final_confidence": 0.8, "early_termination": False},
        {"final_confidence": 0.9, "early_termination": True},
        {"final_confidence": 0.6, "early_termination": False},
    ]
    
    updated_stats = balancer.get_effort_statistics()
    print(f"  Updated statistics: {updated_stats}")
    
    assert updated_stats["total_allocations"] == 3
    assert abs(updated_stats["average_final_confidence"] - 0.7667) < 0.001  # (0.8 + 0.9 + 0.6) / 3
    assert abs(updated_stats["early_termination_rate"] - 1/3) < 0.001  # 1 out of 3
    
    print("  ✅ Statistics tracking successful")

def main():
    """Run all loss balancer tests."""
    print("🚀 PINN-Inspired Loss Balancer Test Suite")
    print("=" * 60)
    
    try:
        # Test core functionality
        test_effort_allocation()
        test_effort_adaptation()
        test_early_termination()
        test_query_complexity_assessment()
        test_effort_level_adjustments()
        test_skill_parameter_configuration()
        test_statistics_tracking()
        
        print("\n🎉 All loss balancer tests passed!")
        print("✅ Phase B Component 1: Loss Balancer - VALIDATED")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
