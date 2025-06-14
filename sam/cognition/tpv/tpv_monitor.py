"""
TPV Monitor Module
Phase 1 - Active Monitoring & Passive Control Integration

Real-time monitoring of SAM's reasoning process with progress scoring.
"""

import logging
import time
import torch
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

from .tpv_core import TPVCore
from .tpv_config import TPVConfig

logger = logging.getLogger(__name__)

@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning process."""
    step: int
    timestamp: float
    score: float
    token_count: int
    content_snippet: str
    confidence: float
    reasoning_quality: float
    meta_analysis: Dict[str, Any]

@dataclass
class ReasoningTrace:
    """Complete trace of reasoning process."""
    query_id: str
    start_time: float
    steps: List[ReasoningStep]
    is_active: bool
    total_tokens: int
    current_score: float
    
    def add_step(self, step: ReasoningStep):
        """Add a reasoning step to the trace."""
        self.steps.append(step)
        self.total_tokens = step.token_count
        self.current_score = step.score
    
    def get_latest_score(self) -> float:
        """Get the most recent reasoning score."""
        return self.current_score if self.steps else 0.0
    
    def get_progress_percentage(self) -> float:
        """Get reasoning progress as percentage (0-100)."""
        return min(self.current_score * 100, 100.0)

class TPVMonitor:
    """Real-time TPV monitoring system for SAM's reasoning process."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize TPV Monitor.
        
        Args:
            config_path: Path to TPV configuration file
        """
        self.tpv_core = TPVCore(config_path)
        self.active_traces: Dict[str, ReasoningTrace] = {}
        self.is_initialized = False
        
        # Monitoring configuration
        self.min_token_interval = 5  # Minimum tokens between TPV evaluations
        self.max_score_change = 0.1  # Maximum score change per step
        self.score_smoothing = 0.7   # Exponential smoothing factor
        
        logger.info("TPV Monitor initialized")
    
    def initialize(self) -> bool:
        """Initialize the TPV monitoring system.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if not self.tpv_core.initialize():
                logger.error("Failed to initialize TPV core")
                return False
            
            self.is_initialized = True
            logger.info("✅ TPV Monitor initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"TPV Monitor initialization failed: {e}")
            return False
    
    def start_monitoring(self, query: str, query_id: Optional[str] = None) -> str:
        """Start monitoring a new reasoning process.
        
        Args:
            query: The user query being processed
            query_id: Optional unique identifier for the query
            
        Returns:
            Query ID for tracking this reasoning process
        """
        if not self.is_initialized:
            logger.warning("TPV Monitor not initialized, starting monitoring anyway")
        
        if query_id is None:
            query_id = f"query_{int(time.time() * 1000)}"
        
        trace = ReasoningTrace(
            query_id=query_id,
            start_time=time.time(),
            steps=[],
            is_active=True,
            total_tokens=0,
            current_score=0.0
        )
        
        self.active_traces[query_id] = trace
        logger.info(f"🔍 Started TPV monitoring for query: {query_id}")
        
        return query_id
    
    def predict_progress(self, 
                        response_text: str, 
                        query_id: str,
                        token_count: Optional[int] = None) -> float:
        """Predict reasoning progress based on current response text.
        
        This is the core method called during token generation to get TPV scores.
        Since we don't have direct access to hidden states from Ollama, we use
        text-based analysis as a proxy for reasoning progress.
        
        Args:
            response_text: Current response text generated so far
            query_id: ID of the query being processed
            token_count: Current token count (estimated if not provided)
            
        Returns:
            Reasoning progress score (0.0 to 1.0)
        """
        try:
            if query_id not in self.active_traces:
                logger.warning(f"No active trace found for query: {query_id}")
                return 0.0
            
            trace = self.active_traces[query_id]
            
            # Estimate token count if not provided
            if token_count is None:
                token_count = len(response_text.split())
            
            # Skip if not enough tokens have been generated since last evaluation
            if trace.steps and token_count - trace.total_tokens < self.min_token_interval:
                return trace.current_score
            
            # Analyze response text for reasoning indicators
            progress_score = self._analyze_reasoning_progress(response_text, trace)
            
            # Apply smoothing to prevent dramatic score changes
            if trace.steps:
                previous_score = trace.current_score
                progress_score = (self.score_smoothing * previous_score + 
                                (1 - self.score_smoothing) * progress_score)
            
            # Create synthetic hidden states for TPV processing
            if self.is_initialized:
                synthetic_states = self._create_synthetic_hidden_states(response_text)
                tpv_results = self.tpv_core.process_thinking(synthetic_states)
                
                confidence = tpv_results.get('confidence_score', 0.5)
                reasoning_quality = tpv_results.get('reasoning_quality', 0.5)
                meta_analysis = tpv_results.get('meta_analysis', {})
            else:
                # Fallback when TPV core not available
                confidence = progress_score
                reasoning_quality = progress_score
                meta_analysis = {'processing_status': 'text_analysis_only'}
            
            # Create reasoning step
            step = ReasoningStep(
                step=len(trace.steps) + 1,
                timestamp=time.time(),
                score=progress_score,
                token_count=token_count,
                content_snippet=response_text[-100:] if len(response_text) > 100 else response_text,
                confidence=confidence,
                reasoning_quality=reasoning_quality,
                meta_analysis=meta_analysis
            )
            
            trace.add_step(step)
            
            logger.debug(f"TPV progress for {query_id}: {progress_score:.3f} (step {step.step})")
            
            return progress_score
            
        except Exception as e:
            logger.error(f"Error predicting progress for {query_id}: {e}")
            return 0.5  # Return neutral score on error
    
    def _analyze_reasoning_progress(self, response_text: str, trace: ReasoningTrace) -> float:
        """Analyze response text to estimate reasoning progress.
        
        This method uses text-based heuristics to estimate how much reasoning
        progress has been made, serving as a proxy for hidden state analysis.
        
        Args:
            response_text: Current response text
            trace: Current reasoning trace
            
        Returns:
            Estimated progress score (0.0 to 1.0)
        """
        if not response_text.strip():
            return 0.0
        
        progress_indicators = {
            # Introduction/setup phase (0.1-0.3)
            'intro_patterns': [
                r'\b(let me|i will|to answer|first|initially)\b',
                r'\b(understanding|analyzing|considering)\b',
                r'\b(the question|your query|this problem)\b'
            ],
            
            # Analysis phase (0.3-0.6)
            'analysis_patterns': [
                r'\b(because|since|due to|therefore|thus)\b',
                r'\b(however|although|while|whereas)\b',
                r'\b(evidence|data|research|studies)\b',
                r'\b(factors|aspects|elements|components)\b'
            ],
            
            # Synthesis phase (0.6-0.8)
            'synthesis_patterns': [
                r'\b(in conclusion|to summarize|overall)\b',
                r'\b(combining|integrating|bringing together)\b',
                r'\b(key points|main findings|important aspects)\b'
            ],
            
            # Conclusion phase (0.8-1.0)
            'conclusion_patterns': [
                r'\b(finally|in summary|to conclude)\b',
                r'\b(recommendation|suggestion|advice)\b',
                r'\b(answer is|solution is|result is)\b'
            ]
        }
        
        text_lower = response_text.lower()
        word_count = len(response_text.split())
        
        # Base progress from text length (longer responses = more progress)
        length_progress = min(word_count / 200.0, 0.8)  # Cap at 0.8 for length alone
        
        # Pattern-based progress scoring
        pattern_score = 0.0
        
        for phase, patterns in progress_indicators.items():
            phase_score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                phase_score += matches * 0.1
            
            # Weight different phases
            if phase == 'intro_patterns':
                pattern_score += min(phase_score, 0.3)
            elif phase == 'analysis_patterns':
                pattern_score += min(phase_score, 0.4) * 0.7
            elif phase == 'synthesis_patterns':
                pattern_score += min(phase_score, 0.3) * 0.8
            elif phase == 'conclusion_patterns':
                pattern_score += min(phase_score, 0.4) * 0.9
        
        # Combine length and pattern scores
        combined_score = (length_progress * 0.4) + (min(pattern_score, 1.0) * 0.6)
        
        # Add some randomness to simulate natural reasoning variation
        noise = np.random.normal(0, 0.05)  # Small random variation
        final_score = np.clip(combined_score + noise, 0.0, 1.0)
        
        return final_score
    
    def _create_synthetic_hidden_states(self, response_text: str) -> torch.Tensor:
        """Create synthetic hidden states from response text for TPV processing.
        
        Args:
            response_text: Current response text
            
        Returns:
            Synthetic hidden states tensor
        """
        try:
            # Get hidden dimension from config
            hidden_dim = self.tpv_core.config.get_hidden_dimension()
            
            # Create synthetic representation based on text characteristics
            text_features = self._extract_text_features(response_text)
            
            # Generate synthetic hidden states
            # This is a simplified approach - in a real implementation with access
            # to the actual model, we would use real hidden states
            batch_size = 1
            seq_len = min(len(response_text.split()), 50)  # Limit sequence length
            
            # Create base tensor with text-derived features
            hidden_states = torch.randn(batch_size, seq_len, hidden_dim)
            
            # Inject text features into the hidden states
            for i, feature_value in enumerate(text_features[:hidden_dim]):
                hidden_states[0, -1, i] = feature_value  # Set last token features
            
            return hidden_states
            
        except Exception as e:
            logger.warning(f"Failed to create synthetic hidden states: {e}")
            # Fallback to random tensor
            hidden_dim = 4096  # Default dimension
            return torch.randn(1, 10, hidden_dim)
    
    def _extract_text_features(self, text: str) -> List[float]:
        """Extract numerical features from text for synthetic hidden state creation.
        
        Args:
            text: Input text
            
        Returns:
            List of numerical features
        """
        if not text:
            return [0.0] * 100
        
        features = []
        
        # Basic text statistics
        features.append(len(text) / 1000.0)  # Normalized length
        features.append(len(text.split()) / 200.0)  # Normalized word count
        features.append(len(set(text.lower().split())) / len(text.split()) if text.split() else 0)  # Vocabulary diversity
        
        # Punctuation and structure
        features.append(text.count('.') / len(text) * 100)  # Period density
        features.append(text.count('?') / len(text) * 100)  # Question density
        features.append(text.count('!') / len(text) * 100)  # Exclamation density
        
        # Reasoning indicators
        reasoning_words = ['because', 'therefore', 'however', 'although', 'since', 'thus']
        reasoning_count = sum(text.lower().count(word) for word in reasoning_words)
        features.append(reasoning_count / len(text.split()) if text.split() else 0)
        
        # Pad to desired length
        while len(features) < 100:
            features.append(np.random.normal(0, 0.1))
        
        return features[:100]
    
    def stop_monitoring(self, query_id: str) -> Optional[ReasoningTrace]:
        """Stop monitoring a reasoning process and return the complete trace.
        
        Args:
            query_id: ID of the query to stop monitoring
            
        Returns:
            Complete reasoning trace, or None if not found
        """
        if query_id in self.active_traces:
            trace = self.active_traces[query_id]
            trace.is_active = False
            
            # Remove from active traces but keep for potential retrieval
            completed_trace = self.active_traces.pop(query_id)
            
            logger.info(f"🏁 Stopped TPV monitoring for query: {query_id} "
                       f"({len(completed_trace.steps)} steps, "
                       f"final score: {completed_trace.current_score:.3f})")
            
            return completed_trace
        
        logger.warning(f"No active trace found for query: {query_id}")
        return None
    
    def get_trace(self, query_id: str) -> Optional[ReasoningTrace]:
        """Get the current reasoning trace for a query.
        
        Args:
            query_id: ID of the query
            
        Returns:
            Current reasoning trace, or None if not found
        """
        return self.active_traces.get(query_id)
    
    def get_active_queries(self) -> List[str]:
        """Get list of currently active query IDs.
        
        Returns:
            List of active query IDs
        """
        return list(self.active_traces.keys())
    
    def get_status(self) -> Dict[str, Any]:
        """Get TPV Monitor status information.
        
        Returns:
            Status dictionary
        """
        return {
            'initialized': self.is_initialized,
            'active_queries': len(self.active_traces),
            'tpv_core_status': self.tpv_core.get_status(),
            'monitoring_config': {
                'min_token_interval': self.min_token_interval,
                'max_score_change': self.max_score_change,
                'score_smoothing': self.score_smoothing
            }
        }
