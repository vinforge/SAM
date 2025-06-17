"""
MEMOIR SOF Integration

Integration module for registering MEMOIR skills with SAM's Skills Orchestration Framework.
Provides automatic skill discovery, registration, and dynamic planner integration.

Author: SAM Development Team
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .sof_integration import SOFIntegration
from .skills.internal.memoir_edit import MEMOIR_EditSkill
from .uif import SAM_UIF
from .config import get_sof_config

logger = logging.getLogger(__name__)

class MEMOIRSOFIntegration:
    """
    MEMOIR integration with SAM's Skills Orchestration Framework.
    
    This class handles:
    - Registration of MEMOIR skills with SOF
    - Dynamic planner integration for MEMOIR operations
    - Skill discovery and capability advertisement
    - Performance monitoring and optimization
    """
    
    def __init__(self, sof_integration: Optional[SOFIntegration] = None):
        """
        Initialize MEMOIR SOF integration.
        
        Args:
            sof_integration: Existing SOF integration instance (optional)
        """
        self.logger = logging.getLogger(f"{__name__}.MEMOIRSOFIntegration")
        self.sof_integration = sof_integration or SOFIntegration()
        self.memoir_skills = {}
        self.config = get_sof_config()
        
        # MEMOIR-specific configuration
        self.memoir_config = {
            'auto_register_skills': True,
            'enable_dynamic_planning': True,
            'default_hidden_size': 4096,
            'default_learning_rate': 1e-4,
            'default_max_training_steps': 10,
            'enable_performance_monitoring': True
        }
        
        self.logger.info("MEMOIR SOF Integration initialized")
    
    def initialize(self) -> bool:
        """
        Initialize MEMOIR integration with SOF.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Ensure SOF is initialized
            if not self.sof_integration._initialized:
                self.sof_integration.initialize()
            
            # Register MEMOIR skills
            if self.memoir_config['auto_register_skills']:
                self._register_memoir_skills()
            
            # Integrate with dynamic planner
            if self.memoir_config['enable_dynamic_planning']:
                self._integrate_with_planner()
            
            self.logger.info("MEMOIR SOF integration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MEMOIR SOF integration: {e}")
            return False
    
    def _register_memoir_skills(self) -> None:
        """Register all MEMOIR skills with SOF."""
        self.logger.info("Registering MEMOIR skills with SOF...")
        
        # Register MEMOIR_EditSkill
        try:
            edit_skill = MEMOIR_EditSkill(
                hidden_size=self.memoir_config['default_hidden_size'],
                learning_rate=self.memoir_config['default_learning_rate'],
                max_training_steps=self.memoir_config['default_max_training_steps']
            )
            
            success = self.sof_integration.register_custom_skill(edit_skill)
            if success:
                self.memoir_skills['MEMOIR_EditSkill'] = edit_skill
                self.logger.info("✅ MEMOIR_EditSkill registered with SOF")
            else:
                self.logger.error("❌ Failed to register MEMOIR_EditSkill")
                
        except Exception as e:
            self.logger.error(f"Failed to register MEMOIR_EditSkill: {e}")
        
        # Register additional MEMOIR skills as they are created
        # (Future skills like FactualCorrectionSkill, etc.)
        
        self.logger.info(f"MEMOIR skill registration completed. Registered {len(self.memoir_skills)} skills.")
    
    def _integrate_with_planner(self) -> None:
        """Integrate MEMOIR capabilities with the dynamic planner."""
        self.logger.info("Integrating MEMOIR with dynamic planner...")
        
        try:
            # Add MEMOIR-specific planning capabilities
            planner = self.sof_integration._coordinator._planner
            
            # Extend planner with MEMOIR skill awareness
            if hasattr(planner, '_skill_capabilities'):
                planner._skill_capabilities.update({
                    'MEMOIR_EditSkill': {
                        'capabilities': ['knowledge_editing', 'factual_correction', 'personalization'],
                        'triggers': ['incorrect_fact', 'user_correction', 'knowledge_update'],
                        'priority': 'high',
                        'execution_time': 2.0
                    }
                })
            
            self.logger.info("✅ MEMOIR integrated with dynamic planner")
            
        except Exception as e:
            self.logger.warning(f"Failed to integrate with dynamic planner: {e}")
    
    def register_memoir_skill(self, skill_class, **kwargs) -> bool:
        """
        Register a custom MEMOIR skill.
        
        Args:
            skill_class: MEMOIR skill class to register
            **kwargs: Initialization arguments for the skill
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            skill_instance = skill_class(**kwargs)
            success = self.sof_integration.register_custom_skill(skill_instance)
            
            if success:
                self.memoir_skills[skill_instance.skill_name] = skill_instance
                self.logger.info(f"✅ Custom MEMOIR skill registered: {skill_instance.skill_name}")
            else:
                self.logger.error(f"❌ Failed to register custom MEMOIR skill: {skill_instance.skill_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to register custom MEMOIR skill: {e}")
            return False
    
    def get_memoir_skills(self) -> Dict[str, Any]:
        """Get information about registered MEMOIR skills."""
        skill_info = {}
        
        for skill_name, skill_instance in self.memoir_skills.items():
            skill_info[skill_name] = {
                'name': skill_instance.skill_name,
                'version': skill_instance.skill_version,
                'description': skill_instance.skill_description,
                'category': skill_instance.skill_category,
                'required_inputs': skill_instance.required_inputs,
                'optional_inputs': skill_instance.optional_inputs,
                'output_keys': skill_instance.output_keys,
                'can_run_parallel': skill_instance.can_run_parallel,
                'estimated_execution_time': skill_instance.estimated_execution_time
            }
        
        return skill_info
    
    def process_memoir_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Process a query that requires MEMOIR capabilities.
        
        Args:
            query: Input query
            **kwargs: Additional parameters
            
        Returns:
            Processing results
        """
        try:
            # Create UIF for the query
            uif = SAM_UIF(input_query=query)
            
            # Add MEMOIR-specific context
            uif.intermediate_data.update(kwargs)
            
            # Process through SOF
            result = self.sof_integration.process_query(query, uif=uif)
            
            return {
                'success': True,
                'result': result,
                'memoir_skills_used': self._extract_memoir_skills_used(result)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process MEMOIR query: {e}")
            return {
                'success': False,
                'error': str(e),
                'memoir_skills_used': []
            }
    
    def _extract_memoir_skills_used(self, result) -> List[str]:
        """Extract which MEMOIR skills were used in processing."""
        memoir_skills_used = []
        
        if hasattr(result, 'execution_report') and result.execution_report:
            for skill_result in result.execution_report.skill_results:
                if skill_result.skill_name in self.memoir_skills:
                    memoir_skills_used.append(skill_result.skill_name)
        
        return memoir_skills_used
    
    def get_memoir_statistics(self) -> Dict[str, Any]:
        """Get comprehensive MEMOIR statistics."""
        stats = {
            'registered_skills': len(self.memoir_skills),
            'skill_details': {},
            'sof_integration_status': self.sof_integration._initialized,
            'configuration': self.memoir_config
        }
        
        # Get statistics from each MEMOIR skill
        for skill_name, skill_instance in self.memoir_skills.items():
            if hasattr(skill_instance, 'get_edit_statistics'):
                stats['skill_details'][skill_name] = skill_instance.get_edit_statistics()
        
        return stats
    
    def configure_memoir_skill(self, skill_name: str, **config) -> bool:
        """
        Configure a specific MEMOIR skill.
        
        Args:
            skill_name: Name of the skill to configure
            **config: Configuration parameters
            
        Returns:
            True if configuration successful, False otherwise
        """
        if skill_name not in self.memoir_skills:
            self.logger.error(f"MEMOIR skill not found: {skill_name}")
            return False
        
        try:
            skill_instance = self.memoir_skills[skill_name]
            
            # Apply configuration
            for key, value in config.items():
                if hasattr(skill_instance, key):
                    setattr(skill_instance, key, value)
                    self.logger.info(f"✅ Configured {skill_name}.{key} = {value}")
                else:
                    self.logger.warning(f"⚠️  Unknown configuration key for {skill_name}: {key}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure MEMOIR skill {skill_name}: {e}")
            return False
    
    def enable_memoir_monitoring(self) -> bool:
        """Enable performance monitoring for MEMOIR skills."""
        try:
            self.memoir_config['enable_performance_monitoring'] = True
            
            # Set up monitoring for each skill
            for skill_name, skill_instance in self.memoir_skills.items():
                if hasattr(skill_instance, 'enable_monitoring'):
                    skill_instance.enable_monitoring()
                    self.logger.info(f"✅ Monitoring enabled for {skill_name}")
            
            self.logger.info("MEMOIR performance monitoring enabled")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable MEMOIR monitoring: {e}")
            return False
    
    def create_memoir_plan_suggestions(self, query: str) -> List[str]:
        """
        Create plan suggestions for queries that could benefit from MEMOIR.
        
        Args:
            query: Input query to analyze
            
        Returns:
            List of suggested plan steps involving MEMOIR
        """
        suggestions = []
        
        # Analyze query for MEMOIR opportunities
        query_lower = query.lower()
        
        # Factual correction patterns
        correction_patterns = [
            'actually', 'correction', 'wrong', 'incorrect', 'mistake',
            'should be', 'not', "that's not right", 'fix', 'update'
        ]
        
        if any(pattern in query_lower for pattern in correction_patterns):
            suggestions.extend([
                'MEMOIR_EditSkill',  # For applying the correction
                'MemoryRetrievalSkill',  # To check existing knowledge
                'ResponseGenerationSkill'  # To confirm the correction
            ])
        
        # Learning/preference patterns
        learning_patterns = [
            'remember', 'learn', 'prefer', 'like', 'always', 'usually',
            'my preference', 'i want', 'save this', 'note that'
        ]
        
        if any(pattern in query_lower for pattern in learning_patterns):
            suggestions.extend([
                'MEMOIR_EditSkill',  # For storing the preference
                'MemoryRetrievalSkill',  # To check for conflicts
                'ResponseGenerationSkill'  # To acknowledge learning
            ])
        
        return suggestions


# Global MEMOIR SOF integration instance
_memoir_sof_integration = None

def get_memoir_sof_integration() -> MEMOIRSOFIntegration:
    """Get the global MEMOIR SOF integration instance."""
    global _memoir_sof_integration
    
    if _memoir_sof_integration is None:
        _memoir_sof_integration = MEMOIRSOFIntegration()
        _memoir_sof_integration.initialize()
    
    return _memoir_sof_integration

def register_memoir_with_sof() -> bool:
    """
    Convenience function to register MEMOIR with SOF.
    
    Returns:
        True if registration successful, False otherwise
    """
    try:
        integration = get_memoir_sof_integration()
        return integration.sof_integration._initialized
    except Exception as e:
        logger.error(f"Failed to register MEMOIR with SOF: {e}")
        return False
