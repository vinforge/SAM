#!/usr/bin/env python3
"""
Unit tests for SAM's Memory Ranking Engine (Phase 3).
"""

import sys
import unittest
import tempfile
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from memory.ranking_engine import (
    MemoryRankingEngine, RankingWeights, RankingConfig, RankedMemoryResult
)

class TestMemoryRankingEngine(unittest.TestCase):
    """Test cases for Memory Ranking Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        
        # Test configuration
        self.test_config = {
            "memory": {
                "ranking_weights": {
                    "semantic": 0.6,
                    "recency": 0.2,
                    "confidence": 0.15,
                    "priority": 0.05
                },
                "ranking_config": {
                    "initial_candidates": 20,
                    "recency_decay_days": 30.0,
                    "min_confidence_threshold": 0.1,
                    "enable_hybrid_ranking": True
                }
            }
        }
        
        # Write test config
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
        
        # Initialize ranking engine with test config
        self.engine = MemoryRankingEngine(str(self.config_file))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ranking_weights_normalization(self):
        """Test that ranking weights are properly normalized."""
        weights = RankingWeights(semantic=0.8, recency=0.4, confidence=0.2, priority=0.1)
        normalized = weights.normalize()
        
        total = normalized.semantic + normalized.recency + normalized.confidence + normalized.priority
        self.assertAlmostEqual(total, 1.0, places=6)
    
    def test_semantic_score_calculation(self):
        """Test semantic score calculation from ChromaDB distance."""
        # Test perfect match (distance = 0)
        score = self.engine.calculate_semantic_score(0.0)
        self.assertEqual(score, 1.0)
        
        # Test complete mismatch (distance = 1)
        score = self.engine.calculate_semantic_score(1.0)
        self.assertEqual(score, 0.0)
        
        # Test partial match
        score = self.engine.calculate_semantic_score(0.3)
        self.assertEqual(score, 0.7)
        
        # Test clamping for values > 1
        score = self.engine.calculate_semantic_score(1.5)
        self.assertEqual(score, 0.0)
    
    def test_recency_score_calculation(self):
        """Test recency score calculation with exponential decay."""
        now = datetime.now(timezone.utc)
        
        # Test current timestamp (should be close to 1.0)
        score = self.engine.calculate_recency_score(now.timestamp())
        self.assertGreater(score, 0.99)
        
        # Test 30 days ago (should be around 0.5 with 30-day half-life)
        thirty_days_ago = now - timedelta(days=30)
        score = self.engine.calculate_recency_score(thirty_days_ago.timestamp())
        self.assertAlmostEqual(score, 0.5, delta=0.1)
        
        # Test very old timestamp (should be close to 0)
        very_old = now - timedelta(days=365)
        score = self.engine.calculate_recency_score(very_old.timestamp())
        self.assertLess(score, 0.1)
        
        # Test ISO format string
        iso_string = now.isoformat()
        score = self.engine.calculate_recency_score(iso_string)
        self.assertGreater(score, 0.99)
    
    def test_confidence_score_extraction(self):
        """Test confidence score extraction from metadata."""
        # Test confidence_score field
        metadata = {"confidence_score": 0.8}
        score = self.engine.calculate_confidence_score(metadata)
        self.assertEqual(score, 0.8)
        
        # Test importance_score field
        metadata = {"importance_score": 0.6}
        score = self.engine.calculate_confidence_score(metadata)
        self.assertEqual(score, 0.6)
        
        # Test clamping
        metadata = {"confidence_score": 1.5}
        score = self.engine.calculate_confidence_score(metadata)
        self.assertEqual(score, 1.0)
        
        # Test default value
        metadata = {}
        score = self.engine.calculate_confidence_score(metadata)
        self.assertEqual(score, 0.5)
    
    def test_priority_score_calculation(self):
        """Test priority score calculation from metadata flags."""
        # Test pinned flag
        metadata = {"pinned": True}
        score = self.engine.calculate_priority_score(metadata)
        self.assertEqual(score, 1.0)
        
        # Test priority field
        metadata = {"priority": 0.7}
        score = self.engine.calculate_priority_score(metadata)
        self.assertEqual(score, 0.7)
        
        # Test high confidence as priority indicator
        metadata = {"confidence_score": 0.9}
        score = self.engine.calculate_priority_score(metadata)
        self.assertEqual(score, 0.3)
        
        # Test no priority indicators
        metadata = {"confidence_score": 0.5}
        score = self.engine.calculate_priority_score(metadata)
        self.assertEqual(score, 0.0)
    
    def test_final_score_calculation(self):
        """Test final hybrid score calculation."""
        # Create test metadata
        now = datetime.now(timezone.utc)
        metadata = {
            "created_at": now.timestamp(),
            "confidence_score": 0.8,
            "pinned": True
        }
        
        # Calculate final score
        final_score, breakdown = self.engine.calculate_final_score(0.2, metadata)
        
        # Verify score breakdown
        self.assertIn("semantic", breakdown)
        self.assertIn("recency", breakdown)
        self.assertIn("confidence", breakdown)
        self.assertIn("priority", breakdown)
        self.assertIn("final", breakdown)
        
        # Verify semantic score
        self.assertAlmostEqual(breakdown["semantic"], 0.8, places=2)  # 1 - 0.2
        
        # Verify confidence score
        self.assertEqual(breakdown["confidence"], 0.8)
        
        # Verify priority score
        self.assertEqual(breakdown["priority"], 1.0)  # pinned = True
        
        # Verify final score is weighted combination
        expected_final = (
            self.engine.weights.semantic * breakdown["semantic"] +
            self.engine.weights.recency * breakdown["recency"] +
            self.engine.weights.confidence * breakdown["confidence"] +
            self.engine.weights.priority * breakdown["priority"]
        )
        self.assertAlmostEqual(final_score, expected_final, places=6)
    
    def test_rank_memory_results(self):
        """Test ranking of ChromaDB results."""
        now = datetime.now(timezone.utc)
        old_time = now - timedelta(days=60)
        
        # Create test ChromaDB results
        chroma_results = [
            {
                "id": "mem_1",
                "document": "Recent high-confidence content",
                "metadata": {
                    "created_at": now.timestamp(),
                    "confidence_score": 0.9,
                    "pinned": False
                },
                "distance": 0.1  # High semantic similarity
            },
            {
                "id": "mem_2", 
                "document": "Old low-confidence content",
                "metadata": {
                    "created_at": old_time.timestamp(),
                    "confidence_score": 0.3,
                    "pinned": False
                },
                "distance": 0.05  # Very high semantic similarity
            },
            {
                "id": "mem_3",
                "document": "Recent pinned content",
                "metadata": {
                    "created_at": now.timestamp(),
                    "confidence_score": 0.7,
                    "pinned": True
                },
                "distance": 0.3  # Lower semantic similarity
            }
        ]
        
        # Rank results
        ranked_results = self.engine.rank_memory_results(chroma_results)
        
        # Verify we got results
        self.assertEqual(len(ranked_results), 3)
        
        # Verify results are sorted by final score (descending)
        for i in range(len(ranked_results) - 1):
            self.assertGreaterEqual(ranked_results[i].final_score, ranked_results[i + 1].final_score)
        
        # Verify RankedMemoryResult structure
        result = ranked_results[0]
        self.assertIsInstance(result, RankedMemoryResult)
        self.assertIsInstance(result.chunk_id, str)
        self.assertIsInstance(result.content, str)
        self.assertIsInstance(result.metadata, dict)
        self.assertIsInstance(result.final_score, float)
        
        # The pinned item should rank highly despite lower semantic similarity
        pinned_result = next((r for r in ranked_results if r.chunk_id == "mem_3"), None)
        self.assertIsNotNone(pinned_result)
        self.assertEqual(pinned_result.priority_score, 1.0)
    
    def test_adaptive_candidate_count(self):
        """Test adaptive candidate count calculation."""
        # Test small memory store
        count = self.engine.get_adaptive_candidate_count(total_memories=50, requested_results=5)
        self.assertGreaterEqual(count, 15)  # At least 3x requested
        self.assertLessEqual(count, 50)     # Not more than total
        
        # Test large memory store
        count = self.engine.get_adaptive_candidate_count(total_memories=1000, requested_results=5)
        self.assertGreaterEqual(count, 15)  # At least 3x requested
        self.assertLessEqual(count, self.engine.config.initial_candidates)  # Respect config limit
        
        # Test very small memory store
        count = self.engine.get_adaptive_candidate_count(total_memories=3, requested_results=5)
        self.assertEqual(count, 3)  # Can't exceed total memories
    
    def test_configuration_loading(self):
        """Test configuration loading from JSON file."""
        # Verify weights were loaded correctly
        self.assertAlmostEqual(self.engine.weights.semantic, 0.6, places=2)
        self.assertAlmostEqual(self.engine.weights.recency, 0.2, places=2)
        self.assertAlmostEqual(self.engine.weights.confidence, 0.15, places=2)
        self.assertAlmostEqual(self.engine.weights.priority, 0.05, places=2)
        
        # Verify config was loaded correctly
        self.assertEqual(self.engine.config.initial_candidates, 20)
        self.assertEqual(self.engine.config.recency_decay_days, 30.0)
        self.assertEqual(self.engine.config.min_confidence_threshold, 0.1)
        self.assertTrue(self.engine.config.enable_hybrid_ranking)

if __name__ == "__main__":
    unittest.main()
