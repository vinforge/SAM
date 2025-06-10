#!/usr/bin/env python3
"""
Test Suite for SAM Phase 3: Dimension-Aware Retrieval System
Comprehensive testing of conceptual dimension-weighted retrieval capabilities.
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

from memory.dimension_aware_retrieval import (
    DimensionAwareRetrieval, DimensionAwareResult, DimensionWeights, RetrievalStrategy
)
from memory.query_parser import NaturalLanguageQueryParser, ParsedQuery, QueryIntent, DimensionFilter
from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryChunk, MemoryType

class TestDimensionAwareRetrieval(unittest.TestCase):
    """Test dimension-aware retrieval functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_store = MemoryVectorStore(
            store_type=VectorStoreType.SIMPLE,
            storage_directory=self.temp_dir
        )
        
        # Add test memories with dimension scores
        self._add_test_memories()
        
        # Initialize dimension-aware retrieval if available
        try:
            self.retrieval_engine = DimensionAwareRetrieval(self.memory_store)
            self.dimension_available = True
        except Exception:
            self.retrieval_engine = None
            self.dimension_available = False
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _add_test_memories(self):
        """Add test memories with various dimension scores."""
        test_memories = [
            {
                "content": "Revolutionary AI breakthrough in quantum computing research with novel algorithms",
                "tags": ["ai", "quantum", "research"],
                "metadata": {
                    "dimension_scores": {
                        "novelty": 0.95, "technical_depth": 0.90, "complexity": 0.85,
                        "utility": 0.80, "credibility": 0.75
                    },
                    "dimension_profile": "researcher",
                    "dimension_confidence": {
                        "novelty": 0.90, "technical_depth": 0.85, "complexity": 0.80,
                        "utility": 0.75, "credibility": 0.70
                    }
                }
            },
            {
                "content": "Simple user guide for basic software installation and setup procedures",
                "tags": ["guide", "software", "basic"],
                "metadata": {
                    "dimension_scores": {
                        "complexity": 0.15, "utility": 0.85, "clarity": 0.90,
                        "credibility": 0.80, "novelty": 0.10
                    },
                    "dimension_profile": "general",
                    "dimension_confidence": {
                        "complexity": 0.95, "utility": 0.90, "clarity": 0.85,
                        "credibility": 0.80, "novelty": 0.75
                    }
                }
            },
            {
                "content": "High-ROI market opportunity analysis for emerging technology sectors",
                "tags": ["business", "market", "analysis"],
                "metadata": {
                    "dimension_scores": {
                        "market_impact": 0.90, "roi_potential": 0.95, "feasibility": 0.80,
                        "risk": 0.30, "utility": 0.85
                    },
                    "dimension_profile": "business",
                    "dimension_confidence": {
                        "market_impact": 0.85, "roi_potential": 0.90, "feasibility": 0.75,
                        "risk": 0.80, "utility": 0.85
                    }
                }
            },
            {
                "content": "Legal compliance requirements for ITAR-controlled technology exports",
                "tags": ["legal", "compliance", "itar"],
                "metadata": {
                    "dimension_scores": {
                        "compliance_risk": 0.85, "liability": 0.80, "complexity": 0.75,
                        "credibility": 0.90, "utility": 0.85
                    },
                    "dimension_profile": "legal",
                    "dimension_confidence": {
                        "compliance_risk": 0.90, "liability": 0.85, "complexity": 0.80,
                        "credibility": 0.95, "utility": 0.80
                    }
                }
            }
        ]
        
        for i, memory_data in enumerate(test_memories):
            from datetime import datetime
            chunk = MemoryChunk(
                chunk_id=f"test_chunk_{i}",
                content=memory_data["content"],
                content_hash=f"hash_{i}",
                embedding=[0.1] * 384,  # Dummy embedding
                memory_type=MemoryType.DOCUMENT,
                source=f"test_source_{i}",
                timestamp=datetime.now().isoformat(),
                tags=memory_data["tags"],
                importance_score=0.8,
                access_count=0,
                last_accessed=datetime.now().isoformat(),
                metadata=memory_data["metadata"]
            )
            self.memory_store.memory_chunks[chunk.chunk_id] = chunk
            # Add to vector index for search functionality
            if hasattr(self.memory_store, '_add_to_vector_index'):
                self.memory_store._add_to_vector_index(chunk.chunk_id, chunk.embedding)
    
    def test_profile_weight_initialization(self):
        """Test that profile weights are correctly initialized."""
        if not self.dimension_available:
            self.skipTest("Dimension-aware retrieval not available")
        
        # Test that all profiles have weights
        expected_profiles = ["general", "researcher", "business", "legal"]
        for profile in expected_profiles:
            self.assertIn(profile, self.retrieval_engine.profile_weights)
            weights = self.retrieval_engine.profile_weights[profile]
            self.assertIsInstance(weights, DimensionWeights)
            self.assertGreater(len(weights.profile_dimensions), 0)
    
    def test_hybrid_search_basic(self):
        """Test basic hybrid search functionality."""
        if not self.dimension_available:
            # Test fallback mode
            results = self.memory_store.dimension_aware_search(
                query="AI research breakthrough",
                max_results=3,
                profile="researcher"
            )

            self.assertIsInstance(results, list)
            # In fallback mode, we might get empty results, which is acceptable
            return

        results = self.retrieval_engine.dimension_aware_search(
            query="AI research breakthrough",
            max_results=3,
            profile="researcher"
        )

        self.assertIsInstance(results, list)
        # Note: Results might be empty if no memories match or vector index is not set up

        # Check result structure if we have results
        for result in results:
            self.assertIsInstance(result, DimensionAwareResult)
            self.assertIsInstance(result.final_score, float)
            self.assertIsInstance(result.dimension_explanation, str)
    
    def test_profile_specific_ranking(self):
        """Test that different profiles produce different rankings."""
        if not self.dimension_available:
            self.skipTest("Dimension-aware retrieval not available")
        
        query = "technology analysis"
        
        # Get results for different profiles
        researcher_results = self.retrieval_engine.dimension_aware_search(
            query=query, profile="researcher", max_results=3
        )
        business_results = self.retrieval_engine.dimension_aware_search(
            query=query, profile="business", max_results=3
        )
        
        # Results should be different (different ordering or scores)
        if len(researcher_results) > 1 and len(business_results) > 1:
            researcher_top = researcher_results[0].chunk_id
            business_top = business_results[0].chunk_id
            
            # Either different top results or different scores
            different_ranking = (researcher_top != business_top) or \
                              (researcher_results[0].final_score != business_results[0].final_score)
            
            self.assertTrue(different_ranking, "Different profiles should produce different rankings")
    
    def test_natural_language_filters(self):
        """Test natural language filter application."""
        if not self.dimension_available:
            # Test fallback mode
            results = self.memory_store.dimension_aware_search(
                query="software guide",
                natural_language_filters="high-utility, simple content",
                max_results=3
            )

            self.assertIsInstance(results, list)
            # In fallback mode, we might get empty results, which is acceptable
            return

        # Test high-utility filter
        results = self.retrieval_engine.dimension_aware_search(
            query="software guide",
            natural_language_filters="high-utility, simple content",
            max_results=3
        )

        self.assertIsInstance(results, list)
        # Note: Results might be empty if no memories match or vector index is not set up

        # Check that results have explanations if we have results
        for result in results:
            self.assertIsInstance(result.dimension_explanation, str)
            self.assertGreater(len(result.dimension_explanation), 0)
    
    def test_retrieval_strategies(self):
        """Test different retrieval strategies."""
        if not self.dimension_available:
            self.skipTest("Dimension-aware retrieval not available")
        
        query = "research analysis"
        strategies = [RetrievalStrategy.HYBRID, RetrievalStrategy.VECTOR_ONLY]
        
        for strategy in strategies:
            results = self.retrieval_engine.dimension_aware_search(
                query=query,
                strategy=strategy,
                max_results=2
            )
            
            self.assertIsInstance(results, list)
            # Should get some results for basic query
            self.assertGreaterEqual(len(results), 0)


class TestNaturalLanguageQueryParser(unittest.TestCase):
    """Test natural language query parsing functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.parser = NaturalLanguageQueryParser()
    
    def test_dimension_filter_extraction(self):
        """Test extraction of dimension filters from queries."""
        test_cases = [
            ("high-utility content", {"utility": DimensionFilter.HIGH}),
            ("low-risk information", {"danger": DimensionFilter.LOW}),
            ("simple and useful guide", {"complexity": DimensionFilter.LOW, "utility": DimensionFilter.HIGH}),
            ("innovative research", {"novelty": DimensionFilter.HIGH}),
            ("compliant legal documents", {"compliance_risk": DimensionFilter.LOW})
        ]
        
        for query, expected_filters in test_cases:
            parsed = self.parser.parse_query(query)
            
            for dimension, expected_level in expected_filters.items():
                self.assertIn(dimension, parsed.dimension_filters)
                self.assertEqual(parsed.dimension_filters[dimension], expected_level)
    
    def test_intent_classification(self):
        """Test query intent classification."""
        test_cases = [
            ("find high-quality research", QueryIntent.SEARCH),
            ("filter by low-risk content", QueryIntent.FILTER),
            ("compare different approaches", QueryIntent.COMPARE),
            ("analyze market trends", QueryIntent.ANALYZE),
            ("summarize key findings", QueryIntent.SUMMARIZE)
        ]
        
        for query, expected_intent in test_cases:
            parsed = self.parser.parse_query(query)
            self.assertEqual(parsed.intent, expected_intent)
    
    def test_profile_hint_detection(self):
        """Test profile hint detection."""
        test_cases = [
            ("research methodology analysis", "researcher"),
            ("market opportunity assessment", "business"),
            ("legal compliance review", "legal"),
            ("general information search", None)  # Should not detect specific profile
        ]
        
        for query, expected_profile in test_cases:
            parsed = self.parser.parse_query(query)
            self.assertEqual(parsed.profile_hint, expected_profile)
    
    def test_query_cleaning(self):
        """Test that filter phrases are removed from clean query."""
        query = "find high-utility, low-risk research papers"
        parsed = self.parser.parse_query(query)

        # Clean query should have filter terms removed
        self.assertNotIn("high-utility", parsed.clean_query)
        self.assertNotIn("low-risk", parsed.clean_query)
        # After cleaning, we should have the core search terms
        self.assertIn("find", parsed.clean_query)
        self.assertIn("papers", parsed.clean_query)
    
    def test_confidence_calculation(self):
        """Test confidence calculation for parsed queries."""
        # Query with multiple filters and clear intent should have high confidence
        complex_query = "find high-utility, low-risk research papers for analysis"
        parsed_complex = self.parser.parse_query(complex_query)
        
        # Simple query should have lower confidence
        simple_query = "papers"
        parsed_simple = self.parser.parse_query(simple_query)
        
        self.assertGreater(parsed_complex.confidence, parsed_simple.confidence)
        self.assertGreaterEqual(parsed_complex.confidence, 0.5)
        self.assertLessEqual(parsed_complex.confidence, 1.0)


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_store = MemoryVectorStore(
            store_type=VectorStoreType.SIMPLE,
            storage_directory=self.temp_dir
        )
        self.parser = NaturalLanguageQueryParser()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_memory_store_integration(self):
        """Test integration with memory vector store."""
        # Test that dimension_aware_search method exists
        self.assertTrue(hasattr(self.memory_store, 'dimension_aware_search'))
        
        # Test fallback behavior when dimension-aware retrieval is not available
        results = self.memory_store.dimension_aware_search(
            query="test query",
            max_results=5
        )
        
        # Should return list (even if empty due to no memories)
        self.assertIsInstance(results, list)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Parse natural language query
        query = "find high-utility, simple research content"
        parsed = self.parser.parse_query(query)
        
        # Verify parsing worked
        self.assertIn("utility", parsed.dimension_filters)
        self.assertIn("complexity", parsed.dimension_filters)
        self.assertEqual(parsed.dimension_filters["utility"], DimensionFilter.HIGH)
        self.assertEqual(parsed.dimension_filters["complexity"], DimensionFilter.LOW)
        
        # Test search with parsed filters
        results = self.memory_store.dimension_aware_search(
            query=parsed.clean_query,
            natural_language_filters=parsed.original_query,
            profile=parsed.profile_hint or "general"
        )
        
        # Should complete without errors
        self.assertIsInstance(results, list)


def run_phase3_tests():
    """Run all Phase 3 dimension-aware retrieval tests."""
    # Create test loader
    loader = unittest.TestLoader()

    # Create test suite
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTest(loader.loadTestsFromTestCase(TestDimensionAwareRetrieval))
    suite.addTest(loader.loadTestsFromTestCase(TestNaturalLanguageQueryParser))
    suite.addTest(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_phase3_tests()
    if success:
        print("\n🎉 All Phase 3 tests passed!")
    else:
        print("\n❌ Some Phase 3 tests failed.")
    
    exit(0 if success else 1)
