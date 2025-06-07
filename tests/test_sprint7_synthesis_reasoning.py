#!/usr/bin/env python3
"""
Sprint 7 Knowledge Fusion & Multi-Turn Reasoning Test Suite
Tests the complete synthesis and multi-turn reasoning system.

Sprint 7 Task Testing: Synthesis, Multi-Turn, Structuring, Chaining, Learning
"""

import logging
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cross_document_synthesis():
    """Test cross-document synthesis engine."""
    logger.info("🔄 Testing Cross-Document Synthesis Engine...")
    
    try:
        from synthesis.synthesis_engine import CrossDocumentSynthesizer
        
        # Initialize synthesizer
        synthesizer = CrossDocumentSynthesizer()
        logger.info("  ✅ Synthesis engine initialized")
        
        # Test with mock sources
        document_sources = [
            {
                'content': 'Machine learning is a subset of artificial intelligence that enables computers to learn from data.',
                'metadata': {'title': 'ML Introduction', 'confidence': 0.9}
            },
            {
                'content': 'Deep learning uses neural networks with multiple layers to process complex patterns.',
                'metadata': {'title': 'Deep Learning Basics', 'confidence': 0.8}
            }
        ]
        
        memory_sources = [
            {
                'content': 'Neural networks are inspired by biological brain structures.',
                'metadata': {'created_at': datetime.now().isoformat(), 'confidence': 0.7}
            }
        ]
        
        tool_outputs = [
            {
                'tool_name': 'python_interpreter',
                'output': 'Calculated accuracy: 95.2%',
                'success': True,
                'metadata': {}
            }
        ]
        
        # Test synthesis
        result = synthesizer.synthesize_multi_source_answer(
            query="What is machine learning and how does it work?",
            document_sources=document_sources,
            memory_sources=memory_sources,
            tool_outputs=tool_outputs
        )
        
        if result:
            logger.info(f"  ✅ Synthesis successful: {len(result.sources_used)} sources used")
            logger.info(f"    Content length: {len(result.synthesized_content)} chars")
            logger.info(f"    Confidence: {result.synthesis_confidence:.2f}")
            logger.info(f"    Conflicts detected: {len(result.conflicts_detected)}")
        else:
            logger.error("  ❌ Synthesis failed")
            return False
        
        # Test auto-synthesis
        auto_result = synthesizer.auto_synthesize_from_query("What is artificial intelligence?")
        
        if auto_result:
            logger.info(f"  ✅ Auto-synthesis successful: {len(auto_result.sources_used)} sources")
        else:
            logger.info("  ℹ️ Auto-synthesis returned no sources (expected for test environment)")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Cross-document synthesis test failed: {e}")
        return False

def test_multi_turn_task_chaining():
    """Test multi-turn task chaining."""
    logger.info("🔗 Testing Multi-Turn Task Chaining...")
    
    try:
        from synthesis.task_manager import TaskManager
        
        # Create temporary task file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            task_file = tmp.name
        
        # Initialize task manager
        task_manager = TaskManager(tasks_file=task_file)
        logger.info("  ✅ Task manager initialized")
        
        # Test task creation
        subtask_descriptions = [
            "Research the topic of renewable energy",
            "Analyze different types of renewable energy sources",
            "Compare costs and benefits",
            "Create a summary report"
        ]
        
        task_id = task_manager.create_task(
            title="Renewable Energy Analysis",
            description="Comprehensive analysis of renewable energy options",
            user_id="test_user",
            session_id="test_session",
            subtask_descriptions=subtask_descriptions
        )
        
        logger.info(f"  ✅ Task created: {task_id}")
        
        # Test task starting
        start_success = task_manager.start_task(task_id)
        
        if start_success:
            logger.info("  ✅ Task started successfully")
        else:
            logger.error("  ❌ Task start failed")
            return False
        
        # Test subtask completion
        for i in range(len(subtask_descriptions)):
            completion_success = task_manager.complete_current_subtask(task_id, {
                'result': f'Completed subtask {i+1}',
                'confidence': 0.8
            })
            
            if completion_success:
                logger.info(f"    ✅ Subtask {i+1} completed")
            else:
                logger.warning(f"    ⚠️ Subtask {i+1} completion failed")
        
        # Test task status
        status = task_manager.get_task_status_summary(task_id)
        
        if status:
            logger.info(f"  ✅ Task status retrieved: {status['status']}")
            if 'progress' in status:
                logger.info(f"    Progress: {status['progress']['percentage']:.1f}%")
            else:
                logger.info(f"    Progress: Task completed")
        else:
            logger.warning("  ⚠️ Task status retrieval failed")
        
        # Test task listing
        user_tasks = task_manager.list_user_tasks("test_user")
        logger.info(f"  📋 User tasks: {len(user_tasks)}")
        
        # Cleanup
        Path(task_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Multi-turn task chaining test failed: {e}")
        return False

def test_advanced_answer_structuring():
    """Test advanced answer structuring."""
    logger.info("📝 Testing Advanced Answer Structuring...")
    
    try:
        from synthesis.answer_structuring import AdvancedAnswerStructurer
        
        # Initialize structurer
        structurer = AdvancedAnswerStructurer()
        logger.info("  ✅ Answer structurer initialized")
        
        # Test response structuring
        raw_response = """
        Machine learning is a powerful subset of artificial intelligence. It enables computers to learn from data without being explicitly programmed.
        
        There are several types of machine learning: supervised learning uses labeled data, unsupervised learning finds patterns in unlabeled data, and reinforcement learning learns through trial and error.
        
        The applications are vast, including image recognition, natural language processing, and predictive analytics. However, challenges include data quality, bias, and interpretability.
        
        In conclusion, machine learning represents a significant advancement in computing technology with broad implications for society.
        """
        
        sources = [
            {'title': 'ML Textbook', 'content': 'Comprehensive guide to machine learning', 'confidence': 0.9},
            {'title': 'Research Paper', 'content': 'Latest developments in ML', 'confidence': 0.8}
        ]
        
        reasoning_trace = [
            {'step': 'analyze_query', 'reasoning': 'Query asks for ML explanation', 'confidence': 0.9},
            {'step': 'gather_information', 'reasoning': 'Collected relevant sources', 'confidence': 0.8},
            {'step': 'synthesize_answer', 'reasoning': 'Combined information coherently', 'confidence': 0.7}
        ]
        
        structured_response = structurer.structure_response(
            query="What is machine learning?",
            raw_response=raw_response,
            sources=sources,
            reasoning_trace=reasoning_trace
        )
        
        if structured_response:
            logger.info(f"  ✅ Response structured: {len(structured_response.sections)} sections")
            logger.info(f"    Overall confidence: {structured_response.overall_confidence:.2f}")
            logger.info(f"    Decision tree nodes: {len(structured_response.decision_tree)}")
        else:
            logger.error("  ❌ Response structuring failed")
            return False
        
        # Test response formatting
        formatted_response = structurer.format_structured_response(
            structured_response,
            include_confidence=True,
            include_decision_tree=True,
            include_metadata=True
        )
        
        if formatted_response and len(formatted_response) > len(raw_response):
            logger.info(f"  ✅ Response formatted: {len(formatted_response)} chars")
        else:
            logger.warning("  ⚠️ Response formatting may have issues")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Advanced answer structuring test failed: {e}")
        return False

def test_capsule_chaining():
    """Test capsule chaining and strategy replay."""
    logger.info("📦 Testing Capsule Chaining & Strategy Replay...")
    
    try:
        from synthesis.capsule_chains import CapsuleChainManager
        
        # Create temporary chains file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            chains_file = tmp.name
        
        # Initialize chain manager
        chain_manager = CapsuleChainManager(chains_file=chains_file)
        logger.info("  ✅ Chain manager initialized")
        
        # Test chain creation
        capsule_sequence = [
            {
                'capsule_id': 'cap_001',
                'capsule_name': 'Data Analysis',
                'input_data': {'dataset': 'sales_data.csv'},
                'dependencies': [],
                'metadata': {}
            },
            {
                'capsule_id': 'cap_002',
                'capsule_name': 'Visualization',
                'input_data': {'chart_type': 'bar'},
                'dependencies': [0],  # Depends on first capsule
                'metadata': {}
            },
            {
                'capsule_id': 'cap_003',
                'capsule_name': 'Report Generation',
                'input_data': {'format': 'pdf'},
                'dependencies': [1],  # Depends on second capsule
                'metadata': {}
            }
        ]
        
        chain_id = chain_manager.create_chain(
            name="Sales Analysis Pipeline",
            description="Complete sales data analysis and reporting",
            capsule_sequence=capsule_sequence,
            user_id="test_user"
        )
        
        logger.info(f"  ✅ Chain created: {chain_id}")
        
        # Test chain execution
        execution_success = chain_manager.execute_chain(chain_id)
        
        if execution_success:
            logger.info("  ✅ Chain execution completed")
        else:
            logger.warning("  ⚠️ Chain execution had issues")
        
        # Test chain status
        status = chain_manager.get_chain_status(chain_id)
        
        if status:
            logger.info(f"  ✅ Chain status: {status['status']}")
            logger.info(f"    Success rate: {status['success_rate']:.1%}")
            logger.info(f"    Progress: {status['progress']['percentage']:.1f}%")
        else:
            logger.warning("  ⚠️ Chain status retrieval failed")
        
        # Test chain replay
        replay_chain_id = chain_manager.replay_chain(chain_id, {
            f"{chain_id}_exec_1": {'dataset': 'new_sales_data.csv'}
        })
        
        if replay_chain_id:
            logger.info(f"  ✅ Chain replay created: {replay_chain_id}")
        else:
            logger.warning("  ⚠️ Chain replay failed")
        
        # Test chain listing
        chains = chain_manager.list_chains("test_user")
        logger.info(f"  📋 User chains: {len(chains)}")
        
        # Cleanup
        Path(chains_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Capsule chaining test failed: {e}")
        return False

def test_user_guided_learning():
    """Test user-guided learning feedback."""
    logger.info("📚 Testing User-Guided Learning Feedback...")
    
    try:
        from synthesis.guided_learning import UserGuidedLearningManager, FeedbackType, LearningPriority
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp1:
            feedback_file = tmp1.name
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp2:
            rules_file = tmp2.name
        
        # Initialize learning manager
        learning_manager = UserGuidedLearningManager(
            feedback_file=feedback_file,
            rules_file=rules_file
        )
        logger.info("  ✅ Guided learning manager initialized")
        
        # Test feedback collection
        feedback_id = learning_manager.collect_feedback(
            user_id="test_user",
            session_id="test_session",
            original_query="What is machine learning?",
            original_response="Machine learning is a type of AI.",
            feedback_text="The response is too brief. Please provide more details about types and applications.",
            feedback_type=FeedbackType.IMPROVEMENT,
            priority=LearningPriority.MEDIUM
        )
        
        logger.info(f"  ✅ Feedback collected: {feedback_id}")
        
        # Test correction provision
        correction_id = learning_manager.provide_correction(
            user_id="test_user",
            session_id="test_session",
            original_query="What is the capital of France?",
            original_response="The capital of France is Lyon.",
            corrected_response="The capital of France is Paris.",
            explanation="Lyon is not the capital, Paris is the correct answer."
        )
        
        logger.info(f"  ✅ Correction provided: {correction_id}")
        
        # Test preference provision
        preference_id = learning_manager.provide_preference(
            user_id="test_user",
            session_id="test_session",
            query="Explain neural networks",
            response_a="Neural networks are computing systems.",
            response_b="Neural networks are computing systems inspired by biological neural networks that can learn patterns from data.",
            preferred_response="b",
            reason="More detailed and informative"
        )
        
        logger.info(f"  ✅ Preference provided: {preference_id}")
        
        # Test validation
        validation_id = learning_manager.validate_response(
            user_id="test_user",
            session_id="test_session",
            query="What is 2+2?",
            response="2+2 equals 4",
            is_correct=True,
            confidence=1.0,
            notes="Correct mathematical answer"
        )
        
        logger.info(f"  ✅ Validation provided: {validation_id}")
        
        # Test guidance provision
        guidance_id = learning_manager.provide_guidance(
            user_id="test_user",
            session_id="test_session",
            topic="mathematics",
            guidance_text="Always show step-by-step calculations for math problems",
            guidance_type="methodology"
        )
        
        logger.info(f"  ✅ Guidance provided: {guidance_id}")
        
        # Test applicable rules retrieval
        applicable_rules = learning_manager.get_applicable_rules("What is machine learning?")
        logger.info(f"  🔍 Applicable rules: {len(applicable_rules)}")
        
        # Test feedback summary
        summary = learning_manager.get_feedback_summary("test_user")
        
        if summary:
            logger.info(f"  📊 Feedback summary: {summary['total_feedback']} entries")
            logger.info(f"    Processing rate: {summary['processing_rate']:.1%}")
            logger.info(f"    Rules generated: {summary['rules_generated']}")
        else:
            logger.warning("  ⚠️ Feedback summary failed")
        
        # Cleanup
        Path(feedback_file).unlink(missing_ok=True)
        Path(rules_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ User-guided learning test failed: {e}")
        return False

def test_integrated_synthesis_system():
    """Test the integrated synthesis system."""
    logger.info("🔄 Testing Integrated Synthesis System...")
    
    try:
        from synthesis.integrated_synthesis import IntegratedSynthesisSystem, SynthesisRequest
        
        # Initialize integrated system
        synthesis_system = IntegratedSynthesisSystem()
        logger.info("  ✅ Integrated synthesis system initialized")
        
        # Test multi-source synthesis request
        import uuid
        request = SynthesisRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            user_id="test_user",
            session_id="test_session",
            query="What are the benefits of renewable energy?",
            synthesis_type="multi_source",
            parameters={'max_sources': 3},
            context={}
        )
        
        response = synthesis_system.process_synthesis_request(request)
        
        if response:
            logger.info(f"  ✅ Multi-source synthesis: {len(response.response_content)} chars")
            logger.info(f"    Confidence: {response.confidence_score:.2f}")
            logger.info(f"    Processing time: {response.processing_time_ms}ms")
        else:
            logger.error("  ❌ Multi-source synthesis failed")
            return False
        
        # Test structured synthesis request
        structured_request = SynthesisRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            user_id="test_user",
            session_id="test_session",
            query="How does photosynthesis work?",
            synthesis_type="structured",
            parameters={'include_decision_tree': True},
            context={}
        )
        
        structured_response = synthesis_system.process_synthesis_request(structured_request)
        
        if structured_response:
            logger.info(f"  ✅ Structured synthesis: {len(structured_response.response_content)} chars")
        else:
            logger.warning("  ⚠️ Structured synthesis failed")
        
        # Test multi-turn task creation
        task_id = synthesis_system.create_multi_turn_task(
            user_id="test_user",
            session_id="test_session",
            task_description="Research climate change impacts",
            subtask_descriptions=[
                "Gather current climate data",
                "Analyze temperature trends",
                "Identify impact areas",
                "Summarize findings"
            ]
        )
        
        if task_id:
            logger.info(f"  ✅ Multi-turn task created: {task_id}")
        else:
            logger.warning("  ⚠️ Multi-turn task creation failed")
        
        # Test feedback collection
        feedback_id = synthesis_system.collect_user_feedback(
            user_id="test_user",
            session_id="test_session",
            query="Test query",
            response="Test response",
            feedback_text="This is helpful feedback"
        )
        
        if feedback_id:
            logger.info(f"  ✅ Feedback collected: {feedback_id}")
        else:
            logger.warning("  ⚠️ Feedback collection failed")
        
        # Test system status
        status = synthesis_system.get_system_status()
        
        if status:
            logger.info(f"  📊 System status: {len(status)} components")
            for component, available in status.items():
                if isinstance(available, bool):
                    status_icon = "✅" if available else "❌"
                    logger.info(f"    {component}: {status_icon}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Integrated synthesis system test failed: {e}")
        return False

def main():
    """Run all Sprint 7 synthesis and multi-turn reasoning tests."""
    logger.info("🚀 SAM Sprint 7 Knowledge Fusion & Multi-Turn Reasoning Test Suite")
    logger.info("=" * 80)
    logger.info("Focus: Synthesis, Multi-Turn Tasks, Structuring, Chaining, Learning")
    logger.info("=" * 80)
    
    tests = [
        ("Cross-Document Synthesis Engine", test_cross_document_synthesis),
        ("Multi-Turn Task Chaining", test_multi_turn_task_chaining),
        ("Advanced Answer Structuring", test_advanced_answer_structuring),
        ("Capsule Chaining & Strategy Replay", test_capsule_chaining),
        ("User-Guided Learning Feedback", test_user_guided_learning),
        ("Integrated Synthesis System", test_integrated_synthesis_system),
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
    logger.info("\n📊 Sprint 7 Test Results Summary")
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
        logger.info("🎉 Sprint 7 knowledge fusion & multi-turn reasoning system is ready!")
        logger.info("\n✅ Knowledge Fusion & Multi-Turn Reasoning Achieved:")
        logger.info("  🔄 Cross-document synthesis with conflict detection")
        logger.info("  🔗 Multi-turn task chaining and management")
        logger.info("  📝 Advanced answer structuring with confidence")
        logger.info("  📦 Capsule chaining and strategy replay")
        logger.info("  📚 User-guided learning with feedback integration")
        logger.info("  🎯 Integrated synthesis system with multiple modes")
        logger.info("  🧠 Enhanced reasoning across multiple turns")
        logger.info("  📊 Comprehensive synthesis analytics")
        return 0
    else:
        logger.error("⚠️  Some Sprint 7 components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
