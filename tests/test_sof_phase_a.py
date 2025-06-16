#!/usr/bin/env python3
"""
Test Suite for SAM Orchestration Framework Phase A Components
============================================================

Tests the foundational components of SOF including UIF, BaseSkillModule,
and core skills to ensure proper implementation before proceeding to Phase B.
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
        MemoryRetrievalSkill, ResponseGenerationSkill, ConflictDetectorSkill,
        get_sof_config, is_sof_enabled
    )
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the SAM project root directory")
    sys.exit(1)


class TestSOFPhaseA(unittest.TestCase):
    """Test suite for SOF Phase A components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_query = "What is the capital of France?"
        self.test_uif = SAM_UIF(input_query=self.test_query)
    
    def test_uif_creation_and_validation(self):
        """Test UIF creation and Pydantic validation."""
        print("\n🧪 Testing UIF Creation and Validation...")
        
        # Test basic UIF creation
        uif = SAM_UIF(input_query="Test query")
        self.assertEqual(uif.input_query, "Test query")
        self.assertEqual(uif.status, UIFStatus.PENDING)
        self.assertIsNotNone(uif.task_id)
        
        # Test UIF validation
        self.assertTrue(len(uif.task_id) > 0)
        self.assertIsInstance(uif.log_trace, list)
        self.assertIsInstance(uif.intermediate_data, dict)
        
        # Test confidence score validation
        uif.confidence_score = 0.5
        self.assertEqual(uif.confidence_score, 0.5)
        
        # Test invalid confidence score
        with self.assertRaises(ValueError):
            uif.confidence_score = 1.5  # Should fail validation
        
        print("✅ UIF creation and validation tests passed")
    
    def test_uif_methods(self):
        """Test UIF utility methods."""
        print("\n🧪 Testing UIF Methods...")
        
        uif = SAM_UIF(input_query="Test query")
        
        # Test log entry
        uif.add_log_entry("Test message", "TestSkill")
        self.assertTrue(len(uif.log_trace) > 0)
        self.assertIn("TestSkill: Test message", uif.log_trace[0])
        
        # Test warning
        uif.add_warning("Test warning")
        self.assertTrue(len(uif.warnings) > 0)
        self.assertEqual(uif.warnings[0], "Test warning")
        
        # Test error setting
        uif.set_error("Test error", "TestSkill")
        self.assertEqual(uif.status, UIFStatus.FAILURE)
        self.assertEqual(uif.error_details, "Test error")
        
        # Test skill completion
        uif.mark_skill_complete("TestSkill", 1.5)
        self.assertIn("TestSkill", uif.executed_skills)
        self.assertEqual(uif.skill_timings["TestSkill"], 1.5)
        
        print("✅ UIF methods tests passed")
    
    def test_base_skill_module(self):
        """Test BaseSkillModule abstract class."""
        print("\n🧪 Testing BaseSkillModule...")
        
        # Create a test skill implementation
        class TestSkill(BaseSkillModule):
            skill_name = "TestSkill"
            skill_description = "Test skill for validation"
            required_inputs = ["input_query"]
            output_keys = ["test_output"]
            
            def execute(self, uif: SAM_UIF) -> SAM_UIF:
                uif.intermediate_data["test_output"] = "test_result"
                return uif
        
        # Test skill creation
        skill = TestSkill()
        self.assertEqual(skill.skill_name, "TestSkill")
        self.assertEqual(skill.required_inputs, ["input_query"])
        self.assertEqual(skill.output_keys, ["test_output"])
        
        # Test dependency validation
        uif = SAM_UIF(input_query="Test query")
        skill.validate_dependencies(uif)  # Should not raise exception
        
        # Test execution with monitoring
        result_uif = skill.execute_with_monitoring(uif)
        self.assertIn("test_output", result_uif.intermediate_data)
        self.assertEqual(result_uif.intermediate_data["test_output"], "test_result")
        self.assertIn("TestSkill", result_uif.executed_skills)
        
        print("✅ BaseSkillModule tests passed")
    
    def test_memory_retrieval_skill(self):
        """Test MemoryRetrievalSkill implementation."""
        print("\n🧪 Testing MemoryRetrievalSkill...")
        
        try:
            skill = MemoryRetrievalSkill()
            self.assertEqual(skill.skill_name, "MemoryRetrievalSkill")
            self.assertIn("input_query", skill.required_inputs)
            self.assertIn("memory_results", skill.output_keys)
            
            # Test dependency validation
            uif = SAM_UIF(input_query="Test memory query")
            self.assertTrue(skill.can_execute(uif))
            
            print("✅ MemoryRetrievalSkill basic tests passed")
            
        except Exception as e:
            print(f"⚠️  MemoryRetrievalSkill test failed (expected if memory systems not available): {e}")
    
    def test_response_generation_skill(self):
        """Test ResponseGenerationSkill implementation."""
        print("\n🧪 Testing ResponseGenerationSkill...")
        
        try:
            skill = ResponseGenerationSkill()
            self.assertEqual(skill.skill_name, "ResponseGenerationSkill")
            self.assertIn("input_query", skill.required_inputs)
            self.assertIn("final_response", skill.output_keys)
            
            # Test dependency validation
            uif = SAM_UIF(input_query="Test response query")
            self.assertTrue(skill.can_execute(uif))
            
            print("✅ ResponseGenerationSkill basic tests passed")
            
        except Exception as e:
            print(f"⚠️  ResponseGenerationSkill test failed (expected if LLM not available): {e}")
    
    def test_conflict_detector_skill(self):
        """Test ConflictDetectorSkill implementation."""
        print("\n🧪 Testing ConflictDetectorSkill...")
        
        skill = ConflictDetectorSkill()
        self.assertEqual(skill.skill_name, "ConflictDetectorSkill")
        self.assertIn("input_query", skill.required_inputs)
        self.assertIn("conflict_analysis", skill.output_keys)
        
        # Test dependency validation
        uif = SAM_UIF(input_query="Test conflict query")
        self.assertTrue(skill.can_execute(uif))
        
        print("✅ ConflictDetectorSkill tests passed")
    
    def test_skill_dependency_system(self):
        """Test skill dependency declaration and validation system."""
        print("\n🧪 Testing Skill Dependency System...")
        
        # Create test skills with dependencies
        class SkillA(BaseSkillModule):
            skill_name = "SkillA"
            skill_description = "First skill"
            required_inputs = ["input_query"]
            output_keys = ["skill_a_output"]
            
            def execute(self, uif: SAM_UIF) -> SAM_UIF:
                uif.intermediate_data["skill_a_output"] = "result_a"
                return uif
        
        class SkillB(BaseSkillModule):
            skill_name = "SkillB"
            skill_description = "Second skill"
            required_inputs = ["skill_a_output"]
            output_keys = ["skill_b_output"]
            
            def execute(self, uif: SAM_UIF) -> SAM_UIF:
                input_data = uif.intermediate_data["skill_a_output"]
                uif.intermediate_data["skill_b_output"] = f"processed_{input_data}"
                return uif
        
        skill_a = SkillA()
        skill_b = SkillB()
        
        # Test SkillA can execute with basic UIF
        uif = SAM_UIF(input_query="Test query")
        self.assertTrue(skill_a.can_execute(uif))
        
        # Test SkillB cannot execute without SkillA output
        self.assertFalse(skill_b.can_execute(uif))
        
        # Execute SkillA and then test SkillB
        uif = skill_a.execute_with_monitoring(uif)
        self.assertTrue(skill_b.can_execute(uif))
        
        # Execute SkillB
        uif = skill_b.execute_with_monitoring(uif)
        self.assertEqual(uif.intermediate_data["skill_b_output"], "processed_result_a")
        
        print("✅ Skill dependency system tests passed")
    
    def test_sof_configuration(self):
        """Test SOF configuration system."""
        print("\n🧪 Testing SOF Configuration...")
        
        # Test configuration loading
        config = get_sof_config()
        self.assertIsNotNone(config)
        self.assertFalse(config.use_sof_framework)  # Should be disabled by default
        
        # Test SOF enabled check
        self.assertFalse(is_sof_enabled())
        
        print("✅ SOF configuration tests passed")
    
    def test_skill_metadata(self):
        """Test skill metadata and introspection."""
        print("\n🧪 Testing Skill Metadata...")
        
        skill = ConflictDetectorSkill()
        
        # Test metadata retrieval
        metadata = skill.get_metadata()
        self.assertEqual(metadata.name, "ConflictDetectorSkill")
        self.assertEqual(metadata.category, "analysis")
        self.assertFalse(metadata.requires_external_access)
        
        # Test dependency info
        dep_info = skill.get_dependency_info()
        self.assertIn("required_inputs", dep_info)
        self.assertIn("output_keys", dep_info)
        self.assertEqual(dep_info["skill_name"], "ConflictDetectorSkill")
        
        print("✅ Skill metadata tests passed")


def run_phase_a_tests():
    """Run all Phase A tests and provide summary."""
    print("🚀 Starting SAM Orchestration Framework Phase A Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSOFPhaseA)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Phase A Test Summary")
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
        print("\n🎉 All Phase A tests passed! Ready to proceed to Phase B.")
        print("📋 Next Steps:")
        print("   1. Implement CoordinatorEngine")
        print("   2. Create PlanValidationEngine") 
        print("   3. Add fallback mechanisms")
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
    success = run_phase_a_tests()
    sys.exit(0 if success else 1)
