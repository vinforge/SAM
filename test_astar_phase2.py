#!/usr/bin/env python3
"""
Test script for A* Search Planner Phase 2: LLM Heuristics & Action Expansion

This script tests the LLM-based components of the A* search implementation:
- HeuristicEstimator: LLM-based cost-to-go estimation
- ActionExpander: LLM-based action generation
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockLLMInterface:
    """Mock LLM interface for testing."""
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 100) -> str:
        """Mock LLM generation."""
        
        # Simulate heuristic estimation responses
        if "ESTIMATE:" in prompt:
            if "complete" in prompt.lower() or "finished" in prompt.lower():
                return "0"
            elif "complex" in prompt.lower() or "difficult" in prompt.lower():
                return "15"
            else:
                return "5"
        
        # Simulate action expansion responses
        elif "SUGGESTED ACTIONS:" in prompt:
            if "document" in prompt.lower():
                return """- summarize_document
- extract_key_questions
- deep_analyze_document"""
            elif "research" in prompt.lower():
                return """- web_search
- arxiv_search
- synthesize_information"""
            else:
                return """- analyze_conversation_context
- search_memory
- create_structured_response"""
        
        return "Mock response"

def test_heuristic_estimator():
    """Test HeuristicEstimator functionality."""
    print("🧪 Testing HeuristicEstimator")
    print("-" * 35)
    
    try:
        from sam.agent_zero.planning import (
            PlanningState, HeuristicEstimator, SAMContextManager
        )
        
        # Create mock LLM and context manager
        mock_llm = MockLLMInterface()
        context_manager = SAMContextManager()
        
        # Add some context
        context_manager.document_context.add_document(
            "research_paper.pdf", 
            {"type": "pdf", "size": 1024}
        )
        
        # Create estimator
        estimator = HeuristicEstimator(
            llm_interface=mock_llm,
            context_manager=context_manager,
            max_cost=50
        )
        print("✅ Created HeuristicEstimator with mock LLM")
        
        # Test basic cost estimation
        state = PlanningState(
            task_description="Analyze uploaded research paper",
            action_history=["read_abstract"],
            current_observation="Abstract discusses AI safety challenges",
            document_context={"research_paper.pdf": {"analyzed": True}}
        )
        
        cost = estimator.estimate_cost_to_go(state)
        print(f"✅ Basic cost estimation: {cost}")
        
        # Test detailed estimation
        detailed_estimate = estimator.get_detailed_estimate(state)
        print(f"✅ Detailed estimate: cost={detailed_estimate.estimated_cost}, confidence={detailed_estimate.confidence:.2f}")
        print(f"   Reasoning: {detailed_estimate.reasoning[:50]}...")
        print(f"   Context factors: {detailed_estimate.context_factors}")
        
        # Test fallback estimation (no LLM)
        fallback_estimator = HeuristicEstimator(llm_interface=None)
        fallback_cost = fallback_estimator.estimate_cost_to_go(state)
        print(f"✅ Fallback estimation: {fallback_cost}")
        
        # Test caching
        cached_cost = estimator.estimate_cost_to_go(state)  # Should use cache
        print(f"✅ Cached estimation: {cached_cost}")
        
        # Test statistics
        stats = estimator.get_estimation_stats()
        print(f"✅ Estimation stats: cache_hit_rate={stats['cache_hit_rate']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ HeuristicEstimator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_action_expander():
    """Test ActionExpander functionality."""
    print("\n🧪 Testing ActionExpander")
    print("-" * 30)
    
    try:
        from sam.agent_zero.planning import (
            PlanningState, ActionExpander, SAMContextManager, get_sam_tool_registry
        )
        
        # Create mock LLM and components
        mock_llm = MockLLMInterface()
        context_manager = SAMContextManager()
        tool_registry = get_sam_tool_registry()
        
        # Add context
        context_manager.document_context.add_document(
            "research_paper.pdf",
            {"type": "pdf", "analyzed": False}
        )
        
        # Create expander
        expander = ActionExpander(
            llm_interface=mock_llm,
            tool_registry=tool_registry,
            context_manager=context_manager,
            max_actions=5
        )
        print("✅ Created ActionExpander with mock LLM")
        
        # Test basic action expansion
        state = PlanningState(
            task_description="Analyze uploaded research paper and extract insights",
            action_history=[],
            current_observation="Starting analysis",
            document_context={"research_paper.pdf": {"uploaded": True}}
        )
        
        actions = expander.get_next_possible_actions(state)
        print(f"✅ Generated {len(actions)} possible actions: {actions}")
        
        # Test detailed action candidates
        candidates = expander.get_action_candidates(state)
        print(f"✅ Generated {len(candidates)} action candidates:")
        for i, candidate in enumerate(candidates[:3]):
            print(f"   {i+1}. {candidate.action_name} (confidence: {candidate.confidence:.2f})")
            print(f"      {candidate.description}")
        
        # Test with different state
        research_state = PlanningState(
            task_description="Research AI safety papers and create summary",
            action_history=["summarize_document"],
            current_observation="Document summarized successfully"
        )
        
        research_actions = expander.get_next_possible_actions(research_state)
        print(f"✅ Research task actions: {research_actions}")
        
        # Test without LLM (fallback)
        fallback_expander = ActionExpander(
            llm_interface=None,
            tool_registry=tool_registry,
            context_manager=context_manager
        )
        fallback_actions = fallback_expander.get_next_possible_actions(state)
        print(f"✅ Fallback actions: {len(fallback_actions)} generated")
        
        # Test statistics
        stats = expander.get_expansion_stats()
        print(f"✅ Expansion stats: cache_hit_rate={stats['cache_hit_rate']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ ActionExpander test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase2_integration():
    """Test integration of Phase 2 components."""
    print("\n🧪 Testing Phase 2 Integration")
    print("-" * 35)
    
    try:
        from sam.agent_zero.planning import (
            PlanningState, SearchNodeFactory, HeuristicEstimator, ActionExpander,
            SAMContextManager, get_sam_tool_registry
        )
        
        # Create integrated system
        mock_llm = MockLLMInterface()
        context_manager = SAMContextManager()
        tool_registry = get_sam_tool_registry()
        
        # Set up context
        context_manager.document_context.add_document(
            "ai_safety_paper.pdf",
            {"type": "pdf", "pages": 20, "uploaded_at": "2024-01-01"}
        )
        context_manager.conversation_context.add_message(
            "user", "Please analyze this AI safety paper and extract key insights"
        )
        
        # Create components
        estimator = HeuristicEstimator(llm_interface=mock_llm, context_manager=context_manager)
        expander = ActionExpander(llm_interface=mock_llm, tool_registry=tool_registry, context_manager=context_manager)
        
        print("✅ Created integrated Phase 2 system")
        
        # Simulate planning scenario
        initial_context = context_manager.get_planning_context()
        root_node = SearchNodeFactory.create_root_node(
            "Analyze AI safety paper and provide comprehensive insights",
            initial_context
        )
        
        # Get heuristic estimate for root
        h_score = estimator.estimate_cost_to_go(root_node.state)
        root_node.update_h_score(h_score)
        print(f"✅ Root node heuristic: h={h_score}, f={root_node.f_score}")
        
        # Expand possible actions
        possible_actions = expander.get_next_possible_actions(root_node.state)
        print(f"✅ Possible actions from root: {len(possible_actions)}")
        
        # Create child nodes and estimate their costs
        child_nodes = []
        for action in possible_actions[:3]:  # Test first 3 actions
            child_state = root_node.state.add_action(action, f"Executed {action}")
            child_h_score = estimator.estimate_cost_to_go(child_state)
            child_node = SearchNodeFactory.create_child_node(
                root_node, action, f"Executed {action}", child_h_score
            )
            child_nodes.append(child_node)
            print(f"   Child '{action}': g={child_node.state.g_score}, h={child_h_score}, f={child_node.f_score}")
        
        # Verify that child nodes have reasonable f-scores
        for child in child_nodes:
            assert child.f_score > 0, f"Child node {child.state.action_history[-1]} has invalid f-score"
            assert child.f_score <= 100, f"Child node {child.state.action_history[-1]} has unreasonably high f-score"
        
        print("✅ Phase 2 integration test passed - components work together")
        
        # Test performance with caching
        print("\n🔍 Testing performance with caching:")
        
        # Multiple estimates of same state (should use cache)
        for i in range(3):
            cached_h = estimator.estimate_cost_to_go(root_node.state)
            cached_actions = expander.get_next_possible_actions(root_node.state)
        
        estimator_stats = estimator.get_estimation_stats()
        expander_stats = expander.get_expansion_stats()
        
        print(f"✅ Estimator cache hit rate: {estimator_stats['cache_hit_rate']:.2f}")
        print(f"✅ Expander cache hit rate: {expander_stats['cache_hit_rate']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 2 integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting A* Search Planner Phase 2 Tests")
    print("=" * 60)
    
    # Run Phase 2 tests
    test1_passed = test_heuristic_estimator()
    test2_passed = test_action_expander()
    test3_passed = test_phase2_integration()
    
    print("\n" + "=" * 60)
    print("📊 PHASE 2 TEST RESULTS:")
    print(f"   HeuristicEstimator: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   ActionExpander: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"   Integration: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 PHASE 2 COMPLETE! LLM Heuristics & Action Expansion working correctly.")
        print("\n💡 Ready for Phase 3: A* Planner Integration")
        print("   • Assemble components into functional A* planner")
        print("   • Integrate with SAM's execution engine")
        print("   • Complete search algorithm implementation")
        sys.exit(0)
    else:
        print("\n💥 PHASE 2 INCOMPLETE! Some components need attention.")
        sys.exit(1)
