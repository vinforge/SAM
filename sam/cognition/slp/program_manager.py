"""
Program Manager
==============

Central orchestrator for the SLP system. Manages program capture, retrieval,
execution, and lifecycle management.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .latent_program import LatentProgram, ExecutionResult, ValidationResult
from .program_signature import ProgramSignature, generate_signature
from .latent_program_store import LatentProgramStore
from .program_executor import ProgramExecutor

# Import validator with fallback
try:
    from .program_validator import ProgramValidator
except ImportError:
    logger.warning("ProgramValidator not available, using basic validation")
    ProgramValidator = None

logger = logging.getLogger(__name__)


class ProgramManager:
    """
    Central orchestrator for the SLP system.
    
    Handles program lifecycle from capture through execution and evolution.
    """
    
    def __init__(self, store: Optional[LatentProgramStore] = None,
                 executor: Optional[ProgramExecutor] = None,
                 validator: Optional['ProgramValidator'] = None):
        """Initialize the program manager."""
        self.store = store or LatentProgramStore()
        self.executor = executor or ProgramExecutor()
        self.validator = validator or (ProgramValidator() if ProgramValidator else None)
        
        # Configuration
        self.similarity_threshold = 0.8
        self.execution_threshold = 0.7
        self.quality_threshold = 0.6
        self.max_programs_per_signature = 5
        
        logger.info("Program manager initialized")
    
    def find_matching_program(self, query: str, context: Dict[str, Any],
                            user_profile: Optional[str] = None) -> Tuple[Optional[LatentProgram], float]:
        """
        Find the best matching program for a query.

        Args:
            query: User's query
            context: Context information
            user_profile: Optional user profile

        Returns:
            Tuple of (best matching program or None, confidence score)
        """
        try:
            # Generate signature for the query
            signature = generate_signature(query, context, user_profile)

            # Find candidate programs
            candidates = self.find_candidate_programs(signature)

            if not candidates:
                logger.debug("No candidate programs found")
                return None, 0.0

            # Score and rank candidates
            best_match = self.score_and_rank_candidates(candidates, signature, query, context)

            if best_match:
                # Get the match confidence score
                match_confidence = getattr(best_match, 'match_score', best_match.confidence_score)

                if match_confidence >= self.execution_threshold:
                    logger.info(f"Found matching program: {best_match.id} (confidence: {match_confidence:.2f})")
                    return best_match, match_confidence
                else:
                    logger.debug(f"Best match confidence {match_confidence:.2f} below threshold {self.execution_threshold}")
                    return None, match_confidence

            return None, 0.0

        except Exception as e:
            logger.error(f"Error finding matching program: {e}")
            return None, 0.0
    
    def find_candidate_programs(self, signature: ProgramSignature) -> List[LatentProgram]:
        """Find candidate programs based on signature similarity."""
        try:
            # First try exact signature hash match
            exact_matches = self.store.get_programs_by_signature_hash(signature.signature_hash)
            
            if exact_matches:
                logger.debug(f"Found {len(exact_matches)} exact signature matches")
                return exact_matches
            
            # Fall back to similarity search
            similar_programs = self.store.find_similar_programs(
                signature, 
                self.similarity_threshold,
                self.max_programs_per_signature
            )
            
            logger.debug(f"Found {len(similar_programs)} similar programs")
            return similar_programs
            
        except Exception as e:
            logger.error(f"Error finding candidate programs: {e}")
            return []
    
    def score_and_rank_candidates(self, candidates: List[LatentProgram],
                                signature: ProgramSignature, query: str,
                                context: Dict[str, Any]) -> Optional[LatentProgram]:
        """Score and rank candidate programs."""
        try:
            if not candidates:
                return None
            
            scored_candidates = []
            
            for program in candidates:
                # Calculate composite score
                score = self._calculate_program_score(program, signature, query, context)
                scored_candidates.append((program, score))
            
            # Sort by score (descending)
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Return the best candidate
            best_program, best_score = scored_candidates[0]
            best_program.match_score = best_score  # Add score for reference
            
            return best_program
            
        except Exception as e:
            logger.error(f"Error scoring candidates: {e}")
            return candidates[0] if candidates else None
    
    def _calculate_program_score(self, program: LatentProgram, signature: ProgramSignature,
                               query: str, context: Dict[str, Any]) -> float:
        """Calculate a composite score for program matching."""
        try:
            factors = []
            
            # Signature similarity (if available)
            if hasattr(program, 'similarity_score'):
                factors.append(('similarity', program.similarity_score, 0.4))
            
            # Program confidence
            factors.append(('confidence', program.confidence_score, 0.3))
            
            # Success rate
            factors.append(('success_rate', program.success_rate, 0.2))
            
            # Usage frequency (normalized)
            usage_score = min(1.0, program.usage_count / 10.0)
            factors.append(('usage', usage_score, 0.1))
            
            # Calculate weighted score
            total_score = sum(score * weight for _, score, weight in factors)
            
            return max(0.0, min(1.0, total_score))
            
        except Exception as e:
            logger.warning(f"Error calculating program score: {e}")
            return program.confidence_score
    
    def execute_program(self, program: LatentProgram, query: str,
                       context: Dict[str, Any]) -> ExecutionResult:
        """Execute a latent program."""
        try:
            logger.info(f"Executing program {program.id}")
            
            # Execute with monitoring
            result = self.executor.execute_with_monitoring(program, query, context)
            
            # Update program performance metrics
            self.store.update_program_performance(
                program.id,
                result.execution_time_ms,
                result.token_count,
                result.success,
                result.quality_score
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Program execution failed: {e}")
            return ExecutionResult(
                response="",
                quality_score=0.0,
                execution_time_ms=0.0,
                program_used=program.id,
                success=False,
                error_message=str(e)
            )
    
    def consider_program_capture(self, query: str, context: Dict[str, Any],
                               result: Dict[str, Any], user_profile: Optional[str] = None) -> bool:
        """Consider capturing a new program from a successful interaction."""
        try:
            # Check if this was a high-quality response
            if not self._should_capture_program(result):
                logger.debug("Response quality insufficient for program capture")
                return False
            
            # Generate signature
            signature = generate_signature(query, context, user_profile)
            
            # Check if we already have similar programs
            existing_programs = self.store.find_similar_programs(signature, 0.9, 3)
            
            if len(existing_programs) >= self.max_programs_per_signature:
                logger.debug("Maximum programs per signature reached")
                return False
            
            # Create new program
            program = self._create_program_from_interaction(
                signature, query, context, result, user_profile
            )
            
            # Validate program safety if validator is available
            if self.validator:
                validation = self.validator.validate_program_safety(program)
                if not validation.is_safe:
                    logger.warning(f"Program failed safety validation: {validation.warnings}")
                    return False
            else:
                logger.debug("Program validator not available, skipping safety validation")
            
            # Store the program
            success = self.store.store_program(program)
            
            if success:
                logger.info(f"Captured new program: {program.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error considering program capture: {e}")
            return False
    
    def _should_capture_program(self, result: Dict[str, Any]) -> bool:
        """Determine if a result is worth capturing as a program."""
        # Check quality indicators
        quality_score = result.get('quality_score', 0.0)
        user_feedback = result.get('user_feedback', 0.0)
        meta_confidence = result.get('meta_confidence', 0.0)
        
        # Require minimum quality thresholds
        if quality_score < self.quality_threshold:
            return False
        
        if user_feedback > 0 and user_feedback < 3.0:  # Negative feedback
            return False
        
        if meta_confidence > 0 and meta_confidence < 0.6:
            return False
        
        return True
    
    def _create_program_from_interaction(self, signature: ProgramSignature,
                                       query: str, context: Dict[str, Any],
                                       result: Dict[str, Any],
                                       user_profile: Optional[str]) -> LatentProgram:
        """Create a new latent program from a successful interaction."""
        
        # Extract configuration that led to success
        tpv_config = result.get('tpv_config', {})
        prompt_template = result.get('prompt_template', '')
        reasoning_trace = result.get('reasoning_trace', {})
        
        # Create context requirements
        context_requirements = {
            'document_types': signature.document_types,
            'content_domains': signature.content_domains,
            'min_context_size': len(str(context))
        }
        
        # Create execution constraints
        execution_constraints = {
            'max_tokens': result.get('token_count', 1000),
            'timeout_seconds': 30
        }
        
        # Create the program
        program = LatentProgram(
            signature=signature.to_dict(),
            reasoning_trace=reasoning_trace,
            tpv_config=tpv_config,
            active_profile=user_profile or 'default',
            prompt_template_used=prompt_template,
            context_requirements=context_requirements,
            execution_constraints=execution_constraints,
            avg_latency_ms=result.get('execution_time_ms', 0.0),
            avg_token_count=result.get('token_count', 0),
            user_feedback_score=result.get('user_feedback', 0.0)
        )
        
        return program
    
    def record_user_feedback(self, program_id: str, feedback_score: float) -> bool:
        """Record user feedback for a program."""
        try:
            return self.store.update_program_performance(
                program_id, 0, 0, True, None, feedback_score
            )
        except Exception as e:
            logger.error(f"Error recording user feedback: {e}")
            return False
    
    def retire_poor_performers(self, min_usage: int = 5, 
                             success_threshold: float = 0.3) -> int:
        """Retire programs that perform poorly."""
        try:
            programs = self.store.get_all_programs()
            retired_count = 0
            
            for program in programs:
                if (program.usage_count >= min_usage and 
                    program.success_rate < success_threshold):
                    
                    if self.store.retire_program(program.id):
                        retired_count += 1
                        logger.info(f"Retired poor performing program: {program.id}")
            
            return retired_count
            
        except Exception as e:
            logger.error(f"Error retiring poor performers: {e}")
            return 0
    
    def get_program_statistics(self) -> Dict[str, Any]:
        """Get comprehensive program statistics."""
        try:
            stats = self.store.get_program_statistics()
            
            # Add additional computed statistics
            programs = self.store.get_all_programs()
            
            if programs:
                # Performance distribution
                confidence_scores = [p.confidence_score for p in programs]
                stats['confidence_distribution'] = {
                    'min': min(confidence_scores),
                    'max': max(confidence_scores),
                    'avg': sum(confidence_scores) / len(confidence_scores)
                }
                
                # Usage distribution
                usage_counts = [p.usage_count for p in programs]
                stats['usage_distribution'] = {
                    'total': sum(usage_counts),
                    'avg': sum(usage_counts) / len(usage_counts),
                    'max': max(usage_counts)
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting program statistics: {e}")
            return {}
    
    def cleanup_old_programs(self, days_unused: int = 30) -> int:
        """Clean up old, unused programs."""
        try:
            return self.store.cleanup_old_programs(days_unused)
        except Exception as e:
            logger.error(f"Error cleaning up old programs: {e}")
            return 0
