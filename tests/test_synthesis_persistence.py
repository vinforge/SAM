#!/usr/bin/env python3
"""
Integration Test Suite for SAM Phase 8B: Re-Ingestion & Persistence

This test suite validates the complete end-to-end process of cognitive synthesis
and re-ingestion into SAM's memory store with proper transparency metadata.
"""

import unittest
import tempfile
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Import SAM components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from memory.synthesis import (
    SynthesisEngine, SynthesisConfig, SyntheticChunkFormatter,
    format_synthesis_output
)
from memory.memory_vectorstore import (
    MemoryVectorStore, VectorStoreType, MemoryType, MemoryChunk, get_memory_store
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSynthesisPersistence(unittest.TestCase):
    """Test suite for Phase 8B synthesis persistence functionality."""
    
    def setUp(self):
        """Set up test environment with temporary storage."""
        self.test_dir = tempfile.mkdtemp()
        self.memory_dir = Path(self.test_dir) / "memory_store"
        self.synthesis_dir = Path(self.test_dir) / "synthesis_output"
        
        # Create test memory store
        self.memory_store = MemoryVectorStore(
            store_type=VectorStoreType.SIMPLE,
            storage_directory=str(self.memory_dir),
            embedding_dimension=384
        )
        
        # Add some test memories for clustering
        self._populate_test_memories()
        
        logger.info(f"Test setup complete: {self.test_dir}")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        logger.info("Test cleanup complete")
    
    def _populate_test_memories(self):
        """Populate memory store with test data for clustering."""
        test_memories = [
            {
                'content': "Cybersecurity threats are increasing in sophistication and frequency.",
                'memory_type': MemoryType.FACT,
                'source': "security_report_1",
                'tags': ['cybersecurity', 'threats'],
                'importance_score': 0.8
            },
            {
                'content': "Advanced persistent threats target critical infrastructure systems.",
                'memory_type': MemoryType.FACT,
                'source': "security_report_2", 
                'tags': ['cybersecurity', 'apt', 'infrastructure'],
                'importance_score': 0.9
            },
            {
                'content': "Zero-day vulnerabilities pose significant risks to enterprise networks.",
                'memory_type': MemoryType.FACT,
                'source': "security_report_3",
                'tags': ['cybersecurity', 'vulnerabilities', 'enterprise'],
                'importance_score': 0.85
            },
            {
                'content': "Machine learning algorithms can detect anomalous network behavior.",
                'memory_type': MemoryType.INSIGHT,
                'source': "ai_security_paper",
                'tags': ['machine_learning', 'cybersecurity', 'detection'],
                'importance_score': 0.7
            },
            {
                'content': "Automated threat response systems reduce incident response time.",
                'memory_type': MemoryType.INSIGHT,
                'source': "automation_study",
                'tags': ['automation', 'cybersecurity', 'response'],
                'importance_score': 0.75
            },
            {
                'content': "Artificial intelligence enhances cybersecurity threat detection capabilities.",
                'memory_type': MemoryType.FACT,
                'source': "ai_security_report",
                'tags': ['ai', 'cybersecurity', 'detection'],
                'importance_score': 0.8
            },
            {
                'content': "Network security monitoring requires real-time analysis of traffic patterns.",
                'memory_type': MemoryType.FACT,
                'source': "network_security_guide",
                'tags': ['network', 'security', 'monitoring'],
                'importance_score': 0.7
            },
            {
                'content': "Behavioral analytics can identify insider threats and anomalous activities.",
                'memory_type': MemoryType.INSIGHT,
                'source': "behavioral_analytics_paper",
                'tags': ['behavioral', 'analytics', 'insider_threats'],
                'importance_score': 0.8
            }
        ]
        
        for memory_data in test_memories:
            self.memory_store.add_memory(**memory_data)
        
        logger.info(f"Added {len(test_memories)} test memories")
    
    def test_synthetic_chunk_formatter(self):
        """Test the SyntheticChunkFormatter functionality."""
        logger.info("🧪 Testing SyntheticChunkFormatter...")
        
        # Create mock synthesis output
        mock_synthesis_data = {
            "synthesis_run_log": {
                "run_id": "test_synthesis_001",
                "timestamp": "2025-06-15T20:30:00.000000",
                "status": "completed"
            },
            "insights": [
                {
                    "cluster_id": "cluster_001",
                    "insight_id": "insight_cluster_001_test",
                    "synthesized_text": "The convergence of cybersecurity threats and machine learning detection capabilities reveals an opportunity for proactive defense systems that can anticipate and neutralize attacks before they impact critical infrastructure.",
                    "source_chunk_ids": ["chunk_001", "chunk_002", "chunk_003"],
                    "confidence_score": 0.85,
                    "novelty_score": 0.72,
                    "utility_score": 0.89,
                    "generated_at": "2025-06-15T20:30:00.000000"
                }
            ]
        }
        
        # Save mock data to file
        output_file = self.synthesis_dir / "test_synthesis_output.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(mock_synthesis_data, f, indent=2)
        
        # Test chunk formatter
        formatter = SyntheticChunkFormatter(self.memory_store)
        synthetic_chunks = formatter.format_synthesis_output(str(output_file))
        
        # Validate results
        self.assertEqual(len(synthetic_chunks), 1)
        
        chunk = synthetic_chunks[0]
        self.assertIsInstance(chunk, MemoryChunk)
        self.assertEqual(chunk.memory_type, MemoryType.SYNTHESIS)
        self.assertEqual(chunk.source, "SAM Cognitive Synthesis")
        self.assertTrue(chunk.metadata['is_synthetic'])
        self.assertEqual(chunk.metadata['synthesis_cluster_id'], "cluster_001")
        self.assertIn('synthetic', chunk.tags)
        
        logger.info("✅ SyntheticChunkFormatter test passed")
    
    def test_deduplication_mechanism(self):
        """Test the de-duplication mechanism for synthetic chunks."""
        logger.info("🧪 Testing de-duplication mechanism...")
        
        # Create initial synthetic chunk
        initial_chunk = MemoryChunk(
            chunk_id="synth_cluster_001_existing",
            content="Initial synthetic insight about cybersecurity.",
            content_hash="initial_hash",
            embedding=None,
            memory_type=MemoryType.SYNTHESIS,
            source="SAM Cognitive Synthesis",
            timestamp="2025-06-15T20:00:00.000000",
            tags=['synthetic', 'cybersecurity'],
            importance_score=0.7,
            access_count=0,
            last_accessed="2025-06-15T20:00:00.000000",
            metadata={
                'is_synthetic': True,
                'synthesis_cluster_id': 'cluster_001',
                'synthesis_confidence_score': 0.7
            }
        )
        
        # Add to memory store
        self.memory_store.memory_chunks[initial_chunk.chunk_id] = initial_chunk
        
        # Create mock synthesis output with same cluster
        mock_synthesis_data = {
            "synthesis_run_log": {"run_id": "test_dedup", "status": "completed"},
            "insights": [
                {
                    "cluster_id": "cluster_001",  # Same cluster ID
                    "insight_id": "insight_cluster_001_new",
                    "synthesized_text": "Improved synthetic insight with higher confidence.",
                    "source_chunk_ids": ["chunk_001", "chunk_002"],
                    "confidence_score": 0.9,  # Higher confidence
                    "novelty_score": 0.8,
                    "utility_score": 0.85,
                    "generated_at": "2025-06-15T20:30:00.000000"
                }
            ]
        }
        
        # Save and process
        output_file = self.synthesis_dir / "test_dedup_output.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(mock_synthesis_data, f, indent=2)
        
        # Test formatter with deduplication
        formatter = SyntheticChunkFormatter(self.memory_store)
        synthetic_chunks = formatter.format_synthesis_output(str(output_file))
        
        # Should return updated chunk, not new one
        self.assertEqual(len(synthetic_chunks), 1)
        updated_chunk = synthetic_chunks[0]
        
        # Should have same chunk_id but updated content
        self.assertEqual(updated_chunk.chunk_id, initial_chunk.chunk_id)
        self.assertNotEqual(updated_chunk.content, initial_chunk.content)
        self.assertEqual(updated_chunk.metadata['synthesis_confidence_score'], 0.9)
        
        logger.info("✅ De-duplication mechanism test passed")
    
    def test_end_to_end_synthesis_persistence(self):
        """Test complete end-to-end synthesis and persistence pipeline."""
        logger.info("🧪 Testing end-to-end synthesis persistence...")
        
        # Get initial memory count
        initial_memories = self.memory_store.get_all_memories()
        initial_count = len(initial_memories)
        
        # Configure synthesis engine with re-ingestion enabled
        config = SynthesisConfig(
            clustering_eps=0.8,  # Higher eps for small dataset
            clustering_min_samples=2,  # Lower min samples
            min_cluster_size=2,  # Lower for testing
            max_clusters=3,      # Limit for testing
            quality_threshold=0.1,  # Much lower for testing
            min_insight_quality=0.1,  # Much lower for testing
            output_directory=str(self.synthesis_dir),
            enable_reingestion=True,
            enable_deduplication=True
        )
        
        # Create synthesis engine (without LLM for testing)
        synthesis_engine = SynthesisEngine(config=config, llm_client=None)
        
        # Mock the insight generation to return test insights
        def mock_generate_insight(prompt):
            return type('MockInsight', (), {
                'insight_id': f"test_insight_{prompt.cluster_id}",
                'cluster_id': prompt.cluster_id,
                'synthesized_text': f"Test synthetic insight for {prompt.cluster_id}: Advanced cybersecurity measures are essential for protecting critical infrastructure from emerging threats.",
                'source_chunk_ids': [chunk.chunk_id for chunk in prompt.source_chunks[:3]],
                'confidence_score': 0.8,
                'novelty_score': 0.7,
                'utility_score': 0.75,
                'synthesis_metadata': {},
                'generated_at': "2025-06-15T20:30:00.000000"
            })()
        
        # Patch the insight generator for testing
        original_method = synthesis_engine.insight_generator.generate_insight
        synthesis_engine.insight_generator.generate_insight = mock_generate_insight
        
        try:
            # Run synthesis with re-ingestion
            result = synthesis_engine.run_synthesis(self.memory_store)
            
            # Validate synthesis results
            self.assertGreater(result.clusters_found, 0)
            self.assertGreater(result.insights_generated, 0)
            self.assertTrue(result.output_file)
            
            # Check that synthetic chunks were re-ingested
            final_memories = self.memory_store.get_all_memories()
            final_count = len(final_memories)
            
            self.assertGreater(final_count, initial_count)
            
            # Find synthetic memories
            synthetic_memories = [
                memory for memory in final_memories 
                if memory.memory_type == MemoryType.SYNTHESIS
            ]
            
            self.assertGreater(len(synthetic_memories), 0)
            
            # Validate synthetic memory properties
            for synthetic_memory in synthetic_memories:
                self.assertEqual(synthetic_memory.source, "SAM Cognitive Synthesis")
                self.assertTrue(synthetic_memory.metadata['is_synthetic'])
                self.assertIn('synthetic', synthetic_memory.tags)
                self.assertIn('synthesis_cluster_id', synthetic_memory.metadata)
            
            logger.info(f"✅ End-to-end test passed: {len(synthetic_memories)} synthetic insights created")
            
        finally:
            # Restore original method
            synthesis_engine.insight_generator.generate_insight = original_method
    
    def test_synthetic_chunk_retrieval(self):
        """Test that synthetic chunks can be retrieved via search."""
        logger.info("🧪 Testing synthetic chunk retrieval...")
        
        # Add a synthetic chunk directly
        synthetic_chunk_id = self.memory_store.add_memory(
            content="Synthetic insight: AI-powered threat detection systems can reduce security incident response time by 60% while improving accuracy of threat classification.",
            memory_type=MemoryType.SYNTHESIS,
            source="SAM Cognitive Synthesis",
            tags=['synthetic', 'ai', 'cybersecurity', 'threat_detection'],
            importance_score=0.85,
            metadata={
                'is_synthetic': True,
                'synthesis_cluster_id': 'cluster_test',
                'synthesis_confidence_score': 0.85,
                'synthesized_from_chunks': ['chunk_a', 'chunk_b']
            }
        )
        
        # Test semantic search retrieval
        search_results = self.memory_store.search_memories(
            query="AI threat detection systems",
            max_results=5
        )
        
        # Should find the synthetic chunk
        self.assertGreater(len(search_results), 0)
        
        # Check if synthetic chunk is in results
        synthetic_found = False
        for result in search_results:
            if result.chunk.chunk_id == synthetic_chunk_id:
                synthetic_found = True
                self.assertEqual(result.chunk.memory_type, MemoryType.SYNTHESIS)
                self.assertTrue(result.chunk.metadata['is_synthetic'])
                break
        
        self.assertTrue(synthetic_found, "Synthetic chunk not found in search results")
        
        logger.info("✅ Synthetic chunk retrieval test passed")

if __name__ == '__main__':
    logger.info("🧪 Running SAM Phase 8B Integration Tests 🧪")
    unittest.main(verbosity=2)
