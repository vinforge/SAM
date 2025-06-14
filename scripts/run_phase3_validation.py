#!/usr/bin/env python3
"""
Phase 3: Complete A/B Validation Pipeline
Master orchestration script for comprehensive validation of Active Reasoning Control
"""

import sys
import time
import logging
import subprocess
from pathlib import Path

# Add SAM to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Phase3Orchestrator:
    """Orchestrates the complete Phase 3 validation pipeline."""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.start_time = time.time()
        
        logger.info("🚀 Phase 3: Complete A/B Validation Pipeline")
        logger.info("=" * 60)
    
    def run_framework_setup(self) -> bool:
        """Step 1: Setup A/B testing framework."""
        logger.info("\n📋 Step 1: Setting up A/B Testing Framework")
        
        try:
            result = subprocess.run([
                sys.executable, 
                str(self.script_dir / "ab_testing_framework.py")
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ A/B Testing Framework setup complete")
                logger.info(result.stdout)
                return True
            else:
                logger.error("❌ Framework setup failed")
                logger.error(result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"❌ Framework setup error: {e}")
            return False
    
    def run_ab_testing(self) -> Path:
        """Step 2: Execute comprehensive A/B testing."""
        logger.info("\n📋 Step 2: Executing A/B Testing")
        
        try:
            result = subprocess.run([
                sys.executable,
                str(self.script_dir / "run_ab_validation.py")
            ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
            
            if result.returncode == 0:
                logger.info("✅ A/B Testing execution complete")
                
                # Extract results file path from output
                output_lines = result.stdout.split('\n')
                results_file = None
                
                for line in output_lines:
                    if 'Results saved to:' in line and '.json' in line:
                        # Extract JSON file path
                        json_path = line.split('JSON: ')[-1].strip()
                        results_file = Path(json_path)
                        break
                
                if results_file and results_file.exists():
                    logger.info(f"📁 Results file: {results_file}")
                    return results_file
                else:
                    logger.error("❌ Could not find results file")
                    return None
            else:
                logger.error("❌ A/B Testing execution failed")
                logger.error(result.stderr)
                return None
                
        except Exception as e:
            logger.error(f"❌ A/B Testing error: {e}")
            return None
    
    def run_evaluation(self, results_file: Path) -> Path:
        """Step 3: Run LLM-as-a-Judge evaluation."""
        logger.info("\n📋 Step 3: Running LLM-as-a-Judge Evaluation")
        
        try:
            result = subprocess.run([
                sys.executable,
                str(self.script_dir / "evaluate_responses.py"),
                str(results_file)
            ], capture_output=True, text=True, timeout=7200)  # 2 hour timeout
            
            if result.returncode == 0:
                logger.info("✅ Response evaluation complete")
                
                # Extract enhanced results file path
                output_lines = result.stdout.split('\n')
                enhanced_file = None
                
                for line in output_lines:
                    if 'Enhanced results saved to:' in line:
                        enhanced_path = line.split('Enhanced results saved to: ')[-1].strip()
                        enhanced_file = Path(enhanced_path)
                        break
                
                if enhanced_file and enhanced_file.exists():
                    logger.info(f"📁 Enhanced results: {enhanced_file}")
                    return enhanced_file
                else:
                    logger.error("❌ Could not find enhanced results file")
                    return None
            else:
                logger.error("❌ Response evaluation failed")
                logger.error(result.stderr)
                return None
                
        except Exception as e:
            logger.error(f"❌ Evaluation error: {e}")
            return None
    
    def generate_final_report(self, enhanced_results_file: Path) -> Path:
        """Step 4: Generate final analysis report."""
        logger.info("\n📋 Step 4: Generating Final Analysis Report")
        
        try:
            result = subprocess.run([
                sys.executable,
                str(self.script_dir / "generate_final_report.py"),
                str(enhanced_results_file)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Final report generation complete")
                
                # Extract report file path
                output_lines = result.stdout.split('\n')
                report_file = None
                
                for line in output_lines:
                    if 'Final report saved to:' in line:
                        report_path = line.split('Final report saved to: ')[-1].strip()
                        report_file = Path(report_path)
                        break
                
                if report_file and report_file.exists():
                    logger.info(f"📁 Final report: {report_file}")
                    return report_file
                else:
                    logger.error("❌ Could not find final report file")
                    return None
            else:
                logger.error("❌ Final report generation failed")
                logger.error(result.stderr)
                return None
                
        except Exception as e:
            logger.error(f"❌ Report generation error: {e}")
            return None
    
    def run_complete_pipeline(self) -> bool:
        """Run the complete Phase 3 validation pipeline."""
        logger.info("🎯 Starting Complete Phase 3 Validation Pipeline")
        
        # Step 1: Framework Setup
        if not self.run_framework_setup():
            logger.error("❌ Pipeline failed at framework setup")
            return False
        
        # Step 2: A/B Testing
        results_file = self.run_ab_testing()
        if not results_file:
            logger.error("❌ Pipeline failed at A/B testing")
            return False
        
        # Step 3: Evaluation
        enhanced_results_file = self.run_evaluation(results_file)
        if not enhanced_results_file:
            logger.error("❌ Pipeline failed at evaluation")
            return False
        
        # Step 4: Final Report
        report_file = self.generate_final_report(enhanced_results_file)
        if not report_file:
            logger.error("❌ Pipeline failed at report generation")
            return False
        
        # Success!
        total_time = time.time() - self.start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 PHASE 3 VALIDATION PIPELINE COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"⏱️ Total Time: {total_time/60:.1f} minutes")
        logger.info(f"📊 Final Report: {report_file}")
        logger.info("🎯 Ready for Go/No-Go Decision!")
        
        # Display final report summary
        try:
            with open(report_file, 'r') as f:
                report_content = f.read()
            
            # Extract key sections
            if "Go/No-Go Decision:" in report_content:
                decision_line = [line for line in report_content.split('\n') if 'Go/No-Go Decision:' in line][0]
                logger.info(f"\n🚦 {decision_line}")
            
            if "Overall Assessment:" in report_content:
                assessment_line = [line for line in report_content.split('\n') if 'Overall Assessment:' in line][0]
                logger.info(f"📈 {assessment_line}")
                
        except Exception as e:
            logger.warning(f"Could not extract report summary: {e}")
        
        return True
    
    def run_quick_validation(self) -> bool:
        """Run a quick validation with subset of prompts for testing."""
        logger.info("⚡ Running Quick Validation (Subset)")
        
        # This would modify the framework to use fewer prompts
        # For now, just run the full pipeline
        return self.run_complete_pipeline()

def main():
    """Main orchestration function."""
    orchestrator = Phase3Orchestrator()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = orchestrator.run_quick_validation()
    else:
        success = orchestrator.run_complete_pipeline()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
