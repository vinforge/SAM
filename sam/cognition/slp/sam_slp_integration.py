"""
SAM-SLP Integration Layer
========================

Integration layer that connects the SLP (Scalable Latent Program) system
with SAM's existing reasoning pipeline for seamless program capture and execution.
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from .program_manager import ProgramManager
from .latent_program import LatentProgram, ExecutionResult
from .program_executor import ProgramExecutor

logger = logging.getLogger(__name__)


class SAMSLPIntegration:
    """
    Integration layer between SAM and the SLP system.
    
    Provides seamless integration for program capture, retrieval, and execution
    within SAM's existing reasoning pipeline.
    """
    
    def __init__(self, tpv_integration=None):
        """Initialize the SAM-SLP integration."""
        self.program_manager = ProgramManager()
        self.tpv_integration = tpv_integration
        self.enabled = True
        
        # Performance tracking
        self.total_queries = 0
        self.program_hits = 0
        self.program_captures = 0
        self.total_time_saved_ms = 0.0
        
        logger.info("SAM-SLP integration initialized")
    
    def generate_response_with_slp(self, query: str, context: Dict[str, Any],
                                  user_profile: Optional[str] = None,
                                  fallback_generator=None) -> Dict[str, Any]:
        """
        Generate response with SLP program matching and capture.
        
        This is the main integration point that wraps SAM's response generation
        with SLP capabilities.
        
        Args:
            query: User's query
            context: Context information including documents, session data, etc.
            user_profile: Optional user profile identifier
            fallback_generator: Function to call for standard response generation
            
        Returns:
            Dictionary with response and SLP metadata
        """
        start_time = time.time()
        self.total_queries += 1
        
        try:
            if not self.enabled:
                return self._generate_standard_response(query, context, fallback_generator, start_time)
            
            # Phase 1: Try to find matching program
            matching_program, confidence = self.program_manager.find_matching_program(
                query, context, user_profile
            )

            if matching_program and confidence >= self.program_manager.execution_threshold:
                # Execute using latent program
                return self._execute_with_program(
                    matching_program, query, context, fallback_generator, start_time, confidence
                )
            else:
                # Generate standard response and consider program capture
                return self._generate_and_capture(
                    query, context, user_profile, fallback_generator, start_time, confidence
                )
                
        except Exception as e:
            logger.error(f"Error in SLP-enabled response generation: {e}")
            return self._generate_fallback_response(query, context, fallback_generator, str(e), start_time)
    
    def _execute_with_program(self, program: LatentProgram, query: str,
                            context: Dict[str, Any], fallback_generator,
                            start_time: float, confidence: float = 0.0) -> Dict[str, Any]:
        """Execute response using a latent program."""
        try:
            logger.info(f"🚀 Executing with latent program: {program.id}")
            
            # Create program executor with TPV integration
            executor = ProgramExecutor(
                tpv_controller=self.tpv_integration,
                reasoning_engine=None  # Will use fallback_generator
            )
            
            # Execute the program
            execution_result = executor.execute_with_monitoring(program, query, context)
            
            if execution_result.success and execution_result.quality_score > 0.6:
                # Successful program execution
                self.program_hits += 1
                self.total_time_saved_ms += max(0, 2000 - execution_result.execution_time_ms)
                
                # Update program performance
                self.program_manager.store.update_program_performance(
                    program.id,
                    execution_result.execution_time_ms,
                    execution_result.token_count,
                    True,
                    execution_result.quality_score
                )
                
                response_time = (time.time() - start_time) * 1000
                
                return {
                    'response': execution_result.response,
                    'slp_metadata': {
                        'used_program': True,
                        'program_id': program.id,
                        'program_confidence': program.confidence_score,
                        'signature_match_confidence': confidence,
                        'execution_time_ms': execution_result.execution_time_ms,
                        'quality_score': execution_result.quality_score,
                        'token_count': execution_result.token_count,
                        'total_response_time_ms': response_time,
                        'program_usage_count': program.usage_count + 1
                    },
                    'sources': context.get('sources', []),
                    'reasoning_trace': program.reasoning_trace
                }
            else:
                # Program execution failed or low quality, fall back
                logger.warning(f"Program execution failed or low quality, falling back to standard generation")
                return self._generate_standard_response(query, context, fallback_generator, start_time)
                
        except Exception as e:
            logger.error(f"Error executing program {program.id}: {e}")
            return self._generate_standard_response(query, context, fallback_generator, start_time)
    
    def _generate_and_capture(self, query: str, context: Dict[str, Any],
                            user_profile: Optional[str], fallback_generator,
                            start_time: float, confidence: float = 0.0) -> Dict[str, Any]:
        """Generate standard response and consider program capture."""
        try:
            # Generate standard response
            result = self._generate_standard_response(query, context, fallback_generator, start_time)
            
            # Consider capturing this interaction as a program
            if result.get('response') and self._should_capture_interaction(result):
                capture_success = self.program_manager.consider_program_capture(
                    query, context, result, user_profile
                )
                
                if capture_success:
                    self.program_captures += 1
                    logger.info(f"📚 Captured new latent program from interaction")
                    
                    # Add capture metadata
                    if 'slp_metadata' not in result:
                        result['slp_metadata'] = {}
                    result['slp_metadata']['captured_program'] = True
                    result['slp_metadata']['total_programs'] = len(self.program_manager.store.get_all_programs())
                    result['slp_metadata']['signature_match_confidence'] = confidence
            
            return result
            
        except Exception as e:
            logger.error(f"Error in generate and capture: {e}")
            return self._generate_fallback_response(query, context, fallback_generator, str(e), start_time)
    
    def _generate_standard_response(self, query: str, context: Dict[str, Any],
                                  fallback_generator, start_time: float) -> Dict[str, Any]:
        """Generate response using standard SAM pipeline."""
        try:
            if fallback_generator:
                # Use provided fallback generator
                if callable(fallback_generator):
                    response = fallback_generator(query, context)
                else:
                    response = str(fallback_generator)
            else:
                # Basic fallback response
                response = f"I understand you're asking about: {query[:100]}..."
            
            response_time = (time.time() - start_time) * 1000
            
            # Estimate quality and other metrics for potential capture
            quality_score = self._estimate_response_quality(response, query, context)
            token_count = len(response.split()) * 1.3  # Rough token estimation
            
            return {
                'response': response,
                'slp_metadata': {
                    'used_program': False,
                    'response_time_ms': response_time,
                    'quality_score': quality_score,
                    'token_count': int(token_count)
                },
                'sources': context.get('sources', []),
                'quality_score': quality_score,
                'execution_time_ms': response_time,
                'token_count': int(token_count)
            }
            
        except Exception as e:
            logger.error(f"Error in standard response generation: {e}")
            return self._generate_fallback_response(query, context, fallback_generator, str(e), start_time)
    
    def _generate_fallback_response(self, query: str, context: Dict[str, Any],
                                  fallback_generator, error_msg: str, start_time: float) -> Dict[str, Any]:
        """Generate fallback response when errors occur."""
        response_time = (time.time() - start_time) * 1000
        
        return {
            'response': f"I apologize, but I encountered an issue processing your request. Error: {error_msg}",
            'slp_metadata': {
                'used_program': False,
                'error': error_msg,
                'response_time_ms': response_time
            },
            'sources': [],
            'quality_score': 0.1,
            'execution_time_ms': response_time,
            'token_count': 20
        }
    
    def _should_capture_interaction(self, result: Dict[str, Any]) -> bool:
        """Determine if an interaction should be captured as a program."""
        try:
            # Check quality thresholds
            quality_score = result.get('quality_score', 0.0)
            if quality_score < 0.6:
                return False
            
            # Check response length (not too short, not too long)
            response = result.get('response', '')
            if len(response) < 50 or len(response) > 3000:
                return False
            
            # Check if response seems coherent
            if not response or response.count('.') < 1:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error in capture decision: {e}")
            return False
    
    def _estimate_response_quality(self, response: str, query: str, context: Dict[str, Any]) -> float:
        """Estimate the quality of a response."""
        try:
            quality_factors = []
            
            # Length factor
            length = len(response)
            if 100 <= length <= 1500:
                length_factor = 1.0
            elif length < 100:
                length_factor = length / 100.0
            else:
                length_factor = max(0.5, 1500 / length)
            quality_factors.append(length_factor)
            
            # Relevance factor (keyword overlap)
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            relevance = len(query_words & response_words) / max(len(query_words), 1)
            quality_factors.append(min(1.0, relevance * 2))
            
            # Structure factor (sentences and coherence)
            sentences = [s.strip() for s in response.split('.') if s.strip()]
            structure_factor = min(1.0, len(sentences) / 5.0)
            quality_factors.append(structure_factor)
            
            # Context utilization factor
            if context.get('sources'):
                context_factor = 0.8  # Assume good context utilization
            else:
                context_factor = 0.6  # No context available
            quality_factors.append(context_factor)
            
            # Calculate weighted average
            weights = [0.3, 0.3, 0.2, 0.2]
            quality_score = sum(factor * weight for factor, weight in zip(quality_factors, weights))
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.warning(f"Error estimating quality: {e}")
            return 0.5
    
    def record_user_feedback(self, program_id: str, feedback_score: float) -> bool:
        """Record user feedback for a program."""
        try:
            return self.program_manager.record_user_feedback(program_id, feedback_score)
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return False
    
    def get_slp_statistics(self) -> Dict[str, Any]:
        """Get comprehensive SLP system statistics."""
        try:
            program_stats = self.program_manager.get_program_statistics()
            
            # Add integration-specific statistics
            hit_rate = (self.program_hits / max(self.total_queries, 1)) * 100
            capture_rate = (self.program_captures / max(self.total_queries, 1)) * 100
            avg_time_saved = self.total_time_saved_ms / max(self.program_hits, 1)
            
            integration_stats = {
                'total_queries': self.total_queries,
                'program_hits': self.program_hits,
                'program_captures': self.program_captures,
                'hit_rate_percent': hit_rate,
                'capture_rate_percent': capture_rate,
                'total_time_saved_ms': self.total_time_saved_ms,
                'avg_time_saved_per_hit_ms': avg_time_saved,
                'enabled': self.enabled
            }
            
            return {
                'integration_stats': integration_stats,
                'program_stats': program_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting SLP statistics: {e}")
            return {}
    
    def enable_slp(self):
        """Enable SLP system."""
        self.enabled = True
        logger.info("SLP system enabled")
    
    def disable_slp(self):
        """Disable SLP system."""
        self.enabled = False
        logger.info("SLP system disabled")
    
    def cleanup_old_programs(self, days_unused: int = 30) -> int:
        """Clean up old, unused programs."""
        try:
            return self.program_manager.cleanup_old_programs(days_unused)
        except Exception as e:
            logger.error(f"Error cleaning up programs: {e}")
            return 0


# Global SLP integration instance
_slp_integration = None

def get_slp_integration(tpv_integration=None) -> SAMSLPIntegration:
    """Get or create the global SLP integration instance."""
    global _slp_integration
    
    if _slp_integration is None:
        _slp_integration = SAMSLPIntegration(tpv_integration)
    
    return _slp_integration

def initialize_slp_integration(tpv_integration=None) -> SAMSLPIntegration:
    """Initialize the SLP integration system."""
    global _slp_integration
    
    try:
        _slp_integration = SAMSLPIntegration(tpv_integration)
        logger.info("SLP integration initialized successfully")
        return _slp_integration
    except Exception as e:
        logger.error(f"Failed to initialize SLP integration: {e}")
        return None
