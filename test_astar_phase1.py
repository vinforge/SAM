#!/usr/bin/env python3
"""
Test script for A* Search Planner Phase 1: Core Data Structures

This script tests the foundational components of the A* search implementation:
- PlanningState: State representation in search tree
- SearchNode: Wrapper with search metadata
- Frontier: Priority queue for node management
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_planning_state():
    """Test PlanningState functionality."""
    print("🧪 Testing PlanningState")
    print("-" * 30)
    
    try:
        from sam.agent_zero.planning import PlanningState
        
        # Test basic state creation
        initial_state = PlanningState(
            task_description="Analyze uploaded research paper on AI safety",
            action_history=[],
            current_observation="Starting analysis"
        )
        
        print(f"✅ Created initial state: {initial_state.get_state_summary()}")
        
        # Test adding actions
        state_after_action = initial_state.add_action(
            "summarize_document", 
            "Document summarized successfully"
        )
        
        print(f"✅ Added action: {state_after_action.get_state_summary()}")
        
        # Test action path reconstruction
        action_path = state_after_action.get_action_path()
        print(f"✅ Action path: {action_path}")
        
        # Test context methods
        context_summary = state_after_action.get_context_summary()
        print(f"✅ Context summary: {context_summary}")
        
        # Test state equality
        duplicate_state = PlanningState(
            task_description="Analyze uploaded research paper on AI safety",
            action_history=["summarize_document"],
            current_observation="Document summarized successfully"
        )
        
        is_equal = state_after_action == duplicate_state
        print(f"✅ State equality test: {is_equal}")
        
        return True
        
    except Exception as e:
        print(f"❌ PlanningState test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_node():
    """Test SearchNode functionality."""
    print("\n🧪 Testing SearchNode")
    print("-" * 30)
    
    try:
        from sam.agent_zero.planning import PlanningState, SearchNode, SearchNodeFactory
        
        # Test node creation via factory
        root_node = SearchNodeFactory.create_root_node(
            "Research AI safety papers and create summary",
            initial_context={'documents': ['paper1.pdf'], 'memory': ['previous_research']}
        )
        
        print(f"✅ Created root node: {root_node.get_search_summary()}")
        
        # Test heuristic score update
        root_node.update_h_score(15)
        print(f"✅ Updated h_score: f={root_node.f_score}, g={root_node.state.g_score}, h={root_node.h_score}")
        
        # Test child node creation
        child_node = SearchNodeFactory.create_child_node(
            root_node,
            "analyze_document_structure",
            "Document has 5 sections: abstract, intro, methods, results, conclusion",
            h_score=12
        )
        
        print(f"✅ Created child node: {child_node.get_search_summary()}")
        
        # Test node comparison
        is_child_better = child_node.is_better_than(root_node)
        print(f"✅ Child better than root: {is_child_better}")
        
        # Test node expansion
        root_node.mark_expanded()
        print(f"✅ Marked root as expanded: expanded={root_node.expanded}, in_frontier={root_node.in_frontier}")
        
        return True
        
    except Exception as e:
        print(f"❌ SearchNode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontier():
    """Test Frontier functionality."""
    print("\n🧪 Testing Frontier")
    print("-" * 30)
    
    try:
        from sam.agent_zero.planning import Frontier, SearchNodeFactory
        
        # Create frontier
        frontier = Frontier(max_size=10)
        print(f"✅ Created frontier: {frontier}")
        
        # Create and add multiple nodes
        nodes = []
        for i in range(5):
            node = SearchNodeFactory.create_root_node(f"Task {i}")
            node.update_h_score(10 - i)  # Varying heuristic scores
            nodes.append(node)
            
            added = frontier.add(node)
            print(f"✅ Added node {i}: {added}, f_score={node.f_score}")
        
        print(f"✅ Frontier size: {frontier.size()}")
        print(f"✅ Frontier summary: {frontier.get_frontier_summary()}")
        
        # Test popping nodes (should come out in f_score order)
        print("\n🔍 Popping nodes in priority order:")
        while not frontier.is_empty():
            best_node = frontier.pop()
            print(f"  Popped: f={best_node.f_score}, task='{best_node.state.task_description}'")
        
        print(f"✅ Frontier empty: {frontier.is_empty()}")
        
        # Test statistics
        stats = frontier.get_statistics()
        print(f"✅ Final statistics: added={stats['total_added']}, popped={stats['total_popped']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontier test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration of all Phase 1 components."""
    print("\n🧪 Testing Phase 1 Integration")
    print("-" * 35)
    
    try:
        from sam.agent_zero.planning import PlanningState, SearchNode, SearchNodeFactory, Frontier
        
        # Simulate a mini A* search scenario
        task = "Analyze research paper and extract key insights"
        
        # Create initial state with context
        initial_context = {
            'documents': {'paper.pdf': 'AI safety research paper'},
            'memory': ['previous_ai_research', 'safety_guidelines'],
            'conversation': {'user_query': 'What are the main findings?'}
        }
        
        root_node = SearchNodeFactory.create_root_node(task, initial_context)
        root_node.update_h_score(20)
        
        print(f"✅ Created root with context: {root_node.state.get_context_summary()}")
        
        # Create frontier and add root
        frontier = Frontier()
        frontier.add(root_node)
        
        # Simulate expanding the root node
        possible_actions = [
            ("read_abstract", "Abstract discusses AI alignment challenges"),
            ("analyze_methodology", "Uses reinforcement learning with human feedback"),
            ("extract_key_findings", "Identifies 3 major safety concerns")
        ]
        
        # Add child nodes for each possible action
        for action, observation in possible_actions:
            child_node = SearchNodeFactory.create_child_node(
                root_node, action, observation, h_score=15
            )
            frontier.add(child_node)
            print(f"  Added child: {action} -> f={child_node.f_score}")
        
        # Mark root as expanded
        root_node.mark_expanded()
        
        # Show frontier state
        print(f"✅ Frontier after expansion: {frontier.get_frontier_summary()}")
        
        # Pop best node
        best_node = frontier.pop()
        print(f"✅ Best node to explore: {best_node.state.action_history[-1] if best_node.state.action_history else 'root'}")
        
        # Verify the best node has the expected properties
        assert best_node.f_score <= 16, f"Expected f_score <= 16, got {best_node.f_score}"
        assert len(best_node.state.action_history) <= 1, "Expected at most 1 action in history"
        
        print("✅ Integration test passed - all components work together")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sam_tool_registry():
    """Test SAM Tool Registry functionality."""
    print("\n🧪 Testing SAM Tool Registry")
    print("-" * 35)

    try:
        from sam.agent_zero.planning import get_sam_tool_registry, ToolCategory

        # Get registry instance
        registry = get_sam_tool_registry()
        print(f"✅ Created tool registry: {len(registry.get_tool_names())} tools")

        # Test getting tools by category
        doc_tools = registry.get_tools_by_category(ToolCategory.DOCUMENT_ANALYSIS)
        print(f"✅ Document analysis tools: {len(doc_tools)}")

        # Test getting available tools with context
        context = {
            'documents': {'paper.pdf': 'research paper'},
            'memory': ['previous_research']
        }
        available_tools = registry.get_available_tools(context)
        print(f"✅ Available tools with context: {len(available_tools)}")

        # Test task-specific tool recommendations
        task = "Analyze uploaded research paper and extract key insights"
        relevant_tools = registry.get_tools_for_task_type(task)
        print(f"✅ Relevant tools for task: {len(relevant_tools)}")

        # Test specific tool retrieval
        summarize_tool = registry.get_tool("summarize_document")
        if summarize_tool:
            print(f"✅ Retrieved tool: {summarize_tool.name} - {summarize_tool.description}")
            can_execute = summarize_tool.can_execute(context)
            print(f"✅ Tool can execute with context: {can_execute}")

        # Test registry summary
        summary = registry.get_registry_summary()
        print(f"✅ Registry summary: {summary['total_tools']} tools in {len(summary['categories'])} categories")

        return True

    except Exception as e:
        print(f"❌ SAM Tool Registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_state_similarity():
    """Test State Similarity Detection functionality."""
    print("\n🧪 Testing State Similarity Detection")
    print("-" * 40)

    try:
        from sam.agent_zero.planning import PlanningState, StateSimilarityDetector

        # Create similarity detector
        detector = StateSimilarityDetector(similarity_threshold=0.7)
        print("✅ Created similarity detector")

        # Create similar states
        state1 = PlanningState(
            task_description="Analyze research paper on AI safety",
            action_history=["read_abstract", "analyze_methodology"],
            current_observation="Found 3 key safety concerns"
        )

        state2 = PlanningState(
            task_description="Analyze research paper on AI safety",
            action_history=["read_abstract", "analyze_results"],
            current_observation="Identified safety challenges"
        )

        # Test similarity computation
        metrics = detector.compute_similarity(state1, state2)
        print(f"✅ Similarity metrics: overall={metrics.overall_similarity:.2f}")
        print(f"   Task: {metrics.task_similarity:.2f}, Action: {metrics.action_similarity:.2f}")
        print(f"   Context: {metrics.context_similarity:.2f}, Obs: {metrics.observation_similarity:.2f}")

        # Test similarity detection
        are_similar = detector.are_states_similar(state1, state2)
        print(f"✅ States are similar: {are_similar}")

        # Test state signature generation
        signature1 = detector.get_state_signature(state1)
        signature2 = detector.get_state_signature(state2)
        print(f"✅ Generated signatures: {signature1[:8]}... vs {signature2[:8]}...")

        # Test finding similar states
        candidate_states = [state1, state2]
        state3 = PlanningState(
            task_description="Analyze research paper on AI safety",
            action_history=["read_abstract"],
            current_observation="Starting analysis"
        )

        similar_states = detector.find_similar_states(state3, candidate_states)
        print(f"✅ Found {len(similar_states)} similar states")

        return True

    except Exception as e:
        print(f"❌ State Similarity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sam_context_manager():
    """Test SAM Context Manager functionality."""
    print("\n🧪 Testing SAM Context Manager")
    print("-" * 35)

    try:
        from sam.agent_zero.planning import SAMContextManager

        # Create context manager
        context_manager = SAMContextManager()
        print("✅ Created SAM context manager")

        # Test document context
        context_manager.document_context.add_document(
            "research_paper.pdf",
            {"size": 1024, "type": "pdf", "uploaded_at": "2024-01-01"}
        )
        context_manager.document_context.set_analysis_result(
            "research_paper.pdf", "summary", "This paper discusses AI safety challenges"
        )
        print("✅ Added document and analysis result")

        # Test memory context
        context_manager.memory_context.add_relevant_memory({
            "id": "mem_001",
            "content": "Previous AI safety research",
            "memory_type": "episodic"
        })
        context_manager.memory_context.add_memory_query("AI safety challenges")
        print("✅ Added memory context")

        # Test conversation context
        context_manager.conversation_context.add_message("user", "Analyze this research paper")
        context_manager.conversation_context.add_message("assistant", "I'll analyze the paper for you")
        context_manager.conversation_context.set_user_intent("document_analysis")
        print("✅ Added conversation context")

        # Test getting planning context
        planning_context = context_manager.get_planning_context()
        print(f"✅ Generated planning context with {len(planning_context)} components")

        # Test context summary
        summary = context_manager.get_context_summary()
        print(f"✅ Context summary: {summary['documents']['count']} docs, {summary['memory']['relevant_memories_count']} memories")

        # Test tool-specific context
        doc_context = context_manager.get_context_for_tool("summarize_document")
        print(f"✅ Tool-specific context: {len(doc_context)} components")

        # Test caching
        context_manager.cache_computation_result("test_key", {"result": "cached_value"})
        cached_result = context_manager.get_cached_result("test_key")
        print(f"✅ Caching works: {cached_result is not None}")

        return True

    except Exception as e:
        print(f"❌ SAM Context Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting A* Search Planner Phase 1 & 1.5 Tests")
    print("=" * 65)

    # Run Phase 1 tests
    test1_passed = test_planning_state()
    test2_passed = test_search_node()
    test3_passed = test_frontier()
    test4_passed = test_integration()

    # Run Phase 1.5 tests
    test5_passed = test_sam_tool_registry()
    test6_passed = test_state_similarity()
    test7_passed = test_sam_context_manager()

    print("\n" + "=" * 65)
    print("📊 TEST RESULTS:")
    print("Phase 1 - Core Data Structures:")
    print(f"   PlanningState: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   SearchNode: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"   Frontier: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    print(f"   Integration: {'✅ PASSED' if test4_passed else '❌ FAILED'}")

    print("Phase 1.5 - SAM Context Integration:")
    print(f"   SAM Tool Registry: {'✅ PASSED' if test5_passed else '❌ FAILED'}")
    print(f"   State Similarity: {'✅ PASSED' if test6_passed else '❌ FAILED'}")
    print(f"   SAM Context Manager: {'✅ PASSED' if test7_passed else '❌ FAILED'}")

    all_passed = all([test1_passed, test2_passed, test3_passed, test4_passed,
                     test5_passed, test6_passed, test7_passed])

    if all_passed:
        print("\n🎉 PHASES 1 & 1.5 COMPLETE! Ready for Phase 2: LLM Heuristics & Action Expansion")
        print("\n💡 Next Phase Features:")
        print("   • LLM-based heuristic estimation for A* search")
        print("   • SAM-aware action expansion with tool integration")
        print("   • Context-aware cost estimation")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED! Components need attention before proceeding.")
        sys.exit(1)
