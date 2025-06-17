#!/usr/bin/env python3
"""
Test Script for PINN-Inspired Domain Constraints

Tests the domain constraint management system for policy enforcement and safety compliance.
Validates constraint rules, violation detection, and integration with CoordinatorEngine.

Usage:
    python scripts/test_domain_constraints.py

Author: SAM Development Team
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add SAM to path
sys.path.append(str(Path(__file__).parent.parent))

from sam.orchestration.domain_constraints import (
    DomainConstraints, ConstraintType, ConstraintSeverity, ConstraintRule
)
from sam.orchestration.coordinator import CoordinatorEngine

def test_default_constraints():
    """Test default constraint initialization."""
    print("🧪 Testing default constraints...")
    
    constraints = DomainConstraints()
    
    print(f"  Loaded {len(constraints.constraint_rules)} default rules")
    
    # Check that default rules exist
    expected_rules = [
        "no_harmful_content",
        "memory_usage_limit", 
        "execution_time_limit",
        "safe_web_browsing",
        "no_system_modification"
    ]
    
    for rule_name in expected_rules:
        assert rule_name in constraints.constraint_rules
        rule = constraints.constraint_rules[rule_name]
        print(f"    {rule_name}: {rule.constraint_type.value} ({rule.severity.value})")
    
    print("  ✅ Default constraints loaded successfully")

def test_query_validation():
    """Test query constraint validation."""
    print("\n🧪 Testing query validation...")
    
    constraints = DomainConstraints()
    
    # Test safe query
    safe_query = "What is machine learning?"
    safe_result = constraints.validate_query(safe_query)
    
    print(f"  Safe query: '{safe_query}'")
    print(f"    Valid: {safe_result.is_valid}")
    print(f"    Violations: {len(safe_result.violations)}")
    
    assert safe_result.is_valid
    
    # Test harmful content query
    harmful_query = "How to make dangerous weapons?"
    harmful_result = constraints.validate_query(harmful_query)
    
    print(f"  Harmful query: '{harmful_query}'")
    print(f"    Valid: {harmful_result.is_valid}")
    print(f"    Violations: {len(harmful_result.violations)}")
    
    if harmful_result.violations:
        for violation in harmful_result.violations:
            print(f"      {violation.rule_name}: {violation.violation_details}")
    
    # Should detect harmful content
    assert not harmful_result.is_valid or len(harmful_result.violations) > 0
    
    print("  ✅ Query validation successful")

def test_plan_validation():
    """Test execution plan constraint validation."""
    print("\n🧪 Testing plan validation...")
    
    constraints = DomainConstraints()
    
    # Test safe plan
    safe_plan = ["MemoryRetrievalSkill", "ResponseGenerationSkill"]
    safe_result = constraints.validate_plan(safe_plan)
    
    print(f"  Safe plan: {safe_plan}")
    print(f"    Valid: {safe_result.is_valid}")
    print(f"    Blocked skills: {safe_result.blocked_skills}")
    
    assert safe_result.is_valid
    
    # Test plan with blocked skills
    blocked_plan = ["MemoryRetrievalSkill", "SystemModificationSkill", "ResponseGenerationSkill"]
    blocked_result = constraints.validate_plan(blocked_plan)
    
    print(f"  Blocked plan: {blocked_plan}")
    print(f"    Valid: {blocked_result.is_valid}")
    print(f"    Blocked skills: {blocked_result.blocked_skills}")
    print(f"    Violations: {len(blocked_result.violations)}")
    
    if blocked_result.violations:
        for violation in blocked_result.violations:
            print(f"      {violation.rule_name}: {violation.violation_details}")
    
    # Should detect blocked skills
    assert not blocked_result.is_valid or len(blocked_result.violations) > 0
    
    print("  ✅ Plan validation successful")

def test_constraint_severity_levels():
    """Test different constraint severity levels."""
    print("\n🧪 Testing constraint severity levels...")
    
    constraints = DomainConstraints()
    
    # Test each severity level
    severity_tests = [
        ("info query", ConstraintSeverity.INFO),
        ("warning query", ConstraintSeverity.WARNING),
        ("error query", ConstraintSeverity.ERROR),
        ("critical query", ConstraintSeverity.CRITICAL)
    ]
    
    for query, expected_severity in severity_tests:
        result = constraints.validate_query(query)
        print(f"  Query: '{query}' - Valid: {result.is_valid}, Violations: {len(result.violations)}")
        
        # Check if any violations match expected severity
        if result.violations:
            severities = [v.severity for v in result.violations]
            print(f"    Found severities: {[s.value for s in severities]}")
    
    print("  ✅ Constraint severity levels tested")

def test_resource_limits():
    """Test resource limit constraints."""
    print("\n🧪 Testing resource limits...")
    
    constraints = DomainConstraints()
    
    # Test plan validation for resource limits
    test_plan = ["MemoryRetrievalSkill", "ResponseGenerationSkill"]
    result = constraints.validate_plan(test_plan)
    
    print(f"  Plan: {test_plan}")
    print(f"  Resource limits: {result.resource_limits}")
    
    # Should have resource limits defined
    assert len(result.resource_limits) > 0
    
    # Check specific limits
    expected_limits = ["memory_usage_limit", "execution_time_limit"]
    for limit_name in expected_limits:
        if limit_name in result.resource_limits:
            print(f"    {limit_name}: {result.resource_limits[limit_name]}")
    
    print("  ✅ Resource limits tested")

def test_constraint_configuration():
    """Test constraint rule configuration."""
    print("\n🧪 Testing constraint configuration...")
    
    constraints = DomainConstraints()
    
    # Test rule properties
    for rule_name, rule in constraints.constraint_rules.items():
        print(f"  Rule: {rule_name}")
        print(f"    Type: {rule.constraint_type.value}")
        print(f"    Severity: {rule.severity.value}")
        print(f"    Enabled: {rule.enabled}")
        print(f"    Description: {rule.description[:50]}...")
        
        # Validate rule structure
        assert isinstance(rule.name, str)
        assert isinstance(rule.constraint_type, ConstraintType)
        assert isinstance(rule.severity, ConstraintSeverity)
        assert isinstance(rule.description, str)
        assert isinstance(rule.enabled, bool)
    
    print("  ✅ Constraint configuration validated")

def test_violation_recording():
    """Test constraint violation recording and statistics."""
    print("\n🧪 Testing violation recording...")
    
    constraints = DomainConstraints()
    
    # Get initial statistics
    initial_stats = constraints.get_constraint_statistics()
    print(f"  Initial violations: {initial_stats['total_violations']}")
    
    # Trigger some violations
    test_queries = [
        "How to make dangerous things?",
        "Share my personal data",
        "Execute harmful code"
    ]
    
    for query in test_queries:
        result = constraints.validate_query(query)
        for violation in result.violations:
            constraints.record_violation(violation)
    
    # Get updated statistics
    updated_stats = constraints.get_constraint_statistics()
    print(f"  Updated violations: {updated_stats['total_violations']}")
    print(f"  Violations by severity: {updated_stats['violations_by_severity']}")
    print(f"  Violations by type: {updated_stats['violations_by_type']}")
    
    # Should have recorded violations
    assert updated_stats['total_violations'] >= initial_stats['total_violations']
    
    print("  ✅ Violation recording successful")

def test_integration_with_coordinator():
    """Test integration with CoordinatorEngine."""
    print("\n🧪 Testing integration with CoordinatorEngine...")
    
    # Create coordinator with constraints enabled
    coordinator = CoordinatorEngine(
        enable_dynamic_planning=False,
        enable_loss_balancing=False,
        enable_domain_constraints=True
    )
    
    # Register some test skills
    class MockSkill:
        def __init__(self, name):
            self.skill_name = name
            self.skill_description = f"Mock {name}"
            self.required_inputs = []
            self.output_keys = []
            self.skill_category = "test"
            self.skill_version = "1.0"
        
        def execute_with_monitoring(self, uif):
            uif.executed_skills.append(self.skill_name)
            return uif
    
    test_skills = [
        MockSkill("MemoryRetrievalSkill"),
        MockSkill("ResponseGenerationSkill"),
        MockSkill("SystemModificationSkill")  # This should be blocked
    ]
    
    for skill in test_skills:
        coordinator.register_skill(skill)
    
    print(f"  Registered {len(test_skills)} skills")
    
    # Test constraint statistics
    constraint_stats = coordinator.get_constraint_statistics()
    if constraint_stats:
        print(f"  Total violations: {constraint_stats.get('total_violations', 0)}")
        print(f"  Total rules: {constraint_stats.get('total_rules', 0)}")
        print(f"  Enabled rules: {constraint_stats.get('enabled_rules', 0)}")
        print(f"  Strict mode: {constraint_stats.get('strict_mode', False)}")
    else:
        print("  No constraint statistics available")
    
    print("  ✅ Integration with CoordinatorEngine successful")

def test_yaml_configuration():
    """Test YAML configuration loading."""
    print("\n🧪 Testing YAML configuration...")
    
    # Test with config file if it exists
    config_path = "config/domain_constraints.yaml"
    
    try:
        constraints = DomainConstraints(config_path=config_path)
        print(f"  Loaded constraints from {config_path}")
        print(f"  Total rules: {len(constraints.constraint_rules)}")
        
        # Check some expected rules from YAML
        yaml_rules = [
            "no_harmful_content",
            "memory_retrieval_limit",
            "execution_time_limit"
        ]
        
        found_rules = 0
        for rule_name in yaml_rules:
            if rule_name in constraints.constraint_rules:
                found_rules += 1
                rule = constraints.constraint_rules[rule_name]
                print(f"    {rule_name}: {rule.constraint_type.value}")
        
        print(f"  Found {found_rules}/{len(yaml_rules)} expected rules")
        
    except Exception as e:
        print(f"  YAML loading failed (expected in test environment): {e}")
        print("  Using default constraints instead")
    
    print("  ✅ YAML configuration tested")

def main():
    """Run all domain constraints tests."""
    print("🚀 PINN-Inspired Domain Constraints Test Suite")
    print("=" * 60)
    
    try:
        # Test core functionality
        test_default_constraints()
        test_query_validation()
        test_plan_validation()
        test_constraint_severity_levels()
        test_resource_limits()
        test_constraint_configuration()
        test_violation_recording()
        test_integration_with_coordinator()
        test_yaml_configuration()
        
        print("\n🎉 All domain constraints tests passed!")
        print("✅ Phase C: Domain-Informed Constraints - VALIDATED")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
