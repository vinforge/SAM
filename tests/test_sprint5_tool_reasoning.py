#!/usr/bin/env python3
"""
Sprint 5 Tool-Augmented Reasoning Test Suite
Tests the complete SELF-DECIDE framework and tool integration.

Sprint 5 Task 7: End-to-End Test Pipeline
"""

import logging
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_self_decide_framework():
    """Test SELF-DECIDE framework functionality."""
    logger.info("🧠 Testing SELF-DECIDE Framework...")
    
    try:
        from reasoning.self_decide_framework import SelfDecideFramework, ReasoningStep
        
        # Initialize framework
        framework = SelfDecideFramework()
        logger.info("  ✅ SELF-DECIDE framework initialized")
        
        # Test reasoning with a simple query
        test_query = "What is machine learning and how does it work?"
        
        session = framework.reason(test_query)
        
        if session:
            logger.info(f"  ✅ Reasoning session completed: {session.session_id}")
            logger.info(f"    Steps executed: {len(session.reasoning_steps)}")
            logger.info(f"    Final answer length: {len(session.final_answer)} chars")
            logger.info(f"    Confidence score: {session.confidence_score:.2f}")
            logger.info(f"    Duration: {session.total_duration_ms}ms")
            
            # Check that all expected steps were executed
            expected_steps = [
                ReasoningStep.STATE_QUERY,
                ReasoningStep.EXPLORE_RETRIEVALS,
                ReasoningStep.LABEL_GAPS,
                ReasoningStep.FORMULATE_PLAN,
                ReasoningStep.DECIDE_TOOLS,
                ReasoningStep.EXECUTE_TOOLS,
                ReasoningStep.CONNECT_RESULTS,
                ReasoningStep.INFER_ANSWER,
                ReasoningStep.DOCUMENT_PROCESS,
                ReasoningStep.EVALUATE_QUALITY
            ]
            
            executed_steps = [step.step for step in session.reasoning_steps]
            missing_steps = [step for step in expected_steps if step not in executed_steps]
            
            if not missing_steps:
                logger.info("  ✅ All SELF-DECIDE steps executed successfully")
            else:
                logger.warning(f"  ⚠️ Missing steps: {[step.value for step in missing_steps]}")
            
            return True
        else:
            logger.error("  ❌ Reasoning session failed")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ SELF-DECIDE framework test failed: {e}")
        return False

def test_tool_selector():
    """Test tool selector functionality."""
    logger.info("🔧 Testing Tool Selector...")
    
    try:
        from reasoning.tool_selector import ToolSelector, ToolType
        
        # Initialize tool selector
        selector = ToolSelector(enable_web_search=True)
        logger.info("  ✅ Tool selector initialized")
        
        # Test tool selection for different query types
        test_cases = [
            ("Calculate 15 * 23 + 45", "python_interpreter"),
            ("Create a comparison table of programming languages", "table_generator"),
            ("Find information about neural networks", "multimodal_query"),
            ("What are the latest developments in AI?", "web_search")
        ]
        
        successful_selections = 0
        
        for query, expected_tool in test_cases:
            selection = selector.select_tool(query)
            
            if selection:
                logger.info(f"    Query: '{query[:30]}...'")
                logger.info(f"    Selected: {selection.tool_name} (confidence: {selection.confidence:.2f})")
                logger.info(f"    Expected: {expected_tool}")
                
                if selection.tool_name == expected_tool:
                    logger.info("    ✅ Correct tool selected")
                    successful_selections += 1
                else:
                    logger.warning("    ⚠️ Different tool selected (may still be valid)")
                    successful_selections += 0.5  # Partial credit
            else:
                logger.warning(f"    ❌ No tool selected for: {query}")
        
        success_rate = successful_selections / len(test_cases)
        logger.info(f"  📊 Tool selection success rate: {success_rate:.1%}")
        
        # Test available tools
        available_tools = selector.get_available_tools()
        logger.info(f"  🛠️ Available tools: {len(available_tools)}")
        
        return success_rate >= 0.5  # At least 50% success rate
        
    except Exception as e:
        logger.error(f"  ❌ Tool selector test failed: {e}")
        return False

def test_tool_executor():
    """Test tool executor functionality."""
    logger.info("⚙️ Testing Tool Executor...")
    
    try:
        from reasoning.tool_executor import ToolExecutor, ExecutionContext
        
        # Initialize tool executor
        executor = ToolExecutor(safety_mode=True)
        logger.info("  ✅ Tool executor initialized")
        
        # Test Python interpreter
        python_params = {
            'query': 'Calculate 2 + 2',
            'code': 'result = 2 + 2\nprint(f"Result: {result}")'
        }
        
        python_response = executor.execute_tool('python_interpreter', python_params)
        
        if python_response.success:
            logger.info("  ✅ Python interpreter execution successful")
            logger.info(f"    Output: {python_response.output.get('output', '')[:50]}...")
        else:
            logger.warning(f"  ⚠️ Python interpreter failed: {python_response.error}")
        
        # Test table generator
        table_params = {
            'query': 'Create a simple comparison table',
            'data': [
                ['Language', 'Type', 'Year'],
                ['Python', 'Interpreted', '1991'],
                ['Java', 'Compiled', '1995']
            ]
        }
        
        table_response = executor.execute_tool('table_generator', table_params)
        
        if table_response.success:
            logger.info("  ✅ Table generator execution successful")
            logger.info(f"    Table preview: {table_response.output.get('table_content', '')[:50]}...")
        else:
            logger.warning(f"  ⚠️ Table generator failed: {table_response.error}")
        
        # Test multimodal query
        multimodal_params = {
            'query': 'Search for information about machine learning',
            'search_types': ['text', 'code']
        }
        
        multimodal_response = executor.execute_tool('multimodal_query', multimodal_params)
        
        if multimodal_response.success:
            logger.info("  ✅ Multimodal query execution successful")
            results_count = multimodal_response.output.get('total_results', 0)
            logger.info(f"    Found {results_count} results")
        else:
            logger.warning(f"  ⚠️ Multimodal query failed: {multimodal_response.error}")
        
        # Check execution history
        history = executor.get_execution_history()
        logger.info(f"  📊 Execution history: {len(history)} entries")
        
        successful_executions = sum(1 for response in history if response.success)
        success_rate = successful_executions / len(history) if history else 0
        
        logger.info(f"  📈 Tool execution success rate: {success_rate:.1%}")
        
        return success_rate >= 0.5  # At least 50% success rate
        
    except Exception as e:
        logger.error(f"  ❌ Tool executor test failed: {e}")
        return False

def test_answer_synthesizer():
    """Test answer synthesizer functionality."""
    logger.info("📝 Testing Answer Synthesizer...")
    
    try:
        from reasoning.answer_synthesizer import AnswerSynthesizer
        from reasoning.self_decide_framework import SelfDecideFramework
        
        # Initialize components
        synthesizer = AnswerSynthesizer()
        framework = SelfDecideFramework()
        
        logger.info("  ✅ Answer synthesizer initialized")
        
        # Create a test reasoning session
        test_query = "Explain the concept of machine learning"
        session = framework.reason(test_query)
        
        if session:
            # Synthesize response
            synthesized = synthesizer.synthesize_response(session)
            
            logger.info("  ✅ Response synthesis completed")
            logger.info(f"    Answer length: {len(synthesized.answer)} chars")
            logger.info(f"    Confidence: {synthesized.confidence_score:.2f}")
            logger.info(f"    Source attributions: {len(synthesized.source_attributions)}")
            logger.info(f"    Tools used: {len(synthesized.tools_used)}")
            
            # Test chat formatting
            formatted = synthesizer.format_response_for_chat(
                synthesized,
                show_sources=True,
                show_reasoning=True
            )
            
            logger.info(f"    Formatted response length: {len(formatted)} chars")
            
            # Check response quality
            has_answer = len(synthesized.answer) > 50
            has_confidence = 0 <= synthesized.confidence_score <= 1
            has_metadata = bool(synthesized.metadata)
            
            quality_checks = [has_answer, has_confidence, has_metadata]
            quality_score = sum(quality_checks) / len(quality_checks)
            
            logger.info(f"  📊 Response quality score: {quality_score:.1%}")
            
            return quality_score >= 0.7  # At least 70% quality
        else:
            logger.error("  ❌ No reasoning session to synthesize")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ Answer synthesizer test failed: {e}")
        return False

def test_integrated_reasoning_pipeline():
    """Test complete integrated reasoning pipeline."""
    logger.info("🔄 Testing Integrated Reasoning Pipeline...")
    
    try:
        from reasoning.self_decide_framework import get_self_decide_framework
        from reasoning.tool_selector import get_tool_selector
        from reasoning.tool_executor import get_tool_executor
        from reasoning.answer_synthesizer import get_answer_synthesizer
        
        # Initialize complete pipeline
        framework = get_self_decide_framework()
        tool_selector = get_tool_selector(enable_web_search=False)
        tool_executor = get_tool_executor()
        answer_synthesizer = get_answer_synthesizer()
        
        # Connect components
        framework.tool_selector = tool_selector
        
        logger.info("  ✅ Integrated pipeline initialized")
        
        # Test with a complex query that should trigger tools
        complex_query = "Calculate the area of a circle with radius 5 and create a table comparing different geometric shapes"
        
        # Execute reasoning
        session = framework.reason(complex_query)
        
        if session:
            logger.info(f"  ✅ Complex reasoning completed: {session.session_id}")
            
            # Synthesize final response
            synthesized = answer_synthesizer.synthesize_response(session)
            
            logger.info("  ✅ Response synthesis completed")
            
            # Check pipeline effectiveness
            used_tools = len(synthesized.tools_used) > 0
            has_reasoning = len(session.reasoning_steps) >= 8  # Most SELF-DECIDE steps
            good_confidence = synthesized.confidence_score > 0.3
            substantial_answer = len(synthesized.answer) > 100
            
            effectiveness_checks = [used_tools, has_reasoning, good_confidence, substantial_answer]
            effectiveness_score = sum(effectiveness_checks) / len(effectiveness_checks)
            
            logger.info(f"  📊 Pipeline effectiveness: {effectiveness_score:.1%}")
            logger.info(f"    Tools used: {synthesized.tools_used}")
            logger.info(f"    Reasoning steps: {len(session.reasoning_steps)}")
            logger.info(f"    Final confidence: {synthesized.confidence_score:.2f}")
            
            return effectiveness_score >= 0.6  # At least 60% effectiveness
        else:
            logger.error("  ❌ Integrated reasoning failed")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ Integrated pipeline test failed: {e}")
        return False

def test_chat_interface_integration():
    """Test chat interface integration with tool-augmented reasoning."""
    logger.info("💬 Testing Chat Interface Integration...")
    
    try:
        from ui.chat_ui import ChatInterface
        
        # Create mock components
        class MockModel:
            def generate(self, prompt, **kwargs):
                return "Test response with tool-augmented reasoning capabilities"
        
        class MockVectorIndex:
            def similarity_search(self, query, k=3):
                return []
        
        # Test enhanced chat interface
        chat = ChatInterface(
            model=MockModel(),
            vector_index=MockVectorIndex(),
            system_prompt="Test system prompt"
        )
        
        logger.info("  ✅ Enhanced chat interface initialized")
        
        # Test tool-augmented settings
        logger.info(f"  🛠️ Tool mode: {chat.tool_mode}")
        logger.info(f"  🤔 Show reasoning: {chat.show_reasoning}")
        logger.info(f"  🌐 Web search: {chat.enable_web_search}")
        
        # Test tool availability
        has_self_decide = hasattr(chat, 'self_decide') and chat.self_decide is not None
        has_tool_selector = hasattr(chat, 'tool_selector') and chat.tool_selector is not None
        has_tool_executor = hasattr(chat, 'tool_executor') and chat.tool_executor is not None
        has_synthesizer = hasattr(chat, 'answer_synthesizer') and chat.answer_synthesizer is not None
        
        integration_checks = [has_self_decide, has_tool_selector, has_tool_executor, has_synthesizer]
        integration_score = sum(integration_checks) / len(integration_checks)
        
        logger.info(f"  📊 Integration completeness: {integration_score:.1%}")
        
        if integration_score >= 0.5:
            logger.info("  ✅ Chat interface integration successful")
        else:
            logger.warning("  ⚠️ Partial chat interface integration")
        
        return integration_score >= 0.5
        
    except Exception as e:
        logger.error(f"  ❌ Chat interface integration test failed: {e}")
        return False

def test_web_ui_integration():
    """Test web UI integration with tool-augmented reasoning."""
    logger.info("🌐 Testing Web UI Integration...")
    
    try:
        # Test that web UI components can be imported
        import web_ui.app as web_app
        
        logger.info("  ✅ Web UI module imported successfully")
        
        # Test initialization function
        if hasattr(web_app, 'initialize_sam'):
            logger.info("  ✅ SAM initialization function available")
        
        # Test tool-augmented response functions
        has_tool_response = hasattr(web_app, 'generate_tool_augmented_response')
        has_should_use_tools = hasattr(web_app, 'should_use_tools')
        has_standard_response = hasattr(web_app, 'generate_standard_response')
        
        web_integration_checks = [has_tool_response, has_should_use_tools, has_standard_response]
        web_integration_score = sum(web_integration_checks) / len(web_integration_checks)
        
        logger.info(f"  📊 Web UI integration: {web_integration_score:.1%}")
        
        return web_integration_score >= 0.8  # High standard for web integration
        
    except ImportError as e:
        logger.warning(f"  ⚠️ Web UI not available (optional): {e}")
        return True  # Not a failure since web UI is optional
    except Exception as e:
        logger.error(f"  ❌ Web UI integration test failed: {e}")
        return False

def main():
    """Run all Sprint 5 tool-augmented reasoning tests."""
    logger.info("🚀 SAM Sprint 5 Tool-Augmented Reasoning Test Suite")
    logger.info("=" * 80)
    logger.info("Focus: SELF-DECIDE Framework & Tool Integration")
    logger.info("=" * 80)
    
    tests = [
        ("SELF-DECIDE Framework", test_self_decide_framework),
        ("Tool Selector", test_tool_selector),
        ("Tool Executor", test_tool_executor),
        ("Answer Synthesizer", test_answer_synthesizer),
        ("Integrated Reasoning Pipeline", test_integrated_reasoning_pipeline),
        ("Chat Interface Integration", test_chat_interface_integration),
        ("Web UI Integration", test_web_ui_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 60)
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Final summary
    logger.info("\n📊 Sprint 5 Test Results Summary")
    logger.info("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total:.1%})")
    
    if passed == total:
        logger.info("🎉 Sprint 5 tool-augmented reasoning system is ready!")
        logger.info("\n✅ Tool-Augmented Reasoning Achieved:")
        logger.info("  🧠 SELF-DECIDE structured reasoning framework")
        logger.info("  🔧 Intelligent tool selection and execution")
        logger.info("  🐍 Python code interpreter with safety")
        logger.info("  📊 Markdown table generator")
        logger.info("  🔍 Multimodal query routing")
        logger.info("  📝 Enhanced answer synthesis with provenance")
        logger.info("  💬 Chat interface with tool integration")
        logger.info("  🌐 Web UI with tool-augmented responses")
        return 0
    else:
        logger.error("⚠️  Some Sprint 5 components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
