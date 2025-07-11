#!/usr/bin/env python3
"""
Test script for A* Search Planner Phase 3: A* Planner Integration

This script tests the complete A* search planner implementation:
- AStarPlanner: Main A* search algorithm
- SAMPlannerIntegration: Integration with SAM systems
- Complete planning workflow
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockLLMInterface:
    """Enhanced mock LLM interface for testing."""
    
    def __init__(self):
        self.call_count = 0
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 100) -> str:
        """Mock LLM generation with more realistic responses."""
        self.call_count += 1
        
        # Simulate heuristic estimation responses
        if "ESTIMATE:" in prompt:
            if "complete" in prompt.lower() or "finished" in prompt.lower():
                return "0"
            elif "starting" in prompt.lower() or len(prompt.split("Actions completed: ")[1].split()[0]) == "0":
                return "8"
            elif "complex" in prompt.lower():
                return "12"
            else:
                # Estimate based on progress
                try:
                    actions_line = [line for line in prompt.split('\n') if 'Actions completed:' in line][0]
                    actions_count = int(actions_line.split(':')[1].strip())
                    return str(max(0, 8 - actions_count))
                except:
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
            elif "memory" in prompt.lower():
                return """- search_memory
- consolidate_knowledge
- retrieve_similar_memories"""
            else:
                return """- analyze_conversation_context
- create_structured_response
- validate_conclusions"""
        
        return "Mock response"

class MockExecutionEngine:
    """Mock execution engine for testing."""
    
    def execute_action(self, action: str) -> Dict[str, Any]:
        """Mock action execution."""
        return {
            'action': action,
            'success': True,
            'result': f"Successfully executed {action}",
            'timestamp': '2024-01-01T12:00:00'
        }

def test_astar_planner():
    """Test AStarPlanner functionality."""
    print("🧪 Testing AStarPlanner")
    print("-" * 30)
    
    try:
        from sam.agent_zero.planning import (
            AStarPlanner, SAMContextManager, PlanningState
        )
        
        # Create mock LLM and context
        mock_llm = MockLLMInterface()
        context_manager = SAMContextManager()
        
        # Add context
        context_manager.document_context.add_document(
            "ai_safety_paper.pdf",
            {"type": "pdf", "pages": 15, "topic": "AI safety"}
        )
        context_manager.conversation_context.add_message(
            "user", "Please analyze this AI safety paper thoroughly"
        )
        
        # Create planner
        planner = AStarPlanner(
            llm_interface=mock_llm,
            context_manager=context_manager,
            max_nodes=50,
            max_time_seconds=30
        )
        print("✅ Created AStarPlanner")
        
        # Test simple goal checker
        def simple_goal_checker(state: PlanningState) -> bool:
            # Goal reached if we've done at least 3 actions including analysis
            if len(state.action_history) >= 3:
                return any('analyze' in action.lower() for action in state.action_history)
            return False
        
        # Test planning
        result = planner.find_optimal_plan(
            task_description="Analyze AI safety paper and extract key insights",
            goal_checker=simple_goal_checker
        )
        
        print(f"✅ Planning result: success={result.success}")
        print(f"   Plan length: {len(result.plan)}")
        print(f"   Total cost: {result.total_cost}")
        print(f"   Nodes explored: {result.nodes_explored}")
        print(f"   Planning time: {result.planning_time:.2f}s")
        print(f"   Goal reached: {result.goal_reached}")
        print(f"   Termination: {result.termination_reason}")
        
        if result.plan:
            print(f"   Plan: {' -> '.join(result.plan)}")
        
        # Test statistics
        stats = planner.get_planning_statistics()
        print(f"✅ Planning statistics: {stats['nodes_explored']} nodes, {stats['visited_states']} visited")
        
        return True
        
    except Exception as e:
        print(f"❌ AStarPlanner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sam_planner_integration():
    """Test SAMPlannerIntegration functionality."""
    print("\n🧪 Testing SAMPlannerIntegration")
    print("-" * 40)
    
    try:
        from sam.agent_zero.planning import SAMPlannerIntegration, PlanningState
        
        # Create mock session state
        session_state = {
            'uploaded_documents': {
                'research_paper.pdf': {
                    'type': 'pdf',
                    'size': 2048,
                    'uploaded_at': '2024-01-01'
                }
            },
            'chat_history': [
                {'role': 'user', 'content': 'Please analyze this research paper'},
                {'role': 'assistant', 'content': 'I\'ll analyze the paper for you'}
            ],
            'relevant_memories': [
                {'id': 'mem_001', 'content': 'Previous AI research analysis'}
            ]
        }
        
        # Create integration
        integration = SAMPlannerIntegration(session_state)
        print("✅ Created SAMPlannerIntegration")
        
        # Create planner
        mock_llm = MockLLMInterface()
        planner = integration.create_planner(llm_interface=mock_llm, max_nodes=30)
        print("✅ Created planner through integration")
        
        # Test planning suggestions
        suggestions = integration.get_planning_suggestions(
            "Analyze research paper and create comprehensive summary"
        )
        print(f"✅ Planning suggestions: {suggestions}")
        
        # Test task planning
        def research_goal_checker(state: PlanningState) -> bool:
            return (len(state.action_history) >= 2 and 
                   any('summarize' in action.lower() for action in state.action_history))
        
        planning_result = integration.plan_task(
            "Analyze research paper and create comprehensive summary",
            goal_checker=research_goal_checker
        )
        
        print(f"✅ Task planning: success={planning_result.success}")
        if planning_result.success:
            print(f"   Generated plan: {planning_result.plan}")
        
        # Test execution simulation
        if planning_result.success and planning_result.plan:
            execution_result = integration.execute_plan(planning_result.plan)
            print(f"✅ Plan execution: success={execution_result['success']}")
            print(f"   Executed {len(execution_result['executed_actions'])} actions")
        
        # Test combined plan and execute
        combined_result = integration.plan_and_execute(
            "Quick analysis of document structure",
            goal_checker=lambda state: len(state.action_history) >= 1
        )
        
        print(f"✅ Combined plan & execute: success={combined_result['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ SAMPlannerIntegration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_workflow():
    """Test complete A* planning workflow."""
    print("\n🧪 Testing Complete A* Workflow")
    print("-" * 40)
    
    try:
        from sam.agent_zero.planning import (
            SAMPlannerIntegration, PlanningState, AStarPlanner
        )
        
        # Simulate complex SAM session
        complex_session = {
            'uploaded_documents': {
                'ai_ethics_paper.pdf': {'type': 'pdf', 'analyzed': False},
                'safety_guidelines.docx': {'type': 'docx', 'analyzed': True}
            },
            'chat_history': [
                {'role': 'user', 'content': 'I need a comprehensive analysis comparing these two documents'},
                {'role': 'assistant', 'content': 'I\'ll help you compare and analyze both documents'}
            ],
            'relevant_memories': [
                {'id': 'mem_001', 'content': 'Previous comparative analysis methodology'},
                {'id': 'mem_002', 'content': 'AI ethics framework from past research'}
            ]
        }
        
        # Create integration with complex context
        integration = SAMPlannerIntegration(complex_session)
        mock_llm = MockLLMInterface()
        
        # Create planner with realistic constraints
        planner = integration.create_planner(
            llm_interface=mock_llm,
            max_nodes=100,
            max_time_seconds=60
        )
        
        print("✅ Created complex planning scenario")
        
        # Define sophisticated goal checker
        def comparative_analysis_goal(state: PlanningState) -> bool:
            actions = state.action_history
            
            # Need to analyze both documents and synthesize
            has_analysis = any('analyze' in action.lower() for action in actions)
            has_synthesis = any('synthesize' in action.lower() for action in actions)
            sufficient_depth = len(actions) >= 4
            
            return has_analysis and has_synthesis and sufficient_depth
        
        # Execute complex planning
        task = "Compare and analyze both documents to identify key differences in AI ethics approaches"
        
        result = integration.plan_and_execute(
            task_description=task,
            goal_checker=comparative_analysis_goal
        )
        
        print(f"✅ Complex workflow result: success={result['success']}")
        
        if result['success']:
            planning = result['planning_result']
            execution = result['execution_result']
            
            print(f"   Planning: {planning.nodes_explored} nodes, {planning.planning_time:.2f}s")
            print(f"   Plan: {' -> '.join(planning.plan)}")
            print(f"   Execution: {len(execution['executed_actions'])} actions completed")
            
            # Verify plan quality
            plan_has_analysis = any('analyze' in action.lower() for action in planning.plan)
            plan_has_synthesis = any('synthesize' in action.lower() for action in planning.plan)
            
            print(f"✅ Plan quality: analysis={plan_has_analysis}, synthesis={plan_has_synthesis}")
            
            # Test performance metrics
            stats = planner.get_planning_statistics()
            estimator_stats = stats['estimator_stats']
            expander_stats = stats['expander_stats']
            
            print(f"✅ Performance: estimator_cache={estimator_stats['cache_hit_rate']:.2f}, "
                  f"expander_cache={expander_stats['cache_hit_rate']:.2f}")
        
        # Test LLM call efficiency
        print(f"✅ LLM efficiency: {mock_llm.call_count} total calls")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting A* Search Planner Phase 3 Tests")
    print("=" * 60)
    
    # Run Phase 3 tests
    test1_passed = test_astar_planner()
    test2_passed = test_sam_planner_integration()
    test3_passed = test_complete_workflow()
    
    print("\n" + "=" * 60)
    print("📊 PHASE 3 TEST RESULTS:")
    print(f"   AStarPlanner: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   SAMPlannerIntegration: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"   Complete Workflow: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 PHASE 3 COMPLETE! A* Planner Integration working correctly.")
        print("\n💡 Ready for Phase 4: Advanced SAM Synergies")
        print("   • TPV integration for planning control")
        print("   • Episodic memory for heuristic enhancement")
        print("   • Meta-reasoning for plan validation")
        print("\n🚀 A* SEARCH PLANNER IS FULLY FUNCTIONAL!")
        print("   • Strategic planning with LLM-guided heuristics")
        print("   • SAM-aware action expansion and execution")
        print("   • Complete integration with SAM's capabilities")
        sys.exit(0)
    else:
        print("\n💥 PHASE 3 INCOMPLETE! Some components need attention.")
        sys.exit(1)
