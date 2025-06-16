"""
Dynamic Planner for SAM Orchestration Framework
===============================================

Implements intelligent plan generation using LLM-as-a-Planner approach.
Generates custom execution plans based on query analysis and available skills.
"""

import json
import logging
import hashlib
import time
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta

from .uif import SAM_UIF
from .skills.base import BaseSkillModule
from .config import get_sof_config

logger = logging.getLogger(__name__)


@dataclass
class PlanCacheEntry:
    """Cache entry for generated plans."""
    plan: List[str]
    confidence: float
    created_at: datetime
    usage_count: int
    query_hash: str
    skill_context: str


@dataclass
class PlanGenerationResult:
    """Result of plan generation."""
    plan: List[str]
    confidence: float
    reasoning: str
    cache_hit: bool
    generation_time: float
    fallback_used: bool


class DynamicPlanner:
    """
    Generates custom execution plans using LLM-as-a-Planner approach.
    
    Features:
    - Intelligent plan generation based on query analysis
    - Plan caching to reduce LLM overhead
    - Fallback to default plans when generation fails
    - Context-aware skill selection
    - Performance optimization
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DynamicPlanner")
        self._config = get_sof_config()
        self._registered_skills: Dict[str, BaseSkillModule] = {}
        self._plan_cache: Dict[str, PlanCacheEntry] = {}
        self._llm_model = None
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize the language model for plan generation."""
        try:
            # Try to import SAM's LLM configuration
            from config.llm_config import get_llm_model
            self._llm_model = get_llm_model()
            self.logger.info("LLM model initialized for plan generation")
            
        except ImportError:
            self.logger.warning("Could not import SAM LLM config, plan generation will use fallbacks")
            self._llm_model = None
        except Exception as e:
            self.logger.error(f"Error initializing LLM: {e}")
            self._llm_model = None
    
    def register_skill(self, skill: BaseSkillModule) -> None:
        """
        Register a skill for plan generation.
        
        Args:
            skill: Skill to register
        """
        self._registered_skills[skill.skill_name] = skill
        self.logger.debug(f"Registered skill for planning: {skill.skill_name}")
    
    def register_skills(self, skills: List[BaseSkillModule]) -> None:
        """
        Register multiple skills for plan generation.
        
        Args:
            skills: List of skills to register
        """
        for skill in skills:
            self.register_skill(skill)
    
    def create_plan(self, uif: SAM_UIF) -> PlanGenerationResult:
        """
        Create a custom execution plan for the given query.
        
        Args:
            uif: Universal Interface Format with query and context
            
        Returns:
            Plan generation result with plan and metadata
        """
        start_time = time.time()
        
        self.logger.info(f"Creating plan for query: {uif.input_query[:100]}...")
        
        try:
            # Check cache first
            if self._config.enable_plan_caching:
                cached_result = self._check_plan_cache(uif)
                if cached_result:
                    generation_time = time.time() - start_time
                    return PlanGenerationResult(
                        plan=cached_result.plan,
                        confidence=cached_result.confidence,
                        reasoning=f"Retrieved from cache (used {cached_result.usage_count} times)",
                        cache_hit=True,
                        generation_time=generation_time,
                        fallback_used=False
                    )
            
            # Generate new plan
            if self._llm_model:
                result = self._generate_llm_plan(uif)
            else:
                result = self._generate_fallback_plan(uif)
            
            # Cache the result if successful
            if self._config.enable_plan_caching and result.plan and result.confidence > 0.5:
                self._cache_plan(uif, result)
            
            generation_time = time.time() - start_time
            result.generation_time = generation_time
            
            self.logger.info(f"Plan created: {result.plan} (confidence: {result.confidence:.2f})")
            
            return result
            
        except Exception as e:
            self.logger.exception("Error during plan generation")
            generation_time = time.time() - start_time
            
            # Return fallback plan
            fallback_plan = self._get_default_fallback_plan()
            return PlanGenerationResult(
                plan=fallback_plan,
                confidence=0.3,
                reasoning=f"Error during generation: {str(e)}",
                cache_hit=False,
                generation_time=generation_time,
                fallback_used=True
            )
    
    def _check_plan_cache(self, uif: SAM_UIF) -> Optional[PlanCacheEntry]:
        """
        Check if a cached plan exists for the query.
        
        Returns:
            Cached plan entry if found, None otherwise
        """
        query_hash = self._generate_query_hash(uif)
        
        if query_hash in self._plan_cache:
            entry = self._plan_cache[query_hash]
            
            # Check if cache entry is still valid
            if self._is_cache_entry_valid(entry):
                entry.usage_count += 1
                self.logger.debug(f"Cache hit for query hash: {query_hash}")
                return entry
            else:
                # Remove expired entry
                del self._plan_cache[query_hash]
                self.logger.debug(f"Removed expired cache entry: {query_hash}")
        
        return None
    
    def _generate_llm_plan(self, uif: SAM_UIF) -> PlanGenerationResult:
        """
        Generate plan using LLM-as-a-Planner approach.
        
        Returns:
            Plan generation result
        """
        try:
            # Create planning prompt
            prompt = self._create_planning_prompt(uif)
            
            # Generate plan using LLM
            response = self._llm_model.generate(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent planning
                max_tokens=500
            )
            
            # Parse the response
            plan_data = self._parse_llm_response(response)
            
            if plan_data and plan_data.get("plan"):
                return PlanGenerationResult(
                    plan=plan_data["plan"],
                    confidence=plan_data.get("confidence", 0.8),
                    reasoning=plan_data.get("reasoning", "Generated by LLM planner"),
                    cache_hit=False,
                    generation_time=0.0,  # Will be set by caller
                    fallback_used=False
                )
            else:
                # LLM response was invalid, use fallback
                return self._generate_fallback_plan(uif)
                
        except Exception as e:
            self.logger.error(f"LLM plan generation failed: {e}")
            return self._generate_fallback_plan(uif)
    
    def _create_planning_prompt(self, uif: SAM_UIF) -> str:
        """
        Create a specialized prompt for plan generation.
        
        Returns:
            Formatted planning prompt
        """
        available_skills = list(self._registered_skills.keys())
        skill_descriptions = {}
        
        for skill_name, skill in self._registered_skills.items():
            skill_descriptions[skill_name] = {
                "description": skill.skill_description,
                "inputs": skill.required_inputs,
                "outputs": skill.output_keys,
                "category": skill.skill_category
            }
        
        prompt_parts = [
            "You are the planning engine for the SAM AI system. Your task is to analyze the user's query and generate a JSON plan specifying the precise skills needed to answer the query, in the correct execution order.",
            "",
            f"User Query: {uif.input_query}",
            "",
            "Available Skills:",
        ]
        
        for skill_name, info in skill_descriptions.items():
            prompt_parts.append(f"- {skill_name}: {info['description']}")
            prompt_parts.append(f"  Inputs: {info['inputs']}")
            prompt_parts.append(f"  Outputs: {info['outputs']}")
            prompt_parts.append(f"  Category: {info['category']}")
            prompt_parts.append("")
        
        # Add context if available
        if uif.user_context:
            prompt_parts.extend([
                "User Context:",
                str(uif.user_context),
                ""
            ])
        
        prompt_parts.extend([
            "Instructions:",
            "1. Analyze the query to understand what information and processing is needed",
            "2. Select the minimum necessary skills to fulfill the request",
            "3. Order skills so that dependencies are satisfied (outputs of earlier skills feed inputs of later skills)",
            "4. Always include ResponseGenerationSkill as the final step to create the user response",
            "5. Consider including MemoryRetrievalSkill if the query might benefit from stored knowledge",
            "6. Include ConflictDetectorSkill if multiple information sources might conflict",
            "",
            "Response Format (JSON only):",
            "{",
            '  "plan": ["SkillName1", "SkillName2", "SkillName3"],',
            '  "reasoning": "Brief explanation of why these skills were chosen and ordered this way",',
            '  "confidence": 0.85',
            "}",
            "",
            "Your JSON response:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse LLM response to extract plan data.
        
        Returns:
            Parsed plan data or None if invalid
        """
        try:
            # Clean the response
            response = response.strip()
            
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                plan_data = json.loads(json_str)
                
                # Validate the plan
                if self._validate_generated_plan(plan_data):
                    return plan_data
            
            return None
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.warning(f"Failed to parse LLM response: {e}")
            return None
    
    def _validate_generated_plan(self, plan_data: Dict[str, Any]) -> bool:
        """
        Validate that the generated plan is valid.
        
        Returns:
            True if plan is valid, False otherwise
        """
        if not isinstance(plan_data, dict):
            return False
        
        if "plan" not in plan_data or not isinstance(plan_data["plan"], list):
            return False
        
        plan = plan_data["plan"]
        
        # Check that all skills exist
        for skill_name in plan:
            if skill_name not in self._registered_skills:
                self.logger.warning(f"Generated plan contains unknown skill: {skill_name}")
                return False
        
        # Check plan length
        if len(plan) > self._config.max_plan_length:
            self.logger.warning(f"Generated plan too long: {len(plan)} > {self._config.max_plan_length}")
            return False
        
        return True
    
    def _generate_fallback_plan(self, uif: SAM_UIF) -> PlanGenerationResult:
        """
        Generate a fallback plan using rule-based logic.
        
        Returns:
            Fallback plan generation result
        """
        plan = []
        reasoning_parts = []
        
        # Analyze query for plan generation
        query_lower = uif.input_query.lower()
        
        # Always start with memory retrieval if available
        if "MemoryRetrievalSkill" in self._registered_skills:
            plan.append("MemoryRetrievalSkill")
            reasoning_parts.append("Added memory retrieval for context")
        
        # Add conflict detection if query suggests multiple sources
        conflict_indicators = ["compare", "versus", "different", "conflicting", "sources"]
        if any(indicator in query_lower for indicator in conflict_indicators):
            if "ConflictDetectorSkill" in self._registered_skills:
                plan.append("ConflictDetectorSkill")
                reasoning_parts.append("Added conflict detection for comparison query")
        
        # Always end with response generation
        if "ResponseGenerationSkill" in self._registered_skills:
            plan.append("ResponseGenerationSkill")
            reasoning_parts.append("Added response generation as final step")
        
        # If no skills were added, use default fallback
        if not plan:
            plan = self._get_default_fallback_plan()
            reasoning_parts = ["Used default fallback plan"]
        
        return PlanGenerationResult(
            plan=plan,
            confidence=0.6,
            reasoning="; ".join(reasoning_parts),
            cache_hit=False,
            generation_time=0.0,
            fallback_used=True
        )
    
    def _get_default_fallback_plan(self) -> List[str]:
        """
        Get the default fallback plan.
        
        Returns:
            List of skill names for default execution
        """
        default_plan = []
        
        # Add available core skills in order
        core_skills = ["MemoryRetrievalSkill", "ResponseGenerationSkill"]
        
        for skill_name in core_skills:
            if skill_name in self._registered_skills:
                default_plan.append(skill_name)
        
        return default_plan or ["ResponseGenerationSkill"]  # Ensure at least one skill
    
    def _cache_plan(self, uif: SAM_UIF, result: PlanGenerationResult) -> None:
        """
        Cache a generated plan for future use.
        
        Args:
            uif: Universal Interface Format
            result: Plan generation result to cache
        """
        query_hash = self._generate_query_hash(uif)
        skill_context = self._generate_skill_context()
        
        entry = PlanCacheEntry(
            plan=result.plan,
            confidence=result.confidence,
            created_at=datetime.now(),
            usage_count=0,
            query_hash=query_hash,
            skill_context=skill_context
        )
        
        self._plan_cache[query_hash] = entry
        self.logger.debug(f"Cached plan for query hash: {query_hash}")
        
        # Clean old cache entries if needed
        self._cleanup_cache()
    
    def _generate_query_hash(self, uif: SAM_UIF) -> str:
        """
        Generate a hash for the query to use as cache key.
        
        Returns:
            Query hash string
        """
        # Include query, user profile, and available skills in hash
        hash_input = f"{uif.input_query}|{uif.active_profile}|{sorted(self._registered_skills.keys())}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _generate_skill_context(self) -> str:
        """
        Generate a context string representing current skill configuration.
        
        Returns:
            Skill context string
        """
        skill_signatures = []
        for skill_name in sorted(self._registered_skills.keys()):
            skill = self._registered_skills[skill_name]
            signature = f"{skill_name}:{skill.skill_version}"
            skill_signatures.append(signature)
        
        return "|".join(skill_signatures)
    
    def _is_cache_entry_valid(self, entry: PlanCacheEntry) -> bool:
        """
        Check if a cache entry is still valid.
        
        Returns:
            True if entry is valid, False otherwise
        """
        # Check TTL
        age = datetime.now() - entry.created_at
        if age.total_seconds() > self._config.plan_cache_ttl:
            return False
        
        # Check if skill context has changed
        current_context = self._generate_skill_context()
        if entry.skill_context != current_context:
            return False
        
        return True
    
    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        expired_keys = []
        
        for key, entry in self._plan_cache.items():
            if not self._is_cache_entry_valid(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._plan_cache[key]
        
        if expired_keys:
            self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_entries = len(self._plan_cache)
        total_usage = sum(entry.usage_count for entry in self._plan_cache.values())
        
        return {
            "total_entries": total_entries,
            "total_usage": total_usage,
            "average_usage": total_usage / total_entries if total_entries > 0 else 0,
            "cache_enabled": self._config.enable_plan_caching
        }
    
    def clear_cache(self) -> None:
        """Clear the plan cache."""
        self._plan_cache.clear()
        self.logger.info("Plan cache cleared")
    
    def get_registered_skills(self) -> List[str]:
        """Get list of registered skill names."""
        return list(self._registered_skills.keys())
