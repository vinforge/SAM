"""
TPV Reasoning Controller Module
Phase 1 - Active Monitoring & Passive Control Integration

Passive reasoning controller that observes but does not interrupt the reasoning process.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from .tpv_monitor import ReasoningTrace, ReasoningStep

logger = logging.getLogger(__name__)

class ControlMode(Enum):
    """Control modes for the reasoning controller."""
    PASSIVE = "passive"      # Observe only, never interrupt
    ACTIVE = "active"        # Can interrupt and redirect reasoning
    DISABLED = "disabled"    # No control or monitoring

class ControlDecision(Enum):
    """Possible control decisions."""
    CONTINUE = "continue"           # Continue normal processing
    INTERRUPT = "interrupt"         # Stop current reasoning
    REDIRECT = "redirect"           # Change reasoning direction
    ENHANCE = "enhance"             # Add additional context
    COMPLETE = "complete"           # Force completion

@dataclass
class ControlAction:
    """Represents a control action taken by the reasoning controller."""
    decision: ControlDecision
    reason: str
    confidence: float
    timestamp: float
    metadata: Dict[str, Any]

class ReasoningController:
    """Passive reasoning controller for TPV-enabled SAM responses.
    
    In Phase 1, this controller operates in PASSIVE mode, meaning it observes
    the reasoning process but never interrupts it. This establishes the
    architectural foundation for active control in future phases.
    """
    
    def __init__(self, mode: ControlMode = ControlMode.PASSIVE):
        """Initialize the reasoning controller.
        
        Args:
            mode: Control mode (PASSIVE for Phase 1)
        """
        self.mode = mode
        self.control_history: List[ControlAction] = []
        
        # Control thresholds (not used in passive mode)
        self.min_confidence_threshold = 0.3
        self.max_reasoning_time = 120.0  # seconds
        self.max_tokens = 1000
        self.min_progress_rate = 0.01  # minimum progress per step
        
        # Passive mode statistics
        self.total_decisions = 0
        self.continue_decisions = 0
        
        logger.info(f"Reasoning Controller initialized in {mode.value} mode")
    
    def should_continue(self, trace: ReasoningTrace) -> bool:
        """Determine if reasoning should continue.
        
        This is the core method called during the generation loop.
        In Phase 1 (PASSIVE mode), this always returns True unless
        hard limits are reached.
        
        Args:
            trace: Current reasoning trace
            
        Returns:
            True if reasoning should continue, False otherwise
        """
        try:
            self.total_decisions += 1
            
            if self.mode == ControlMode.DISABLED:
                return True
            
            # Check hard limits that apply regardless of mode
            if self._check_hard_limits(trace):
                action = ControlAction(
                    decision=ControlDecision.INTERRUPT,
                    reason="Hard limit reached",
                    confidence=1.0,
                    timestamp=time.time(),
                    metadata=self._get_trace_metadata(trace)
                )
                self.control_history.append(action)
                logger.warning(f"Hard limit reached for query {trace.query_id}, stopping reasoning")
                return False
            
            if self.mode == ControlMode.PASSIVE:
                # In passive mode, we observe but never interrupt
                decision = self._make_passive_decision(trace)
                
                action = ControlAction(
                    decision=decision,
                    reason="Passive observation",
                    confidence=0.5,
                    timestamp=time.time(),
                    metadata=self._get_trace_metadata(trace)
                )
                self.control_history.append(action)
                
                self.continue_decisions += 1
                return True  # Always continue in passive mode
            
            elif self.mode == ControlMode.ACTIVE:
                # Active mode logic (for future phases)
                return self._make_active_decision(trace)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in should_continue for {trace.query_id}: {e}")
            return True  # Default to continue on error
    
    def _check_hard_limits(self, trace: ReasoningTrace) -> bool:
        """Check if any hard limits have been exceeded.
        
        Args:
            trace: Current reasoning trace
            
        Returns:
            True if hard limits exceeded, False otherwise
        """
        # Check maximum reasoning time
        elapsed_time = time.time() - trace.start_time
        if elapsed_time > self.max_reasoning_time:
            logger.warning(f"Maximum reasoning time exceeded: {elapsed_time:.1f}s")
            return True
        
        # Check maximum tokens
        if trace.total_tokens > self.max_tokens:
            logger.warning(f"Maximum token count exceeded: {trace.total_tokens}")
            return True
        
        # Check for stalled reasoning (no progress)
        if len(trace.steps) > 10:
            recent_steps = trace.steps[-5:]
            if all(step.score < 0.1 for step in recent_steps):
                logger.warning("Reasoning appears stalled (very low scores)")
                return True
        
        return False
    
    def _make_passive_decision(self, trace: ReasoningTrace) -> ControlDecision:
        """Make a passive observation decision.
        
        In passive mode, we analyze the reasoning but don't act on it.
        This builds the foundation for active control in future phases.
        
        Args:
            trace: Current reasoning trace
            
        Returns:
            Control decision (always CONTINUE in passive mode)
        """
        # Analyze reasoning quality for logging/learning purposes
        if trace.steps:
            latest_step = trace.steps[-1]
            
            # Log interesting patterns for future active control development
            if latest_step.confidence < self.min_confidence_threshold:
                logger.debug(f"Low confidence detected: {latest_step.confidence:.3f}")
            
            if len(trace.steps) > 5:
                progress_rate = self._calculate_progress_rate(trace)
                if progress_rate < self.min_progress_rate:
                    logger.debug(f"Slow progress detected: {progress_rate:.4f}")
            
            # Check for reasoning quality patterns
            if latest_step.reasoning_quality > 0.8:
                logger.debug(f"High quality reasoning detected: {latest_step.reasoning_quality:.3f}")
        
        return ControlDecision.CONTINUE
    
    def _make_active_decision(self, trace: ReasoningTrace) -> bool:
        """Make an active control decision based on reasoning quality.

        Phase 2: Active Control Logic
        Implements completion threshold, plateau detection, and token limits.

        Args:
            trace: Current reasoning trace

        Returns:
            True if reasoning should continue, False otherwise
        """
        try:
            # Load control parameters from config
            from .tpv_config import TPVConfig
            config = TPVConfig()
            control_params = config.control_params

            # Check minimum steps requirement
            if len(trace.steps) < control_params.min_steps:
                logger.debug(f"Below minimum steps ({len(trace.steps)} < {control_params.min_steps})")
                return True

            # Hard Stop: Maximum token limit
            if trace.total_tokens >= control_params.max_tokens:
                reason = f"Maximum token limit reached ({trace.total_tokens} >= {control_params.max_tokens})"
                logger.info(f"🛑 Active Control: {reason}")
                self._record_control_action(trace, "HALT", reason)
                return False

            # Completion Stop: High reasoning quality achieved
            if trace.current_score >= control_params.completion_threshold:
                reason = f"Completion threshold reached (score: {trace.current_score:.3f} >= {control_params.completion_threshold})"
                logger.info(f"✅ Active Control: {reason}")
                self._record_control_action(trace, "COMPLETE", reason)
                return False

            # Plateau Stop: Reasoning has stagnated
            if len(trace.steps) >= control_params.plateau_patience:
                recent_steps = trace.steps[-control_params.plateau_patience:]
                score_changes = []

                for i in range(1, len(recent_steps)):
                    score_change = abs(recent_steps[i].score - recent_steps[i-1].score)
                    score_changes.append(score_change)

                if score_changes:
                    avg_change = sum(score_changes) / len(score_changes)

                    if avg_change < control_params.plateau_threshold:
                        reason = f"Reasoning plateau detected (avg change: {avg_change:.4f} < {control_params.plateau_threshold})"
                        logger.info(f"📊 Active Control: {reason}")
                        self._record_control_action(trace, "PLATEAU", reason)
                        return False

            # Continue reasoning
            logger.debug(f"Active Control: Continue (score: {trace.current_score:.3f}, tokens: {trace.total_tokens})")
            return True

        except Exception as e:
            logger.error(f"Error in active control decision: {e}")
            return True  # Default to continue on error

    def _record_control_action(self, trace: ReasoningTrace, action: str, reason: str):
        """Record a control action for transparency and debugging.

        Args:
            trace: Current reasoning trace
            action: Action taken (HALT, COMPLETE, PLATEAU)
            reason: Reason for the action
        """
        # Map action string to ControlDecision enum
        decision_map = {
            'HALT': ControlDecision.INTERRUPT,
            'COMPLETE': ControlDecision.INTERRUPT,
            'PLATEAU': ControlDecision.INTERRUPT,
            'CONTINUE': ControlDecision.CONTINUE
        }

        decision = decision_map.get(action, ControlDecision.INTERRUPT)

        control_action = ControlAction(
            decision=decision,
            reason=reason,
            confidence=trace.current_score if trace else 0.0,
            timestamp=time.time(),
            metadata=self._get_trace_metadata(trace)
        )

        # Store action type in metadata for UI display
        control_action.metadata['action_type'] = action

        self.control_history.append(control_action)

        # Keep history manageable
        if len(self.control_history) > 100:
            self.control_history = self.control_history[-50:]
    
    def _calculate_progress_rate(self, trace: ReasoningTrace) -> float:
        """Calculate the rate of reasoning progress.
        
        Args:
            trace: Current reasoning trace
            
        Returns:
            Progress rate (score change per step)
        """
        if len(trace.steps) < 2:
            return 0.0
        
        recent_steps = trace.steps[-5:]  # Look at last 5 steps
        if len(recent_steps) < 2:
            return 0.0
        
        score_change = recent_steps[-1].score - recent_steps[0].score
        step_count = len(recent_steps) - 1
        
        return score_change / step_count if step_count > 0 else 0.0
    
    def _get_trace_metadata(self, trace: ReasoningTrace) -> Dict[str, Any]:
        """Extract metadata from reasoning trace for control decisions.
        
        Args:
            trace: Current reasoning trace
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'query_id': trace.query_id,
            'step_count': len(trace.steps),
            'total_tokens': trace.total_tokens,
            'current_score': trace.current_score,
            'elapsed_time': time.time() - trace.start_time
        }
        
        if trace.steps:
            latest_step = trace.steps[-1]
            metadata.update({
                'latest_confidence': latest_step.confidence,
                'latest_reasoning_quality': latest_step.reasoning_quality,
                'progress_rate': self._calculate_progress_rate(trace)
            })
        
        return metadata
    
    def get_control_statistics(self) -> Dict[str, Any]:
        """Get statistics about control decisions made.
        
        Returns:
            Statistics dictionary
        """
        return {
            'mode': self.mode.value,
            'total_decisions': self.total_decisions,
            'continue_decisions': self.continue_decisions,
            'interrupt_decisions': self.total_decisions - self.continue_decisions,
            'continue_rate': self.continue_decisions / self.total_decisions if self.total_decisions > 0 else 0.0,
            'control_actions': len(self.control_history)
        }
    
    def get_recent_actions(self, limit: int = 10) -> List[ControlAction]:
        """Get recent control actions.
        
        Args:
            limit: Maximum number of actions to return
            
        Returns:
            List of recent control actions
        """
        return self.control_history[-limit:] if self.control_history else []
    
    def reset_statistics(self):
        """Reset control statistics and history."""
        self.total_decisions = 0
        self.continue_decisions = 0
        self.control_history.clear()
        logger.info("Control statistics reset")
    
    def set_mode(self, mode: ControlMode):
        """Change the control mode.
        
        Args:
            mode: New control mode
        """
        old_mode = self.mode
        self.mode = mode
        logger.info(f"Control mode changed from {old_mode.value} to {mode.value}")
    
    def configure_thresholds(self, 
                           min_confidence: Optional[float] = None,
                           max_reasoning_time: Optional[float] = None,
                           max_tokens: Optional[int] = None,
                           min_progress_rate: Optional[float] = None):
        """Configure control thresholds.
        
        Args:
            min_confidence: Minimum confidence threshold
            max_reasoning_time: Maximum reasoning time in seconds
            max_tokens: Maximum token count
            min_progress_rate: Minimum progress rate per step
        """
        if min_confidence is not None:
            self.min_confidence_threshold = min_confidence
        if max_reasoning_time is not None:
            self.max_reasoning_time = max_reasoning_time
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if min_progress_rate is not None:
            self.min_progress_rate = min_progress_rate
        
        logger.info("Control thresholds updated")
    
    def get_status(self) -> Dict[str, Any]:
        """Get controller status information.
        
        Returns:
            Status dictionary
        """
        return {
            'mode': self.mode.value,
            'initialized': True,
            'statistics': self.get_control_statistics(),
            'thresholds': {
                'min_confidence': self.min_confidence_threshold,
                'max_reasoning_time': self.max_reasoning_time,
                'max_tokens': self.max_tokens,
                'min_progress_rate': self.min_progress_rate
            }
        }
