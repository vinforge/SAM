"""
CoordinatorEngine for SAM Orchestration Framework
=================================================

Orchestrates the execution of skills according to validated plans.
Provides comprehensive error handling, fallback mechanisms, and execution monitoring.
"""

import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .uif import SAM_UIF, UIFStatus
from .skills.base import BaseSkillModule, SkillExecutionError
from .validator import PlanValidationEngine, PlanValidationReport
from .planner import DynamicPlanner, PlanGenerationResult
from .config import get_sof_config

logger = logging.getLogger(__name__)


class ExecutionResult(str, Enum):
    """Execution result enumeration."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ExecutionReport:
    """Comprehensive execution report."""
    result: ExecutionResult
    uif: SAM_UIF
    executed_skills: List[str]
    failed_skills: List[str]
    execution_time: float
    validation_report: Optional[PlanValidationReport]
    fallback_used: bool
    error_details: Optional[str] = None


class CoordinatorEngine:
    """
    Orchestrates skill execution with validation and error handling.
    
    Features:
    - Plan validation before execution
    - Comprehensive error handling and recovery
    - Fallback mechanisms for failed plans
    - Execution monitoring and metrics
    - Timeout management
    """
    
    def __init__(self, fallback_generator: Optional[Callable[[str], str]] = None,
                 enable_dynamic_planning: bool = True):
        """
        Initialize the coordinator engine.

        Args:
            fallback_generator: Optional fallback function for generating responses
            enable_dynamic_planning: Whether to enable dynamic plan generation
        """
        self.logger = logging.getLogger(f"{__name__}.CoordinatorEngine")
        self._registered_skills: Dict[str, BaseSkillModule] = {}
        self._validator = PlanValidationEngine()
        self._dynamic_planner = DynamicPlanner() if enable_dynamic_planning else None
        self._fallback_generator = fallback_generator
        self._execution_history: List[ExecutionReport] = []

        # Load configuration
        self._config = get_sof_config()

        self.logger.info(f"CoordinatorEngine initialized (dynamic planning: {enable_dynamic_planning})")
    
    def register_skill(self, skill: BaseSkillModule) -> None:
        """
        Register a skill for execution.

        Args:
            skill: Skill to register
        """
        self._registered_skills[skill.skill_name] = skill
        self._validator.register_skill(skill)

        # Register with dynamic planner if available
        if self._dynamic_planner:
            self._dynamic_planner.register_skill(skill)

        self.logger.info(f"Registered skill: {skill.skill_name}")
    
    def register_skills(self, skills: List[BaseSkillModule]) -> None:
        """
        Register multiple skills for execution.
        
        Args:
            skills: List of skills to register
        """
        for skill in skills:
            self.register_skill(skill)
    
    def execute_plan(self, plan: List[str], uif: SAM_UIF, use_dynamic_planning: bool = False) -> ExecutionReport:
        """
        Execute a validated plan with comprehensive error handling.

        Args:
            plan: List of skill names to execute in order
            uif: Universal Interface Format with execution context
            use_dynamic_planning: Whether to use dynamic planning to generate/modify the plan

        Returns:
            Comprehensive execution report
        """
        start_time = time.time()
        
        self.logger.info(f"Starting plan execution: {plan}")
        uif.add_log_entry(f"CoordinatorEngine starting plan execution: {plan}")
        uif.execution_plan = plan.copy()
        uif.start_time = datetime.now().isoformat()
        
        try:
            # Phase 0: Dynamic plan generation if requested
            if use_dynamic_planning and self._dynamic_planner:
                plan_result = self._dynamic_planner.create_plan(uif)
                if plan_result.plan:
                    plan = plan_result.plan
                    uif.add_log_entry(f"Dynamic plan generated: {plan} (confidence: {plan_result.confidence:.2f})")
                else:
                    uif.add_warning("Dynamic planning failed, using provided plan")

            # Phase 1: Validate the plan
            if self._config.enable_plan_validation:
                validation_report = self._validator.validate_plan(plan, uif)
                
                if not validation_report.is_valid:
                    return self._handle_invalid_plan(plan, uif, validation_report, start_time)
                
                # Use optimized plan if available
                execution_plan = validation_report.optimized_plan
                uif.add_log_entry(f"Plan validated successfully, executing optimized plan: {execution_plan}")
            else:
                validation_report = None
                execution_plan = plan
                uif.add_log_entry("Plan validation disabled, executing original plan")
            
            # Phase 2: Execute the plan
            execution_result = self._execute_validated_plan(execution_plan, uif)
            
            # Phase 3: Create execution report
            execution_time = time.time() - start_time
            uif.end_time = datetime.now().isoformat()
            
            report = ExecutionReport(
                result=execution_result,
                uif=uif,
                executed_skills=uif.executed_skills.copy(),
                failed_skills=self._get_failed_skills(uif),
                execution_time=execution_time,
                validation_report=validation_report,
                fallback_used=False
            )
            
            self._execution_history.append(report)
            self.logger.info(f"Plan execution completed: {execution_result} in {execution_time:.2f}s")
            
            return report
            
        except Exception as e:
            self.logger.exception("Unexpected error during plan execution")
            return self._handle_execution_error(plan, uif, str(e), start_time)
    
    def _execute_validated_plan(self, plan: List[str], uif: SAM_UIF) -> ExecutionResult:
        """
        Execute a validated plan step by step.
        
        Args:
            plan: Validated execution plan
            uif: Universal Interface Format
            
        Returns:
            Execution result
        """
        uif.status = UIFStatus.RUNNING
        failed_skills = []
        
        for i, skill_name in enumerate(plan):
            try:
                # Check timeout
                if self._is_execution_timeout(uif):
                    uif.add_warning("Execution timeout reached")
                    return ExecutionResult.TIMEOUT
                
                # Get the skill
                if skill_name not in self._registered_skills:
                    error_msg = f"Skill '{skill_name}' not found during execution"
                    uif.set_error(error_msg)
                    failed_skills.append(skill_name)
                    
                    if not self._config.continue_on_skill_failure:
                        return ExecutionResult.FAILURE
                    continue
                
                skill = self._registered_skills[skill_name]
                
                # Execute the skill with monitoring
                uif.add_log_entry(f"Executing skill {i+1}/{len(plan)}: {skill_name}")
                uif = skill.execute_with_monitoring(uif)
                
                # Check if skill failed
                if uif.status == UIFStatus.FAILURE:
                    failed_skills.append(skill_name)
                    uif.add_log_entry(f"Skill {skill_name} failed: {uif.error_details}")
                    
                    if not self._config.continue_on_skill_failure:
                        return ExecutionResult.FAILURE
                    
                    # Reset status to continue with next skill
                    uif.status = UIFStatus.RUNNING
                
            except Exception as e:
                error_msg = f"Unexpected error in skill {skill_name}: {str(e)}"
                self.logger.exception(error_msg)
                uif.add_log_entry(error_msg)
                failed_skills.append(skill_name)
                
                if not self._config.continue_on_skill_failure:
                    uif.set_error(error_msg)
                    return ExecutionResult.FAILURE
        
        # Determine final result
        if not failed_skills:
            uif.status = UIFStatus.SUCCESS
            return ExecutionResult.SUCCESS
        elif len(failed_skills) < len(plan):
            uif.add_warning(f"Partial execution: {len(failed_skills)} skills failed")
            return ExecutionResult.PARTIAL_SUCCESS
        else:
            uif.set_error("All skills in plan failed")
            return ExecutionResult.FAILURE
    
    def _handle_invalid_plan(self, plan: List[str], uif: SAM_UIF, 
                           validation_report: PlanValidationReport, start_time: float) -> ExecutionReport:
        """Handle execution of an invalid plan."""
        error_details = f"Plan validation failed: {validation_report.errors_count} errors"
        uif.set_error(error_details)
        
        self.logger.warning(f"Plan validation failed: {[issue.description for issue in validation_report.issues]}")
        
        # Try fallback if enabled
        if self._config.enable_fallback_plans:
            fallback_result = self._try_fallback_execution(uif)
            if fallback_result:
                return fallback_result
        
        execution_time = time.time() - start_time
        
        return ExecutionReport(
            result=ExecutionResult.FAILURE,
            uif=uif,
            executed_skills=[],
            failed_skills=plan,
            execution_time=execution_time,
            validation_report=validation_report,
            fallback_used=False,
            error_details=error_details
        )
    
    def _handle_execution_error(self, plan: List[str], uif: SAM_UIF, 
                              error_message: str, start_time: float) -> ExecutionReport:
        """Handle unexpected execution errors."""
        uif.set_error(f"Execution error: {error_message}")
        execution_time = time.time() - start_time
        
        # Try fallback if enabled
        if self._config.enable_fallback_plans:
            fallback_result = self._try_fallback_execution(uif)
            if fallback_result:
                return fallback_result
        
        return ExecutionReport(
            result=ExecutionResult.FAILURE,
            uif=uif,
            executed_skills=uif.executed_skills.copy(),
            failed_skills=self._get_failed_skills(uif),
            execution_time=execution_time,
            validation_report=None,
            fallback_used=False,
            error_details=error_message
        )
    
    def _try_fallback_execution(self, uif: SAM_UIF) -> Optional[ExecutionReport]:
        """
        Try fallback execution mechanisms.
        
        Returns:
            ExecutionReport if fallback succeeds, None otherwise
        """
        self.logger.info("Attempting fallback execution")
        uif.add_log_entry("Attempting fallback execution")
        
        # Try default safe plan
        default_plan = self._get_default_safe_plan()
        if default_plan:
            try:
                # Reset UIF status for fallback attempt
                uif.status = UIFStatus.PENDING
                uif.error_details = None
                
                validation_report = self._validator.validate_plan(default_plan, uif)
                if validation_report.is_valid:
                    result = self._execute_validated_plan(default_plan, uif)
                    
                    if result == ExecutionResult.SUCCESS:
                        return ExecutionReport(
                            result=ExecutionResult.SUCCESS,
                            uif=uif,
                            executed_skills=uif.executed_skills.copy(),
                            failed_skills=[],
                            execution_time=0.0,  # Will be updated by caller
                            validation_report=validation_report,
                            fallback_used=True
                        )
            except Exception as e:
                self.logger.error(f"Fallback execution failed: {e}")
        
        # Try fallback generator if available
        if self._fallback_generator:
            try:
                fallback_response = self._fallback_generator(uif.input_query)
                uif.final_response = fallback_response
                uif.status = UIFStatus.SUCCESS
                uif.add_log_entry("Used fallback generator for response")
                
                return ExecutionReport(
                    result=ExecutionResult.SUCCESS,
                    uif=uif,
                    executed_skills=["fallback_generator"],
                    failed_skills=[],
                    execution_time=0.0,
                    validation_report=None,
                    fallback_used=True
                )
            except Exception as e:
                self.logger.error(f"Fallback generator failed: {e}")
        
        return None
    
    def _get_default_safe_plan(self) -> List[str]:
        """
        Get a default safe execution plan.
        
        Returns:
            List of skill names for safe execution
        """
        # Default plan: memory retrieval + response generation
        safe_skills = []
        
        if "MemoryRetrievalSkill" in self._registered_skills:
            safe_skills.append("MemoryRetrievalSkill")
        
        if "ResponseGenerationSkill" in self._registered_skills:
            safe_skills.append("ResponseGenerationSkill")
        
        return safe_skills
    
    def _is_execution_timeout(self, uif: SAM_UIF) -> bool:
        """Check if execution has timed out."""
        if not uif.start_time:
            return False

        try:
            start_dt = datetime.fromisoformat(uif.start_time)
            elapsed = (datetime.now() - start_dt).total_seconds()
            return elapsed > self._config.max_execution_time
        except (ValueError, TypeError):
            # If we can't parse the timestamp, assume no timeout
            return False
    
    def _get_failed_skills(self, uif: SAM_UIF) -> List[str]:
        """Get list of skills that failed during execution."""
        # This is a simple implementation - could be enhanced to track failures more precisely
        planned_skills = set(uif.execution_plan)
        executed_skills = set(uif.executed_skills)
        return list(planned_skills - executed_skills)
    
    def get_execution_history(self) -> List[ExecutionReport]:
        """Get execution history."""
        return self._execution_history.copy()
    
    def get_registered_skills(self) -> List[str]:
        """Get list of registered skill names."""
        return list(self._registered_skills.keys())
    
    def clear_execution_history(self) -> None:
        """Clear execution history."""
        self._execution_history.clear()
        self.logger.debug("Execution history cleared")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary with execution statistics
        """
        if not self._execution_history:
            return {"total_executions": 0}
        
        total_executions = len(self._execution_history)
        successful_executions = sum(1 for report in self._execution_history 
                                  if report.result == ExecutionResult.SUCCESS)
        failed_executions = sum(1 for report in self._execution_history 
                              if report.result == ExecutionResult.FAILURE)
        fallback_used = sum(1 for report in self._execution_history if report.fallback_used)
        
        avg_execution_time = sum(report.execution_time for report in self._execution_history) / total_executions
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions,
            "fallback_usage_rate": fallback_used / total_executions,
            "average_execution_time": avg_execution_time
        }

    def execute_with_dynamic_planning(self, uif: SAM_UIF) -> ExecutionReport:
        """
        Execute with dynamic plan generation.

        Args:
            uif: Universal Interface Format with query context

        Returns:
            Execution report
        """
        # Use empty plan - will be generated dynamically
        return self.execute_plan([], uif, use_dynamic_planning=True)
