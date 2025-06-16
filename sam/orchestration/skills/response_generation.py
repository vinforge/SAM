"""
ResponseGenerationSkill - SAM LLM Response Generation
====================================================

Wraps SAM's core language model capabilities into the SOF skill framework.
Integrates with TPV (Thinking Process Verification) and handles response generation
with context from memory retrieval and other skills.
"""

import logging
from typing import Dict, Any, Optional, List
from ..uif import SAM_UIF
from .base import BaseSkillModule, SkillExecutionError

logger = logging.getLogger(__name__)


class ResponseGenerationSkill(BaseSkillModule):
    """
    Skill that generates final responses using SAM's language model.
    
    Integrates with:
    - TPV (Thinking Process Verification) system
    - Memory retrieval results
    - External tool outputs
    - User personalization profiles
    """
    
    skill_name = "ResponseGenerationSkill"
    skill_version = "1.0.0"
    skill_description = "Generates final responses using SAM's language model with TPV integration"
    skill_category = "generation"
    
    # Dependency declarations
    required_inputs = ["input_query"]
    optional_inputs = [
        "memory_results", "tool_outputs", "user_context", "active_profile",
        "retrieved_documents", "external_content", "use_tpv_control"
    ]
    output_keys = ["final_response", "response_confidence", "reasoning_trace", "tpv_analysis"]
    
    # Skill characteristics
    requires_external_access = False
    requires_vetting = False
    can_run_parallel = False  # Response generation should be final step
    estimated_execution_time = 2.0  # seconds
    max_execution_time = 30.0  # Maximum 30 seconds for response generation
    
    def __init__(self):
        super().__init__()
        self._llm_model = None
        self._tpv_integration = None
        self._initialize_generation_systems()
    
    def _initialize_generation_systems(self) -> None:
        """Initialize LLM and TPV systems."""
        try:
            # Initialize LLM model
            self._initialize_llm()
            
            # Initialize TPV integration if available
            self._initialize_tpv()
            
            self.logger.info("Response generation systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing generation systems: {e}")
            raise SkillExecutionError(f"Generation system setup error: {e}")
    
    def _initialize_llm(self) -> None:
        """Initialize the language model."""
        try:
            # Try to import SAM's LLM configuration
            from config.llm_config import get_llm_model
            self._llm_model = get_llm_model()
            
        except ImportError:
            # Fallback to basic model initialization
            self.logger.warning("Could not import SAM LLM config, using fallback")
            self._llm_model = None
    
    def _initialize_tpv(self) -> None:
        """Initialize TPV integration if available."""
        try:
            from sam.cognition.tpv.sam_integration import sam_tpv_integration
            self._tpv_integration = sam_tpv_integration
            self.logger.info("TPV integration initialized")
            
        except ImportError:
            self.logger.info("TPV system not available, proceeding without TPV")
            self._tpv_integration = None
    
    def execute(self, uif: SAM_UIF) -> SAM_UIF:
        """
        Generate final response using all available context and TPV if enabled.
        
        Args:
            uif: Universal Interface Format with query and context
            
        Returns:
            Updated UIF with generated response
        """
        try:
            query = uif.input_query
            
            # Determine if TPV should be used
            use_tpv = self._should_use_tpv(uif)
            
            self.logger.info(f"Generating response for query (TPV: {use_tpv}): {query[:100]}...")
            
            # Gather all available context
            context = self._gather_response_context(uif)
            
            # Generate response with or without TPV
            if use_tpv and self._tpv_integration:
                response_data = self._generate_tpv_response(query, context, uif)
            else:
                response_data = self._generate_standard_response(query, context, uif)
            
            # Store results in UIF
            uif.final_response = response_data["response"]
            uif.confidence_score = response_data["confidence"]
            
            uif.intermediate_data["final_response"] = response_data["response"]
            uif.intermediate_data["response_confidence"] = response_data["confidence"]
            uif.intermediate_data["reasoning_trace"] = response_data.get("reasoning_trace", [])
            uif.intermediate_data["tpv_analysis"] = response_data.get("tpv_analysis", {})
            
            # Set skill outputs
            uif.set_skill_output(self.skill_name, {
                "response_length": len(response_data["response"]),
                "confidence": response_data["confidence"],
                "used_tpv": use_tpv,
                "context_sources": list(context.keys()),
                "reasoning_steps": len(response_data.get("reasoning_trace", []))
            })
            
            self.logger.info(f"Response generated successfully (confidence: {response_data['confidence']:.3f})")
            
            return uif
            
        except Exception as e:
            self.logger.exception("Error during response generation")
            raise SkillExecutionError(f"Response generation failed: {str(e)}")
    
    def _should_use_tpv(self, uif: SAM_UIF) -> bool:
        """
        Determine if TPV should be used for this response.
        
        Returns:
            True if TPV should be used, False otherwise
        """
        # Check explicit TPV control flag
        use_tpv_flag = uif.intermediate_data.get("use_tpv_control")
        if use_tpv_flag is not None:
            return bool(use_tpv_flag)
        
        # Check if TPV is available
        if not self._tpv_integration:
            return False
        
        # Default TPV usage logic
        query = uif.input_query.lower()
        
        # Use TPV for complex reasoning tasks
        tpv_triggers = [
            "analyze", "compare", "evaluate", "explain why", "reasoning",
            "logic", "problem", "solution", "strategy", "decision"
        ]
        
        return any(trigger in query for trigger in tpv_triggers)
    
    def _gather_response_context(self, uif: SAM_UIF) -> Dict[str, Any]:
        """
        Gather all available context for response generation.
        
        Returns:
            Dictionary with organized context information
        """
        context = {
            "query": uif.input_query,
            "user_profile": uif.active_profile,
            "session_context": {}
        }
        
        # Add user context
        if uif.user_context:
            context["session_context"] = uif.user_context
        
        # Add memory retrieval results
        memory_results = uif.intermediate_data.get("memory_results")
        if memory_results:
            context["memory"] = self._format_memory_context(memory_results)
        
        # Add tool outputs
        tool_outputs = uif.intermediate_data.get("tool_outputs", {})
        if tool_outputs:
            context["tools"] = tool_outputs
        
        # Add external content (if vetted)
        external_content = uif.intermediate_data.get("external_content")
        if external_content:
            context["external"] = external_content
        
        # Add retrieved documents
        documents = uif.intermediate_data.get("retrieved_documents", [])
        if documents:
            context["documents"] = documents
        
        return context
    
    def _format_memory_context(self, memory_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format memory results for response generation context.
        
        Returns:
            Formatted memory context
        """
        if not memory_results:
            return {}
        
        formatted = {
            "relevant_memories": [],
            "confidence": memory_results.get("summary", {}).get("highest_confidence", 0.0),
            "sources": memory_results.get("summary", {}).get("sources_used", [])
        }
        
        # Extract top relevant memories
        all_results = memory_results.get("all_results", [])
        top_memories = sorted(all_results, key=lambda x: x.get("confidence", 0.0), reverse=True)[:5]
        
        for memory in top_memories:
            formatted["relevant_memories"].append({
                "content": memory.get("content", ""),
                "confidence": memory.get("confidence", 0.0),
                "source": memory.get("source", "unknown")
            })
        
        return formatted
    
    def _generate_tpv_response(self, query: str, context: Dict[str, Any], uif: SAM_UIF) -> Dict[str, Any]:
        """
        Generate response using TPV (Thinking Process Verification).
        
        Returns:
            Dictionary with response and TPV analysis
        """
        try:
            # Use TPV integration for enhanced reasoning
            tpv_result = self._tpv_integration.generate_response(
                query=query,
                context=context,
                user_id=uif.user_id,
                session_id=uif.session_id
            )
            
            return {
                "response": tpv_result.response,
                "confidence": tpv_result.confidence,
                "reasoning_trace": tpv_result.reasoning_steps,
                "tpv_analysis": {
                    "reasoning_quality": tpv_result.reasoning_quality,
                    "intervention_triggered": tpv_result.intervention_triggered,
                    "verification_score": tpv_result.verification_score
                }
            }
            
        except Exception as e:
            self.logger.error(f"TPV response generation failed: {e}")
            # Fallback to standard response
            return self._generate_standard_response(query, context, uif)
    
    def _generate_standard_response(self, query: str, context: Dict[str, Any], uif: SAM_UIF) -> Dict[str, Any]:
        """
        Generate response using standard LLM without TPV.
        
        Returns:
            Dictionary with response and basic analysis
        """
        try:
            # Create comprehensive prompt
            prompt = self._create_response_prompt(query, context)
            
            # Generate response using LLM
            if self._llm_model:
                response = self._llm_model.generate(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=1000
                )
            else:
                # Fallback response if no LLM available
                response = self._create_fallback_response(query, context)
            
            # Calculate confidence based on available context
            confidence = self._calculate_response_confidence(context)
            
            return {
                "response": response,
                "confidence": confidence,
                "reasoning_trace": [f"Generated response using standard LLM for query: {query[:50]}..."],
                "tpv_analysis": {}
            }
            
        except Exception as e:
            self.logger.error(f"Standard response generation failed: {e}")
            return {
                "response": f"I apologize, but I encountered an error while generating a response: {str(e)}",
                "confidence": 0.1,
                "reasoning_trace": [f"Error in response generation: {str(e)}"],
                "tpv_analysis": {}
            }
    
    def _create_response_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """
        Create a comprehensive prompt for response generation.
        
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            f"User Query: {query}",
            ""
        ]
        
        # Add memory context
        memory = context.get("memory", {})
        if memory and memory.get("relevant_memories"):
            prompt_parts.append("Relevant Information from Memory:")
            for i, mem in enumerate(memory["relevant_memories"][:3], 1):
                prompt_parts.append(f"{i}. {mem['content']} (confidence: {mem['confidence']:.2f})")
            prompt_parts.append("")
        
        # Add tool outputs
        tools = context.get("tools", {})
        if tools:
            prompt_parts.append("Tool Results:")
            for tool_name, output in tools.items():
                prompt_parts.append(f"- {tool_name}: {str(output)[:200]}...")
            prompt_parts.append("")
        
        # Add external content
        external = context.get("external", {})
        if external:
            prompt_parts.append("External Information:")
            prompt_parts.append(str(external)[:500] + "...")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "Please provide a comprehensive, helpful response based on the available information.",
            "If you're uncertain about something, please indicate your level of confidence.",
            "",
            "Response:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _create_fallback_response(self, query: str, context: Dict[str, Any]) -> str:
        """
        Create a fallback response when LLM is not available.
        
        Returns:
            Fallback response string
        """
        response_parts = [
            f"I understand you're asking about: {query}",
            ""
        ]
        
        # Include memory information if available
        memory = context.get("memory", {})
        if memory and memory.get("relevant_memories"):
            response_parts.append("Based on my memory, here's what I found:")
            for mem in memory["relevant_memories"][:2]:
                response_parts.append(f"- {mem['content']}")
            response_parts.append("")
        
        # Include tool results if available
        tools = context.get("tools", {})
        if tools:
            response_parts.append("Additional information from tools:")
            for tool_name, output in tools.items():
                response_parts.append(f"- {tool_name}: {str(output)[:100]}...")
            response_parts.append("")
        
        response_parts.append("I apologize that I cannot provide a more detailed response at this time.")
        
        return "\n".join(response_parts)
    
    def _calculate_response_confidence(self, context: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the response based on available context.
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = 0.5  # Base confidence for any response
        
        # Boost confidence based on memory results
        memory = context.get("memory", {})
        if memory:
            memory_confidence = memory.get("confidence", 0.0)
            base_confidence += memory_confidence * 0.3
        
        # Boost confidence based on tool results
        tools = context.get("tools", {})
        if tools:
            base_confidence += 0.2
        
        # Boost confidence based on external content
        external = context.get("external", {})
        if external:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
