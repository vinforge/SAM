"""
Integration Tests for Implicit Knowledge Engine
==============================================

Tests for the integration of ImplicitKnowledgeSkill with the broader SAM system,
including Q&A workflow, DynamicPlanner, and ResponseGenerationSkill integration.
"""

import unittest
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sam.orchestration.uif import SAM_UIF
from sam.orchestration.skills.reasoning.implicit_knowledge import ImplicitKnowledgeSkill
from sam.orchestration.skills.response_generation import ResponseGenerationSkill
from sam.orchestration.planner import DynamicPlanner
from sam.orchestration.coordinator import CoordinatorEngine


class TestImplicitKnowledgeIntegration(unittest.TestCase):
    """Integration tests for the Implicit Knowledge Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.implicit_skill = ImplicitKnowledgeSkill()
        self.response_skill = ResponseGenerationSkill()
        
    def test_skill_registration(self):
        """Test that ImplicitKnowledgeSkill can be registered with coordinator."""
        coordinator = CoordinatorEngine()
        
        # Register the skill
        coordinator.register_skill(self.implicit_skill)
        
        # Verify registration
        registered_skills = coordinator.get_registered_skills()
        self.assertIn("ImplicitKnowledgeSkill", registered_skills)
    
    def test_dynamic_planner_multi_hop_detection(self):
        """Test that DynamicPlanner detects multi-hop questions."""
        planner = DynamicPlanner()
        
        # Register ImplicitKnowledgeSkill
        planner.register_skill(self.implicit_skill)
        
        # Test multi-hop query
        multi_hop_query = "How does machine learning relate to quantum computing in optimization?"
        uif = SAM_UIF(input_query=multi_hop_query)
        
        # Generate fallback plan (since we don't have LLM in tests)
        plan_result = planner._generate_fallback_plan(uif)
        
        # Should include ImplicitKnowledgeSkill for multi-hop reasoning
        self.assertIn("ImplicitKnowledgeSkill", plan_result.plan)
    
    def test_dynamic_planner_simple_query(self):
        """Test that DynamicPlanner doesn't include ImplicitKnowledgeSkill for simple queries."""
        planner = DynamicPlanner()
        
        # Register skills
        planner.register_skill(self.implicit_skill)
        planner.register_skill(self.response_skill)
        
        # Test simple query
        simple_query = "What is the weather today?"
        uif = SAM_UIF(input_query=simple_query)
        
        # Generate fallback plan
        plan_result = planner._generate_fallback_plan(uif)
        
        # Should not include ImplicitKnowledgeSkill for simple queries
        self.assertNotIn("ImplicitKnowledgeSkill", plan_result.plan)
    
    def test_response_generation_with_implicit_knowledge(self):
        """Test ResponseGenerationSkill integration with implicit knowledge."""
        uif = SAM_UIF(input_query="Test query requiring implicit connections")
        
        # Add implicit knowledge data to UIF
        uif.intermediate_data["unified_context"] = "Enhanced context with implicit connections"
        uif.intermediate_data["implicit_knowledge_summary"] = "Inferred Connection: Test connection"
        uif.intermediate_data["implicit_knowledge_confidence"] = 0.85
        
        # Test context gathering
        context = self.response_skill._gather_response_context(uif)
        
        # Verify implicit knowledge is included in context
        self.assertIn("implicit_knowledge", context)
        self.assertEqual(context["implicit_knowledge"]["summary"], "Inferred Connection: Test connection")
        self.assertEqual(context["implicit_knowledge"]["confidence"], 0.85)
    
    def test_response_generation_prompt_with_implicit_knowledge(self):
        """Test that response generation prompt includes implicit knowledge."""
        query = "How are these concepts connected?"
        context = {
            "query": query,
            "implicit_knowledge": {
                "unified_context": "Enhanced context with discovered connections",
                "summary": "Inferred Connection: Concepts are related through shared principles",
                "confidence": 0.9
            }
        }
        
        prompt = self.response_skill._create_response_prompt(query, context)
        
        # Verify implicit knowledge is included in prompt
        self.assertIn("Implicit Knowledge Connections:", prompt)
        self.assertIn("Inferred Connection: Concepts are related through shared principles", prompt)
        self.assertIn("Enhanced Context:", prompt)
    
    def test_confidence_calculation_with_implicit_knowledge(self):
        """Test confidence calculation includes implicit knowledge contribution."""
        context_without_ik = {
            "memory": {"confidence": 0.7}
        }
        
        context_with_ik = {
            "memory": {"confidence": 0.7},
            "implicit_knowledge": {"confidence": 0.8}
        }
        
        confidence_without = self.response_skill._calculate_response_confidence(context_without_ik)
        confidence_with = self.response_skill._calculate_response_confidence(context_with_ik)
        
        # Confidence should be higher with implicit knowledge
        self.assertGreater(confidence_with, confidence_without)
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow with ImplicitKnowledgeSkill."""
        # Create coordinator and register skills
        coordinator = CoordinatorEngine()
        coordinator.register_skill(self.implicit_skill)
        coordinator.register_skill(self.response_skill)
        
        # Create UIF with multi-hop query
        uif = SAM_UIF(input_query="How does renewable energy connect to electric vehicles?")
        uif.intermediate_data["explicit_knowledge_chunks"] = [
            "Solar panels convert sunlight into electricity using photovoltaic cells.",
            "Electric vehicles use battery packs to store electrical energy.",
            "Grid integration allows renewable energy to charge electric vehicles."
        ]
        
        # Execute plan
        plan = ["ImplicitKnowledgeSkill", "ResponseGenerationSkill"]
        
        with patch.object(self.implicit_skill, '_get_ollama_model') as mock_ollama:
            # Mock Ollama model
            mock_model = Mock()
            mock_model.generate.return_value = "These concepts are connected through energy storage and distribution systems."
            mock_ollama.return_value = mock_model
            
            with patch.object(self.response_skill, '_llm_model') as mock_response_llm:
                mock_response_llm.generate.return_value = "Renewable energy and electric vehicles are connected through sustainable energy systems."
                
                execution_report = coordinator.execute_plan(plan, uif)
                
                # Verify successful execution
                self.assertEqual(execution_report.result.value, "success")
                self.assertIn("ImplicitKnowledgeSkill", execution_report.skills_executed)
                self.assertIn("ResponseGenerationSkill", execution_report.skills_executed)
                
                # Verify implicit knowledge was generated and used
                self.assertIn("implicit_knowledge_summary", uif.intermediate_data)
                self.assertIn("unified_context", uif.intermediate_data)
    
    def test_reasoning_trace_transparency(self):
        """Test that reasoning traces include implicit knowledge information."""
        uif = SAM_UIF(input_query="Test transparency query")
        
        # Add implicit knowledge context
        context = {
            "query": "Test query",
            "implicit_knowledge": {
                "summary": "Inferred Connection: Test connection for transparency",
                "confidence": 0.75
            }
        }
        
        with patch.object(self.response_skill, '_llm_model') as mock_llm:
            mock_llm.generate.return_value = "Test response"
            
            response_data = self.response_skill._generate_standard_response("Test query", context, uif)
            
            # Verify reasoning trace includes implicit knowledge information
            reasoning_trace = response_data["reasoning_trace"]
            self.assertTrue(any("Implicit Knowledge Integration" in step for step in reasoning_trace))
            self.assertTrue(any("Test connection for transparency" in step for step in reasoning_trace))
    
    def test_error_handling_in_integration(self):
        """Test error handling in integrated workflow."""
        coordinator = CoordinatorEngine()
        coordinator.register_skill(self.implicit_skill)
        
        # Create UIF with invalid data
        uif = SAM_UIF(input_query="Test error handling")
        uif.intermediate_data["explicit_knowledge_chunks"] = ["Only one chunk"]  # Insufficient
        
        # Execute plan
        plan = ["ImplicitKnowledgeSkill"]
        execution_report = coordinator.execute_plan(plan, uif)
        
        # Should handle error gracefully
        self.assertEqual(execution_report.result.value, "failure")
        self.assertGreater(len(execution_report.error_details), 0)


class TestSOFIntegration(unittest.TestCase):
    """Test SOF (SAM Orchestration Framework) integration."""
    
    def test_sof_skill_availability(self):
        """Test that ImplicitKnowledgeSkill is available through SOF."""
        try:
            from sam.orchestration import ImplicitKnowledgeSkill as SOFImplicitSkill
            
            skill = SOFImplicitSkill()
            self.assertEqual(skill.skill_name, "ImplicitKnowledgeSkill")
            
        except ImportError:
            self.fail("ImplicitKnowledgeSkill not available through SOF imports")
    
    def test_sof_integration_initialization(self):
        """Test SOF integration initialization includes ImplicitKnowledgeSkill."""
        try:
            from sam.orchestration.sof_integration import SOFIntegration
            
            sof = SOFIntegration()
            
            # Mock initialization to avoid external dependencies
            with patch.object(sof, '_register_core_skills') as mock_register:
                sof.initialize()
                mock_register.assert_called_once()
                
        except ImportError:
            self.fail("SOF integration components not available")


if __name__ == '__main__':
    unittest.main()
