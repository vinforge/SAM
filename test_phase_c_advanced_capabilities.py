#!/usr/bin/env python3
"""
Test script for SAM's Cognitive Memory Core - Phase C: Advanced Capabilities
Tests advanced graph reasoning, real-time integration, citation tracking, and performance optimization.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add SAM to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_advanced_graph_reasoning():
    """Test the Advanced Graph Reasoning Engine."""
    print("\n🧠 Testing Advanced Graph Reasoning Engine...")
    
    try:
        from sam.memory.graph.advanced_reasoning import AdvancedGraphReasoner
        
        # Initialize reasoning engine
        reasoner = AdvancedGraphReasoner()
        
        print(f"✅ Advanced Graph Reasoner initialized")
        print(f"   📊 Max reasoning depth: {reasoner.max_reasoning_depth}")
        print(f"   🎯 Confidence threshold: {reasoner.min_confidence_threshold}")
        
        # Test different types of reasoning
        test_queries = [
            {
                "query": "How does artificial intelligence relate to machine learning?",
                "types": ["semantic", "causal"],
                "description": "Semantic and causal reasoning"
            },
            {
                "query": "What causes deep learning to be more effective than traditional methods?",
                "types": ["causal", "temporal"],
                "description": "Causal and temporal reasoning"
            },
            {
                "query": "Compare neural networks to biological brain structures",
                "types": ["analogical", "semantic"],
                "description": "Analogical and semantic reasoning"
            },
            {
                "query": "Explain the comprehensive development of AI over time",
                "types": ["temporal", "semantic", "causal"],
                "description": "Multi-type reasoning"
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n   🔍 Test {i}: {test_case['description']}")
            
            # Perform reasoning
            start_time = time.time()
            result = await reasoner.reason_about_query(
                query=test_case["query"],
                reasoning_types=test_case["types"]
            )
            execution_time = time.time() - start_time
            
            print(f"      ✅ Reasoning completed in {execution_time:.3f}s")
            print(f"      📊 Confidence: {result.confidence:.3f}")
            print(f"      🛤️ Reasoning paths: {len(result.reasoning_paths)}")
            print(f"      🔗 Concept clusters: {len(result.concept_clusters)}")
            print(f"      💡 Key insights: {len(result.key_insights)}")
            print(f"      📏 Max depth: {result.reasoning_depth}")
            
            # Show sample insights
            if result.key_insights:
                print(f"      🧠 Sample insight: {result.key_insights[0]}")
        
        # Test specialized reasoning methods
        print(f"\n   🔍 Testing specialized reasoning methods...")
        
        # Test analogies
        analogies = await reasoner.find_analogies("neural_network", "brain", max_analogies=3)
        print(f"      🔗 Found {len(analogies)} analogies")
        
        # Test causal chains
        chains = await reasoner.trace_causal_chains("artificial_intelligence", max_depth=3)
        print(f"      ⛓️ Found {len(chains)} causal chains")
        
        # Test temporal patterns
        patterns = await reasoner.detect_temporal_patterns(["ai", "ml", "dl"])
        print(f"      ⏰ Found {len(patterns['trends'])} trends, {len(patterns['events'])} events")
        
        # Get statistics
        stats = reasoner.get_reasoning_statistics()
        print(f"      📊 Reasoning stats: {stats}")
        
        print("✅ Advanced Graph Reasoning Engine tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Advanced Graph Reasoning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_realtime_graph_integration():
    """Test the Real-Time Graph Database Integration."""
    print("\n🔗 Testing Real-Time Graph Database Integration...")
    
    try:
        from sam.memory.graph.realtime_integration import RealTimeGraphDatabase, ConnectionConfig
        
        # Test with NetworkX (in-memory)
        config = ConnectionConfig(database_type="networkx", max_connections=5)
        db = RealTimeGraphDatabase(config)
        
        await db.initialize()
        
        print(f"✅ Real-time graph database initialized")
        print(f"   🔧 Database type: {config.database_type}")
        print(f"   🔗 Max connections: {config.max_connections}")
        
        # Test different query types
        test_queries = [
            {
                "query": "FIND nodes",
                "description": "Find all nodes",
                "parameters": None
            },
            {
                "query": "FIND nodes WHERE type=Concept",
                "description": "Find concept nodes",
                "parameters": {"type": "Concept"}
            },
            {
                "query": "FIND paths FROM concept_ai TO concept_ml",
                "description": "Find paths between concepts",
                "parameters": {"source": "concept_ai", "target": "concept_ml"}
            },
            {
                "query": "FIND neighbors OF concept_sam",
                "description": "Find neighbors of SAM concept",
                "parameters": {"node": "concept_sam"}
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n   🔍 Test {i}: {test_case['description']}")
            
            # Execute query
            result = await db.query(
                query=test_case["query"],
                parameters=test_case["parameters"],
                use_cache=True
            )
            
            print(f"      ✅ Query executed: {result.success}")
            print(f"      ⏱️ Execution time: {result.execution_time:.3f}s")
            print(f"      📊 Results: {len(result.data)}")
            print(f"      💾 Cached: {result.cached}")
            
            if result.success and result.data:
                print(f"      📝 Sample result: {list(result.data[0].keys())}")
        
        # Test caching performance
        print(f"\n   💾 Testing query caching...")
        
        # First query (cache miss)
        start_time = time.time()
        result1 = await db.query("FIND nodes", use_cache=True)
        first_time = time.time() - start_time
        
        # Second query (cache hit)
        start_time = time.time()
        result2 = await db.query("FIND nodes", use_cache=True)
        second_time = time.time() - start_time
        
        print(f"      🔍 First query: {first_time:.3f}s (cache miss)")
        print(f"      ⚡ Second query: {second_time:.3f}s (cache hit: {result2.cached})")
        
        # Get statistics
        stats = db.get_statistics()
        print(f"      📊 Database stats: {stats}")
        
        # Cleanup
        await db.close()
        
        print("✅ Real-time graph database integration tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Real-time graph integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_citation_engine():
    """Test the Enhanced Citation and Source Tracking Engine."""
    print("\n📚 Testing Enhanced Citation Engine...")
    
    try:
        from sam.memory.graph.citation_engine import CitationEngine, SourceType
        
        # Initialize citation engine
        engine = CitationEngine()
        
        print(f"✅ Citation Engine initialized")
        print(f"   ⚖️ Credibility weights: {engine.credibility_weights}")
        
        # Test source registration
        test_sources = [
            {
                "data": {
                    "type": "document",
                    "title": "Artificial Intelligence: A Modern Approach",
                    "author": "Stuart Russell",
                    "url": "https://example.com/ai-book",
                    "publication_date": datetime(2020, 1, 1)
                },
                "content": "This comprehensive textbook covers artificial intelligence methods and applications.",
                "description": "High-quality academic source"
            },
            {
                "data": {
                    "type": "web_page",
                    "title": "Introduction to Machine Learning",
                    "author": "Unknown",
                    "url": "https://wikipedia.org/ml",
                    "publication_date": datetime(2023, 6, 1)
                },
                "content": "Machine learning is a subset of artificial intelligence.",
                "description": "Wikipedia source"
            },
            {
                "data": {
                    "type": "conversation",
                    "title": "SAM AI Discussion",
                    "author": "User",
                    "publication_date": datetime.now()
                },
                "content": "SAM is an advanced AI system with memory capabilities.",
                "description": "User conversation"
            }
        ]
        
        registered_sources = []
        for i, test_source in enumerate(test_sources, 1):
            print(f"\n   📝 Test {i}: Registering {test_source['description']}")
            
            source_metadata = await engine.register_source(
                source_data=test_source["data"],
                content=test_source["content"]
            )
            
            registered_sources.append(source_metadata)
            
            print(f"      ✅ Source registered: {source_metadata.source_id}")
            print(f"      📊 Credibility score: {source_metadata.credibility_score:.3f}")
            print(f"      🏷️ Credibility level: {source_metadata.credibility_level.value}")
            print(f"      🔗 Domain: {source_metadata.domain}")
        
        # Test citation creation
        print(f"\n   📎 Testing citation creation...")
        
        citations = []
        for i, source in enumerate(registered_sources):
            citation = await engine.create_citation(
                source_id=source.source_id,
                content_snippet=f"Sample content from source {i+1}",
                context="Testing citation creation",
                metadata={"confidence": 0.9, "section": f"Chapter {i+1}"}
            )
            
            citations.append(citation)
            print(f"      ✅ Citation created: {citation.citation_id}")
            print(f"      📊 Confidence: {citation.confidence}")
        
        # Test citation graph generation
        print(f"\n   🕸️ Testing citation graph generation...")
        
        citation_graph = await engine.generate_citation_graph(
            query="artificial intelligence machine learning",
            max_depth=3
        )
        
        print(f"      ✅ Citation graph generated: {citation_graph.graph_id}")
        print(f"      📊 Nodes: {len(citation_graph.nodes)}")
        print(f"      🔗 Edges: {len(citation_graph.edges)}")
        print(f"      📝 Metadata: {citation_graph.metadata}")
        
        # Test credibility assessment updates
        print(f"\n   ⚖️ Testing credibility updates...")
        
        if registered_sources:
            source_id = registered_sources[0].source_id
            updated_assessment = await engine.update_credibility_assessment(
                source_id=source_id,
                new_factors={"peer_validation": 0.9, "content_accuracy": 0.95}
            )
            
            if updated_assessment:
                print(f"      ✅ Credibility updated for {source_id}")
                print(f"      📊 New score: {updated_assessment.overall_score:.3f}")
                print(f"      🧠 Reasoning: {updated_assessment.reasoning}")
        
        # Get statistics
        stats = engine.get_source_statistics()
        print(f"\n   📊 Citation engine statistics:")
        print(f"      📚 Total sources: {stats['total_sources']}")
        print(f"      📎 Total citations: {stats['total_citations']}")
        print(f"      ⚖️ Average credibility: {stats['average_credibility']}")
        print(f"      📈 Credibility distribution: {stats['credibility_distribution']}")
        print(f"      🏷️ Source type distribution: {stats['source_type_distribution']}")
        
        print("✅ Citation Engine tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Citation Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_performance_optimization():
    """Test the Performance Optimization Suite."""
    print("\n⚡ Testing Performance Optimization Suite...")

    try:
        from sam.memory.graph.performance_optimizer import PerformanceOptimizer, LRUCache, QueryPaginator

        # Initialize performance optimizer
        config = {
            "cache_size": 100,
            "cache_ttl_minutes": 5,
            "memory_threshold_mb": 512.0,
            "max_workers": 2
        }

        optimizer = PerformanceOptimizer(config)
        await optimizer.start_background_tasks()

        print(f"✅ Performance Optimizer initialized")
        print(f"   💾 Cache size: {optimizer.cache_size}")
        print(f"   ⏰ Cache TTL: {optimizer.cache_ttl}")
        print(f"   🧠 Memory threshold: {optimizer.memory_threshold_mb} MB")

        # Test LRU Cache
        print(f"\n   💾 Testing LRU Cache...")

        cache = LRUCache(max_size=5, default_ttl=timedelta(seconds=10))

        # Add items to cache
        for i in range(7):  # More than max_size to test eviction
            cache.put(f"key_{i}", f"value_{i}")

        cache_stats = cache.get_stats()
        print(f"      ✅ Cache populated: {cache_stats['size']}/{cache_stats['max_size']}")
        print(f"      📊 Evictions: {cache_stats['evictions']}")

        # Test cache hits and misses
        hit_value = cache.get("key_6")  # Should exist
        miss_value = cache.get("key_0")  # Should be evicted

        final_stats = cache.get_stats()
        print(f"      🎯 Hit rate: {final_stats['hit_rate']:.2f}")
        print(f"      ❌ Miss rate: {final_stats['miss_rate']:.2f}")

        # Test Query Paginator
        print(f"\n   📄 Testing Query Paginator...")

        paginator = QueryPaginator(default_page_size=5, max_page_size=10)

        # Create test data
        test_data = [f"item_{i}" for i in range(23)]

        # Test pagination
        page_1 = paginator.paginate(test_data, page=1, page_size=5)
        page_2 = paginator.paginate(test_data, page=2, page_size=5)
        last_page = paginator.paginate(test_data, page=5, page_size=5)

        print(f"      ✅ Page 1: {len(page_1.data)} items, has_next: {page_1.has_next}")
        print(f"      ✅ Page 2: {len(page_2.data)} items, has_previous: {page_2.has_previous}")
        print(f"      ✅ Last page: {len(last_page.data)} items, total_pages: {last_page.total_pages}")

        # Test cached query decorator
        print(f"\n   🎯 Testing cached query decorator...")

        @optimizer.cached_query(ttl=timedelta(seconds=5))
        async def sample_query(param: str):
            await asyncio.sleep(0.1)  # Simulate work
            return f"result_for_{param}"

        # First call (cache miss)
        start_time = time.time()
        result1 = await sample_query("test")
        first_time = time.time() - start_time

        # Second call (cache hit)
        start_time = time.time()
        result2 = await sample_query("test")
        second_time = time.time() - start_time

        print(f"      🔍 First call: {first_time:.3f}s (cache miss)")
        print(f"      ⚡ Second call: {second_time:.3f}s (cache hit)")
        print(f"      ✅ Results match: {result1 == result2}")

        # Test concurrent processing
        print(f"\n   🔄 Testing concurrent processing...")

        async def sample_processor(item):
            await asyncio.sleep(0.01)  # Simulate work
            return f"processed_{item}"

        test_items = [f"item_{i}" for i in range(10)]

        start_time = time.time()
        results = await optimizer.process_concurrently(
            items=test_items,
            processor_func=sample_processor,
            batch_size=3
        )
        processing_time = time.time() - start_time

        print(f"      ✅ Processed {len(results)} items in {processing_time:.3f}s")
        print(f"      📊 Average time per item: {processing_time/len(results):.3f}s")

        # Test memory optimization
        print(f"\n   🧠 Testing memory optimization...")

        memory_before = optimizer.memory_optimizer.get_memory_usage()
        optimization_result = optimizer.optimize_memory_if_needed()
        memory_after = optimizer.memory_optimizer.get_memory_usage()

        print(f"      📊 Memory before: {memory_before['rss_mb']:.1f} MB")
        print(f"      📊 Memory after: {memory_after['rss_mb']:.1f} MB")
        if optimization_result:
            print(f"      ♻️ Optimization performed: {optimization_result}")
        else:
            print(f"      ✅ No optimization needed")

        # Get performance metrics
        print(f"\n   📊 Testing performance metrics...")

        metrics = optimizer.get_performance_metrics()
        cache_stats = optimizer.get_cache_statistics()

        print(f"      📈 Cache hit rate: {metrics.cache_hit_rate:.2f}")
        print(f"      ⏱️ Average query time: {metrics.avg_query_time:.3f}s")
        print(f"      🧠 Memory usage: {metrics.memory_usage_mb:.1f} MB")
        print(f"      🖥️ CPU usage: {metrics.cpu_usage_percent:.1f}%")
        print(f"      📊 Total operations: {metrics.total_operations}")
        print(f"      ❌ Error rate: {metrics.error_rate:.3f}")

        print(f"      💾 Total cache size: {cache_stats['total_cache_size_mb']:.2f} MB")

        # Cleanup
        await optimizer.shutdown()

        print("✅ Performance Optimization Suite tests completed")
        return True

    except Exception as e:
        print(f"❌ Performance Optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integrated_phase_c_workflow():
    """Test integrated Phase C workflow combining all components."""
    print("\n🔗 Testing Integrated Phase C Workflow...")

    try:
        from sam.memory.graph.advanced_reasoning import AdvancedGraphReasoner
        from sam.memory.graph.realtime_integration import RealTimeGraphDatabase, ConnectionConfig
        from sam.memory.graph.citation_engine import CitationEngine
        from sam.memory.graph.performance_optimizer import PerformanceOptimizer

        # Initialize all components
        reasoner = AdvancedGraphReasoner()

        db_config = ConnectionConfig(database_type="networkx")
        database = RealTimeGraphDatabase(db_config)
        await database.initialize()

        citation_engine = CitationEngine()

        optimizer_config = {"cache_size": 50, "max_workers": 2}
        optimizer = PerformanceOptimizer(optimizer_config)
        await optimizer.start_background_tasks()

        print(f"✅ All Phase C components initialized")

        # Integrated workflow test
        complex_query = "How do neural networks in artificial intelligence systems like SAM relate to biological brain structures and what are the implications for future AI development?"

        print(f"\n🔍 Processing complex query: {complex_query[:60]}...")

        # Step 1: Advanced reasoning
        print(f"   🧠 Step 1: Advanced reasoning analysis...")
        reasoning_result = await reasoner.reason_about_query(
            query=complex_query,
            reasoning_types=["semantic", "analogical", "causal", "temporal"]
        )

        print(f"      ✅ Reasoning paths: {len(reasoning_result.reasoning_paths)}")
        print(f"      🔗 Concept clusters: {len(reasoning_result.concept_clusters)}")
        print(f"      💡 Key insights: {len(reasoning_result.key_insights)}")

        # Step 2: Graph database queries
        print(f"   🔗 Step 2: Graph database integration...")

        @optimizer.cached_query()
        async def enhanced_graph_query(query_text):
            return await database.query(
                "FIND nodes WHERE type=Concept",
                parameters={"type": "Concept"}
            )

        graph_result = await enhanced_graph_query(complex_query)
        print(f"      ✅ Graph query executed: {len(graph_result.data)} results")
        print(f"      ⚡ Cached: {graph_result.cached}")

        # Step 3: Citation tracking
        print(f"   📚 Step 3: Citation and source tracking...")

        # Register sources for the query results
        source_data = {
            "type": "knowledge_base",
            "title": "SAM AI System Knowledge Base",
            "author": "SAM System",
            "publication_date": datetime.now()
        }

        source_metadata = await citation_engine.register_source(
            source_data=source_data,
            content=complex_query
        )

        # Create citations for reasoning results
        citations = []
        for i, insight in enumerate(reasoning_result.key_insights[:3]):
            citation = await citation_engine.create_citation(
                source_id=source_metadata.source_id,
                content_snippet=insight,
                context="Advanced reasoning analysis",
                metadata={"confidence": 0.9}
            )
            citations.append(citation)

        print(f"      ✅ Source registered: {source_metadata.credibility_score:.3f} credibility")
        print(f"      📎 Citations created: {len(citations)}")

        # Step 4: Performance optimization
        print(f"   ⚡ Step 4: Performance optimization...")

        # Process reasoning paths concurrently
        async def analyze_path(path):
            await asyncio.sleep(0.01)  # Simulate analysis
            return {
                "path_id": path.nodes[0] if path.nodes else "unknown",
                "confidence": path.confidence,
                "analysis": f"Analyzed {path.reasoning_type} path"
            }

        path_analyses = await optimizer.process_concurrently(
            items=reasoning_result.reasoning_paths,
            processor_func=analyze_path,
            batch_size=5
        )

        print(f"      ✅ Concurrent analysis: {len(path_analyses)} paths processed")

        # Step 5: Generate comprehensive results
        print(f"   📊 Step 5: Generating comprehensive results...")

        # Create citation graph
        citation_graph = await citation_engine.generate_citation_graph(
            query=complex_query,
            max_depth=2
        )

        # Get performance metrics
        performance_metrics = optimizer.get_performance_metrics()

        # Compile integrated results
        integrated_results = {
            "query": complex_query,
            "reasoning": {
                "confidence": reasoning_result.confidence,
                "paths_count": len(reasoning_result.reasoning_paths),
                "clusters_count": len(reasoning_result.concept_clusters),
                "insights": reasoning_result.key_insights[:3],
                "execution_time": reasoning_result.execution_time
            },
            "graph_data": {
                "results_count": len(graph_result.data),
                "execution_time": graph_result.execution_time,
                "cached": graph_result.cached
            },
            "citations": {
                "source_credibility": source_metadata.credibility_score,
                "citations_count": len(citations),
                "graph_nodes": len(citation_graph.nodes),
                "graph_edges": len(citation_graph.edges)
            },
            "performance": {
                "cache_hit_rate": performance_metrics.cache_hit_rate,
                "memory_usage_mb": performance_metrics.memory_usage_mb,
                "concurrent_analyses": len(path_analyses)
            }
        }

        print(f"\n📊 Integrated Phase C Results:")
        print(f"   🧠 Reasoning confidence: {integrated_results['reasoning']['confidence']:.3f}")
        print(f"   🔗 Graph results: {integrated_results['graph_data']['results_count']}")
        print(f"   📚 Source credibility: {integrated_results['citations']['source_credibility']:.3f}")
        print(f"   ⚡ Cache hit rate: {integrated_results['performance']['cache_hit_rate']:.2f}")
        print(f"   🧠 Memory usage: {integrated_results['performance']['memory_usage_mb']:.1f} MB")

        # Cleanup
        await database.close()
        await optimizer.shutdown()

        print("✅ Integrated Phase C workflow test completed")
        return True

    except Exception as e:
        print(f"❌ Integrated Phase C workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all Phase C tests."""
    print("🚀 SAM Cognitive Memory Core - Phase C: Advanced Capabilities Testing")
    print("=" * 80)

    tests = [
        ("Advanced Graph Reasoning Engine", test_advanced_graph_reasoning),
        ("Real-Time Graph Database Integration", test_realtime_graph_integration),
        ("Enhanced Citation and Source Tracking", test_citation_engine),
        ("Performance Optimization Suite", test_performance_optimization),
        ("Integrated Phase C Workflow", test_integrated_phase_c_workflow)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("📊 PHASE C TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 PHASE C: ADVANCED CAPABILITIES COMPLETE!")
        print("✅ SAM's Cognitive Memory Core is now fully operational with:")
        print("   🧠 Advanced multi-type reasoning capabilities")
        print("   🔗 Real-time graph database integration")
        print("   📚 Comprehensive citation and source tracking")
        print("   ⚡ High-performance optimization suite")
        print("   🔄 Integrated workflow processing")
    else:
        print("⚠️ Some tests failed. Please review and fix issues.")

    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
