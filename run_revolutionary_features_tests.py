#!/usr/bin/env python3
"""
SAM Revolutionary Features Test Runner

This script runs comprehensive tests to validate that all of SAM's revolutionary
features are properly enabled, configured, and functioning as expected.

Revolutionary Features Tested:
1. 🧠 Human-Like Conceptual Understanding (Phase 2)
2. 🤖 Dynamic Agent Architecture (SOF v2)
3. 🎨 Cognitive Synthesis Engine (Dream Catcher)
4. 🔒 Enterprise-Grade Security (SAM Secure Enclave)
5. ⚡ Active Reasoning Control (TPV System)
6. 🧬 Autonomous Cognitive Automation (SLP System)
7. 🧮 Mathematical Query Routing (SOF v2 Integration)

Usage:
    python run_revolutionary_features_tests.py [--verbose] [--specific-test TEST_NAME]
"""

import sys
import os
import argparse
import subprocess
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class RevolutionaryFeaturesTestRunner:
    """Comprehensive test runner for SAM's revolutionary features."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_results = {}
        self.project_root = project_root
        
    def run_test_suite(self, test_file, test_name):
        """Run a specific test suite and capture results."""
        logger.info(f"🧪 Running {test_name}")
        
        try:
            # Construct command
            cmd = [sys.executable, str(self.project_root / "tests" / test_file)]
            
            # Run the test
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Store results
            self.test_results[test_name] = {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
            if result.returncode == 0:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                if self.verbose:
                    logger.error(f"STDOUT: {result.stdout}")
                    logger.error(f"STDERR: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            self.test_results[test_name] = {
                'success': False,
                'error': str(e),
                'returncode': -1
            }
            return False
    
    def run_all_tests(self):
        """Run all revolutionary features tests."""
        logger.info("🚀 Starting SAM Revolutionary Features Test Suite")
        logger.info("=" * 80)
        
        # Define test suites
        test_suites = [
            ("test_revolutionary_features_integration.py", "Revolutionary Features Integration"),
            ("test_mathematical_query_routing.py", "Mathematical Query Routing"),
            ("test_sof_phase_a.py", "SOF v2 Phase A (Core Architecture)"),
            ("test_sof_phase_b.py", "SOF v2 Phase B (Coordination & Validation)"),
            ("test_sof_phase_c.py", "SOF v2 Phase C (Dynamic Planning & Tools)"),
        ]
        
        # Run each test suite
        total_tests = len(test_suites)
        passed_tests = 0
        
        for test_file, test_name in test_suites:
            if self.run_test_suite(test_file, test_name):
                passed_tests += 1
            logger.info("-" * 40)
        
        # Generate summary
        self.generate_summary(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def run_specific_test(self, test_name):
        """Run a specific test suite."""
        test_mapping = {
            "integration": ("test_revolutionary_features_integration.py", "Revolutionary Features Integration"),
            "math": ("test_mathematical_query_routing.py", "Mathematical Query Routing"),
            "sof-a": ("test_sof_phase_a.py", "SOF v2 Phase A"),
            "sof-b": ("test_sof_phase_b.py", "SOF v2 Phase B"),
            "sof-c": ("test_sof_phase_c.py", "SOF v2 Phase C"),
        }
        
        if test_name not in test_mapping:
            logger.error(f"❌ Unknown test: {test_name}")
            logger.info(f"Available tests: {', '.join(test_mapping.keys())}")
            return False
        
        test_file, full_name = test_mapping[test_name]
        return self.run_test_suite(test_file, full_name)
    
    def generate_summary(self, passed_tests, total_tests):
        """Generate comprehensive test summary."""
        logger.info("=" * 80)
        logger.info("🎉 SAM REVOLUTIONARY FEATURES TEST SUMMARY")
        logger.info("=" * 80)
        
        # Feature status overview
        feature_categories = {
            "Revolutionary Features Integration": "🧠🤖🎨🔒⚡🧬 All Revolutionary Features",
            "Mathematical Query Routing": "🧮 SOF v2 Mathematical Query Integration",
            "SOF v2 Phase A": "🏗️ SOF v2 Core Architecture",
            "SOF v2 Phase B": "🔧 SOF v2 Coordination & Validation",
            "SOF v2 Phase C": "🚀 SOF v2 Dynamic Planning & Tools"
        }
        
        for test_name, description in feature_categories.items():
            if test_name in self.test_results:
                status = "✅ PASSED" if self.test_results[test_name]['success'] else "❌ FAILED"
                logger.info(f"{description}: {status}")
        
        logger.info("=" * 80)
        logger.info(f"📈 OVERALL RESULTS: {passed_tests}/{total_tests} Test Suites Passed")
        
        # Determine overall status
        if passed_tests == total_tests:
            logger.info("🎉 ALL REVOLUTIONARY FEATURES ARE FULLY OPERATIONAL!")
            logger.info("✅ SAM is ready for production deployment with complete feature set")
            logger.info("🧮 Mathematical queries will now route to CalculatorTool via SOF v2")
            logger.info("🤖 Dynamic agent architecture is fully functional")
            logger.info("🧠 Human-like conceptual understanding is operational")
            logger.info("🧬 Autonomous cognitive automation is available")
        elif passed_tests >= total_tests * 0.8:
            logger.info("✅ MOST REVOLUTIONARY FEATURES ARE OPERATIONAL")
            logger.info("⚠️ Some features may need additional configuration in production")
            logger.info("🔧 Review failed tests for specific configuration requirements")
        else:
            logger.info("⚠️ SOME REVOLUTIONARY FEATURES NEED ATTENTION")
            logger.info("🔧 Review failed tests and ensure proper system configuration")
            logger.info("📋 Check dependencies and environment setup")
        
        logger.info("=" * 80)
        
        # Detailed failure analysis
        if passed_tests < total_tests:
            logger.info("🔍 FAILURE ANALYSIS:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    logger.info(f"❌ {test_name}:")
                    if 'error' in result:
                        logger.info(f"   Error: {result['error']}")
                    elif result.get('stderr'):
                        logger.info(f"   Details: {result['stderr'][:200]}...")
            logger.info("=" * 80)
    
    def check_prerequisites(self):
        """Check system prerequisites for running tests."""
        logger.info("🔍 Checking System Prerequisites")
        
        prerequisites = []
        
        # Check Python version
        if sys.version_info >= (3, 8):
            logger.info("✅ Python version: OK")
        else:
            logger.error("❌ Python 3.8+ required")
            prerequisites.append("Python 3.8+")
        
        # Check project structure
        required_dirs = ["sam", "tests", "memory", "security", "reasoning"]
        for dir_name in required_dirs:
            if (self.project_root / dir_name).exists():
                logger.info(f"✅ Directory {dir_name}: OK")
            else:
                logger.warning(f"⚠️ Directory {dir_name}: Missing")
        
        # Check key files
        key_files = [
            "config/sof_config.json",
            "secure_streamlit_app.py",
            "tests/test_revolutionary_features_integration.py"
        ]
        for file_path in key_files:
            if (self.project_root / file_path).exists():
                logger.info(f"✅ File {file_path}: OK")
            else:
                logger.error(f"❌ File {file_path}: Missing")
                prerequisites.append(file_path)
        
        if prerequisites:
            logger.error(f"❌ Missing prerequisites: {', '.join(prerequisites)}")
            return False
        
        logger.info("✅ All prerequisites satisfied")
        return True


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Run SAM Revolutionary Features Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_revolutionary_features_tests.py                    # Run all tests
    python run_revolutionary_features_tests.py --verbose          # Run with verbose output
    python run_revolutionary_features_tests.py --specific-test math  # Run only math routing tests
    python run_revolutionary_features_tests.py --specific-test integration  # Run integration tests
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output including test details'
    )
    
    parser.add_argument(
        '--specific-test', '-t',
        type=str,
        help='Run a specific test suite (integration, math, sof-a, sof-b, sof-c)'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check prerequisites without running tests'
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = RevolutionaryFeaturesTestRunner(verbose=args.verbose)
    
    # Check prerequisites
    if not runner.check_prerequisites():
        logger.error("❌ Prerequisites not satisfied")
        return 1
    
    if args.check_only:
        logger.info("✅ Prerequisites check complete")
        return 0
    
    # Run tests
    if args.specific_test:
        success = runner.run_specific_test(args.specific_test)
    else:
        success = runner.run_all_tests()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
