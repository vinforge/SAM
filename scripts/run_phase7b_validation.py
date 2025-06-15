#!/usr/bin/env python3
"""
Phase 7B SLP Validation Orchestrator
===================================

Master orchestrator for Phase 7B SLP (Scalable Latent Program) validation.
Implements the complete validation pipeline specified in task3.md:

1. Framework Setup & Environment Validation
2. Stateful A/B Testing (Sequential execution for pattern learning)
3. LLM-as-a-Judge Evaluation (Enhanced for SLP metrics)
4. Final Analysis & Reporting (SLP performance analysis)

This orchestrator ensures proper sequential execution to enable:
- Pattern capture in first queries of each group
- Pattern reuse validation in subsequent similar queries
- Comprehensive performance comparison across three test arms

Test Arms:
- Arm A (Baseline): Original SAM with no TPV or SLP
- Arm B (TPV Only): Phase 2 system with Active Reasoning Control only  
- Arm C (SLP Active): Full Phase 7 system with both TPV and SLP enabled
"""

import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('phase7b_validation.log')
    ]
)
logger = logging.getLogger(__name__)

class Phase7BOrchestrator:
    """Master orchestrator for Phase 7B SLP validation pipeline."""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.output_dir = self.script_dir.parent / "validation_results" / "phase7b"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🚀 Phase 7B SLP Validation Orchestrator Initialized")
        logger.info(f"📁 Output directory: {self.output_dir}")
    
    def run_framework_setup(self) -> bool:
        """Step 1: Setup and validate the Phase 7B testing framework."""
        logger.info("\n📋 Step 1: Phase 7B Framework Setup & Validation")
        
        try:
            # Import and setup the Phase 7B framework
            from phase7b_ab_testing_framework import Phase7BTestFramework
            
            framework = Phase7BTestFramework()
            
            # Validate test environment
            if not framework.setup_test_environment():
                logger.error("❌ Framework setup failed")
                return False
            
            # Log test configuration
            logger.info("📊 Test Configuration:")
            for arm, config in framework.test_arms.items():
                logger.info(f"  {arm.value}: {config['description']}")
            
            logger.info(f"📝 Benchmark Dataset: {len(framework.dataset.prompts)} prompts in {len(framework.dataset.get_sequential_prompts())} sequential order")
            
            # Log prompt groups for validation
            from phase7b_ab_testing_framework import PromptGroup
            for group in PromptGroup:
                group_prompts = framework.dataset.get_prompts_by_group(group)
                logger.info(f"  {group.value}: {len(group_prompts)} prompts")
            
            logger.info("✅ Framework setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Framework setup failed: {e}")
            return False
    
    def run_stateful_ab_testing(self) -> Optional[Path]:
        """Step 2: Execute stateful A/B testing with sequential pattern learning."""
        logger.info("\n📋 Step 2: Stateful A/B Testing Execution")
        logger.info("🔄 Sequential execution strategy for pattern learning validation")
        
        try:
            from phase7b_ab_testing_framework import Phase7BTestFramework
            
            framework = Phase7BTestFramework()
            
            # Execute stateful testing
            results = framework.execute_stateful_testing()
            
            if not results:
                logger.error("❌ No test results generated")
                return None
            
            # Save results
            results_file = framework.save_results(self.output_dir)
            
            # Log summary
            summary = framework.get_test_summary()
            logger.info("📊 Test Execution Summary:")
            logger.info(f"  Total Tests: {summary.get('total_tests', 0)}")
            
            for arm, stats in summary.get('by_arm', {}).items():
                logger.info(f"  {arm}: {stats['test_count']} tests, {stats['avg_latency_ms']:.0f}ms avg, {stats['success_rate']:.1f}% success")
            
            # SLP-specific summary
            slp_perf = summary.get('slp_performance', {})
            if slp_perf:
                logger.info(f"🧠 SLP Performance:")
                logger.info(f"  Program Uses: {slp_perf['program_uses']}/{slp_perf['total_slp_tests']} ({slp_perf['hit_rate']:.1f}%)")
                logger.info(f"  Program Captures: {slp_perf['program_captures']} ({slp_perf['capture_rate']:.1f}%)")
            
            logger.info("✅ Stateful A/B Testing complete")
            return results_file
            
        except Exception as e:
            logger.error(f"❌ Stateful A/B Testing failed: {e}")
            return None
    
    def run_enhanced_evaluation(self, results_file: Path) -> Optional[Path]:
        """Step 3: Run enhanced LLM-as-a-Judge evaluation with SLP metrics."""
        logger.info("\n📋 Step 3: Enhanced LLM-as-a-Judge Evaluation")
        logger.info("🔍 Evaluating responses with SLP-aware quality assessment")
        
        try:
            # Use the existing evaluation script but with enhanced prompts for SLP
            result = subprocess.run([
                sys.executable,
                str(self.script_dir / "evaluate_responses.py"),
                str(results_file),
                "--slp-mode"  # Flag for SLP-aware evaluation
            ], capture_output=True, text=True, timeout=7200)  # 2 hour timeout
            
            if result.returncode == 0:
                logger.info("✅ Enhanced evaluation complete")
                
                # Extract enhanced results file path
                output_lines = result.stdout.split('\n')
                enhanced_file = None
                
                for line in output_lines:
                    if 'Enhanced results saved to:' in line and '.json' in line:
                        json_path = line.split('Enhanced results saved to: ')[-1].strip()
                        enhanced_file = Path(json_path)
                        break
                
                if enhanced_file and enhanced_file.exists():
                    logger.info(f"📁 Enhanced results: {enhanced_file}")
                    return enhanced_file
                else:
                    logger.error("❌ Could not find enhanced results file")
                    return None
            else:
                logger.error("❌ Enhanced evaluation failed")
                logger.error(result.stderr)
                return None
                
        except Exception as e:
            logger.error(f"❌ Enhanced evaluation error: {e}")
            return None
    
    def generate_slp_analysis_report(self, enhanced_results_file: Path) -> Optional[Path]:
        """Step 4: Generate comprehensive SLP analysis report."""
        logger.info("\n📋 Step 4: SLP Analysis Report Generation")
        logger.info("📊 Generating comprehensive Phase 7B performance analysis")
        
        try:
            result = subprocess.run([
                sys.executable,
                str(self.script_dir / "generate_phase7b_report.py"),
                str(enhanced_results_file)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ SLP analysis report generated")
                
                # Extract report file path
                output_lines = result.stdout.split('\n')
                report_file = None
                
                for line in output_lines:
                    if 'Report saved to:' in line:
                        report_path = line.split('Report saved to: ')[-1].strip()
                        report_file = Path(report_path)
                        break
                
                if report_file and report_file.exists():
                    logger.info(f"📄 Final report: {report_file}")
                    return report_file
                else:
                    logger.error("❌ Could not find report file")
                    return None
            else:
                logger.error("❌ Report generation failed")
                logger.error(result.stderr)
                return None
                
        except Exception as e:
            logger.error(f"❌ Report generation error: {e}")
            return None
    
    def run_complete_pipeline(self) -> bool:
        """Run the complete Phase 7B SLP validation pipeline."""
        logger.info("🎯 Starting Complete Phase 7B SLP Validation Pipeline")
        logger.info("🧠 Validating Scalable Latent Program Cognitive Automation Engine")
        
        # Step 1: Framework Setup
        if not self.run_framework_setup():
            logger.error("❌ Pipeline failed at framework setup")
            return False
        
        # Step 2: Stateful A/B Testing
        results_file = self.run_stateful_ab_testing()
        if not results_file:
            logger.error("❌ Pipeline failed at stateful A/B testing")
            return False
        
        # Step 3: Enhanced Evaluation
        enhanced_results_file = self.run_enhanced_evaluation(results_file)
        if not enhanced_results_file:
            logger.warning("⚠️ Enhanced evaluation failed, proceeding with basic results")
            enhanced_results_file = results_file
        
        # Step 4: SLP Analysis Report
        report_file = self.generate_slp_analysis_report(enhanced_results_file)
        if not report_file:
            logger.error("❌ Pipeline failed at report generation")
            return False
        
        # Success!
        logger.info("\n🎉 Phase 7B SLP Validation Pipeline Complete!")
        logger.info("📊 Key Deliverables:")
        logger.info(f"  📁 Test Results: {results_file}")
        if enhanced_results_file != results_file:
            logger.info(f"  📁 Enhanced Results: {enhanced_results_file}")
        logger.info(f"  📄 Final Report: {report_file}")
        
        logger.info("\n🎯 Next Steps:")
        logger.info("  1. Review the final report for performance analysis")
        logger.info("  2. Validate hypothesis testing results")
        logger.info("  3. Make data-driven decision on SLP deployment")
        
        return True
    
    def run_quick_validation(self) -> bool:
        """Run a quick validation with subset of prompts for testing."""
        logger.info("⚡ Running Quick Phase 7B Validation (Subset)")
        logger.info("🧪 Testing framework with reduced prompt set")
        
        # For now, run the full pipeline but could be modified to use fewer prompts
        return self.run_complete_pipeline()

def main():
    """Main orchestration function."""
    orchestrator = Phase7BOrchestrator()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = orchestrator.run_quick_validation()
    else:
        success = orchestrator.run_complete_pipeline()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
