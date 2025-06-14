#!/usr/bin/env python3
"""
Phase 3: Automated A/B Test Execution
Runs benchmark dataset against all three test arms and collects comprehensive metrics
"""

import sys
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
try:
    import pandas as pd
except ImportError:
    logger.warning("pandas not available - CSV export will be skipped")
    pd = None

# Add SAM to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ab_testing_framework import ABTestingFramework, TestArm, TestResult, TestPrompt, PromptCategory

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ABTestExecutor:
    """Executes A/B tests across all arms and collects comprehensive data."""
    
    def __init__(self, framework: ABTestingFramework):
        self.framework = framework
        self.results: List[TestResult] = []
        
        # Initialize TPV integrations for Arms B and C
        self._setup_tpv_integrations()
    
    def _setup_tpv_integrations(self):
        """Setup TPV integrations for monitoring and active control arms."""
        try:
            from sam.cognition.tpv import SAMTPVIntegration, ReasoningController, ControlMode, UserProfile
            
            # Arm B: Monitoring Only (Phase 1)
            self.integration_b = SAMTPVIntegration()
            self.integration_b.reasoning_controller.mode = ControlMode.PASSIVE
            if not self.integration_b.is_initialized:
                self.integration_b.initialize()
            
            # Arm C: Active Control (Phase 2)
            self.integration_c = SAMTPVIntegration()
            self.integration_c.reasoning_controller.mode = ControlMode.ACTIVE
            if not self.integration_c.is_initialized:
                self.integration_c.initialize()
            
            logger.info("✅ TPV integrations initialized for Arms B and C")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup TPV integrations: {e}")
            raise
    
    def _execute_baseline_arm(self, prompt: TestPrompt) -> TestResult:
        """Execute test for Arm A (Baseline - No TPV)."""
        start_time = time.time()
        
        try:
            # Direct Ollama call without TPV
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                    "prompt": prompt.text,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                },
                timeout=60
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get('response', '').strip()
                token_count = len(response_text.split())  # Approximate token count
                
                return TestResult(
                    prompt_id=prompt.prompt_id,
                    test_arm=TestArm.BASELINE,
                    end_to_end_latency_ms=latency_ms,
                    total_tokens_generated=token_count,
                    tpv_halt_reason=None,
                    response_text=response_text,
                    timestamp=time.time(),
                    tpv_enabled=False
                )
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            return TestResult(
                prompt_id=prompt.prompt_id,
                test_arm=TestArm.BASELINE,
                end_to_end_latency_ms=(time.time() - start_time) * 1000,
                total_tokens_generated=0,
                tpv_halt_reason=None,
                response_text="",
                timestamp=time.time(),
                error=str(e),
                tpv_enabled=False
            )
    
    def _execute_monitoring_arm(self, prompt: TestPrompt) -> TestResult:
        """Execute test for Arm B (Monitoring Only - Phase 1)."""
        start_time = time.time()
        
        try:
            # Use TPV integration in passive mode
            tpv_response = self.integration_b.generate_response_with_tpv(
                prompt=prompt.text,
                user_profile=self._get_user_profile_for_prompt(prompt),
                initial_confidence=0.5,
                ollama_params={
                    "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                }
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return TestResult(
                prompt_id=prompt.prompt_id,
                test_arm=TestArm.MONITORING,
                end_to_end_latency_ms=latency_ms,
                total_tokens_generated=len(tpv_response.content.split()),
                tpv_halt_reason=None,  # Passive mode doesn't halt
                response_text=tpv_response.content,
                timestamp=time.time(),
                tpv_enabled=tpv_response.tpv_enabled,
                tpv_steps=len(tpv_response.tpv_trace.steps) if tpv_response.tpv_trace else 0,
                final_score=tpv_response.tpv_trace.current_score if tpv_response.tpv_trace else 0.0,
                trigger_type=tpv_response.trigger_result.trigger_type if tpv_response.trigger_result else None
            )
            
        except Exception as e:
            return TestResult(
                prompt_id=prompt.prompt_id,
                test_arm=TestArm.MONITORING,
                end_to_end_latency_ms=(time.time() - start_time) * 1000,
                total_tokens_generated=0,
                tpv_halt_reason=None,
                response_text="",
                timestamp=time.time(),
                error=str(e),
                tpv_enabled=False
            )
    
    def _execute_active_control_arm(self, prompt: TestPrompt) -> TestResult:
        """Execute test for Arm C (Active Control - Phase 2)."""
        start_time = time.time()
        
        try:
            # Use TPV integration in active mode
            tpv_response = self.integration_c.generate_response_with_tpv(
                prompt=prompt.text,
                user_profile=self._get_user_profile_for_prompt(prompt),
                initial_confidence=0.5,
                ollama_params={
                    "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                }
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Get control decision from recent actions
            control_decision = "CONTINUE"
            halt_reason = None
            
            if hasattr(self.integration_c, 'reasoning_controller'):
                recent_actions = self.integration_c.reasoning_controller.get_recent_actions(1)
                if recent_actions:
                    control_decision = recent_actions[0].metadata.get('action_type', 'CONTINUE')
                    if control_decision != 'CONTINUE':
                        halt_reason = control_decision
            
            return TestResult(
                prompt_id=prompt.prompt_id,
                test_arm=TestArm.ACTIVE_CONTROL,
                end_to_end_latency_ms=latency_ms,
                total_tokens_generated=len(tpv_response.content.split()),
                tpv_halt_reason=halt_reason,
                response_text=tpv_response.content,
                timestamp=time.time(),
                tpv_enabled=tpv_response.tpv_enabled,
                tpv_steps=len(tpv_response.tpv_trace.steps) if tpv_response.tpv_trace else 0,
                final_score=tpv_response.tpv_trace.current_score if tpv_response.tpv_trace else 0.0,
                trigger_type=tpv_response.trigger_result.trigger_type if tpv_response.trigger_result else None,
                control_decision=control_decision
            )
            
        except Exception as e:
            return TestResult(
                prompt_id=prompt.prompt_id,
                test_arm=TestArm.ACTIVE_CONTROL,
                end_to_end_latency_ms=(time.time() - start_time) * 1000,
                total_tokens_generated=0,
                tpv_halt_reason=None,
                response_text="",
                timestamp=time.time(),
                error=str(e),
                tpv_enabled=False
            )
    
    def _get_user_profile_for_prompt(self, prompt: TestPrompt):
        """Determine appropriate user profile based on prompt category."""
        from sam.cognition.tpv import UserProfile
        
        profile_map = {
            PromptCategory.SIMPLE_FACTUAL: UserProfile.GENERAL,
            PromptCategory.COMPLEX_ANALYSIS: UserProfile.RESEARCHER,
            PromptCategory.SUMMARIZATION: UserProfile.BUSINESS,
            PromptCategory.OPEN_ENDED: UserProfile.GENERAL
        }
        
        return profile_map.get(prompt.category, UserProfile.GENERAL)
    
    def run_comprehensive_test(self) -> List[TestResult]:
        """Run comprehensive A/B test across all prompts and arms."""
        logger.info("🚀 Starting Comprehensive A/B Test Execution")
        logger.info("=" * 60)
        
        prompts = self.framework.dataset.get_prompts()
        total_tests = len(prompts) * 3  # 3 arms per prompt
        completed_tests = 0
        
        logger.info(f"📊 Total tests to execute: {total_tests}")
        logger.info(f"📋 Prompts: {len(prompts)}")
        logger.info(f"🎯 Arms: 3 (Baseline, Monitoring, Active Control)")
        
        for i, prompt in enumerate(prompts):
            logger.info(f"\n📋 Testing Prompt {i+1}/{len(prompts)}: {prompt.prompt_id}")
            logger.info(f"  Category: {prompt.category.value}")
            logger.info(f"  Text: {prompt.text[:100]}...")
            
            # Test Arm A (Baseline)
            logger.info("  🔍 Testing Arm A (Baseline)...")
            result_a = self._execute_baseline_arm(prompt)
            self.results.append(result_a)
            completed_tests += 1
            
            if result_a.error:
                logger.warning(f"    ⚠️ Error: {result_a.error}")
            else:
                logger.info(f"    ✅ Latency: {result_a.end_to_end_latency_ms:.1f}ms, Tokens: {result_a.total_tokens_generated}")
            
            # Test Arm B (Monitoring)
            logger.info("  🔍 Testing Arm B (Monitoring)...")
            result_b = self._execute_monitoring_arm(prompt)
            self.results.append(result_b)
            completed_tests += 1
            
            if result_b.error:
                logger.warning(f"    ⚠️ Error: {result_b.error}")
            else:
                logger.info(f"    ✅ Latency: {result_b.end_to_end_latency_ms:.1f}ms, Tokens: {result_b.total_tokens_generated}, TPV: {result_b.tpv_enabled}")
            
            # Test Arm C (Active Control)
            logger.info("  🔍 Testing Arm C (Active Control)...")
            result_c = self._execute_active_control_arm(prompt)
            self.results.append(result_c)
            completed_tests += 1
            
            if result_c.error:
                logger.warning(f"    ⚠️ Error: {result_c.error}")
            else:
                halt_info = f", Halt: {result_c.tpv_halt_reason}" if result_c.tpv_halt_reason else ""
                logger.info(f"    ✅ Latency: {result_c.end_to_end_latency_ms:.1f}ms, Tokens: {result_c.total_tokens_generated}, TPV: {result_c.tpv_enabled}{halt_info}")
            
            # Progress update
            progress = (completed_tests / total_tests) * 100
            logger.info(f"  📊 Progress: {completed_tests}/{total_tests} ({progress:.1f}%)")
        
        logger.info(f"\n✅ A/B Test Execution Complete!")
        logger.info(f"📊 Total results collected: {len(self.results)}")
        
        return self.results
    
    def save_results(self, output_file: Path):
        """Save test results to structured file."""
        # Convert results to dictionaries
        results_data = []
        for result in self.results:
            result_dict = {
                'prompt_id': result.prompt_id,
                'test_arm': result.test_arm.value,
                'end_to_end_latency_ms': result.end_to_end_latency_ms,
                'total_tokens_generated': result.total_tokens_generated,
                'tpv_halt_reason': result.tpv_halt_reason,
                'response_text': result.response_text,
                'timestamp': result.timestamp,
                'error': result.error,
                'tpv_enabled': result.tpv_enabled,
                'tpv_steps': result.tpv_steps,
                'final_score': result.final_score,
                'trigger_type': result.trigger_type,
                'control_decision': result.control_decision
            }
            results_data.append(result_dict)
        
        # Save as JSON
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        # Also save as CSV for easy analysis if pandas available
        if pd is not None:
            csv_file = output_file.with_suffix('.csv')
            df = pd.DataFrame(results_data)
            df.to_csv(csv_file, index=False)

            logger.info(f"📁 Results saved to:")
            logger.info(f"  JSON: {output_file}")
            logger.info(f"  CSV: {csv_file}")
        else:
            logger.info(f"📁 Results saved to: {output_file}")

def main():
    """Main execution function."""
    logger.info("🚀 Starting Phase 3: Automated A/B Test Execution")
    
    # Initialize framework
    framework = ABTestingFramework()
    
    # Create executor
    executor = ABTestExecutor(framework)
    
    # Run comprehensive test
    results = executor.run_comprehensive_test()
    
    # Save results
    results_file = framework.output_dir / f"ab_test_results_{int(time.time())}.json"
    executor.save_results(results_file)
    
    logger.info("🎉 A/B Test Execution Complete!")
    logger.info(f"📊 Results ready for qualitative analysis")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
