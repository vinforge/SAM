"""
SAM-TPV Integration Module
Phase 1B - Integration with SAM's Response Generation

Integrates TPV monitoring into SAM's secure response generation pipeline.
"""

import logging
import time
import requests
import json
from typing import Dict, Any, Optional, Callable, Generator
from dataclasses import dataclass

from .tpv_monitor import TPVMonitor, ReasoningTrace
from .tpv_controller import ReasoningController, ControlMode
from .tpv_trigger import TPVTrigger, UserProfile, TriggerResult

logger = logging.getLogger(__name__)

@dataclass
class TPVEnabledResponse:
    """Response with TPV monitoring data."""
    content: str
    tpv_trace: Optional[ReasoningTrace]
    tpv_enabled: bool
    trigger_result: Optional[TriggerResult]
    performance_metrics: Dict[str, Any]

class SAMTPVIntegration:
    """Integration layer between SAM and TPV system."""
    
    def __init__(self):
        """Initialize SAM-TPV integration."""
        self.tpv_monitor = TPVMonitor()
        self.reasoning_controller = ReasoningController(mode=ControlMode.PASSIVE)
        self.tpv_trigger = TPVTrigger()

        self.is_initialized = False
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        # Performance tracking
        self.total_requests = 0
        self.tpv_enabled_requests = 0
        self.average_overhead = 0.0

        # Phase 4: Deployment configuration
        self.deployment_config = self._load_deployment_config()
        self.user_tpv_enabled = self.deployment_config.get('tpv_enabled_by_default', False)

        logger.info("SAM-TPV Integration initialized")
        logger.info(f"TPV enabled by default: {self.user_tpv_enabled}")

    def _load_deployment_config(self) -> Dict[str, Any]:
        """Load deployment configuration from TPV config."""
        try:
            from .tpv_config import TPVConfig
            config = TPVConfig()
            return config.config.get('deployment_params', {})
        except Exception as e:
            logger.warning(f"Could not load deployment config: {e}")
            return {
                'tpv_enabled_by_default': False,
                'allow_user_override': True,
                'show_performance_warning': True,
                'enable_telemetry': True
            }
    
    def initialize(self) -> bool:
        """Initialize the TPV integration system.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if not self.tpv_monitor.initialize():
                logger.error("Failed to initialize TPV monitor")
                return False
            
            self.is_initialized = True
            logger.info("✅ SAM-TPV Integration initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"SAM-TPV Integration initialization failed: {e}")
            return False
    
    def generate_response_with_tpv(self,
                                  prompt: str,
                                  user_profile: Optional[UserProfile] = None,
                                  initial_confidence: Optional[float] = None,
                                  context: Optional[Dict[str, Any]] = None,
                                  ollama_params: Optional[Dict[str, Any]] = None) -> TPVEnabledResponse:
        """Generate response with TPV monitoring.
        
        This is the main integration point that wraps SAM's response generation
        with TPV monitoring capabilities.
        
        Args:
            prompt: The prompt to send to the model
            user_profile: User's profile for contextual triggering
            initial_confidence: Initial confidence score
            context: Additional context information
            ollama_params: Parameters for Ollama API call
            
        Returns:
            TPVEnabledResponse with content and monitoring data
        """
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Step 1: Check if user has TPV enabled
            if not self.user_tpv_enabled:
                logger.info("TPV disabled by user setting - using standard response")
                # Create a disabled trigger result
                from .tpv_trigger import TriggerResult
                disabled_trigger = TriggerResult(
                    should_activate=False,
                    trigger_type="user_disabled",
                    confidence=0.0,
                    reason="TPV disabled by user setting",
                    metadata={}
                )
                return self._generate_standard_response(
                    prompt, disabled_trigger, ollama_params, start_time
                )

            # Step 2: Evaluate TPV trigger
            trigger_result = self.tpv_trigger.should_activate_tpv(
                query=prompt,
                user_profile=user_profile,
                initial_confidence=initial_confidence,
                context=context
            )

            logger.info(f"TPV trigger evaluation: {trigger_result.should_activate} ({trigger_result.trigger_type})")

            if trigger_result.should_activate:
                # TPV-enabled response generation
                return self._generate_with_tpv_monitoring(
                    prompt, trigger_result, ollama_params, start_time
                )
            else:
                # Standard response generation without TPV
                return self._generate_standard_response(
                    prompt, trigger_result, ollama_params, start_time
                )
                
        except Exception as e:
            logger.error(f"Error in TPV-enabled response generation: {e}")
            # Fallback to standard generation
            return self._generate_fallback_response(prompt, str(e), start_time)
    
    def _generate_with_tpv_monitoring(self,
                                    prompt: str,
                                    trigger_result: TriggerResult,
                                    ollama_params: Optional[Dict[str, Any]],
                                    start_time: float) -> TPVEnabledResponse:
        """Generate response with active TPV monitoring.
        
        Args:
            prompt: The prompt to send to the model
            trigger_result: TPV trigger evaluation result
            ollama_params: Parameters for Ollama API call
            start_time: Request start time
            
        Returns:
            TPVEnabledResponse with TPV monitoring data
        """
        self.tpv_enabled_requests += 1
        
        # Start TPV monitoring
        query_id = self.tpv_monitor.start_monitoring(prompt)
        
        try:
            # Generate response with streaming simulation
            response_content = self._call_ollama_with_monitoring(
                prompt, query_id, ollama_params
            )
            
            # Stop monitoring and get trace
            tpv_trace = self.tpv_monitor.stop_monitoring(query_id)
            
            # Calculate performance metrics
            total_time = time.time() - start_time
            self._update_performance_metrics(total_time)
            
            performance_metrics = {
                'total_time': total_time,
                'tpv_overhead': total_time * 0.1,  # Estimated TPV overhead
                'tpv_steps': len(tpv_trace.steps) if tpv_trace else 0,
                'final_score': tpv_trace.current_score if tpv_trace else 0.0
            }
            
            logger.info(f"TPV-enabled response completed: {len(response_content)} chars, "
                       f"{performance_metrics['tpv_steps']} TPV steps, "
                       f"{performance_metrics['total_time']:.2f}s")
            
            return TPVEnabledResponse(
                content=response_content,
                tpv_trace=tpv_trace,
                tpv_enabled=True,
                trigger_result=trigger_result,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            logger.error(f"Error in TPV monitoring: {e}")
            # Clean up monitoring
            self.tpv_monitor.stop_monitoring(query_id)
            raise
    
    def _call_ollama_with_monitoring(self,
                                   prompt: str,
                                   query_id: str,
                                   ollama_params: Optional[Dict[str, Any]]) -> str:
        """Call Ollama API with TPV monitoring simulation.
        
        Since Ollama doesn't support streaming with hidden states, we simulate
        the token-by-token monitoring by making the call and then analyzing
        the response progressively.
        
        Args:
            prompt: The prompt to send to Ollama
            query_id: TPV monitoring query ID
            ollama_params: Parameters for Ollama API call
            
        Returns:
            Generated response content
        """
        # Default Ollama parameters
        default_params = {
            "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        # Merge with provided parameters
        if ollama_params:
            default_params.update(ollama_params)
        
        # Make Ollama API call
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=default_params,
            timeout=180  # Extended timeout for complex reasoning tasks
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}")
        
        response_data = response.json()
        full_response = response_data.get('response', '').strip()
        
        if not full_response:
            raise Exception("Empty response from Ollama")
        
        # Simulate progressive monitoring by analyzing response in chunks
        self._simulate_progressive_monitoring(full_response, query_id)
        
        return full_response
    
    def _simulate_progressive_monitoring(self, full_response: str, query_id: str):
        """Simulate progressive TPV monitoring of response generation.
        
        Args:
            full_response: Complete response from Ollama
            query_id: TPV monitoring query ID
        """
        words = full_response.split()
        chunk_size = max(5, len(words) // 10)  # Divide into ~10 chunks
        
        current_text = ""
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            current_text += " " + " ".join(chunk)
            current_text = current_text.strip()
            
            # Get TPV score for current text
            score = self.tpv_monitor.predict_progress(
                current_text, 
                query_id, 
                token_count=len(current_text.split())
            )
            
            # Check if should continue (passive mode always returns True)
            trace = self.tpv_monitor.get_trace(query_id)
            if trace:
                should_continue = self.reasoning_controller.should_continue(trace)
                if not should_continue:
                    logger.warning(f"Controller indicated stop for {query_id}")
                    break
            
            # Small delay to simulate real-time generation
            time.sleep(0.05)
    
    def _generate_standard_response(self,
                                  prompt: str,
                                  trigger_result: TriggerResult,
                                  ollama_params: Optional[Dict[str, Any]],
                                  start_time: float) -> TPVEnabledResponse:
        """Generate standard response without TPV monitoring.
        
        Args:
            prompt: The prompt to send to the model
            trigger_result: TPV trigger evaluation result
            ollama_params: Parameters for Ollama API call
            start_time: Request start time
            
        Returns:
            TPVEnabledResponse without TPV monitoring data
        """
        # Default Ollama parameters
        default_params = {
            "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        # Merge with provided parameters
        if ollama_params:
            default_params.update(ollama_params)
        
        # Make Ollama API call
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=default_params,
            timeout=180  # Extended timeout for complex reasoning tasks
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}")
        
        response_data = response.json()
        response_content = response_data.get('response', '').strip()
        
        if not response_content:
            raise Exception("Empty response from Ollama")
        
        # Calculate performance metrics
        total_time = time.time() - start_time
        performance_metrics = {
            'total_time': total_time,
            'tpv_overhead': 0.0,
            'tpv_steps': 0,
            'final_score': 0.0
        }
        
        logger.info(f"Standard response completed: {len(response_content)} chars, {total_time:.2f}s")
        
        return TPVEnabledResponse(
            content=response_content,
            tpv_trace=None,
            tpv_enabled=False,
            trigger_result=trigger_result,
            performance_metrics=performance_metrics
        )
    
    def _generate_fallback_response(self,
                                  prompt: str,
                                  error_message: str,
                                  start_time: float) -> TPVEnabledResponse:
        """Generate fallback response when TPV integration fails.
        
        Args:
            prompt: The original prompt
            error_message: Error that occurred
            start_time: Request start time
            
        Returns:
            TPVEnabledResponse with error information
        """
        fallback_content = f"I apologize, but I encountered an issue processing your request: {error_message}"
        
        total_time = time.time() - start_time
        performance_metrics = {
            'total_time': total_time,
            'tpv_overhead': 0.0,
            'tpv_steps': 0,
            'final_score': 0.0,
            'error': error_message
        }
        
        return TPVEnabledResponse(
            content=fallback_content,
            tpv_trace=None,
            tpv_enabled=False,
            trigger_result=None,
            performance_metrics=performance_metrics
        )
    
    def _update_performance_metrics(self, total_time: float):
        """Update running performance metrics.
        
        Args:
            total_time: Total time for this request
        """
        # Update average overhead (simple exponential moving average)
        alpha = 0.1
        estimated_overhead = total_time * 0.1  # Estimate 10% overhead for TPV
        self.average_overhead = (alpha * estimated_overhead + 
                               (1 - alpha) * self.average_overhead)
    
    def get_active_monitoring_sessions(self) -> Dict[str, Any]:
        """Get information about active TPV monitoring sessions.
        
        Returns:
            Dictionary of active session information
        """
        active_queries = self.tpv_monitor.get_active_queries()
        sessions = {}
        
        for query_id in active_queries:
            trace = self.tpv_monitor.get_trace(query_id)
            if trace:
                sessions[query_id] = {
                    'start_time': trace.start_time,
                    'steps': len(trace.steps),
                    'current_score': trace.current_score,
                    'progress_percentage': trace.get_progress_percentage(),
                    'is_active': trace.is_active
                }
        
        return sessions
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get TPV integration status and statistics.
        
        Returns:
            Status and statistics dictionary
        """
        return {
            'initialized': self.is_initialized,
            'total_requests': self.total_requests,
            'tpv_enabled_requests': self.tpv_enabled_requests,
            'tpv_activation_rate': (self.tpv_enabled_requests / self.total_requests
                                  if self.total_requests > 0 else 0.0),
            'average_overhead': self.average_overhead,
            'active_sessions': len(self.get_active_monitoring_sessions()),
            'user_tpv_enabled': self.user_tpv_enabled,
            'deployment_config': self.deployment_config,
            'components': {
                'monitor': self.tpv_monitor.get_status(),
                'controller': self.reasoning_controller.get_status(),
                'trigger': self.tpv_trigger.get_status()
            }
        }

    # Phase 4: User Control Methods for Production Deployment

    def set_user_tpv_enabled(self, enabled: bool) -> bool:
        """Enable or disable TPV for the user.

        Args:
            enabled: Whether to enable TPV for this user

        Returns:
            True if setting was successful
        """
        if not self.deployment_config.get('allow_user_override', True):
            logger.warning("User TPV override not allowed by deployment config")
            return False

        self.user_tpv_enabled = enabled
        logger.info(f"User TPV setting changed to: {enabled}")

        # Log telemetry if enabled
        if self.deployment_config.get('enable_telemetry', True):
            self._log_user_setting_change(enabled)

        return True

    def get_user_tpv_enabled(self) -> bool:
        """Get current user TPV setting."""
        return self.user_tpv_enabled

    def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment configuration and user settings."""
        return {
            'user_tpv_enabled': self.user_tpv_enabled,
            'default_enabled': self.deployment_config.get('tpv_enabled_by_default', False),
            'allow_user_override': self.deployment_config.get('allow_user_override', True),
            'show_performance_warning': self.deployment_config.get('show_performance_warning', True),
            'telemetry_enabled': self.deployment_config.get('enable_telemetry', True),
            'optimizations_enabled': self.deployment_config.get('enable_optimizations', True)
        }

    def _log_user_setting_change(self, enabled: bool):
        """Log user setting changes for telemetry."""
        try:
            import time
            log_entry = {
                'timestamp': time.time(),
                'action': 'user_tpv_setting_change',
                'enabled': enabled,
                'user_id': 'anonymous'  # Anonymous telemetry
            }
            logger.info(f"TPV Setting Change: {log_entry}")
        except Exception as e:
            logger.warning(f"Could not log setting change: {e}")

# Global integration instance
sam_tpv_integration = SAMTPVIntegration()
