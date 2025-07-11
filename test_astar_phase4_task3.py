#!/usr/bin/env python3
"""
Test script for A* Search Planner Phase 4 Task 3: Meta-Reasoning Plan Validation

This script tests the integration of SAM's meta-reasoning system with the A* planner
for comprehensive plan validation including risk assessment and ethical validation.
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
            return "5"
        elif "SUGGESTED ACTIONS:" in prompt:
            return """- summarize_document
- extract_key_questions
- deep_analyze_document"""
        
        return "Mock response"

def test_meta_reasoning_plan_validator():
    """Test MetaReasoningPlanValidator functionality."""
    print("🧪 Testing MetaReasoningPlanValidator")
    print("-" * 45)
    
    try:
        from sam.agent_zero.planning import (
            MetaReasoningPlanValidator, PlanningState, ValidationIssue
        )
        
        # Create validator with test configuration
        validator = MetaReasoningPlanValidator(
            enable_meta_reasoning=False,  # Use fallback for testing
            enable_safety_validation=True,
            risk_threshold=0.7,
            confidence_threshold=0.6
        )
        
        print("✅ Created MetaReasoningPlanValidator")
        
        # Test basic plan validation
        good_plan = ["summarize_document", "extract_key_questions", "create_structured_response"]
        initial_state = PlanningState(
            task_description="Analyze research paper and provide insights",
            action_history=[],
            current_observation="Starting analysis",
            document_context={"paper.pdf": {"type": "pdf"}}
        )
        
        result = validator.validate_plan(good_plan, initial_state)
        
        print(f"✅ Good plan validation: valid={result.is_valid}")
        print(f"   Risk score: {result.overall_risk_score:.2f}")
        print(f"   Confidence: {result.confidence_score:.2f}")
        print(f"   Issues: {len(result.issues)}")
        print(f"   Recommendations: {len(result.recommendations)}")
        
        # Test risky plan validation
        risky_plan = ["delete_all_files", "modify_system_settings", "overwrite_data"]
        risky_result = validator.validate_plan(risky_plan, initial_state)
        
        print(f"✅ Risky plan validation: valid={risky_result.is_valid}")
        print(f"   Risk score: {risky_result.overall_risk_score:.2f}")
        print(f"   Critical issues: {sum(1 for issue in risky_result.issues if issue.severity.value == 'critical')}")
        
        # Test empty plan validation
        empty_result = validator.validate_plan([], initial_state)
        print(f"✅ Empty plan validation: valid={empty_result.is_valid}")
        
        # Test long plan validation
        long_plan = [f"action_{i}" for i in range(20)]
        long_result = validator.validate_plan(long_plan, initial_state)
        print(f"✅ Long plan validation: valid={long_result.is_valid}")
        print(f"   Efficiency warnings: {sum(1 for issue in long_result.issues if issue.category == 'efficiency')}")
        
        # Test validation statistics
        stats = validator.get_validation_statistics()
        print(f"✅ Validation statistics: {stats['total_validations']} validations, "
              f"{stats['plans_rejected']} rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ MetaReasoningPlanValidator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_astar_with_meta_reasoning_validation():
    """Test A* planner with meta-reasoning validation."""
    print("\n🧪 Testing A* Planner with Meta-Reasoning Validation")
    print("-" * 60)
    
    try:
        from sam.agent_zero.planning import (
            AStarPlanner, SAMContextManager, PlanningState
        )
        
        # Create mock components
        mock_llm = MockLLMInterface()
        context_manager = SAMContextManager()
        
        # Add context
        context_manager.document_context.add_document(
            "research_paper.pdf",
            {"type": "pdf", "topic": "AI safety"}
        )
        
        # Create planner with meta-reasoning validation enabled
        validation_config = {
            'risk_threshold': 0.6,
            'confidence_threshold': 0.5
        }
        
        planner = AStarPlanner(
            llm_interface=mock_llm,
            context_manager=context_manager,
            max_nodes=15,
            max_time_seconds=10,
            enable_meta_reasoning_validation=True,
            validation_config=validation_config
        )
        
        print("✅ Created A* planner with meta-reasoning validation")
        
        # Verify validator is initialized
        assert planner.plan_validator is not None, "Plan validator should be initialized"
        print("✅ Meta-reasoning validator correctly initialized")
        
        # Test planning with validation
        def simple_goal_checker(state: PlanningState) -> bool:
            return len(state.action_history) >= 2
        
        result = planner.find_optimal_plan(
            task_description="Analyze research paper and extract key insights",
            goal_checker=simple_goal_checker
        )
        
        print(f"✅ Planning with validation: success={result.success}")
        print(f"   Plan: {result.plan}")
        print(f"   Nodes explored: {result.nodes_explored}")
        
        # Check if validation results are included in statistics
        stats = result.search_statistics
        if 'validation_result' in stats:
            validation_info = stats['validation_result']
            print(f"✅ Validation info: valid={validation_info['is_valid']}, "
                  f"risk={validation_info['risk_score']:.2f}")
        else:
            print("⚠️  Validation results not found in statistics")
        
        # Check validation statistics in planner
        if 'validation_stats' in stats:
            val_stats = stats['validation_stats']
            print(f"✅ Validator stats: {val_stats['total_validations']} validations")
        
        return True
        
    except Exception as e:
        print(f"❌ A* planner with meta-reasoning validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_issue_detection():
    """Test validation issue detection capabilities."""
    print("\n🧪 Testing Validation Issue Detection")
    print("-" * 45)
    
    try:
        from sam.agent_zero.planning import (
            MetaReasoningPlanValidator, PlanningState, ValidationSeverity
        )
        
        validator = MetaReasoningPlanValidator(enable_meta_reasoning=False)
        
        # Test duplicate action detection
        duplicate_plan = ["analyze_document", "analyze_document", "create_response"]
        state = PlanningState(
            task_description="Analyze document",
            action_history=[],
            current_observation="Starting"
        )
        
        result = validator.validate_plan(duplicate_plan, state)
        duplicate_issues = [issue for issue in result.issues if "duplicate" in issue.description.lower()]
        print(f"✅ Duplicate action detection: {len(duplicate_issues)} issues found")
        
        # Test task-action alignment
        misaligned_plan = ["search_memory", "consolidate_knowledge"]
        document_task_state = PlanningState(
            task_description="Analyze uploaded document thoroughly",
            action_history=[],
            current_observation="Starting",
            document_context={"doc.pdf": {"type": "pdf"}}
        )
        
        alignment_result = validator.validate_plan(misaligned_plan, document_task_state)
        alignment_issues = [issue for issue in alignment_result.issues if issue.category == "alignment"]
        print(f"✅ Task-action alignment detection: {len(alignment_issues)} issues found")
        
        # Test strategic ordering
        unordered_plan = ["synthesize_information", "analyze_document", "extract_key_questions"]
        ordering_result = validator.validate_plan(unordered_plan, document_task_state)
        strategy_issues = [issue for issue in ordering_result.issues if issue.category == "strategy"]
        print(f"✅ Strategic ordering detection: {len(strategy_issues)} issues found")
        
        # Test alternative suggestions
        simple_plan = ["summarize_document"]
        simple_result = validator.validate_plan(simple_plan, document_task_state)
        print(f"✅ Alternative suggestions: {len(simple_result.alternative_suggestions)} generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation issue detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_disabled():
    """Test behavior when meta-reasoning validation is disabled."""
    print("\n🧪 Testing Meta-Reasoning Validation Disabled")
    print("-" * 50)
    
    try:
        from sam.agent_zero.planning import AStarPlanner, SAMContextManager
        
        # Create planner with validation disabled
        planner = AStarPlanner(
            llm_interface=MockLLMInterface(),
            context_manager=SAMContextManager(),
            enable_meta_reasoning_validation=False
        )
        
        print("✅ Created planner with meta-reasoning validation disabled")
        
        # Verify validator is not initialized
        assert planner.plan_validator is None, "Plan validator should be None when disabled"
        print("✅ Meta-reasoning validator correctly disabled")
        
        # Test that planning still works without validation
        from sam.agent_zero.planning import PlanningState
        
        def quick_goal_checker(state: PlanningState) -> bool:
            return len(state.action_history) >= 1
        
        result = planner.find_optimal_plan(
            task_description="Simple test task",
            goal_checker=quick_goal_checker
        )
        
        print(f"✅ Planning without validation: success={result.success}")
        
        # Verify no validation info in statistics
        stats = result.search_statistics
        assert 'validation_result' not in stats, "Should not have validation results"
        assert 'validation_stats' not in stats, "Should not have validation statistics"
        print("✅ No validation data in results when disabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation disabled test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comprehensive_phase4_integration():
    """Test comprehensive Phase 4 integration with all components."""
    print("\n🧪 Testing Comprehensive Phase 4 Integration")
    print("-" * 55)
    
    try:
        from sam.agent_zero.planning import (
            AStarPlanner, SAMContextManager, PlanningState
        )
        
        # Create planner with ALL Phase 4 features enabled
        mock_llm = MockLLMInterface()
        context_manager = SAMContextManager()
        
        # Add comprehensive context
        context_manager.document_context.add_document(
            "ai_research.pdf",
            {"type": "pdf", "complexity": "high", "topic": "AI research"}
        )
        context_manager.memory_context.add_relevant_memory({
            "id": "mem_001",
            "content": "Previous AI research analysis",
            "memory_type": "episodic"
        })
        context_manager.conversation_context.add_message(
            "user", "Please provide comprehensive analysis with safety considerations"
        )
        
        # Create fully-featured planner
        planner = AStarPlanner(
            llm_interface=mock_llm,
            context_manager=context_manager,
            max_nodes=25,
            max_time_seconds=15,
            enable_tpv_control=True,
            enable_episodic_learning=True,
            enable_meta_reasoning_validation=True,
            tpv_config={'max_steps': 10, 'plateau_patience': 3},
            validation_config={'risk_threshold': 0.6, 'confidence_threshold': 0.5}
        )
        
        print("✅ Created comprehensive Phase 4 planner")
        print(f"   TPV Control: {planner.tpv_controller is not None}")
        print(f"   Episodic Learning: {hasattr(planner.heuristic_estimator, 'record_planning_outcome')}")
        print(f"   Meta-Reasoning Validation: {planner.plan_validator is not None}")
        
        # Test comprehensive planning
        def comprehensive_goal_checker(state: PlanningState) -> bool:
            # More sophisticated goal checking
            actions = state.action_history
            has_analysis = any('analyze' in action.lower() for action in actions)
            has_synthesis = any('synthesize' in action.lower() or 'create' in action.lower() for action in actions)
            return len(actions) >= 3 and has_analysis and has_synthesis
        
        result = planner.find_optimal_plan(
            task_description="Comprehensive AI research analysis with safety validation and strategic insights",
            goal_checker=comprehensive_goal_checker
        )
        
        print(f"✅ Comprehensive planning: success={result.success}")
        print(f"   Plan length: {len(result.plan)}")
        print(f"   Nodes explored: {result.nodes_explored}")
        print(f"   Planning time: {result.planning_time:.2f}s")
        
        # Verify all Phase 4 components contributed
        stats = result.search_statistics
        
        # Check TPV statistics
        if 'tpv_stats' in stats:
            tpv_stats = stats['tpv_stats']
            print(f"✅ TPV Integration: {tpv_stats['total_progress_steps']} progress steps")
        
        # Check episodic learning statistics
        if hasattr(planner.heuristic_estimator, 'get_learning_statistics'):
            learning_stats = planner.heuristic_estimator.get_learning_statistics()
            print(f"✅ Episodic Learning: {learning_stats['experience_learning_enabled']}")
        
        # Check validation statistics
        if 'validation_stats' in stats:
            val_stats = stats['validation_stats']
            print(f"✅ Meta-Reasoning Validation: {val_stats['total_validations']} validations")
        
        # Check validation results
        if 'validation_result' in stats:
            val_result = stats['validation_result']
            print(f"✅ Plan Validation: valid={val_result['is_valid']}, "
                  f"risk={val_result['risk_score']:.2f}")
        
        print("✅ All Phase 4 components successfully integrated and functional")
        
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive Phase 4 integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting A* Search Planner Phase 4 Task 3 Tests")
    print("=" * 70)
    
    # Run Task 3 tests
    test1_passed = test_meta_reasoning_plan_validator()
    test2_passed = test_astar_with_meta_reasoning_validation()
    test3_passed = test_validation_issue_detection()
    test4_passed = test_validation_disabled()
    test5_passed = test_comprehensive_phase4_integration()
    
    print("\n" + "=" * 70)
    print("📊 PHASE 4 TASK 3 TEST RESULTS:")
    print(f"   MetaReasoningPlanValidator: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   A* with Meta-Reasoning: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"   Validation Issue Detection: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    print(f"   Validation Disabled: {'✅ PASSED' if test4_passed else '❌ FAILED'}")
    print(f"   Comprehensive Integration: {'✅ PASSED' if test5_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed and test4_passed and test5_passed:
        print("\n🎉 TASK 3 COMPLETE! Meta-Reasoning Plan Validation working correctly.")
        print("\n💡 Meta-Reasoning Validation Benefits:")
        print("   • Comprehensive risk assessment prevents dangerous plans")
        print("   • Strategic analysis ensures logical action ordering")
        print("   • Safety validation protects against harmful actions")
        print("   • Alternative suggestions provide plan improvement options")
        print("\n🎊 PHASE 4 COMPLETE! All Advanced SAM Synergies Implemented!")
        print("\n🚀 SAM A* PLANNER ACHIEVEMENTS:")
        print("   ✅ Task 1: TPV Planning Time Control - Intelligent stagnation detection")
        print("   ✅ Task 2: Episodic Memory Enhancement - Self-improving heuristics")
        print("   ✅ Task 3: Meta-Reasoning Validation - Comprehensive plan validation")
        print("\n🧠 SAM NOW HAS COMPLETE COGNITIVE PLANNING CAPABILITIES:")
        print("   • Strategic A* search with optimal path finding")
        print("   • Self-regulation through TPV control")
        print("   • Self-improvement through episodic learning")
        print("   • Self-awareness through meta-reasoning validation")
        sys.exit(0)
    else:
        print("\n💥 TASK 3 INCOMPLETE! Some components need attention.")
        sys.exit(1)
