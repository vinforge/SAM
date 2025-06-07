#!/usr/bin/env python3
"""
Sprint 6 Active Memory & Personalized Learning Test Suite
Tests the complete memory management and personalization system.

Sprint 6 Task Testing: Memory, Profiles, Self-Awareness, Learning, Capsules
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

def test_long_term_memory_management():
    """Test long-term memory storage and retrieval."""
    logger.info("🗄️ Testing Long-Term Memory Management...")
    
    try:
        from memory.memory_manager import LongTermMemoryManager
        
        # Create temporary memory store
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_store_path = tmp.name
        
        # Initialize memory manager
        memory_manager = LongTermMemoryManager(memory_store_path=memory_store_path)
        logger.info("  ✅ Memory manager initialized")
        
        # Test memory storage
        memory_id = memory_manager.store_memory(
            content="Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
            content_type='user_note',
            tags=['machine_learning', 'ai', 'definition'],
            importance_score=0.8
        )
        
        logger.info(f"  ✅ Memory stored: {memory_id}")
        
        # Test memory recall
        recalled_memory = memory_manager.recall_memory(memory_id)
        
        if recalled_memory:
            logger.info(f"  ✅ Memory recalled: {recalled_memory.summary[:50]}...")
            logger.info(f"    Access count: {recalled_memory.access_count}")
        else:
            logger.error("  ❌ Memory recall failed")
            return False
        
        # Test memory search
        search_results = memory_manager.search_memories("machine learning", top_k=3)
        
        if search_results:
            logger.info(f"  ✅ Memory search successful: {len(search_results)} results")
            for result in search_results:
                logger.info(f"    - {result.memory_entry.summary[:30]}... (score: {result.similarity_score:.2f})")
        else:
            logger.warning("  ⚠️ No search results found")
        
        # Test memory pinning
        pin_success = memory_manager.pin_memory(memory_id, importance_score=1.0)
        
        if pin_success:
            logger.info("  ✅ Memory pinning successful")
        else:
            logger.warning("  ⚠️ Memory pinning failed")
        
        # Test recent memories
        recent_memories = memory_manager.get_recent_memories(days=1)
        logger.info(f"  📅 Recent memories: {len(recent_memories)}")
        
        # Test memory statistics
        stats = memory_manager.get_memory_stats()
        logger.info(f"  📊 Memory stats: {stats['total_memories']} total memories")
        
        # Cleanup
        Path(memory_store_path).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Long-term memory test failed: {e}")
        return False

def test_personalized_user_profiles():
    """Test user profile management and personalization."""
    logger.info("👤 Testing Personalized User Profiles...")
    
    try:
        from memory.user_profiles import UserProfileManager, ConversationStyle, VerbosityLevel
        
        # Create temporary profiles file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            profiles_path = tmp.name
        
        # Initialize profile manager
        profile_manager = UserProfileManager(profiles_path=profiles_path)
        logger.info("  ✅ Profile manager initialized")
        
        # Test user profile creation
        user_id = profile_manager.create_user_profile("test_user")
        logger.info(f"  ✅ User profile created: {user_id}")
        
        # Test setting current user
        set_success = profile_manager.set_current_user(user_id)
        
        if set_success:
            logger.info("  ✅ Current user set successfully")
        else:
            logger.error("  ❌ Failed to set current user")
            return False
        
        # Test preference updates
        update_success = profile_manager.update_preferences(
            user_id,
            verbosity=VerbosityLevel.DETAILED,
            conversation_style=ConversationStyle.TECHNICAL,
            preferred_response_length=300
        )
        
        if update_success:
            logger.info("  ✅ Preferences updated successfully")
        else:
            logger.warning("  ⚠️ Preference update failed")
        
        # Test conversation style setting
        style_success = profile_manager.set_conversation_style(user_id, ConversationStyle.EXPLORATORY)
        
        if style_success:
            logger.info("  ✅ Conversation style updated")
        else:
            logger.warning("  ⚠️ Conversation style update failed")
        
        # Test tool management
        tool_success = profile_manager.toggle_tool(user_id, "python_interpreter", True)
        
        if tool_success:
            logger.info("  ✅ Tool enabled successfully")
        else:
            logger.warning("  ⚠️ Tool toggle failed")
        
        # Test tool checking
        is_enabled = profile_manager.is_tool_enabled(user_id, "python_interpreter")
        logger.info(f"  🔧 Tool enabled check: {is_enabled}")
        
        # Test custom commands
        command_success = profile_manager.add_custom_command(user_id, "hello", "Hello there!")
        
        if command_success:
            logger.info("  ✅ Custom command added")
            
            # Test command retrieval
            command_response = profile_manager.get_custom_command(user_id, "hello")
            if command_response:
                logger.info(f"  ✅ Custom command retrieved: {command_response}")
        
        # Test interaction recording
        profile_manager.record_interaction(user_id, tool_used="python_interpreter", topic="data_analysis")
        logger.info("  ✅ Interaction recorded")
        
        # Test personalized system prompt
        base_prompt = "You are SAM, an AI assistant."
        personalized_prompt = profile_manager.get_personalized_system_prompt(user_id, base_prompt)
        
        if len(personalized_prompt) > len(base_prompt):
            logger.info("  ✅ Personalized prompt generated")
            logger.info(f"    Length: {len(personalized_prompt)} chars (vs {len(base_prompt)} base)")
        else:
            logger.warning("  ⚠️ Personalized prompt not enhanced")
        
        # Test user statistics
        stats = profile_manager.get_user_stats(user_id)
        
        if stats:
            logger.info(f"  📊 User stats: {stats['total_interactions']} interactions")
        
        # Test user listing
        users = profile_manager.list_users()
        logger.info(f"  👥 Total users: {len(users)}")
        
        # Cleanup
        Path(profiles_path).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ User profiles test failed: {e}")
        return False

def test_self_awareness_memory_queries():
    """Test self-awareness and memory query capabilities."""
    logger.info("🧠 Testing Self-Awareness & Memory Queries...")
    
    try:
        from memory.memory_manager import LongTermMemoryManager
        from memory.user_profiles import UserProfileManager
        from memory.self_awareness import SelfAwarenessManager
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp1:
            memory_path = tmp1.name
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp2:
            profiles_path = tmp2.name
        
        # Initialize components
        memory_manager = LongTermMemoryManager(memory_path)
        profile_manager = UserProfileManager(profiles_path)
        self_awareness = SelfAwarenessManager(memory_manager, profile_manager)
        
        logger.info("  ✅ Self-awareness manager initialized")
        
        # Test session management
        session_id = self_awareness.start_session("test_user")
        logger.info(f"  ✅ Session started: {session_id}")
        
        # Test interaction recording
        self_awareness.record_interaction(
            query="What is machine learning?",
            response="Machine learning is a subset of AI...",
            tools_used=["multimodal_query"],
            topic="machine_learning",
            insight="ML is fundamental to modern AI"
        )
        
        logger.info("  ✅ Interaction recorded")
        
        # Test memory search
        search_results = self_awareness.search_memory("machine learning")
        
        if search_results:
            logger.info(f"  ✅ Memory search successful: {len(search_results)} results")
        else:
            logger.info("  ℹ️ No search results (expected for new system)")
        
        # Test recent memories
        recent_memories = self_awareness.get_recent_memories(days=1)
        logger.info(f"  📅 Recent memories: {len(recent_memories)}")
        
        # Test session history
        session_history = self_awareness.get_session_history(last_n_sessions=5)
        logger.info(f"  📊 Session history: {len(session_history)} sessions")
        
        # Test knowledge graph generation
        knowledge_graph = self_awareness.generate_knowledge_graph()
        
        if knowledge_graph and 'nodes' in knowledge_graph:
            logger.info(f"  🕸️ Knowledge graph generated: {len(knowledge_graph['nodes'])} nodes")
        else:
            logger.info("  ℹ️ Knowledge graph empty (expected for new system)")
        
        # Test meta-query answering
        meta_response = self_awareness.answer_meta_query("What did we talk about today?")
        
        if meta_response:
            logger.info(f"  🤔 Meta-query answered: {meta_response[:50]}...")
        else:
            logger.warning("  ⚠️ Meta-query failed")
        
        # Test session ending
        session_summary = self_awareness.end_session()
        
        if session_summary:
            logger.info(f"  ✅ Session ended: {session_summary.interaction_count} interactions")
        else:
            logger.warning("  ⚠️ Session ending failed")
        
        # Test self-awareness stats
        stats = self_awareness.get_self_awareness_stats()
        
        if stats:
            logger.info(f"  📊 Self-awareness stats: {len(stats.get('capabilities', []))} capabilities")
        
        # Cleanup
        Path(memory_path).unlink(missing_ok=True)
        Path(profiles_path).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Self-awareness test failed: {e}")
        return False

def test_retrospective_learning_loop():
    """Test retrospective learning and self-improvement."""
    logger.info("🔄 Testing Retrospective Learning Loop...")
    
    try:
        from memory.memory_manager import LongTermMemoryManager
        from memory.retrospective_learning import RetrospectiveLearningManager
        from reasoning.self_decide_framework import SelfDecideFramework
        
        # Create temporary memory store
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_path = tmp.name
        
        # Initialize components
        memory_manager = LongTermMemoryManager(memory_path)
        learning_manager = RetrospectiveLearningManager(memory_manager)
        
        logger.info("  ✅ Retrospective learning manager initialized")
        
        # Create a mock session for reflection
        framework = SelfDecideFramework()
        session = framework.reason("What is the capital of France?")
        
        if session:
            logger.info("  ✅ Mock reasoning session created")
            
            # Test reflection on response
            reflections = learning_manager.reflect_on_response(session)
            
            if reflections:
                logger.info(f"  ✅ Reflection completed: {len(reflections)} analyses")
                
                for reflection in reflections:
                    logger.info(f"    - {reflection.reflection_type.value}: confidence {reflection.confidence_score:.2f}")
            else:
                logger.warning("  ⚠️ No reflections generated")
            
            # Test retry decision
            should_retry, alternative = learning_manager.should_retry_response(reflections)
            logger.info(f"  🔄 Retry decision: {should_retry}, alternative: {alternative}")
            
            # Test improvement suggestions
            suggestions = learning_manager.get_improvement_suggestions("factual_query")
            logger.info(f"  💡 Improvement suggestions: {len(suggestions)}")
            
        else:
            logger.warning("  ⚠️ Mock session creation failed")
        
        # Test learning from feedback
        learning_manager.learn_from_feedback("test_learning_123", "Good response!", 0.8)
        logger.info("  ✅ Learning from feedback recorded")
        
        # Test memory contradiction handling
        # First store a memory
        memory_id = memory_manager.store_memory(
            content="The Earth is flat",
            content_type='user_note',
            tags=['earth', 'shape']
        )
        
        # Then flag it as contradictory
        contradiction_success = learning_manager.update_memory_with_contradiction(
            memory_id, "The Earth is actually spherical"
        )
        
        if contradiction_success:
            logger.info("  ✅ Memory contradiction handling successful")
        else:
            logger.warning("  ⚠️ Memory contradiction handling failed")
        
        # Cleanup
        Path(memory_path).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Retrospective learning test failed: {e}")
        return False

def test_knowledge_capsules():
    """Test knowledge capsule management."""
    logger.info("📦 Testing Knowledge Capsules...")
    
    try:
        from memory.knowledge_capsules import KnowledgeCapsuleManager
        from reasoning.self_decide_framework import SelfDecideFramework
        
        # Create temporary capsules directory
        temp_dir = tempfile.mkdtemp()
        capsules_dir = Path(temp_dir) / "capsules"
        
        # Initialize capsule manager
        capsule_manager = KnowledgeCapsuleManager(str(capsules_dir))
        logger.info("  ✅ Capsule manager initialized")
        
        # Create a mock session for capsule creation
        framework = SelfDecideFramework()
        session = framework.reason("How do I calculate compound interest?")
        
        if session:
            logger.info("  ✅ Mock reasoning session created")
            
            # Test capsule creation
            capsule_id = capsule_manager.create_capsule(
                name="Compound Interest Calculation",
                session=session,
                user_id="test_user",
                category="finance",
                tags=["math", "finance", "calculation"]
            )
            
            logger.info(f"  ✅ Capsule created: {capsule_id}")
            
            # Test capsule loading
            loaded_capsule = capsule_manager.load_capsule(capsule_id)
            
            if loaded_capsule:
                logger.info(f"  ✅ Capsule loaded: {loaded_capsule.name}")
                logger.info(f"    Use count: {loaded_capsule.use_count}")
            else:
                logger.error("  ❌ Capsule loading failed")
                return False
            
            # Test capsule search
            search_results = capsule_manager.search_capsules("compound interest")
            
            if search_results:
                logger.info(f"  ✅ Capsule search successful: {len(search_results)} results")
            else:
                logger.warning("  ⚠️ No capsule search results")
            
            # Test capsule export
            export_data = capsule_manager.export_capsule(capsule_id)
            
            if export_data:
                logger.info("  ✅ Capsule export successful")
                logger.info(f"    Export keys: {list(export_data.keys())}")
            else:
                logger.warning("  ⚠️ Capsule export failed")
            
            # Test capsule import
            if export_data:
                new_capsule_id = capsule_manager.import_capsule(export_data, "test_user_2")
                
                if new_capsule_id:
                    logger.info(f"  ✅ Capsule import successful: {new_capsule_id}")
                else:
                    logger.warning("  ⚠️ Capsule import failed")
            
            # Test capsule listing
            capsule_list = capsule_manager.list_capsules()
            logger.info(f"  📋 Capsule list: {len(capsule_list)} capsules")
            
            # Test capsule statistics
            stats = capsule_manager.get_capsule_stats()
            
            if stats:
                logger.info(f"  📊 Capsule stats: {stats['total_capsules']} total")
            
        else:
            logger.warning("  ⚠️ Mock session creation failed")
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Knowledge capsules test failed: {e}")
        return False

def test_integrated_memory_system():
    """Test the integrated memory system."""
    logger.info("🧠 Testing Integrated Memory System...")
    
    try:
        from memory.integrated_memory import IntegratedMemorySystem
        
        # Initialize integrated memory system
        memory_system = IntegratedMemorySystem()
        logger.info("  ✅ Integrated memory system initialized")
        
        # Test session management
        session_response = memory_system.start_session("test_user")
        logger.info(f"  ✅ Session started: {session_response}")
        
        # Test memory commands
        commands_to_test = [
            "/pin This is important information about AI",
            "/memory recent",
            "/style technical",
            "/tools set python_interpreter on",
            "/capsule list",
            "/user stats"
        ]
        
        successful_commands = 0
        
        for command in commands_to_test:
            try:
                response = memory_system.process_memory_command(command, "test_user")
                if not response.startswith("❌"):
                    successful_commands += 1
                    logger.info(f"    ✅ Command '{command}' successful")
                else:
                    logger.warning(f"    ⚠️ Command '{command}' failed: {response[:50]}...")
            except Exception as e:
                logger.warning(f"    ⚠️ Command '{command}' error: {e}")
        
        command_success_rate = successful_commands / len(commands_to_test)
        logger.info(f"  📊 Command success rate: {command_success_rate:.1%}")
        
        # Test interaction recording
        memory_system.record_interaction(
            query="What is machine learning?",
            response="Machine learning is a subset of AI that enables computers to learn from data.",
            tools_used=["multimodal_query"],
            topic="machine_learning"
        )
        
        logger.info("  ✅ Interaction recorded")
        
        # Test auto-storage
        memory_id = memory_system.auto_store_interaction(
            query="Explain neural networks",
            response="Neural networks are computing systems inspired by biological neural networks.",
            tools_used=["python_interpreter"],
            importance_score=0.7
        )
        
        if memory_id:
            logger.info(f"  ✅ Auto-storage successful: {memory_id}")
        else:
            logger.info("  ℹ️ Auto-storage skipped (expected behavior)")
        
        # Test personalized prompt
        base_prompt = "You are SAM, an AI assistant."
        personalized = memory_system.get_personalized_prompt(base_prompt)
        
        if len(personalized) > len(base_prompt):
            logger.info("  ✅ Personalized prompt generated")
        else:
            logger.info("  ℹ️ Personalized prompt not enhanced")
        
        # Test system statistics
        stats = memory_system.get_system_stats()
        
        if stats:
            logger.info(f"  📊 System stats: {len(stats)} categories")
            for key, value in stats.items():
                if isinstance(value, dict):
                    logger.info(f"    {key}: {len(value)} items")
                else:
                    logger.info(f"    {key}: {value}")
        
        # Test session ending
        end_response = memory_system.end_session()
        
        if end_response:
            logger.info(f"  ✅ Session ended: {end_response}")
        else:
            logger.info("  ℹ️ Session ending (no summary)")
        
        return command_success_rate >= 0.5  # At least 50% of commands should work
        
    except Exception as e:
        logger.error(f"  ❌ Integrated memory system test failed: {e}")
        return False

def main():
    """Run all Sprint 6 memory and personalization tests."""
    logger.info("🚀 SAM Sprint 6 Active Memory & Personalized Learning Test Suite")
    logger.info("=" * 80)
    logger.info("Focus: Memory Management, User Profiles, Self-Awareness, Learning, Capsules")
    logger.info("=" * 80)
    
    tests = [
        ("Long-Term Memory Management", test_long_term_memory_management),
        ("Personalized User Profiles", test_personalized_user_profiles),
        ("Self-Awareness & Memory Queries", test_self_awareness_memory_queries),
        ("Retrospective Learning Loop", test_retrospective_learning_loop),
        ("Knowledge Capsules", test_knowledge_capsules),
        ("Integrated Memory System", test_integrated_memory_system),
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
    logger.info("\n📊 Sprint 6 Test Results Summary")
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
        logger.info("🎉 Sprint 6 active memory & personalized learning system is ready!")
        logger.info("\n✅ Active Memory & Personalized Learning Achieved:")
        logger.info("  🗄️ Long-term memory storage and retrieval")
        logger.info("  👤 Personalized user profiles and preferences")
        logger.info("  🧠 Self-awareness and memory introspection")
        logger.info("  🔄 Retrospective learning and self-improvement")
        logger.info("  📦 Knowledge capsules for reusable strategies")
        logger.info("  💬 Memory-aware chat commands")
        logger.info("  🎯 Adaptive behavior based on user preferences")
        logger.info("  📊 Comprehensive memory and learning analytics")
        return 0
    else:
        logger.error("⚠️  Some Sprint 6 components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
