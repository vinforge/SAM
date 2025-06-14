#!/usr/bin/env python3
"""
Phase 4: Production Deployment Script
Deploys Active Reasoning Control to production with monitoring and rollback capabilities
"""

import sys
import time
import logging
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add SAM to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TPVProductionDeployer:
    """Handles production deployment of Active Reasoning Control."""
    
    def __init__(self):
        self.deployment_timestamp = time.time()
        self.backup_dir = Path("deployment_backups") / f"backup_{int(self.deployment_timestamp)}"
        self.deployment_log = []
        
    def deploy_to_production(self, enable_by_default: bool = False) -> Dict[str, Any]:
        """Deploy TPV to production with comprehensive monitoring."""
        logger.info("🚀 Starting Production Deployment of Active Reasoning Control")
        logger.info("=" * 70)
        
        try:
            # Step 1: Pre-deployment Validation
            logger.info("🔍 Step 1: Pre-deployment Validation")
            validation_result = self._validate_pre_deployment()
            if not validation_result['success']:
                return self._deployment_failed("Pre-deployment validation failed", validation_result)
            
            # Step 2: Create Backup
            logger.info("💾 Step 2: Creating System Backup")
            backup_result = self._create_system_backup()
            if not backup_result['success']:
                return self._deployment_failed("System backup failed", backup_result)
            
            # Step 3: Update Configuration
            logger.info("⚙️ Step 3: Updating Production Configuration")
            config_result = self._update_production_config(enable_by_default)
            if not config_result['success']:
                return self._deployment_failed("Configuration update failed", config_result)
            
            # Step 4: Deploy Optimizations
            logger.info("🔧 Step 4: Deploying Performance Optimizations")
            optimization_result = self._deploy_optimizations()
            if not optimization_result['success']:
                logger.warning("⚠️ Performance optimizations failed - continuing with basic deployment")
            
            # Step 5: Initialize Monitoring
            logger.info("📊 Step 5: Initializing Production Monitoring")
            monitoring_result = self._initialize_monitoring()
            if not monitoring_result['success']:
                logger.warning("⚠️ Monitoring initialization failed - continuing without monitoring")
            
            # Step 6: Validate Deployment
            logger.info("✅ Step 6: Validating Production Deployment")
            final_validation = self._validate_production_deployment()
            if not final_validation['success']:
                logger.error("❌ Production validation failed - initiating rollback")
                rollback_result = self._rollback_deployment()
                return self._deployment_failed("Production validation failed", final_validation, rollback_result)
            
            # Step 7: Enable User Access
            logger.info("🎯 Step 7: Enabling User Access")
            access_result = self._enable_user_access(enable_by_default)
            
            # Deployment Success
            deployment_summary = self._create_deployment_summary(
                validation_result, backup_result, config_result, 
                optimization_result, monitoring_result, final_validation, access_result
            )
            
            logger.info("🎉 PRODUCTION DEPLOYMENT SUCCESSFUL!")
            logger.info(f"📊 TPV Active Reasoning Control is now {'enabled by default' if enable_by_default else 'available as opt-in'}")
            
            return deployment_summary
            
        except Exception as e:
            logger.error(f"❌ Deployment failed with exception: {e}")
            rollback_result = self._rollback_deployment()
            return self._deployment_failed(f"Deployment exception: {e}", {}, rollback_result)
    
    def _validate_pre_deployment(self) -> Dict[str, Any]:
        """Validate system readiness for deployment."""
        try:
            validation_checks = []
            
            # Check TPV integration availability
            try:
                from sam.cognition.tpv.sam_integration import sam_tpv_integration
                if sam_tpv_integration.is_initialized or sam_tpv_integration.initialize():
                    validation_checks.append({"check": "TPV Integration", "status": "✅ PASS"})
                else:
                    validation_checks.append({"check": "TPV Integration", "status": "❌ FAIL"})
                    return {"success": False, "checks": validation_checks}
            except Exception as e:
                validation_checks.append({"check": "TPV Integration", "status": f"❌ FAIL: {e}"})
                return {"success": False, "checks": validation_checks}
            
            # Check Ollama availability
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    validation_checks.append({"check": "Ollama API", "status": "✅ PASS"})
                else:
                    validation_checks.append({"check": "Ollama API", "status": "❌ FAIL"})
                    return {"success": False, "checks": validation_checks}
            except Exception as e:
                validation_checks.append({"check": "Ollama API", "status": f"❌ FAIL: {e}"})
                return {"success": False, "checks": validation_checks}
            
            # Check A/B testing results
            ab_results_dir = Path("ab_testing_results")
            if ab_results_dir.exists():
                result_files = list(ab_results_dir.glob("final_report_*.md"))
                if result_files:
                    validation_checks.append({"check": "A/B Test Results", "status": "✅ PASS"})
                else:
                    validation_checks.append({"check": "A/B Test Results", "status": "⚠️ WARNING: No results found"})
            else:
                validation_checks.append({"check": "A/B Test Results", "status": "⚠️ WARNING: Results directory not found"})
            
            # Check system resources
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent < 80 and memory_percent < 80:
                validation_checks.append({"check": "System Resources", "status": f"✅ PASS (CPU: {cpu_percent:.1f}%, RAM: {memory_percent:.1f}%)"})
            else:
                validation_checks.append({"check": "System Resources", "status": f"⚠️ WARNING: High usage (CPU: {cpu_percent:.1f}%, RAM: {memory_percent:.1f}%)"})
            
            logger.info("✅ Pre-deployment validation completed")
            for check in validation_checks:
                logger.info(f"  {check['check']}: {check['status']}")
            
            return {"success": True, "checks": validation_checks}
            
        except Exception as e:
            logger.error(f"Pre-deployment validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_system_backup(self) -> Dict[str, Any]:
        """Create backup of current system configuration."""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_items = []
            
            # Backup TPV configuration
            tpv_config_path = Path("sam/cognition/tpv/tpv_config.yaml")
            if tpv_config_path.exists():
                backup_config_path = self.backup_dir / "tpv_config.yaml"
                shutil.copy2(tpv_config_path, backup_config_path)
                backup_items.append(f"TPV Config: {backup_config_path}")
            
            # Backup secure app configuration
            secure_app_path = Path("secure_streamlit_app.py")
            if secure_app_path.exists():
                backup_app_path = self.backup_dir / "secure_streamlit_app.py"
                shutil.copy2(secure_app_path, backup_app_path)
                backup_items.append(f"Secure App: {backup_app_path}")
            
            # Create backup manifest
            backup_manifest = {
                "backup_timestamp": self.deployment_timestamp,
                "backup_items": backup_items,
                "backup_reason": "TPV Production Deployment",
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform
                }
            }
            
            manifest_path = self.backup_dir / "backup_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(backup_manifest, f, indent=2)
            
            logger.info(f"✅ System backup created: {self.backup_dir}")
            logger.info(f"📁 Backup items: {len(backup_items)}")
            
            return {"success": True, "backup_dir": str(self.backup_dir), "items": backup_items}
            
        except Exception as e:
            logger.error(f"System backup failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _update_production_config(self, enable_by_default: bool) -> Dict[str, Any]:
        """Update configuration for production deployment."""
        try:
            config_updates = []
            
            # Update TPV configuration
            tpv_config_path = Path("sam/cognition/tpv/tpv_config.yaml")
            if tpv_config_path.exists():
                import yaml
                
                with open(tpv_config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Update deployment parameters
                if 'deployment_params' not in config:
                    config['deployment_params'] = {}
                
                config['deployment_params'].update({
                    'tpv_enabled_by_default': enable_by_default,
                    'production_deployment': True,
                    'deployment_timestamp': self.deployment_timestamp,
                    'deployment_version': '4.0.0',
                    'allow_user_override': True,
                    'enable_telemetry': True,
                    'enable_optimizations': True
                })
                
                with open(tpv_config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                
                config_updates.append("TPV Config: Updated deployment parameters")
            
            logger.info("✅ Production configuration updated")
            for update in config_updates:
                logger.info(f"  {update}")
            
            return {"success": True, "updates": config_updates, "enabled_by_default": enable_by_default}
            
        except Exception as e:
            logger.error(f"Configuration update failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _deploy_optimizations(self) -> Dict[str, Any]:
        """Deploy performance optimizations."""
        try:
            # Run optimization script
            import subprocess
            
            result = subprocess.run([
                sys.executable,
                str(Path(__file__).parent / "optimize_tpv_performance.py")
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Performance optimizations deployed successfully")
                return {"success": True, "optimization_output": result.stdout}
            else:
                logger.warning("⚠️ Performance optimization failed")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            logger.warning(f"Optimization deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _initialize_monitoring(self) -> Dict[str, Any]:
        """Initialize production monitoring."""
        try:
            monitoring_config = {
                "metrics_collection": True,
                "performance_tracking": True,
                "error_reporting": True,
                "user_feedback_collection": True,
                "intervention_rate_monitoring": True,
                "efficiency_tracking": True
            }
            
            # Create monitoring directory
            monitoring_dir = Path("monitoring")
            monitoring_dir.mkdir(exist_ok=True)
            
            # Save monitoring configuration
            with open(monitoring_dir / "monitoring_config.json", 'w') as f:
                json.dump(monitoring_config, f, indent=2)
            
            logger.info("✅ Production monitoring initialized")
            return {"success": True, "monitoring_config": monitoring_config}
            
        except Exception as e:
            logger.error(f"Monitoring initialization failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_production_deployment(self) -> Dict[str, Any]:
        """Validate the production deployment."""
        try:
            validation_tests = []
            
            # Test TPV integration
            try:
                from sam.cognition.tpv.sam_integration import sam_tpv_integration
                status = sam_tpv_integration.get_integration_status()
                if status['initialized']:
                    validation_tests.append({"test": "TPV Integration", "status": "✅ PASS"})
                else:
                    validation_tests.append({"test": "TPV Integration", "status": "❌ FAIL"})
                    return {"success": False, "tests": validation_tests}
            except Exception as e:
                validation_tests.append({"test": "TPV Integration", "status": f"❌ FAIL: {e}"})
                return {"success": False, "tests": validation_tests}
            
            # Test response generation
            try:
                test_response = sam_tpv_integration.generate_response_with_tpv(
                    prompt="Test deployment validation",
                    initial_confidence=0.5
                )
                if test_response and test_response.content:
                    validation_tests.append({"test": "Response Generation", "status": "✅ PASS"})
                else:
                    validation_tests.append({"test": "Response Generation", "status": "❌ FAIL"})
                    return {"success": False, "tests": validation_tests}
            except Exception as e:
                validation_tests.append({"test": "Response Generation", "status": f"❌ FAIL: {e}"})
                return {"success": False, "tests": validation_tests}
            
            logger.info("✅ Production deployment validation completed")
            for test in validation_tests:
                logger.info(f"  {test['test']}: {test['status']}")
            
            return {"success": True, "tests": validation_tests}
            
        except Exception as e:
            logger.error(f"Production validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _enable_user_access(self, enable_by_default: bool) -> Dict[str, Any]:
        """Enable user access to TPV features."""
        try:
            access_config = {
                "tpv_enabled_by_default": enable_by_default,
                "user_controls_available": True,
                "performance_warnings_enabled": True,
                "telemetry_enabled": True
            }
            
            logger.info(f"✅ User access enabled (Default: {'ON' if enable_by_default else 'OFF'})")
            return {"success": True, "access_config": access_config}
            
        except Exception as e:
            logger.error(f"User access enablement failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _rollback_deployment(self) -> Dict[str, Any]:
        """Rollback deployment in case of failure."""
        try:
            logger.warning("🔄 Initiating deployment rollback...")
            
            rollback_actions = []
            
            # Restore from backup
            if self.backup_dir.exists():
                backup_manifest_path = self.backup_dir / "backup_manifest.json"
                if backup_manifest_path.exists():
                    with open(backup_manifest_path, 'r') as f:
                        manifest = json.load(f)
                    
                    # Restore TPV config
                    backup_config = self.backup_dir / "tpv_config.yaml"
                    if backup_config.exists():
                        target_config = Path("sam/cognition/tpv/tpv_config.yaml")
                        shutil.copy2(backup_config, target_config)
                        rollback_actions.append("Restored TPV configuration")
                    
                    # Restore secure app
                    backup_app = self.backup_dir / "secure_streamlit_app.py"
                    if backup_app.exists():
                        target_app = Path("secure_streamlit_app.py")
                        shutil.copy2(backup_app, target_app)
                        rollback_actions.append("Restored secure app configuration")
            
            logger.info(f"✅ Rollback completed: {len(rollback_actions)} actions")
            return {"success": True, "actions": rollback_actions}
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _deployment_failed(self, reason: str, details: Dict[str, Any], rollback_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle deployment failure."""
        return {
            "success": False,
            "deployment_status": "FAILED",
            "failure_reason": reason,
            "failure_details": details,
            "rollback_result": rollback_result,
            "deployment_timestamp": self.deployment_timestamp
        }
    
    def _create_deployment_summary(self, *step_results) -> Dict[str, Any]:
        """Create comprehensive deployment summary."""
        validation, backup, config, optimization, monitoring, final_validation, access = step_results
        
        return {
            "success": True,
            "deployment_status": "SUCCESSFUL",
            "deployment_timestamp": self.deployment_timestamp,
            "deployment_version": "4.0.0",
            "steps_completed": {
                "pre_deployment_validation": validation,
                "system_backup": backup,
                "configuration_update": config,
                "optimization_deployment": optimization,
                "monitoring_initialization": monitoring,
                "production_validation": final_validation,
                "user_access_enablement": access
            },
            "production_features": {
                "active_reasoning_control": True,
                "performance_optimizations": optimization.get('success', False),
                "production_monitoring": monitoring.get('success', False),
                "user_controls": True,
                "telemetry": True
            },
            "backup_location": str(self.backup_dir)
        }

def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy TPV Active Reasoning Control to production")
    parser.add_argument("--enable-by-default", action="store_true", 
                       help="Enable TPV by default for all users")
    parser.add_argument("--opt-in-only", action="store_true",
                       help="Deploy as opt-in only (default)")
    
    args = parser.parse_args()
    
    # Determine deployment mode
    enable_by_default = args.enable_by_default and not args.opt_in_only
    
    logger.info("🚀 Starting TPV Production Deployment")
    logger.info(f"📋 Deployment Mode: {'Enabled by Default' if enable_by_default else 'Opt-in Only'}")
    
    deployer = TPVProductionDeployer()
    result = deployer.deploy_to_production(enable_by_default)
    
    # Save deployment results
    results_file = Path("deployment_results") / f"deployment_result_{int(time.time())}.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    logger.info(f"📁 Deployment results saved to: {results_file}")
    
    if result['success']:
        logger.info("🎉 TPV PRODUCTION DEPLOYMENT SUCCESSFUL!")
        return 0
    else:
        logger.error("❌ TPV PRODUCTION DEPLOYMENT FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
