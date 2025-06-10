#!/usr/bin/env python3
"""
Test Suite for SAM Phase 5: Reflective Meta-Reasoning & Self-Aware Critique System
Comprehensive testing of meta-cognitive capabilities and introspective reasoning.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any

# Import SAM components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from reasoning.reflective_meta_reasoning import (
    ReflectiveMetaReasoningEngine, ReflectiveResult, CritiqueLevel,
    DimensionConflict, AlternativePerspective
)
from reasoning.dimension_conflict_detector import (
    AdvancedDimensionConflictDetector, ConflictType, ConflictSeverity
)
from reasoning.confidence_justifier import (
    AdvancedConfidenceJustifier, ConfidenceLevel, EvidenceType, ConfidenceJustification
)
from reasoning.phase5_integration import (
    Phase5ResponseEnhancer, Phase5EnhancedResponse, enhance_sam_response
)

class TestReflectiveMetaReasoning(unittest.TestCase):
    """Test reflective meta-reasoning engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = ReflectiveMetaReasoningEngine(CritiqueLevel.MODERATE)
        
        # Sample response analysis
        self.sample_response_analysis = {
            "response_length": 200,
            "assumptions": ["assumes user has technical background"],
            "uncertainty_indicators": ["might be", "could potentially"],
            "confidence_indicators": ["clearly", "definitely"],
            "dimension_scores": {
                "utility": 0.8,
                "danger": 0.7,
                "complexity": 0.9,
                "clarity": 0.4,
                "novelty": 0.85,
                "feasibility": 0.3
            },
            "evidence_sources": [
                {"metadata": {"source_type": "academic", "peer_reviewed": True}},
                {"metadata": {"source_type": "technical", "publication_date": "2024"}}
            ]
        }
    
    def test_reflective_reasoning_cycle(self):
        """Test complete reflective reasoning cycle."""
        query = "How can we implement secure AI systems?"
        initial_response = "AI systems can be secured through multiple layers of protection including access controls, encryption, and monitoring."
        
        result = self.engine.reflective_reasoning_cycle(query, initial_response)
        
        # Verify result structure
        self.assertIsInstance(result, ReflectiveResult)
        self.assertEqual(result.original_query, query)
        self.assertEqual(result.initial_response, initial_response)
        self.assertIsInstance(result.alternative_perspectives, list)
        self.assertIsInstance(result.adversarial_critiques, list)
        self.assertIsInstance(result.reasoning_chain, list)
        self.assertIsInstance(result.meta_confidence, float)
        self.assertGreaterEqual(result.meta_confidence, 0.0)
        self.assertLessEqual(result.meta_confidence, 1.0)
    
    def test_assumption_detection(self):
        """Test detection of assumptions in responses."""
        response_with_assumptions = "This assumes that users have proper training and that the system will be maintained regularly."
        
        assumptions = self.engine._detect_assumptions(response_with_assumptions)
        
        self.assertGreater(len(assumptions), 0)
        self.assertTrue(any("assumes" in assumption.lower() for assumption in assumptions))
    
    def test_alternative_perspective_generation(self):
        """Test generation of alternative perspectives."""
        query = "Should we implement this new technology?"
        response = "Yes, we should implement it because it offers significant benefits."
        
        alternatives = self.engine._generate_alternative_perspectives(query, response, None)
        
        self.assertIsInstance(alternatives, list)
        self.assertGreater(len(alternatives), 0)
        
        # Check for different perspective types
        perspective_names = [alt.perspective_name for alt in alternatives]
        self.assertTrue(any("Researcher" in name for name in perspective_names))
        self.assertTrue(any("Business" in name for name in perspective_names))
    
    def test_adversarial_critique_generation(self):
        """Test adversarial critique generation."""
        response = "This solution is definitely the best approach and will certainly succeed."
        alternatives = []
        
        critiques = self.engine._generate_adversarial_critiques(response, alternatives, None)
        
        self.assertIsInstance(critiques, list)
        self.assertGreater(len(critiques), 0)
        
        critique = critiques[0]
        self.assertIsInstance(critique.severity, float)
        self.assertGreaterEqual(critique.severity, 0.0)
        self.assertLessEqual(critique.severity, 1.0)
        self.assertIsInstance(critique.counter_arguments, list)


class TestDimensionConflictDetector(unittest.TestCase):
    """Test dimension conflict detection."""
    
    def setUp(self):
        """Set up test environment."""
        self.detector = AdvancedDimensionConflictDetector()
    
    def test_utility_risk_conflict(self):
        """Test detection of utility vs risk conflicts."""
        dimension_scores = {
            "utility": 0.9,
            "danger": 0.8,
            "complexity": 0.5
        }
        
        conflicts = self.detector.detect_conflicts(dimension_scores)
        
        # Should detect utility-risk conflict
        utility_risk_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.UTILITY_RISK]
        self.assertGreater(len(utility_risk_conflicts), 0)
        
        conflict = utility_risk_conflicts[0]
        self.assertIn("utility", conflict.dimensions_involved)
        self.assertIn("danger", conflict.dimensions_involved)
        self.assertIsInstance(conflict.severity, ConflictSeverity)
    
    def test_innovation_feasibility_conflict(self):
        """Test detection of innovation vs feasibility conflicts."""
        dimension_scores = {
            "novelty": 0.95,
            "feasibility": 0.2,
            "utility": 0.7
        }
        
        conflicts = self.detector.detect_conflicts(dimension_scores)
        
        # Should detect innovation-feasibility conflict
        innovation_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.INNOVATION_FEASIBILITY]
        self.assertGreater(len(innovation_conflicts), 0)
        
        conflict = innovation_conflicts[0]
        self.assertIn("novelty", conflict.dimensions_involved)
        self.assertIn("feasibility", conflict.dimensions_involved)
    
    def test_no_conflicts(self):
        """Test when no conflicts should be detected."""
        dimension_scores = {
            "utility": 0.6,
            "danger": 0.3,
            "complexity": 0.5,
            "clarity": 0.7
        }
        
        conflicts = self.detector.detect_conflicts(dimension_scores)
        
        # Should detect no significant conflicts
        self.assertEqual(len(conflicts), 0)
    
    def test_context_enhancement(self):
        """Test context-specific conflict enhancement."""
        dimension_scores = {
            "utility": 0.8,
            "danger": 0.7
        }
        
        context = {"domain": "cybersecurity", "profile": "researcher"}
        
        conflicts = self.detector.detect_conflicts(dimension_scores, context)
        
        if conflicts:
            # Cybersecurity domain should boost security-related conflicts
            conflict = conflicts[0]
            self.assertIn("cybersecurity", " ".join(conflict.context_factors).lower())


class TestConfidenceJustifier(unittest.TestCase):
    """Test confidence justification system."""
    
    def setUp(self):
        """Set up test environment."""
        self.justifier = AdvancedConfidenceJustifier("general")
        
        self.sample_response_analysis = {
            "evidence_sources": [
                {"metadata": {"source_type": "academic", "peer_reviewed": True}},
                {"metadata": {"source_type": "technical"}}
            ],
            "tool_outputs": [{"type": "search", "confidence": 0.8}],
            "dimension_scores": {
                "credibility": 0.8,
                "utility": 0.7,
                "complexity": 0.6
            },
            "assumptions": ["assumes proper implementation"],
            "uncertainty_indicators": ["might", "could"],
            "confidence_indicators": ["clearly"]
        }
    
    def test_confidence_justification(self):
        """Test complete confidence justification."""
        justification = self.justifier.justify_confidence(self.sample_response_analysis)
        
        self.assertIsInstance(justification, ConfidenceJustification)
        self.assertIsInstance(justification.confidence_score, float)
        self.assertGreaterEqual(justification.confidence_score, 0.0)
        self.assertLessEqual(justification.confidence_score, 1.0)
        self.assertIsInstance(justification.confidence_level, ConfidenceLevel)
        self.assertIsInstance(justification.evidence_items, list)
        self.assertGreater(len(justification.evidence_items), 0)
    
    def test_source_credibility_assessment(self):
        """Test source credibility assessment."""
        evidence = self.justifier._assess_source_credibility(self.sample_response_analysis)
        
        self.assertEqual(evidence.evidence_type, EvidenceType.SOURCE_CREDIBILITY)
        self.assertIsInstance(evidence.score, float)
        self.assertGreaterEqual(evidence.score, 0.0)
        self.assertLessEqual(evidence.score, 1.0)
        self.assertIn("academic", " ".join(evidence.supporting_details).lower())
    
    def test_evidence_quantity_assessment(self):
        """Test evidence quantity assessment."""
        evidence = self.justifier._assess_evidence_quantity(self.sample_response_analysis)
        
        self.assertEqual(evidence.evidence_type, EvidenceType.EVIDENCE_QUANTITY)
        self.assertGreater(evidence.score, 0.0)  # Should have some evidence
    
    def test_dimension_consistency_assessment(self):
        """Test dimension consistency assessment."""
        evidence = self.justifier._assess_dimension_consistency(self.sample_response_analysis)
        
        self.assertEqual(evidence.evidence_type, EvidenceType.DIMENSION_CONSISTENCY)
        self.assertIsInstance(evidence.score, float)
        self.assertIn("dimension", evidence.description.lower())
    
    def test_profile_specific_weights(self):
        """Test that different profiles use different evidence weights."""
        researcher_justifier = AdvancedConfidenceJustifier("researcher")
        business_justifier = AdvancedConfidenceJustifier("business")
        
        researcher_result = researcher_justifier.justify_confidence(self.sample_response_analysis)
        business_result = business_justifier.justify_confidence(self.sample_response_analysis)
        
        # Results should be different due to different weighting
        self.assertNotEqual(researcher_result.confidence_score, business_result.confidence_score)


class TestPhase5Integration(unittest.TestCase):
    """Test Phase 5 integration with SAM."""
    
    def setUp(self):
        """Set up test environment."""
        self.enhancer = Phase5ResponseEnhancer(
            critique_level=CritiqueLevel.MODERATE,
            profile="general"
        )
    
    def test_response_enhancement(self):
        """Test complete response enhancement."""
        query = "How should we approach AI safety?"
        initial_response = "AI safety requires careful consideration of risks and benefits."
        
        context = {
            "memory_results": [{"content": "AI safety research", "similarity": 0.8}],
            "domain": "research"
        }
        
        enhanced = self.enhancer.enhance_response(query, initial_response, context)
        
        self.assertIsInstance(enhanced, Phase5EnhancedResponse)
        self.assertEqual(enhanced.original_response, initial_response)
        self.assertIsInstance(enhanced.enhanced_response, str)
        self.assertGreater(len(enhanced.enhanced_response), len(initial_response))
        self.assertIsInstance(enhanced.processing_time_ms, int)
    
    def test_fallback_behavior(self):
        """Test fallback behavior when Phase 5 components fail."""
        # Create enhancer with invalid configuration to trigger fallback
        enhancer = Phase5ResponseEnhancer()
        enhancer.phase5_available = False
        
        query = "Test query"
        response = "Test response"
        
        enhanced = enhancer.enhance_response(query, response)
        
        self.assertFalse(enhanced.phase5_enabled)
        self.assertIn("temporarily unavailable", enhanced.enhanced_response)
    
    def test_critique_level_configuration(self):
        """Test dynamic critique level configuration."""
        self.enhancer.configure_critique_level(CritiqueLevel.RIGOROUS)
        self.assertEqual(self.enhancer.critique_level, CritiqueLevel.RIGOROUS)
    
    def test_profile_configuration(self):
        """Test dynamic profile configuration."""
        self.enhancer.configure_profile("researcher")
        self.assertEqual(self.enhancer.profile, "researcher")
    
    def test_phase5_status(self):
        """Test Phase 5 status reporting."""
        status = self.enhancer.get_phase5_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("phase5_available", status)
        self.assertIn("critique_level", status)
        self.assertIn("profile", status)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions for easy integration."""
    
    def test_enhance_sam_response_function(self):
        """Test convenience function for response enhancement."""
        query = "What are the benefits of renewable energy?"
        response = "Renewable energy offers environmental and economic benefits."
        
        enhanced = enhance_sam_response(
            query=query,
            initial_response=response,
            profile="general",
            critique_level=CritiqueLevel.GENTLE
        )
        
        self.assertIsInstance(enhanced, Phase5EnhancedResponse)
        self.assertEqual(enhanced.original_response, response)


def run_phase5_tests():
    """Run all Phase 5 meta-reasoning tests."""
    # Create test loader
    loader = unittest.TestLoader()
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(loader.loadTestsFromTestCase(TestReflectiveMetaReasoning))
    suite.addTest(loader.loadTestsFromTestCase(TestDimensionConflictDetector))
    suite.addTest(loader.loadTestsFromTestCase(TestConfidenceJustifier))
    suite.addTest(loader.loadTestsFromTestCase(TestPhase5Integration))
    suite.addTest(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_phase5_tests()
    if success:
        print("\n🎉 All Phase 5 tests passed!")
        print("🧠 Reflective meta-reasoning system is working correctly!")
    else:
        print("\n❌ Some Phase 5 tests failed.")
    
    exit(0 if success else 1)
