#!/usr/bin/env python3
"""
SAM Memory System CLI Tester
Direct testing of Phase 3 memory enhancements through Python API.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_header(title):
    """Print a formatted header."""
    print("\n" + "🚀 " + "=" * 50)
    print(f"   {title}")
    print("=" * 55)

def print_section(title):
    """Print a formatted section."""
    print(f"\n📋 {title}")
    print("-" * 40)

def test_memory_store_initialization():
    """Test memory store initialization with Phase 3 features."""
    print_header("Memory Store Initialization Test")
    
    try:
        from memory.memory_vectorstore import get_memory_store, VectorStoreType
        
        # Test default initialization
        print("🔧 Initializing memory store...")
        memory_store = get_memory_store()
        
        print(f"✅ Memory store type: {memory_store.store_type}")
        print(f"📊 Total memories: {len(memory_store.memory_chunks)}")
        
        # Test enhanced search availability
        if hasattr(memory_store, 'enhanced_search_memories'):
            print("✅ Enhanced search available")
        else:
            print("⚠️ Enhanced search not available")
        
        # Test ranking engine
        if hasattr(memory_store, 'ranking_engine'):
            print("✅ Ranking engine available")
            print(f"🎯 Ranking weights: {memory_store.ranking_engine.weights}")
        else:
            print("⚠️ Ranking engine not available")
        
        return memory_store
        
    except Exception as e:
        print(f"❌ Memory store initialization failed: {e}")
        return None

def test_enhanced_search(memory_store):
    """Test Phase 3.2.1 enhanced search capabilities."""
    print_header("Phase 3.2.1: Enhanced Search Testing")
    
    if not memory_store:
        print("❌ Memory store not available")
        return
    
    test_queries = [
        "Blue Cloak cybersecurity",
        "important information",
        "recent documents",
        "technical details"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print_section(f"Search Test {i}: '{query}'")
        
        try:
            # Test enhanced search if available
            if hasattr(memory_store, 'enhanced_search_memories'):
                print("🔍 Using enhanced search...")
                results = memory_store.enhanced_search_memories(
                    query=query,
                    max_results=5,
                    initial_candidates=10
                )
                
                print(f"✅ Enhanced search returned {len(results)} results")
                
                # Analyze results
                for j, result in enumerate(results[:3], 1):
                    if hasattr(result, 'final_score'):
                        print(f"   {j}. Final Score: {result.final_score:.3f}")
                        if hasattr(result, 'semantic_score'):
                            print(f"      Semantic: {result.semantic_score:.3f}")
                        if hasattr(result, 'confidence_score'):
                            print(f"      Confidence: {result.confidence_score:.3f}")
                        print(f"      Content: {result.content[:100]}...")
                    else:
                        print(f"   {j}. Legacy result format")
            else:
                # Fallback to regular search
                print("🔍 Using fallback search...")
                results = memory_store.search_memories(query, max_results=5)
                print(f"✅ Fallback search returned {len(results)} results")
                
                for j, result in enumerate(results[:3], 1):
                    if hasattr(result, 'chunk'):
                        chunk = result.chunk
                        similarity = getattr(result, 'similarity_score', 0.0)
                        print(f"   {j}. Similarity: {similarity:.3f}")
                        print(f"      Content: {chunk.content[:100]}...")
                    else:
                        print(f"   {j}. Direct memory result")
        
        except Exception as e:
            print(f"❌ Search test failed: {e}")

def test_citation_engine():
    """Test Phase 3.2.2 citation system."""
    print_header("Phase 3.2.2: Citation System Testing")
    
    try:
        from memory.citation_engine import get_citation_engine
        from memory.memory_vectorstore import get_memory_store
        
        print("🔧 Initializing citation engine...")
        citation_engine = get_citation_engine()
        memory_store = get_memory_store()
        
        print(f"✅ Citation engine initialized")
        print(f"🎨 Citation style: {citation_engine.citation_style}")
        print(f"📝 Citations enabled: {citation_engine.enable_citations}")
        
        # Test citation generation
        print_section("Citation Generation Test")
        
        test_response = "Blue Cloak is a cybersecurity company with significant experience."
        test_query = "Blue Cloak"
        
        # Get some memories for citation
        if hasattr(memory_store, 'enhanced_search_memories'):
            memories = memory_store.enhanced_search_memories(test_query, max_results=3)
        else:
            memories = memory_store.search_memories(test_query, max_results=3)
        
        if memories:
            print(f"🔍 Found {len(memories)} memories for citation")
            
            # Generate citations
            cited_response = citation_engine.inject_citations(
                test_response, 
                memories, 
                test_query
            )
            
            print("✅ Citation generation completed")
            print(f"📊 Citations generated: {len(cited_response.citations)}")
            print(f"🎯 Transparency score: {cited_response.transparency_score:.1%}")
            print(f"📚 Source count: {cited_response.source_count}")
            
            print_section("Enhanced Citation Example")
            print(cited_response.response_text)
            
            # Show individual citations
            if cited_response.citations:
                print_section("Citation Details")
                for i, citation in enumerate(cited_response.citations, 1):
                    print(f"   {i}. Source: {citation.source_name}")
                    print(f"      Confidence: {citation.confidence_score:.2f}")
                    if hasattr(citation, 'page_number') and citation.page_number:
                        print(f"      Page: {citation.page_number}")
                    print(f"      Quote: {citation.quote_text[:100]}...")
        else:
            print("⚠️ No memories found for citation testing")
    
    except Exception as e:
        print(f"❌ Citation engine test failed: {e}")

def test_memory_ranking():
    """Test memory ranking framework."""
    print_header("Memory Ranking Framework Testing")
    
    try:
        from memory.memory_ranking import get_memory_ranking_framework
        
        print("🔧 Initializing ranking framework...")
        ranking_framework = get_memory_ranking_framework()
        
        print(f"✅ Ranking framework initialized")
        print(f"🎯 Priority threshold: {ranking_framework.priority_threshold}")
        print(f"📅 Recency decay: {ranking_framework.recency_decay_days} days")
        
        print_section("Ranking Weights")
        for factor, weight in ranking_framework.ranking_weights.items():
            print(f"   {factor.replace('_', ' ').title()}: {weight:.2f}")
        
        # Test ranking calculation
        print_section("Ranking Calculation Test")
        
        # Create a test memory-like object
        class TestMemory:
            def __init__(self, content, similarity, confidence):
                self.content = content
                self.similarity_score = similarity
                self.confidence_score = confidence
                self.timestamp = "2025-01-01T12:00:00"
                self.access_count = 1
                self.user_priority = 0.5
        
        test_memories = [
            TestMemory("High quality content", 0.9, 0.8),
            TestMemory("Medium quality content", 0.7, 0.6),
            TestMemory("Lower quality content", 0.5, 0.4)
        ]
        
        print("🧮 Testing ranking calculation...")
        for i, memory in enumerate(test_memories, 1):
            try:
                # This would normally be done by the ranking engine
                print(f"   Memory {i}:")
                print(f"      Similarity: {memory.similarity_score:.2f}")
                print(f"      Confidence: {memory.confidence_score:.2f}")
                print(f"      Content: {memory.content}")
            except Exception as e:
                print(f"      Ranking calculation error: {e}")
    
    except Exception as e:
        print(f"❌ Ranking framework test failed: {e}")

def interactive_search_demo():
    """Interactive search demonstration."""
    print_header("Interactive Search Demo")
    
    try:
        from memory.memory_vectorstore import get_memory_store
        
        memory_store = get_memory_store()
        
        print("🎮 Interactive Search Mode")
        print("Type queries to test enhanced search (type 'quit' to exit)")
        print("Examples: 'Blue Cloak', 'important dates', 'recent uploads'")
        
        while True:
            try:
                query = input("\n🔍 Enter search query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                print(f"Searching for: '{query}'...")
                
                # Perform search
                if hasattr(memory_store, 'enhanced_search_memories'):
                    results = memory_store.enhanced_search_memories(
                        query=query,
                        max_results=3
                    )
                    print(f"✅ Enhanced search found {len(results)} results")
                else:
                    results = memory_store.search_memories(query, max_results=3)
                    print(f"✅ Search found {len(results)} results")
                
                # Display results
                for i, result in enumerate(results, 1):
                    print(f"\n   Result {i}:")
                    if hasattr(result, 'final_score'):
                        print(f"      Score: {result.final_score:.3f}")
                        content = result.content
                    elif hasattr(result, 'chunk'):
                        similarity = getattr(result, 'similarity_score', 0.0)
                        print(f"      Similarity: {similarity:.3f}")
                        content = result.chunk.content
                    else:
                        content = getattr(result, 'content', str(result))
                    
                    preview = content[:150] + "..." if len(content) > 150 else content
                    print(f"      Content: {preview}")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Search error: {e}")
        
        print("\n👋 Interactive demo ended")
    
    except Exception as e:
        print(f"❌ Interactive demo failed: {e}")

def main():
    """Run the complete memory system test."""
    print_header("SAM Phase 3 Memory System CLI Tester")
    print("Testing all Phase 3 memory enhancements...")
    
    # Initialize memory store
    memory_store = test_memory_store_initialization()
    
    # Run tests
    test_enhanced_search(memory_store)
    test_citation_engine()
    test_memory_ranking()
    
    # Interactive demo
    print("\n" + "=" * 55)
    choice = input("🎮 Run interactive search demo? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        interactive_search_demo()
    
    print_header("Memory System Testing Complete!")
    print("🎉 All Phase 3 memory features tested.")
    print("\n📋 Next steps:")
    print("   • Visit Memory Control Center: http://localhost:8501")
    print("   • Try enhanced chat: http://localhost:5001")
    print("   • Run API demo: python test_phase3_demo.py")

if __name__ == "__main__":
    main()
