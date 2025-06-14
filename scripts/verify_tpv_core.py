#!/usr/bin/env python3
"""
Enhanced TPV Core Verification Script
Phase 0 - Task 5: Enhanced Sanity Check & Verification

This script performs comprehensive verification of the TPV core installation,
including configuration loading, model initialization, and basic functionality testing.
"""

import sys
import os
import logging
import torch
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Add SAM to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TPVVerifier:
    """Comprehensive TPV verification system."""
    
    def __init__(self):
        self.verification_results = {}
        self.test_passed = 0
        self.test_failed = 0
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result and update counters."""
        if passed:
            self.test_passed += 1
            logger.info(f"✅ {test_name}: PASSED {details}")
        else:
            self.test_failed += 1
            logger.error(f"❌ {test_name}: FAILED {details}")
        
        self.verification_results[test_name] = {
            'passed': passed,
            'details': details
        }
    
    def verify_dependencies(self) -> bool:
        """Verify all required dependencies are available."""
        logger.info("🔍 Verifying TPV dependencies...")
        
        dependencies = {
            'torch': 'PyTorch',
            'einops': 'Einops tensor operations',
            'yaml': 'YAML configuration',
            'sklearn': 'Scikit-learn'
        }
        
        all_passed = True
        
        for module, description in dependencies.items():
            try:
                if module == 'sklearn':
                    import sklearn
                    version = sklearn.__version__
                else:
                    imported = __import__(module)
                    version = getattr(imported, '__version__', 'unknown')
                
                self.log_test_result(
                    f"Dependency: {module}",
                    True,
                    f"({description} v{version})"
                )
            except ImportError as e:
                self.log_test_result(
                    f"Dependency: {module}",
                    False,
                    f"({description} - {e})"
                )
                all_passed = False
        
        return all_passed
    
    def verify_configuration(self) -> bool:
        """Verify TPV configuration can be loaded."""
        logger.info("🔍 Verifying TPV configuration...")
        
        try:
            from sam.cognition.tpv.tpv_config import TPVConfig
            
            # Test configuration loading
            config = TPVConfig()
            
            # Verify configuration validation
            if config.validate_config():
                hidden_dim = config.get_hidden_dimension()
                device = config.get_device()
                
                self.log_test_result(
                    "Configuration Loading",
                    True,
                    f"(hidden_dim={hidden_dim}, device={device})"
                )
                
                # Test configuration properties
                model_params = config.model_params
                tpv_params = config.tpv_params
                runtime_params = config.runtime_params
                
                self.log_test_result(
                    "Configuration Properties",
                    True,
                    f"(model={model_params.model_name[:30]}...)"
                )
                
                return True
            else:
                self.log_test_result(
                    "Configuration Validation",
                    False,
                    "(validation failed)"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Configuration Loading",
                False,
                f"({e})"
            )
            return False
    
    def verify_tpv_core_import(self) -> bool:
        """Verify TPV core can be imported."""
        logger.info("🔍 Verifying TPV core import...")
        
        try:
            from sam.cognition.tpv import TPVCore, TPVConfig
            
            self.log_test_result(
                "TPV Core Import",
                True,
                "(TPVCore and TPVConfig imported successfully)"
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "TPV Core Import",
                False,
                f"({e})"
            )
            return False
    
    def verify_tpv_initialization(self) -> Tuple[bool, Optional[Any]]:
        """Verify TPV core can be initialized."""
        logger.info("🔍 Verifying TPV core initialization...")
        
        try:
            from sam.cognition.tpv import TPVCore
            
            # Initialize TPV core
            tpv_core = TPVCore()
            
            # Check initial state
            status = tpv_core.get_status()
            
            self.log_test_result(
                "TPV Core Creation",
                True,
                f"(device={status['device']}, initialized={status['initialized']})"
            )
            
            # Initialize the core
            if tpv_core.initialize():
                self.log_test_result(
                    "TPV Core Initialization",
                    True,
                    "(processor initialized successfully)"
                )
                return True, tpv_core
            else:
                self.log_test_result(
                    "TPV Core Initialization",
                    False,
                    "(initialization failed)"
                )
                return False, None
                
        except Exception as e:
            self.log_test_result(
                "TPV Core Initialization",
                False,
                f"({e})"
            )
            return False, None
    
    def verify_tpv_processing(self, tpv_core) -> bool:
        """Verify TPV can process dummy tensor input."""
        logger.info("🔍 Verifying TPV processing functionality...")
        
        try:
            # Get configuration for correct dimensions
            hidden_dim = tpv_core.config.get_hidden_dimension()
            
            # Create dummy input tensor
            batch_size = 1
            seq_len = 10
            dummy_input = torch.randn(batch_size, seq_len, hidden_dim)
            
            self.log_test_result(
                "Dummy Tensor Creation",
                True,
                f"(shape={dummy_input.shape})"
            )
            
            # Process through TPV
            results = tpv_core.process_thinking(dummy_input)
            
            # Verify results structure
            required_keys = ['confidence_score', 'reasoning_quality', 'meta_analysis']
            missing_keys = [key for key in required_keys if key not in results]
            
            if not missing_keys:
                confidence = results['confidence_score']
                reasoning_quality = results['reasoning_quality']
                
                self.log_test_result(
                    "TPV Processing",
                    True,
                    f"(confidence={confidence:.3f}, quality={reasoning_quality:.3f})"
                )
                
                # Verify output ranges
                if 0.0 <= confidence <= 1.0 and 0.0 <= reasoning_quality <= 1.0:
                    self.log_test_result(
                        "Output Range Validation",
                        True,
                        "(scores within valid range [0,1])"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Output Range Validation",
                        False,
                        f"(scores outside range: conf={confidence}, qual={reasoning_quality})"
                    )
                    return False
            else:
                self.log_test_result(
                    "TPV Processing",
                    False,
                    f"(missing keys: {missing_keys})"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "TPV Processing",
                False,
                f"({e})"
            )
            return False
    
    def verify_asset_integrity(self) -> bool:
        """Verify TPV assets are present and valid."""
        logger.info("🔍 Verifying TPV asset integrity...")
        
        try:
            assets_dir = Path("sam/assets/tpv")
            
            if not assets_dir.exists():
                self.log_test_result(
                    "Assets Directory",
                    False,
                    "(directory not found)"
                )
                return False
            
            self.log_test_result(
                "Assets Directory",
                True,
                f"(found at {assets_dir})"
            )
            
            # Check required files
            required_files = [
                "tpv_model_weights.bin",
                "tpv_model_config.json",
                "asset_manifest.json"
            ]
            
            all_files_present = True
            for filename in required_files:
                file_path = assets_dir / filename
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    self.log_test_result(
                        f"Asset: {filename}",
                        True,
                        f"({file_size} bytes)"
                    )
                else:
                    self.log_test_result(
                        f"Asset: {filename}",
                        False,
                        "(file not found)"
                    )
                    all_files_present = False
            
            return all_files_present
            
        except Exception as e:
            self.log_test_result(
                "Asset Integrity",
                False,
                f"({e})"
            )
            return False
    
    def verify_integration_readiness(self) -> bool:
        """Verify TPV is ready for integration with SAM."""
        logger.info("🔍 Verifying integration readiness...")
        
        try:
            # Check if TPV can be imported from SAM namespace
            from sam.cognition.tpv import TPVCore
            
            # Verify configuration compatibility
            tpv_core = TPVCore()
            status = tpv_core.get_status()
            
            # Check phase and version
            phase = status.get('phase', '')
            version = status.get('version', '')
            
            if 'Phase 0' in phase:
                self.log_test_result(
                    "Phase Compatibility",
                    True,
                    f"({phase}, v{version})"
                )
            else:
                self.log_test_result(
                    "Phase Compatibility",
                    False,
                    f"(unexpected phase: {phase})"
                )
                return False
            
            # Check device compatibility
            device = status.get('device', 'unknown')
            if device in ['cpu', 'cuda', 'mps']:
                self.log_test_result(
                    "Device Compatibility",
                    True,
                    f"(device={device})"
                )
            else:
                self.log_test_result(
                    "Device Compatibility",
                    False,
                    f"(unsupported device: {device})"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Integration Readiness",
                False,
                f"({e})"
            )
            return False
    
    def run_comprehensive_verification(self) -> bool:
        """Run all verification tests."""
        logger.info("🚀 Starting Comprehensive TPV Verification (Phase 0 - Task 5)")
        logger.info("=" * 70)
        
        # Test sequence
        tests = [
            ("Dependencies", self.verify_dependencies),
            ("Configuration", self.verify_configuration),
            ("Core Import", self.verify_tpv_core_import),
            ("Asset Integrity", self.verify_asset_integrity),
        ]
        
        # Run basic tests
        for test_name, test_func in tests:
            logger.info(f"\n📋 {test_name} Verification")
            test_func()
        
        # Advanced tests requiring initialization
        logger.info(f"\n📋 Initialization & Processing Verification")
        init_success, tpv_core = self.verify_tpv_initialization()
        
        if init_success and tpv_core:
            self.verify_tpv_processing(tpv_core)
        
        # Integration readiness
        logger.info(f"\n📋 Integration Readiness Verification")
        self.verify_integration_readiness()
        
        # Summary
        total_tests = self.test_passed + self.test_failed
        success_rate = (self.test_passed / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {self.test_passed}")
        logger.info(f"Failed: {self.test_failed}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_failed == 0:
            logger.info("🎉 ALL VERIFICATION TESTS PASSED!")
            logger.info("✅ TPV Core is ready for Phase 1 integration")
            logger.info("✅ All components verified and functional")
            logger.info("✅ Configuration and assets validated")
            logger.info("\n🚀 Phase 0 COMPLETE - Ready for Phase 1!")
            return True
        else:
            logger.error("❌ VERIFICATION FAILED!")
            logger.error(f"Please resolve {self.test_failed} failed test(s) before proceeding")
            
            # Show failed tests
            failed_tests = [name for name, result in self.verification_results.items() 
                          if not result['passed']]
            logger.error("Failed tests:")
            for test in failed_tests:
                details = self.verification_results[test]['details']
                logger.error(f"  - {test}: {details}")
            
            return False

def main():
    """Main verification function."""
    verifier = TPVVerifier()
    
    try:
        success = verifier.run_comprehensive_verification()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Verification script failed with unexpected error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
