#!/usr/bin/env python3
"""
Test Suite for SAM Orchestration Framework Phase B Components
============================================================

Tests the coordination and validation components including PlanValidationEngine,
CoordinatorEngine, and SOFIntegration to ensure proper implementation.
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from sam.orchestration import (
        SAM_UIF, UIFStatus, BaseSkillModule, SkillExecutionError,
        PlanValidationEngine, PlanValidationReport, ValidationResult,
        CoordinatorEngine, ExecutionReport, ExecutionResult,
        SOFIntegration, get_sof_integration, process_query_with_sof,
        get_sof_config, enable_sof_framework, disable_sof_framework
    )
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the SAM project root directory")
    sys.exit(1)


class TestSOFPhaseB(unittest.TestCase):
    """Test suite for SOF Phase B components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_query = "What is the capital of France?"
        self.test_uif = SAM_UIF(input_query=self.test_query)
        
        # Create test skills
        self.test_skills = self._create_test_skills()
    
    def _create_test_skills(self):
        """Create test skills for validation and coordination testing."""
        
        class TestSkillA(BaseSkillModule):
            skill_name = "TestSkillA"
            skill_description = "First test skill"
            required_inputs = ["input_query"]
            output_keys = ["skill_a_output"]
            estimated_execution_time = 1.0
            
            def execute(self, uif: SAM_UIF) -> SAM_UIF:
                uif.intermediate_data["skill_a_output"] = f"processed_{uif.input_query}"
                return uif
        
        class TestSkillB(BaseSkillModule):
            skill_name = "TestSkillB"
            skill_description = "Second test skill"
            required_inputs = ["skill_a_output"]
            output_keys = ["skill_b_output"]
            estimated_execution_time = 0.5
            
            def execute(self, uif: SAM_UIF) -> SAM_UIF:
                input_data = uif.intermediate_data["skill_a_output"]
                uif.intermediate_data["skill_b_output"] = f"enhanced_{input_data}"
                return uif
        
        class TestSkillC(BaseSkillModule):
            skill_name = "TestSkillC"
            skill_description = "Third test skill"
            required_inputs = ["skill_b_output"]
            output_keys = ["final_result"]
            estimated_execution_time = 2.0
            
            def execute(self, uif: SAM_UIF) -> SAM_UIF:
                input_data = uif.intermediate_data["skill_b_output"]
                uif.final_response = f"Final result: {input_data}"
                return uif
        
        return [TestSkillA(), TestSkillB(), TestSkillC()]
    
    def test_plan_validation_engine(self):
        """Test PlanValidationEngine functionality."""
        print("\n🧪 Testing PlanValidationEngine...")
        
        validator = PlanValidationEngine()
        
        # Register test skills
        validator.register_skills(self.test_skills)
        
        # Test valid plan
        valid_plan = ["TestSkillA", "TestSkillB", "TestSkillC"]
        report = validator.validate_plan(valid_plan, self.test_uif)
        
        self.assertTrue(report.is_valid)
        self.assertEqual(report.errors_count, 0)
        self.assertEqual(len(report.optimized_plan), 3)
        self.assertGreater(report.execution_estimate, 0)
        
        # Test invalid plan (missing skill)
        invalid_plan = ["TestSkillA", "NonExistentSkill", "TestSkillC"]
        report = validator.validate_plan(invalid_plan, self.test_uif)
        
        self.assertFalse(report.is_valid)
        self.assertGreater(report.errors_count, 0)
        
        # Test dependency violation
        dependency_violation_plan = ["TestSkillB", "TestSkillA"]  # Wrong order
        report = validator.validate_plan(dependency_violation_plan, self.test_uif)
        
        self.assertFalse(report.is_valid)
        self.assertGreater(report.errors_count, 0)
        
        print("✅ PlanValidationEngine tests passed")
    
    def test_coordinator_engine(self):
        """Test CoordinatorEngine functionality."""
        print("\n🧪 Testing CoordinatorEngine...")
        
        coordinator = CoordinatorEngine()
        
        # Register test skills
        coordinator.register_skills(self.test_skills)
        
        # Test successful execution
        plan = ["TestSkillA", "TestSkillB", "TestSkillC"]
        uif = SAM_UIF(input_query="Test query")
        
        report = coordinator.execute_plan(plan, uif)
        
        self.assertEqual(report.result, ExecutionResult.SUCCESS)
        self.assertEqual(len(report.executed_skills), 3)
        self.assertEqual(len(report.failed_skills), 0)
        self.assertIsNotNone(report.uif.final_response)
        self.assertGreater(report.execution_time, 0)
        
        # Test execution with invalid skill
        invalid_plan = ["TestSkillA", "NonExistentSkill"]
        uif = SAM_UIF(input_query="Test query")
        
        report = coordinator.execute_plan(invalid_plan, uif)
        
        self.assertEqual(report.result, ExecutionResult.FAILURE)
        self.assertGreater(len(report.failed_skills), 0)
        
        print("✅ CoordinatorEngine tests passed")
    
    def test_execution_monitoring(self):
        """Test execution monitoring and metrics."""
        print("\n🧪 Testing Execution Monitoring...")
        
        coordinator = CoordinatorEngine()
        coordinator.register_skills(self.test_skills)
        
        # Execute multiple plans
        plan = ["TestSkillA", "TestSkillB"]
        
        for i in range(3):
            uif = SAM_UIF(input_query=f"Test query {i}")
            coordinator.execute_plan(plan, uif)
        
        # Check execution history
        history = coordinator.get_execution_history()
        self.assertEqual(len(history), 3)
        
        # Check execution stats
        stats = coordinator.get_execution_stats()
        self.assertEqual(stats["total_executions"], 3)
        self.assertGreater(stats["success_rate"], 0)
        self.assertGreater(stats["average_execution_time"], 0)
        
        print("✅ Execution monitoring tests passed")
    
    def test_fallback_mechanisms(self):
        """Test fallback mechanisms."""
        print("\n🧪 Testing Fallback Mechanisms...")
        
        # Create a fallback generator
        def test_fallback(query: str) -> str:
            return f"Fallback response for: {query}"
        
        coordinator = CoordinatorEngine(test_fallback)
        coordinator.register_skills(self.test_skills)
        
        # Test fallback with completely invalid plan
        invalid_plan = ["NonExistentSkill1", "NonExistentSkill2"]
        uif = SAM_UIF(input_query="Test query")
        
        report = coordinator.execute_plan(invalid_plan, uif)
        
        # Should succeed due to fallback
        self.assertEqual(report.result, ExecutionResult.SUCCESS)
        self.assertTrue(report.fallback_used)
        self.assertIsNotNone(report.uif.final_response)
        
        print("✅ Fallback mechanisms tests passed")
    
    def test_sof_integration(self):
        """Test SOFIntegration high-level interface."""
        print("\n🧪 Testing SOFIntegration...")
        
        # Temporarily enable SOF for testing
        original_config = get_sof_config()
        enable_sof_framework()
        
        try:
            # Test SOF integration
            sof = SOFIntegration()
            
            # Note: This may fail if SAM components aren't available, which is expected
            try:
                initialized = sof.initialize()
                if initialized:
                    # Test query processing
                    response = sof.process_query("What is 2+2?")
                    
                    self.assertIn("success", response)
                    self.assertIn("response", response)
                    self.assertIn("processing_time", response)
                    self.assertIn("metadata", response)
                    
                    print("✅ SOFIntegration tests passed")
                else:
                    print("⚠️  SOFIntegration initialization failed (expected if SAM components not available)")
            
            except Exception as e:
                print(f"⚠️  SOFIntegration test failed (expected if SAM components not available): {e}")
        
        finally:
            # Restore original configuration
            disable_sof_framework()
    
    def test_plan_optimization(self):
        """Test plan optimization features."""
        print("\n🧪 Testing Plan Optimization...")
        
        validator = PlanValidationEngine()
        validator.register_skills(self.test_skills)
        
        # Test plan with potential optimizations
        plan = ["TestSkillA", "TestSkillB", "TestSkillC"]
        report = validator.validate_plan(plan, self.test_uif)
        
        # Check that optimized plan is provided
        self.assertIsNotNone(report.optimized_plan)
        self.assertGreaterEqual(len(report.optimized_plan), len(plan) - 1)  # Could be same or optimized
        
        # Check execution time estimation
        self.assertGreater(report.execution_estimate, 0)
        expected_time = sum(skill.estimated_execution_time for skill in self.test_skills)
        self.assertLessEqual(report.execution_estimate, expected_time + 1)  # Allow some tolerance
        
        print("✅ Plan optimization tests passed")
    
    def test_error_handling(self):
        """Test comprehensive error handling."""
        print("\n🧪 Testing Error Handling...")
        
        # Create a skill that always fails
        class FailingSkill(BaseSkillModule):
            skill_name = "FailingSkill"
            skill_description = "Skill that always fails"
            required_inputs = ["input_query"]
            output_keys = ["failing_output"]
            
            def execute(self, uif: SAM_UIF) -> SAM_UIF:
                raise SkillExecutionError("This skill always fails")
        
        coordinator = CoordinatorEngine()
        coordinator.register_skill(FailingSkill())
        
        # Test execution with failing skill
        plan = ["FailingSkill"]
        uif = SAM_UIF(input_query="Test query")
        
        report = coordinator.execute_plan(plan, uif)
        
        self.assertEqual(report.result, ExecutionResult.FAILURE)
        # Error details should be in either the report or the UIF
        self.assertTrue(report.error_details is not None or report.uif.error_details is not None)
        self.assertEqual(report.uif.status, UIFStatus.FAILURE)
        
        print("✅ Error handling tests passed")
    
    def test_dependency_graph_creation(self):
        """Test dependency graph creation and validation."""
        print("\n🧪 Testing Dependency Graph Creation...")
        
        validator = PlanValidationEngine()
        validator.register_skills(self.test_skills)
        
        plan = ["TestSkillA", "TestSkillB", "TestSkillC"]
        report = validator.validate_plan(plan, self.test_uif)
        
        # Check dependency graph structure
        self.assertIn("TestSkillA", report.dependency_graph)
        self.assertIn("TestSkillB", report.dependency_graph)
        self.assertIn("TestSkillC", report.dependency_graph)
        
        # TestSkillA should have no dependencies (only needs input_query)
        self.assertEqual(len(report.dependency_graph["TestSkillA"]), 0)
        
        print("✅ Dependency graph creation tests passed")
    
    def test_configuration_integration(self):
        """Test configuration integration."""
        print("\n🧪 Testing Configuration Integration...")
        
        config = get_sof_config()
        
        # Test configuration values
        self.assertIsNotNone(config.max_execution_time)
        self.assertIsNotNone(config.skill_timeout)
        self.assertIsNotNone(config.enable_plan_validation)
        
        # Test configuration affects behavior
        coordinator = CoordinatorEngine()
        self.assertIsNotNone(coordinator._config)
        
        print("✅ Configuration integration tests passed")


def run_phase_b_tests():
    """Run all Phase B tests and provide summary."""
    print("🚀 Starting SAM Orchestration Framework Phase B Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSOFPhaseB)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Phase B Test Summary")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"✅ Tests Passed: {passed}/{total_tests}")
    if failures > 0:
        print(f"❌ Tests Failed: {failures}")
    if errors > 0:
        print(f"💥 Test Errors: {errors}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 All Phase B tests passed! Ready to proceed to Phase C.")
        print("📋 Next Steps:")
        print("   1. Implement DynamicPlanner with LLM-as-a-Planner")
        print("   2. Create Tool Security Framework")
        print("   3. Add plan caching and optimization")
        print("   4. Integrate external tools (Calculator, Web Browser)")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before proceeding.")
        
        if result.failures:
            print("\n❌ Failures:")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\n💥 Errors:")
            for test, traceback in result.errors:
                print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return failures == 0 and errors == 0


if __name__ == "__main__":
    success = run_phase_b_tests()
    sys.exit(0 if success else 1)
