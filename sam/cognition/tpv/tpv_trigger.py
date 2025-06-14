"""
TPV Trigger System
Phase 1 - Active Monitoring & Passive Control Integration

Hybrid trigger mechanism to determine when TPV monitoring should be activated.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class UserProfile(Enum):
    """User profile types for contextual triggering."""
    RESEARCHER = "researcher"
    LEGAL = "legal"
    MEDICAL = "medical"
    TECHNICAL = "technical"
    BUSINESS = "business"
    STUDENT = "student"
    GENERAL = "general"

class QueryIntent(Enum):
    """Query intent types for contextual triggering."""
    ANALYZE = "analyze"
    COMPARE = "compare"
    EXPLAIN = "explain"
    SUMMARIZE = "summarize"
    RESEARCH = "research"
    SOLVE = "solve"
    CREATE = "create"
    SIMPLE = "simple"

@dataclass
class TriggerResult:
    """Result of TPV trigger evaluation."""
    should_activate: bool
    trigger_type: str
    confidence: float
    reason: str
    metadata: Dict[str, Any]

class TPVTrigger:
    """Hybrid trigger system for TPV activation.
    
    Combines contextual triggers (user profile + query intent) with
    confidence-based triggers to determine when TPV monitoring should be active.
    """
    
    def __init__(self):
        """Initialize the TPV trigger system."""
        
        # Contextual trigger configuration
        self.profile_trigger_map = {
            UserProfile.RESEARCHER: ["analyze", "research", "compare", "explain"],
            UserProfile.LEGAL: ["analyze", "compare", "research"],
            UserProfile.MEDICAL: ["analyze", "explain", "research"],
            UserProfile.TECHNICAL: ["solve", "analyze", "explain", "compare"],
            UserProfile.BUSINESS: ["analyze", "compare", "summarize"],
            UserProfile.STUDENT: ["explain", "summarize"],
            UserProfile.GENERAL: []  # General users need confidence trigger or complex queries
        }
        
        # Query intent patterns
        self.intent_patterns = {
            QueryIntent.ANALYZE: [
                r'\b(analyz|examin|investigat|evaluat|assess)\w*\b',
                r'\b(what.*factors|why.*happen|how.*work)\b',
                r'\b(breakdown|break down|dissect)\b'
            ],
            QueryIntent.COMPARE: [
                r'\b(compar|contrast|versus|vs\.?|differ)\w*\b',
                r'\b(better|worse|advantage|disadvantage)\b',
                r'\b(similarities|differences)\b'
            ],
            QueryIntent.EXPLAIN: [
                r'\b(explain|describe|tell me|what is|how does)\b',
                r'\b(clarify|elaborate|detail)\w*\b',
                r'\b(meaning|definition|concept)\b'
            ],
            QueryIntent.SUMMARIZE: [
                r'\b(summar|overview|brief|outline)\w*\b',
                r'\b(key points|main ideas|highlights)\b',
                r'\b(in short|briefly)\b'
            ],
            QueryIntent.RESEARCH: [
                r'\b(research|study|investigation|findings)\b',
                r'\b(evidence|data|statistics|studies)\b',
                r'\b(literature|papers|articles)\b'
            ],
            QueryIntent.SOLVE: [
                r'\b(solve|solution|fix|resolve|troubleshoot)\b',
                r'\b(problem|issue|error|bug)\b',
                r'\b(how to|step by step)\b'
            ],
            QueryIntent.CREATE: [
                r'\b(create|generate|make|build|design)\b',
                r'\b(write|compose|draft|develop)\b',
                r'\b(plan|strategy|approach)\b'
            ],
            QueryIntent.SIMPLE: [
                r'\b(simple|basic|easy|quick)\b',
                r'\b(yes|no|true|false)\b',
                r'^.{1,50}$'  # Very short queries
            ]
        }
        
        # Confidence thresholds
        self.confidence_threshold = 0.7
        self.high_complexity_threshold = 0.8
        
        # Default user profile
        self.default_profile = UserProfile.GENERAL
        
        logger.info("TPV Trigger system initialized")
    
    def should_activate_tpv(self, 
                           query: str,
                           user_profile: Optional[UserProfile] = None,
                           initial_confidence: Optional[float] = None,
                           context: Optional[Dict[str, Any]] = None) -> TriggerResult:
        """Determine if TPV monitoring should be activated.
        
        Args:
            query: User query text
            user_profile: User's profile type
            initial_confidence: Initial confidence score from pre-analysis
            context: Additional context information
            
        Returns:
            TriggerResult indicating whether to activate TPV
        """
        try:
            # Step A: Contextual Trigger Check
            contextual_result = self._check_contextual_trigger(query, user_profile)
            
            # Step B: Confidence Trigger Check
            confidence_result = self._check_confidence_trigger(initial_confidence)
            
            # Combine results
            should_activate = contextual_result.should_activate or confidence_result.should_activate
            
            # Determine primary trigger type and confidence
            if contextual_result.should_activate and confidence_result.should_activate:
                trigger_type = "hybrid"
                confidence = max(contextual_result.confidence, confidence_result.confidence)
                reason = f"Both contextual ({contextual_result.reason}) and confidence ({confidence_result.reason}) triggers activated"
            elif contextual_result.should_activate:
                trigger_type = "contextual"
                confidence = contextual_result.confidence
                reason = contextual_result.reason
            elif confidence_result.should_activate:
                trigger_type = "confidence"
                confidence = confidence_result.confidence
                reason = confidence_result.reason
            else:
                trigger_type = "none"
                confidence = 0.0
                reason = "No triggers activated"
            
            # Compile metadata
            metadata = {
                'query_length': len(query),
                'query_word_count': len(query.split()),
                'detected_intent': self._detect_query_intent(query).value,
                'user_profile': (user_profile or self.default_profile).value,
                'initial_confidence': initial_confidence,
                'contextual_trigger': contextual_result.should_activate,
                'confidence_trigger': confidence_result.should_activate,
                'context': context or {}
            }
            
            result = TriggerResult(
                should_activate=should_activate,
                trigger_type=trigger_type,
                confidence=confidence,
                reason=reason,
                metadata=metadata
            )
            
            logger.info(f"TPV trigger evaluation: {should_activate} ({trigger_type}, {confidence:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in TPV trigger evaluation: {e}")
            # Default to not activating on error
            return TriggerResult(
                should_activate=False,
                trigger_type="error",
                confidence=0.0,
                reason=f"Error in trigger evaluation: {e}",
                metadata={}
            )
    
    def _check_contextual_trigger(self, 
                                 query: str, 
                                 user_profile: Optional[UserProfile] = None) -> TriggerResult:
        """Check if contextual triggers (profile + intent) should activate TPV.
        
        Args:
            query: User query text
            user_profile: User's profile type
            
        Returns:
            TriggerResult for contextual trigger
        """
        profile = user_profile or self.default_profile
        detected_intent = self._detect_query_intent(query)
        
        # Check if this profile + intent combination should trigger TPV
        trigger_intents = self.profile_trigger_map.get(profile, [])
        should_activate = detected_intent.value in trigger_intents
        
        # Calculate confidence based on intent detection strength
        intent_confidence = self._calculate_intent_confidence(query, detected_intent)
        
        # Boost confidence for complex profiles
        profile_boost = {
            UserProfile.RESEARCHER: 0.2,
            UserProfile.LEGAL: 0.15,
            UserProfile.MEDICAL: 0.15,
            UserProfile.TECHNICAL: 0.1,
            UserProfile.BUSINESS: 0.05,
            UserProfile.STUDENT: 0.0,
            UserProfile.GENERAL: 0.0
        }
        
        confidence = min(intent_confidence + profile_boost.get(profile, 0.0), 1.0)
        
        reason = f"Profile: {profile.value}, Intent: {detected_intent.value}"
        
        return TriggerResult(
            should_activate=should_activate,
            trigger_type="contextual",
            confidence=confidence,
            reason=reason,
            metadata={
                'profile': profile.value,
                'detected_intent': detected_intent.value,
                'intent_confidence': intent_confidence
            }
        )
    
    def _check_confidence_trigger(self, initial_confidence: Optional[float]) -> TriggerResult:
        """Check if confidence-based trigger should activate TPV.
        
        Args:
            initial_confidence: Initial confidence score
            
        Returns:
            TriggerResult for confidence trigger
        """
        if initial_confidence is None:
            return TriggerResult(
                should_activate=False,
                trigger_type="confidence",
                confidence=0.0,
                reason="No initial confidence provided",
                metadata={}
            )
        
        should_activate = initial_confidence < self.confidence_threshold
        confidence = 1.0 - initial_confidence  # Lower initial confidence = higher trigger confidence
        
        reason = f"Initial confidence {initial_confidence:.3f} < threshold {self.confidence_threshold}"
        
        return TriggerResult(
            should_activate=should_activate,
            trigger_type="confidence",
            confidence=confidence,
            reason=reason,
            metadata={
                'initial_confidence': initial_confidence,
                'threshold': self.confidence_threshold
            }
        )
    
    def _detect_query_intent(self, query: str) -> QueryIntent:
        """Detect the intent of a user query.
        
        Args:
            query: User query text
            
        Returns:
            Detected query intent
        """
        query_lower = query.lower()
        
        # Score each intent based on pattern matches
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            
            intent_scores[intent] = score
        
        # Return intent with highest score, or SIMPLE if no clear match
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            if intent_scores[best_intent] > 0:
                return best_intent
        
        return QueryIntent.SIMPLE
    
    def _calculate_intent_confidence(self, query: str, intent: QueryIntent) -> float:
        """Calculate confidence in the detected intent.
        
        Args:
            query: User query text
            intent: Detected intent
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        query_lower = query.lower()
        patterns = self.intent_patterns.get(intent, [])
        
        if not patterns:
            return 0.0
        
        total_matches = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, query_lower))
            total_matches += matches
        
        # Normalize by query length and number of patterns
        query_words = len(query.split())
        confidence = min(total_matches / (query_words * 0.5), 1.0)
        
        return confidence
    
    def configure_thresholds(self, 
                           confidence_threshold: Optional[float] = None,
                           high_complexity_threshold: Optional[float] = None):
        """Configure trigger thresholds.
        
        Args:
            confidence_threshold: Confidence threshold for activation
            high_complexity_threshold: High complexity threshold
        """
        if confidence_threshold is not None:
            self.confidence_threshold = confidence_threshold
        if high_complexity_threshold is not None:
            self.high_complexity_threshold = high_complexity_threshold
        
        logger.info("TPV trigger thresholds updated")
    
    def get_status(self) -> Dict[str, Any]:
        """Get trigger system status.
        
        Returns:
            Status dictionary
        """
        return {
            'confidence_threshold': self.confidence_threshold,
            'high_complexity_threshold': self.high_complexity_threshold,
            'supported_profiles': [p.value for p in UserProfile],
            'supported_intents': [i.value for i in QueryIntent],
            'profile_trigger_count': sum(len(intents) for intents in self.profile_trigger_map.values())
        }
