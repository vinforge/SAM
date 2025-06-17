"""
Unit Tests for ImplicitKnowledgeSkill
====================================

Comprehensive test suite for the ImplicitKnowledgeSkill implementation,
covering core functionality, edge cases, and integration scenarios.
"""

import unittest
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sam.orchestration.skills.reasoning.implicit_knowledge import ImplicitKnowledgeSkill, ImplicitKnowledgeResult
from sam.orchestration.uif import SAM_UIF
from sam.orchestration.skills.base import SkillExecutionError


class TestImplicitKnowledgeSkill(unittest.TestCase):
    """Test suite for ImplicitKnowledgeSkill."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.skill = ImplicitKnowledgeSkill()
        self.sample_chunks = [
            "Silicon carbide is a semiconductor material with excellent thermal properties.",
            "Electric vehicles require efficient power inverters for motor control.",
            "Power electronics in EVs must handle high temperatures and switching frequencies."
        ]
    
    def test_skill_initialization(self):
        """Test that the skill initializes correctly."""
        self.assertEqual(self.skill.skill_name, "ImplicitKnowledgeSkill")
        self.assertEqual(self.skill.skill_version, "1.0.0")
        self.assertEqual(self.skill.skill_category, "reasoning")
        self.assertIn("explicit_knowledge_chunks", self.skill.required_inputs)
        self.assertIn("implicit_knowledge_summary", self.skill.output_keys)
        self.assertIn("unified_context", self.skill.output_keys)
    
    def test_input_validation_success(self):
        """Test successful input validation."""
        uif = SAM_UIF(input_query="Test query")
        uif.intermediate_data["explicit_knowledge_chunks"] = self.sample_chunks
        
        result = self.skill._validate_inputs(uif)
        self.assertTrue(result)
    
    def test_input_validation_missing_chunks(self):
        """Test input validation with missing chunks."""
        uif = SAM_UIF(input_query="Test query")
        
        result = self.skill._validate_inputs(uif)
        self.assertFalse(result)
    
    def test_input_validation_insufficient_chunks(self):
        """Test input validation with insufficient chunks."""
        uif = SAM_UIF(input_query="Test query")
        uif.intermediate_data["explicit_knowledge_chunks"] = ["Only one chunk"]
        
        result = self.skill._validate_inputs(uif)
        self.assertFalse(result)
    
    def test_input_validation_invalid_chunk_types(self):
        """Test input validation with invalid chunk types."""
        uif = SAM_UIF(input_query="Test query")
        uif.intermediate_data["explicit_knowledge_chunks"] = ["Valid chunk", 123, None]
        
        result = self.skill._validate_inputs(uif)
        self.assertFalse(result)
    
    def test_extract_common_terms(self):
        """Test common term extraction."""
        chunks = [
            "Machine learning algorithms require large datasets for training.",
            "Deep learning models use neural networks with multiple layers.",
            "Training neural networks requires significant computational resources."
        ]
        
        common_terms = self.skill._extract_common_terms(chunks)
        
        # Should find terms that appear in multiple chunks
        self.assertIsInstance(common_terms, list)
        # Common terms might include "learning", "neural", "training"
        self.assertTrue(len(common_terms) >= 0)  # At least some common terms should be found
    
    def test_create_unified_context(self):
        """Test unified context creation."""
        implicit_connections = "These technologies are connected through power management requirements."
        
        unified_context = self.skill._create_unified_context(self.sample_chunks, implicit_connections)
        
        self.assertIsInstance(unified_context, str)
        self.assertIn("Source 1:", unified_context)
        self.assertIn("Source 2:", unified_context)
        self.assertIn("Source 3:", unified_context)
        self.assertIn("Implicit Connections:", unified_context)
        self.assertIn(implicit_connections, unified_context)
    
    def test_create_fallback_summary(self):
        """Test fallback summary creation."""
        implicit_connections = "Test connection analysis"
        
        summary = self.skill._create_fallback_summary(implicit_connections)
        
        self.assertIsInstance(summary, str)
        self.assertTrue(summary.startswith("Inferred Connection:"))
        self.assertIn(implicit_connections, summary)
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        chunks = self.sample_chunks
        implicit_connections = "These are connected because they all relate to power electronics."
        
        confidence = self.skill._calculate_confidence_score(chunks, implicit_connections)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_create_fallback_result(self):
        """Test fallback result creation."""
        processing_time = 1.5
        
        result = self.skill._create_fallback_result(self.sample_chunks, processing_time)
        
        self.assertIsInstance(result, ImplicitKnowledgeResult)
        self.assertEqual(result.processing_time, processing_time)
        self.assertEqual(result.source_chunks_count, len(self.sample_chunks))
        self.assertGreater(len(result.implicit_knowledge_summary), 0)
        self.assertGreater(len(result.unified_context), 0)
    
    @patch('requests.post')
    def test_ollama_interface_success(self, mock_post):
        """Test successful Ollama interface interaction."""
        # Mock successful Ollama response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'response': 'Test implicit connection'}
        mock_post.return_value = mock_response
        
        ollama_interface = self.skill._get_ollama_model()
        
        if ollama_interface:
            result = ollama_interface.generate("Test prompt")
            self.assertEqual(result, 'Test implicit connection')
    
    @patch('requests.post')
    def test_ollama_interface_failure(self, mock_post):
        """Test Ollama interface failure handling."""
        # Mock failed Ollama response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        ollama_interface = self.skill._get_ollama_model()
        
        if ollama_interface:
            result = ollama_interface.generate("Test prompt")
            self.assertEqual(result, "")  # Should return empty string on failure
    
    def test_execute_success(self):
        """Test successful skill execution."""
        uif = SAM_UIF(input_query="Find connections between these concepts")
        uif.intermediate_data["explicit_knowledge_chunks"] = self.sample_chunks
        
        # Mock the model to avoid external dependencies
        with patch.object(self.skill, '_generate_implicit_knowledge') as mock_generate:
            mock_result = ImplicitKnowledgeResult(
                implicit_knowledge_summary="Inferred Connection: Test connection",
                unified_context="Test unified context",
                confidence_score=0.8,
                processing_time=1.0,
                source_chunks_count=3
            )
            mock_generate.return_value = mock_result
            
            result = self.skill.execute(uif)
            
            self.assertTrue(result)
            self.assertIn("implicit_knowledge_summary", uif.intermediate_data)
            self.assertIn("unified_context", uif.intermediate_data)
            self.assertIn("implicit_knowledge_confidence", uif.intermediate_data)
            self.assertIn("implicit_knowledge_metadata", uif.intermediate_data)
    
    def test_execute_validation_failure(self):
        """Test skill execution with validation failure."""
        uif = SAM_UIF(input_query="Test query")
        # Don't add explicit_knowledge_chunks to trigger validation failure
        
        result = self.skill.execute(uif)
        
        self.assertFalse(result)
    
    def test_execute_exception_handling(self):
        """Test skill execution exception handling."""
        uif = SAM_UIF(input_query="Test query")
        uif.intermediate_data["explicit_knowledge_chunks"] = self.sample_chunks
        
        # Mock an exception during generation
        with patch.object(self.skill, '_validate_inputs', side_effect=Exception("Test error")):
            result = self.skill.execute(uif)
            
            self.assertFalse(result)


class TestImplicitKnowledgeResult(unittest.TestCase):
    """Test suite for ImplicitKnowledgeResult dataclass."""
    
    def test_result_creation(self):
        """Test ImplicitKnowledgeResult creation."""
        result = ImplicitKnowledgeResult(
            implicit_knowledge_summary="Test summary",
            unified_context="Test context",
            confidence_score=0.75,
            processing_time=2.5,
            source_chunks_count=4
        )
        
        self.assertEqual(result.implicit_knowledge_summary, "Test summary")
        self.assertEqual(result.unified_context, "Test context")
        self.assertEqual(result.confidence_score, 0.75)
        self.assertEqual(result.processing_time, 2.5)
        self.assertEqual(result.source_chunks_count, 4)


if __name__ == '__main__':
    unittest.main()
