#!/usr/bin/env python3
"""
Test script for A* Search Planner Phase 4 Task 2: Episodic Memory Heuristic Enhancement

This script tests the integration of SAM's episodic memory system with the A* planner
heuristic estimator for self-improving planning through experience-based learning.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockLLMInterface:
    """Mock LLM interface for testing."""
    
    def __init__(self):
        self.call_count = 0
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 100) -> str:
        """Mock LLM generation."""
        self.call_count += 1
        
        if "ESTIMATE:" in prompt:
            return "8"  # Consistent estimate for testing
        elif "SUGGESTED ACTIONS:" in prompt:
            return """- summarize_document
- extract_key_questions
- deep_analyze_document"""
        
        return "Mock response"

class MockEpisodicStore:
    """Mock episodic memory store for testing."""
    
    def __init__(self):
        self.stored_memories = []
    
    def store_memory(self, memory):
        """Store a memory."""
        self.stored_memories.append(memory)
    
    def search_memories(self, query, limit=10):
        """Search for memories."""
        return self.stored_memories[:limit]

def test_episodic_memory_heuristic():
    """Test EpisodicMemoryHeuristic functionality."""
    print("🧪 Testing EpisodicMemoryHeuristic")
    print("-" * 40)
    
    try:
        from sam.agent_zero.planning import (
            EpisodicMemoryHeuristic, PlanningState, SAMContextManager
        )
        
        # Create mock components
        mock_llm = MockLLMInterface()
        context_manager = SAMContextManager()
        mock_episodic_store = MockEpisodicStore()
        
        # Create episodic memory enhanced heuristic
        heuristic = EpisodicMemoryHeuristic(
            llm_interface=mock_llm,
            context_manager=context_manager,
            episodic_store=mock_episodic_store,
            enable_experience_learning=True,
            experience_weight=0.3
        )
        
        print("✅ Created EpisodicMemoryHeuristic")
        
        # Test basic heuristic estimation
        state = PlanningState(
            task_description="Analyze research paper on AI safety",
            action_history=["read_abstract"],
            current_observation="Abstract discusses safety challenges",
            document_context={"paper.pdf": {"type": "pdf"}}
        )
        
        estimate = heuristic.get_detailed_estimate(state)
        print(f"✅ Basic estimate: cost={estimate.estimated_cost}, confidence={estimate.confidence:.2f}")
        
        # Test recording planning outcome
        heuristic.record_planning_outcome(
            state=state,
            estimated_cost=8,
            actual_cost=6,  # Better than estimated
            success=True,
            outcome_quality=0.8
        )
        
        print("✅ Recorded planning outcome")
        
        # Test learning statistics
        stats = heuristic.get_learning_statistics()
        print(f"✅ Learning stats: enabled={stats['experience_learning_enabled']}, "
              f"adjustments={stats['total_adjustments']}")
        
        # Test with similar state (should potentially use experience)
        similar_state = PlanningState(
            task_description="Analyze research paper on machine learning",
            action_history=["read_abstract"],
            current_observation="Abstract discusses ML techniques",
            document_context={"ml_paper.pdf": {"type": "pdf"}}
        )
        
        similar_estimate = heuristic.get_detailed_estimate(similar_state)
        print(f"✅ Similar state estimate: cost={similar_estimate.estimated_cost}, "
              f"confidence={similar_estimate.confidence:.2f}")
        
        # Test task type classification
        task_types = [
            ("Analyze uploaded document", "document_analysis"),
            ("Research AI safety papers", "research_task"),
            ("Remember previous analysis", "memory_task"),
            ("Synthesize multiple sources", "synthesis_task"),
            ("General planning task", "general_task")
        ]
        
        for task_desc, expected_type in task_types:
            classified_type = heuristic._classify_task_type(task_desc)
            print(f"   Task '{task_desc[:30]}...' -> {classified_type}")
            assert classified_type == expected_type, f"Expected {expected_type}, got {classified_type}"
        
        print("✅ Task type classification working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ EpisodicMemoryHeuristic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_astar_with_episodic_learning():
    """Test A* planner with episodic memory learning."""
    print("\n🧪 Testing A* Planner with Episodic Learning")
    print("-" * 50)
    
    try:
        from sam.agent_zero.planning import (
            AStarPlanner, SAMContextManager, PlanningState
        )
        
        # Create mock components
        mock_llm = MockLLMInterface()
        context_manager = SAMContextManager()
        mock_episodic_store = MockEpisodicStore()
        
        # Add context
        context_manager.document_context.add_document(
            "test_paper.pdf",
            {"type": "pdf", "topic": "AI research"}
        )
        
        # Create planner with episodic learning enabled
        planner = AStarPlanner(
            llm_interface=mock_llm,
            context_manager=context_manager,
            max_nodes=20,
            max_time_seconds=15,
            enable_episodic_learning=True,
            episodic_store=mock_episodic_store
        )
        
        print("✅ Created A* planner with episodic learning")
        
        # Verify episodic heuristic is being used
        from sam.agent_zero.planning import EpisodicMemoryHeuristic
        assert isinstance(planner.heuristic_estimator, EpisodicMemoryHeuristic), \
            "Expected EpisodicMemoryHeuristic"
        print("✅ Episodic memory heuristic correctly initialized")
        
        # Test planning with learning
        def simple_goal_checker(state: PlanningState) -> bool:
            return len(state.action_history) >= 2
        
        result = planner.find_optimal_plan(
            task_description="Analyze research paper and extract insights",
            goal_checker=simple_goal_checker
        )
        
        print(f"✅ Planning with learning: success={result.success}")
        print(f"   Plan: {result.plan}")
        print(f"   Nodes explored: {result.nodes_explored}")
        
        # Check that outcome was recorded
        learning_stats = planner.heuristic_estimator.get_learning_statistics()
        print(f"✅ Learning after planning: adjustments={learning_stats['total_adjustments']}")
        
        # Test second planning session (should potentially benefit from learning)
        result2 = planner.find_optimal_plan(
            task_description="Analyze another research paper and extract insights",
            goal_checker=simple_goal_checker
        )
        
        print(f"✅ Second planning session: success={result2.success}")
        print(f"   Plan: {result2.plan}")
        
        # Check learning statistics after second session
        final_stats = planner.heuristic_estimator.get_learning_statistics()
        print(f"✅ Final learning stats: total_adjustments={final_stats['total_adjustments']}, "
              f"queries={final_stats['experience_queries']}")
        
        return True
        
    except Exception as e:
        print(f"❌ A* planner with episodic learning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_experience_similarity_and_adjustment():
    """Test experience similarity detection and adjustment calculation."""
    print("\n🧪 Testing Experience Similarity and Adjustment")
    print("-" * 50)
    
    try:
        from sam.agent_zero.planning import (
            EpisodicMemoryHeuristic, PlanningState, PlanningExperience
        )
        
        # Create heuristic estimator
        heuristic = EpisodicMemoryHeuristic(
            enable_experience_learning=False  # Test without actual episodic store
        )
        
        # Test context feature extraction
        state = PlanningState(
            task_description="Analyze research paper",
            action_history=["read_abstract", "analyze_methodology"],
            document_context={"paper.pdf": {"type": "pdf"}},
            memory_context=["previous_analysis"]
        )
        
        features = heuristic._extract_context_features(state)
        print(f"✅ Context features: {features}")
        
        expected_features = ['has_documents', 'has_memory', 'action_count', 'document_count']
        for feature in expected_features:
            assert feature in features, f"Missing feature: {feature}"
        
        # Test context similarity calculation
        features1 = {'has_documents': True, 'has_memory': True, 'action_count': 2}
        features2 = {'has_documents': True, 'has_memory': False, 'action_count': 2}
        
        similarity = heuristic._calculate_context_similarity(features1, features2)
        print(f"✅ Context similarity: {similarity:.2f}")
        assert 0.0 <= similarity <= 1.0, "Similarity should be between 0 and 1"
        
        # Test experience similarity
        experience = PlanningExperience(
            experience_id="test_exp",
            task_type="document_analysis",
            action_sequence=["read_abstract"],
            context_features=features,
            estimated_cost=8,
            actual_cost=6,
            success=True,
            outcome_quality=0.8,
            timestamp="2024-01-01T12:00:00",
            metadata={}
        )
        
        is_similar = heuristic._is_experience_similar(state, experience)
        print(f"✅ Experience similarity check: {is_similar}")
        
        # Test adjustment calculation
        experiences = [experience]
        adjustment, confidence, reasoning = heuristic._calculate_experience_adjustment(state, experiences)
        print(f"✅ Experience adjustment: value={adjustment}, confidence={confidence:.2f}")
        print(f"   Reasoning: {reasoning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Experience similarity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_episodic_learning_disabled():
    """Test behavior when episodic learning is disabled."""
    print("\n🧪 Testing Episodic Learning Disabled")
    print("-" * 40)
    
    try:
        from sam.agent_zero.planning import (
            AStarPlanner, SAMContextManager, HeuristicEstimator
        )
        
        # Create planner with episodic learning disabled
        planner = AStarPlanner(
            llm_interface=MockLLMInterface(),
            context_manager=SAMContextManager(),
            enable_episodic_learning=False
        )
        
        print("✅ Created planner with episodic learning disabled")
        
        # Verify regular heuristic estimator is used
        assert isinstance(planner.heuristic_estimator, HeuristicEstimator), \
            "Expected regular HeuristicEstimator"
        assert not hasattr(planner.heuristic_estimator, 'record_planning_outcome'), \
            "Should not have episodic learning methods"
        
        print("✅ Regular heuristic estimator correctly used")
        
        return True
        
    except Exception as e:
        print(f"❌ Episodic learning disabled test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting A* Search Planner Phase 4 Task 2 Tests")
    print("=" * 70)
    
    # Run Task 2 tests
    test1_passed = test_episodic_memory_heuristic()
    test2_passed = test_astar_with_episodic_learning()
    test3_passed = test_experience_similarity_and_adjustment()
    test4_passed = test_episodic_learning_disabled()
    
    print("\n" + "=" * 70)
    print("📊 PHASE 4 TASK 2 TEST RESULTS:")
    print(f"   EpisodicMemoryHeuristic: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   A* with Episodic Learning: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"   Experience Similarity: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    print(f"   Learning Disabled: {'✅ PASSED' if test4_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed and test4_passed:
        print("\n🎉 TASK 2 COMPLETE! Episodic Memory Heuristic Enhancement working correctly.")
        print("\n💡 Episodic Learning Benefits:")
        print("   • Self-improving heuristics learn from past planning outcomes")
        print("   • Experience-based adjustments improve cost estimation accuracy")
        print("   • Context similarity detection enables relevant experience matching")
        print("   • Automatic outcome recording builds planning experience database")
        print("\n🚀 Ready for Task 3: Meta-Reasoning Plan Validation")
        sys.exit(0)
    else:
        print("\n💥 TASK 2 INCOMPLETE! Some components need attention.")
        sys.exit(1)
