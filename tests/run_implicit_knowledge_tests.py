#!/usr/bin/env python3
"""
Test Runner for Implicit Knowledge Engine
=========================================

Comprehensive test runner for all Implicit Knowledge Engine components,
including unit tests, integration tests, and end-to-end tests.
"""

import unittest
import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_unit_tests():
    """Run unit tests for ImplicitKnowledgeSkill."""
    logger.info("🧪 Running unit tests for ImplicitKnowledgeSkill...")

    try:
        from test_implicit_knowledge_skill import TestImplicitKnowledgeSkill, TestImplicitKnowledgeResult

        # Create test suite
        suite = unittest.TestSuite()

        # Add unit tests
        suite.addTest(unittest.makeSuite(TestImplicitKnowledgeSkill))
        suite.addTest(unittest.makeSuite(TestImplicitKnowledgeResult))

        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()

    except ImportError as e:
        logger.error(f"❌ Failed to import unit test modules: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error running unit tests: {e}")
        return False


def run_integration_tests():
    """Run integration tests for Implicit Knowledge Engine."""
    logger.info("🔗 Running integration tests for Implicit Knowledge Engine...")

    try:
        from test_implicit_knowledge_integration import TestImplicitKnowledgeIntegration, TestSOFIntegration

        # Create test suite
        suite = unittest.TestSuite()

        # Add integration tests
        suite.addTest(unittest.makeSuite(TestImplicitKnowledgeIntegration))
        suite.addTest(unittest.makeSuite(TestSOFIntegration))

        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()

    except ImportError as e:
        logger.error(f"❌ Failed to import integration test modules: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error running integration tests: {e}")
        return False


def run_e2e_tests():
    """Run end-to-end tests for Dream Canvas functionality."""
    logger.info("🎨 Running end-to-end tests for Dream Canvas...")

    try:
        from test_dream_canvas_e2e import TestDreamCanvasImplicitKnowledge, TestDreamCanvasIntegrationScenarios

        # Create test suite
        suite = unittest.TestSuite()

        # Add e2e tests
        suite.addTest(unittest.makeSuite(TestDreamCanvasImplicitKnowledge))
        suite.addTest(unittest.makeSuite(TestDreamCanvasIntegrationScenarios))

        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()

    except ImportError as e:
        logger.error(f"❌ Failed to import e2e test modules: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error running e2e tests: {e}")
        return False


def run_smoke_tests():
    """Run smoke tests to verify basic functionality."""
    logger.info("💨 Running smoke tests...")

    try:
        # Test 1: Import ImplicitKnowledgeSkill
        logger.info("  Testing ImplicitKnowledgeSkill import...")
        from sam.orchestration.skills.reasoning.implicit_knowledge import ImplicitKnowledgeSkill
        skill = ImplicitKnowledgeSkill()
        assert skill.skill_name == "ImplicitKnowledgeSkill"
        logger.info("  ✅ ImplicitKnowledgeSkill import successful")

        # Test 2: Test skill registration
        logger.info("  Testing skill registration...")
        from sam.orchestration import ImplicitKnowledgeSkill as SOFSkill
        sof_skill = SOFSkill()
        assert sof_skill.skill_name == "ImplicitKnowledgeSkill"
        logger.info("  ✅ Skill registration successful")

        # Test 3: Test UIF integration
        logger.info("  Testing UIF integration...")
        from sam.orchestration.uif import SAM_UIF
        uif = SAM_UIF(input_query="Test query")
        uif.intermediate_data["explicit_knowledge_chunks"] = ["chunk1", "chunk2"]
        assert skill._validate_inputs(uif) == True
        logger.info("  ✅ UIF integration successful")

        return True

    except Exception as e:
        logger.error(f"❌ Smoke test failed: {e}")
        return False


def generate_test_report(results):
    """Generate a comprehensive test report."""
    logger.info("📊 Generating test report...")

    report = []
    report.append("=" * 60)
    report.append("IMPLICIT KNOWLEDGE ENGINE TEST REPORT")
    report.append("=" * 60)
    report.append("")

    # Test results summary
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests

    report.append(f"Total Test Suites: {total_tests}")
    report.append(f"Passed: {passed_tests}")
    report.append(f"Failed: {failed_tests}")
    report.append(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    report.append("")

    # Detailed results
    report.append("DETAILED RESULTS:")
    report.append("-" * 20)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        report.append(f"{test_name}: {status}")

    report.append("")
    report.append("=" * 60)

    # Print report
    for line in report:
        print(line)


def main():
    """Main test runner function."""
    logger.info("🚀 Starting Implicit Knowledge Engine Test Suite")

    # Run all test suites
    results = {}

    # Smoke tests first
    results["Smoke Tests"] = run_smoke_tests()

    # Unit tests
    results["Unit Tests"] = run_unit_tests()

    # Integration tests
    results["Integration Tests"] = run_integration_tests()

    # End-to-end tests
    results["End-to-End Tests"] = run_e2e_tests()

    # Generate report
    generate_test_report(results)

    # Overall result
    all_passed = all(results.values())

    if all_passed:
        logger.info("🎉 All tests passed! Implicit Knowledge Engine is ready for deployment.")
        return 0
    else:
        logger.error("💥 Some tests failed. Please review the test report.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


def run_unit_tests():
    """Run unit tests for ImplicitKnowledgeSkill."""
    logger.info("🧪 Running unit tests for ImplicitKnowledgeSkill...")
    
    try:
        from test_implicit_knowledge_skill import TestImplicitKnowledgeSkill, TestImplicitKnowledgeResult
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add unit tests
        suite.addTest(unittest.makeSuite(TestImplicitKnowledgeSkill))
        suite.addTest(unittest.makeSuite(TestImplicitKnowledgeResult))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except ImportError as e:
        logger.error(f"❌ Failed to import unit test modules: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error running unit tests: {e}")
        return False


def run_integration_tests():
    """Run integration tests for Implicit Knowledge Engine."""
    logger.info("🔗 Running integration tests for Implicit Knowledge Engine...")
    
    try:
        from test_implicit_knowledge_integration import TestImplicitKnowledgeIntegration, TestSOFIntegration
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add integration tests
        suite.addTest(unittest.makeSuite(TestImplicitKnowledgeIntegration))
        suite.addTest(unittest.makeSuite(TestSOFIntegration))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except ImportError as e:
        logger.error(f"❌ Failed to import integration test modules: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error running integration tests: {e}")
        return False


def run_e2e_tests():
    """Run end-to-end tests for Dream Canvas functionality."""
    logger.info("🎨 Running end-to-end tests for Dream Canvas...")
    
    try:
        from test_dream_canvas_e2e import TestDreamCanvasImplicitKnowledge, TestDreamCanvasIntegrationScenarios
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add e2e tests
        suite.addTest(unittest.makeSuite(TestDreamCanvasImplicitKnowledge))
        suite.addTest(unittest.makeSuite(TestDreamCanvasIntegrationScenarios))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except ImportError as e:
        logger.error(f"❌ Failed to import e2e test modules: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error running e2e tests: {e}")
        return False


def run_smoke_tests():
    """Run smoke tests to verify basic functionality."""
    logger.info("💨 Running smoke tests...")
    
    try:
        # Test 1: Import ImplicitKnowledgeSkill
        logger.info("  Testing ImplicitKnowledgeSkill import...")
        from sam.orchestration.skills.reasoning.implicit_knowledge import ImplicitKnowledgeSkill
        skill = ImplicitKnowledgeSkill()
        assert skill.skill_name == "ImplicitKnowledgeSkill"
        logger.info("  ✅ ImplicitKnowledgeSkill import successful")
        
        # Test 2: Test skill registration
        logger.info("  Testing skill registration...")
        from sam.orchestration import ImplicitKnowledgeSkill as SOFSkill
        sof_skill = SOFSkill()
        assert sof_skill.skill_name == "ImplicitKnowledgeSkill"
        logger.info("  ✅ Skill registration successful")
        
        # Test 3: Test UIF integration
        logger.info("  Testing UIF integration...")
        from sam.orchestration.uif import SAM_UIF
        uif = SAM_UIF(input_query="Test query")
        uif.intermediate_data["explicit_knowledge_chunks"] = ["chunk1", "chunk2"]
        assert skill._validate_inputs(uif) == True
        logger.info("  ✅ UIF integration successful")
        
        # Test 4: Test basic execution (mocked)
        logger.info("  Testing basic execution...")
        from unittest.mock import patch
        with patch.object(skill, '_generate_implicit_knowledge') as mock_gen:
            from sam.orchestration.skills.reasoning.implicit_knowledge import ImplicitKnowledgeResult
            mock_gen.return_value = ImplicitKnowledgeResult(
                implicit_knowledge_summary="Test summary",
                unified_context="Test context",
                confidence_score=0.8,
                processing_time=1.0,
                source_chunks_count=2
            )
            result = skill.execute(uif)
            assert result == True
        logger.info("  ✅ Basic execution successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Smoke test failed: {e}")
        return False


def generate_test_report(results):
    """Generate a comprehensive test report."""
    logger.info("📊 Generating test report...")
    
    report = []
    report.append("=" * 60)
    report.append("IMPLICIT KNOWLEDGE ENGINE TEST REPORT")
    report.append("=" * 60)
    report.append("")
    
    # Test results summary
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    report.append(f"Total Test Suites: {total_tests}")
    report.append(f"Passed: {passed_tests}")
    report.append(f"Failed: {failed_tests}")
    report.append(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    report.append("")
    
    # Detailed results
    report.append("DETAILED RESULTS:")
    report.append("-" * 20)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        report.append(f"{test_name}: {status}")
    
    report.append("")
    report.append("=" * 60)
    
    # Print report
    for line in report:
        print(line)
    
    # Save report to file
    try:
        report_file = project_root / "tests" / "test_report.txt"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report))
        logger.info(f"📄 Test report saved to: {report_file}")
    except Exception as e:
        logger.warning(f"⚠️ Could not save test report: {e}")


def main():
    """Main test runner function."""
    logger.info("🚀 Starting Implicit Knowledge Engine Test Suite")
    logger.info(f"📁 Project root: {project_root}")
    
    # Run all test suites
    results = {}
    
    # Smoke tests first
    results["Smoke Tests"] = run_smoke_tests()
    
    # Unit tests
    results["Unit Tests"] = run_unit_tests()
    
    # Integration tests
    results["Integration Tests"] = run_integration_tests()
    
    # End-to-end tests
    results["End-to-End Tests"] = run_e2e_tests()
    
    # Generate report
    generate_test_report(results)
    
    # Overall result
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("🎉 All tests passed! Implicit Knowledge Engine is ready for deployment.")
        return 0
    else:
        logger.error("💥 Some tests failed. Please review the test report.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
