#!/usr/bin/env python3
"""
Phase 8B Working Demonstration

This script demonstrates that Phase 8B: Re-Ingestion & Persistence is fully
functional by showing the complete pipeline from synthesis output to memory store.
"""

import logging
import tempfile
import shutil
import json
from pathlib import Path

# Add SAM root to path
import sys
sys.path.append(str(Path(__file__).parent))

from memory.synthesis import SynthesisEngine, SynthesisConfig
from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def demonstrate_phase8b():
    """Demonstrate Phase 8B functionality with realistic synthesis output."""
    print("🧠 SAM PHASE 8B: RE-INGESTION & PERSISTENCE DEMONSTRATION 🧠")
    print("=" * 70)
    
    # Create temporary test environment
    test_dir = tempfile.mkdtemp()
    memory_dir = Path(test_dir) / "memory_store"
    synthesis_dir = Path(test_dir) / "synthesis_output"
    
    try:
        # Create test memory store
        print("📚 Setting up test memory store...")
        memory_store = MemoryVectorStore(
            store_type=VectorStoreType.SIMPLE,
            storage_directory=str(memory_dir),
            embedding_dimension=384
        )
        
        # Add initial memories
        initial_memories = [
            "Cybersecurity threats are increasing in sophistication and frequency.",
            "Machine learning can enhance threat detection capabilities.",
            "Zero-day vulnerabilities pose significant risks to organizations."
        ]
        
        for i, content in enumerate(initial_memories):
            memory_store.add_memory(
                content=content,
                memory_type=MemoryType.FACT,
                source=f"initial_doc_{i}",
                tags=['cybersecurity'],
                importance_score=0.7
            )
        
        initial_count = len(memory_store.get_all_memories())
        print(f"✅ Initial memory store: {initial_count} memories")
        
        # Create realistic synthesis output
        print("\n🔧 Creating realistic synthesis output...")
        synthesis_data = {
            "synthesis_run_log": {
                "run_id": "demo_synthesis_001",
                "timestamp": "2025-06-15T21:45:00.000000",
                "status": "completed",
                "statistics": {
                    "clusters_analyzed": 3,
                    "prompts_generated": 3,
                    "insights_created": 3
                }
            },
            "insights": [
                {
                    "cluster_id": "cluster_cybersecurity_001",
                    "insight_id": "insight_cyber_001",
                    "synthesized_text": "The escalating sophistication of cybersecurity threats necessitates the integration of machine learning technologies to create proactive defense systems that can identify and neutralize zero-day vulnerabilities before they compromise organizational security.",
                    "source_chunk_ids": ["mem_001", "mem_002", "mem_003"],
                    "confidence_score": 0.89,
                    "novelty_score": 0.76,
                    "utility_score": 0.92,
                    "generated_at": "2025-06-15T21:45:00.000000",
                    "synthesis_metadata": {
                        "source_count": 3,
                        "source_types": ["fact", "fact", "fact"],
                        "synthesis_method": "cognitive_consolidation"
                    }
                },
                {
                    "cluster_id": "cluster_ai_security_002",
                    "insight_id": "insight_ai_002", 
                    "synthesized_text": "Machine learning-powered threat detection represents a paradigm shift from reactive to predictive cybersecurity, enabling organizations to anticipate attack patterns and implement countermeasures before threats materialize.",
                    "source_chunk_ids": ["mem_004", "mem_005"],
                    "confidence_score": 0.84,
                    "novelty_score": 0.81,
                    "utility_score": 0.87,
                    "generated_at": "2025-06-15T21:45:00.000000",
                    "synthesis_metadata": {
                        "source_count": 2,
                        "source_types": ["fact", "insight"],
                        "synthesis_method": "cognitive_consolidation"
                    }
                },
                {
                    "cluster_id": "cluster_vulnerability_003",
                    "insight_id": "insight_vuln_003",
                    "synthesized_text": "Zero-day vulnerability management requires a multi-faceted approach combining continuous monitoring, rapid patch deployment, and behavioral analytics to minimize exposure windows and protect critical assets.",
                    "source_chunk_ids": ["mem_006", "mem_007", "mem_008"],
                    "confidence_score": 0.86,
                    "novelty_score": 0.73,
                    "utility_score": 0.90,
                    "generated_at": "2025-06-15T21:45:00.000000",
                    "synthesis_metadata": {
                        "source_count": 3,
                        "source_types": ["fact", "insight", "procedure"],
                        "synthesis_method": "cognitive_consolidation"
                    }
                }
            ]
        }
        
        # Save synthesis output
        synthesis_dir.mkdir(parents=True, exist_ok=True)
        output_file = synthesis_dir / "demo_synthesis_output.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(synthesis_data, f, indent=2)
        
        print(f"💾 Created synthesis output: {output_file}")
        print(f"   📊 Contains {len(synthesis_data['insights'])} synthesized insights")
        
        # Configure synthesis engine with re-ingestion
        print("\n🔧 Configuring synthesis engine with Phase 8B enabled...")
        config = SynthesisConfig(
            output_directory=str(synthesis_dir),
            enable_reingestion=True,
            enable_deduplication=True
        )
        
        synthesis_engine = SynthesisEngine(config=config)
        
        # Test re-ingestion directly
        print("\n🔄 Testing Phase 8B re-ingestion pipeline...")
        reingested_count = synthesis_engine._reingest_synthetic_insights(
            str(output_file), 
            memory_store
        )
        
        print(f"✅ Re-ingestion completed: {reingested_count} synthetic chunks added")
        
        # Verify results
        print("\n🔍 Verifying Phase 8B results...")
        final_memories = memory_store.get_all_memories()
        final_count = len(final_memories)
        
        print(f"📊 Memory store growth: {initial_count} → {final_count} (+{final_count - initial_count})")
        
        # Find synthetic memories
        synthetic_memories = [
            memory for memory in final_memories 
            if memory.memory_type == MemoryType.SYNTHESIS
        ]
        
        print(f"✨ Synthetic memories created: {len(synthetic_memories)}")
        
        # Display synthetic memory details
        for i, synthetic_memory in enumerate(synthetic_memories, 1):
            print(f"\n📝 Synthetic Memory {i}:")
            print(f"   ID: {synthetic_memory.chunk_id}")
            print(f"   Source: {synthetic_memory.source}")
            print(f"   Type: {synthetic_memory.memory_type.value}")
            print(f"   Importance: {synthetic_memory.importance_score:.2f}")
            print(f"   Tags: {', '.join(synthetic_memory.tags)}")
            print(f"   Content: {synthetic_memory.content[:100]}...")
            
            # Show transparency metadata
            metadata = synthetic_memory.metadata
            print(f"   🔍 Transparency Metadata:")
            print(f"      • Is Synthetic: {metadata.get('is_synthetic')}")
            print(f"      • Cluster ID: {metadata.get('synthesis_cluster_id')}")
            print(f"      • Confidence: {metadata.get('synthesis_confidence_score', 0):.2f}")
            print(f"      • Source Chunks: {len(metadata.get('synthesized_from_chunks', []))}")
        
        # Test searchability
        print("\n🔍 Testing synthetic memory searchability...")
        search_results = memory_store.search_memories(
            query="machine learning cybersecurity threat detection",
            max_results=5
        )
        
        print(f"🔎 Search results: {len(search_results)} memories found")
        
        synthetic_in_results = 0
        for result in search_results:
            if result.chunk.memory_type == MemoryType.SYNTHESIS:
                synthetic_in_results += 1
                print(f"   ✨ Found synthetic insight (similarity: {result.similarity_score:.3f})")
        
        print(f"✅ Synthetic memories in search: {synthetic_in_results}/{len(synthetic_memories)}")
        
        # Final validation
        print("\n✅ PHASE 8B VALIDATION COMPLETE")
        print("=" * 50)
        
        validations = [
            ("Synthesis output processed", reingested_count > 0),
            ("Memory store updated", final_count > initial_count),
            ("Synthetic memories created", len(synthetic_memories) > 0),
            ("Transparency metadata present", all(m.metadata.get('is_synthetic') for m in synthetic_memories)),
            ("Source traceability maintained", all(m.metadata.get('synthesized_from_chunks') for m in synthetic_memories)),
            ("Memories are searchable", synthetic_in_results > 0),
            ("Proper memory type assigned", all(m.memory_type == MemoryType.SYNTHESIS for m in synthetic_memories))
        ]
        
        all_passed = True
        for validation, passed in validations:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}: {validation}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 PHASE 8B: RE-INGESTION & PERSISTENCE - FULLY OPERATIONAL! 🎉")
            print("💡 The Dream Catcher can now 'wake up' and integrate insights into memory!")
        else:
            print("\n❌ Some validations failed. Please check the implementation.")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)
        print("\n🧹 Cleanup completed")

if __name__ == "__main__":
    success = demonstrate_phase8b()
    
    if success:
        print("\n✅ DEMONSTRATION SUCCESSFUL - Phase 8B is ready for deployment!")
    else:
        print("\n❌ DEMONSTRATION FAILED - Please check the errors above.")
        sys.exit(1)
