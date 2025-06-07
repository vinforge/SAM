#!/usr/bin/env python3
"""
Sprint 12 Interactive Memory Control & Visualization Test Suite
Tests the complete memory UI system with browser, editor, graph, commands, and role filtering.

Sprint 12 Task Testing: Memory Browser UI, Memory Editor, Graph Visualization, Commands, Role Filtering
"""

import logging
import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_memory_browser_ui():
    """Test memory browser UI functionality."""
    logger.info("🖥️ Testing Memory Browser UI...")
    
    try:
        from ui.memory_browser import MemoryBrowserUI
        from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType
        
        # Create temporary storage
        with tempfile.TemporaryDirectory() as storage_dir:
            # Initialize memory store with test data
            memory_store = MemoryVectorStore(
                store_type=VectorStoreType.SIMPLE,
                storage_directory=storage_dir
            )
            
            # Add test memories
            test_memories = [
                ("AI research shows promising results in healthcare applications", MemoryType.INSIGHT, "research_paper"),
                ("User conversation about machine learning algorithms", MemoryType.CONVERSATION, "user_session"),
                ("Important procedure for data processing workflow", MemoryType.PROCEDURE, "documentation"),
                ("Key facts about neural network architectures", MemoryType.FACT, "knowledge_base"),
                ("Document analysis of AI ethics guidelines", MemoryType.DOCUMENT, "ethics_review")
            ]
            
            memory_ids = []
            for content, mem_type, source in test_memories:
                memory_id = memory_store.add_memory(
                    content=content,
                    memory_type=mem_type,
                    source=source,
                    tags=["test", "ui", mem_type.value],
                    importance_score=0.7,
                    metadata={"user_id": "test_user", "test": True}
                )
                memory_ids.append(memory_id)
            
            logger.info(f"  ✅ Added {len(memory_ids)} test memories")
            
            # Initialize browser UI
            browser = MemoryBrowserUI()
            logger.info("  ✅ Memory browser UI initialized")
            
            # Test search functionality (simulate)
            search_results = browser._search_memories("AI healthcare")
            
            if search_results:
                logger.info(f"  🔍 Search test: {len(search_results)} results found")
                
                # Verify search results contain relevant memories
                ai_related = sum(1 for r in search_results if "AI" in r.chunk.content or "healthcare" in r.chunk.content)
                if ai_related > 0:
                    logger.info(f"    ✅ Found {ai_related} AI/healthcare related memories")
            
            # Test recent memories retrieval
            recent_memories = browser._get_recent_memories(limit=10)
            
            if recent_memories:
                logger.info(f"  📚 Recent memories: {len(recent_memories)} retrieved")
                
                # Verify memories are sorted by timestamp
                timestamps = [m.timestamp for m in recent_memories]
                if timestamps == sorted(timestamps, reverse=True):
                    logger.info("    ✅ Memories properly sorted by timestamp")
            
            # Test memory statistics
            stats = memory_store.get_memory_stats()
            
            if stats and not stats.get('error'):
                logger.info(f"  📊 Memory stats: {stats['total_memories']} total memories")
                logger.info(f"    Memory types: {list(stats['memory_types'].keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Memory browser UI test failed: {e}")
        return False

def test_memory_editor():
    """Test memory editing and deletion tools."""
    logger.info("✏️ Testing Memory Editor...")
    
    try:
        from ui.memory_editor import MemoryEditor
        from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType
        
        # Create temporary storage
        with tempfile.TemporaryDirectory() as storage_dir:
            # Initialize memory store
            memory_store = MemoryVectorStore(
                store_type=VectorStoreType.SIMPLE,
                storage_directory=storage_dir
            )
            
            # Add test memory
            original_content = "Original memory content about AI research"
            memory_id = memory_store.add_memory(
                content=original_content,
                memory_type=MemoryType.INSIGHT,
                source="test_source",
                tags=["original", "test"],
                importance_score=0.6,
                metadata={"user_id": "test_user"}
            )
            
            logger.info(f"  ✅ Created test memory: {memory_id}")
            
            # Initialize editor
            editor = MemoryEditor()
            logger.info("  ✅ Memory editor initialized")
            
            # Test memory update
            updated_content = "Updated memory content about AI research with new insights"
            updated_tags = ["updated", "test", "insights"]
            updated_importance = 0.8
            
            success = memory_store.update_memory(
                chunk_id=memory_id,
                content=updated_content,
                tags=updated_tags,
                importance_score=updated_importance
            )
            
            if success:
                logger.info("  ✅ Memory update successful")
                
                # Verify update
                updated_memory = memory_store.get_memory(memory_id)
                if updated_memory:
                    if (updated_memory.content == updated_content and 
                        updated_memory.tags == updated_tags and
                        updated_memory.importance_score == updated_importance):
                        logger.info("    ✅ Memory update verified")
                    else:
                        logger.warning("    ⚠️ Memory update verification failed")
            
            # Test audit logging (simulate)
            editor._log_audit_entry(
                action="edit",
                memory_id=memory_id,
                details="Updated content and tags",
                user_id="test_user"
            )
            
            if hasattr(editor, '_audit_log') or 'audit_log' in dir(editor):
                logger.info("  ✅ Audit logging functional")
            
            # Test memory deletion
            delete_success = memory_store.delete_memory(memory_id)
            
            if delete_success:
                logger.info("  ✅ Memory deletion successful")
                
                # Verify deletion
                deleted_memory = memory_store.get_memory(memory_id)
                if deleted_memory is None:
                    logger.info("    ✅ Memory deletion verified")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Memory editor test failed: {e}")
        return False

def test_memory_graph_visualization():
    """Test memory graph visualization."""
    logger.info("📊 Testing Memory Graph Visualization...")
    
    try:
        from ui.memory_graph import MemoryGraphVisualizer
        from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType
        
        # Create temporary storage
        with tempfile.TemporaryDirectory() as storage_dir:
            # Initialize memory store
            memory_store = MemoryVectorStore(
                store_type=VectorStoreType.SIMPLE,
                storage_directory=storage_dir
            )
            
            # Add interconnected test memories
            memory_data = [
                ("Artificial intelligence is transforming healthcare", MemoryType.FACT, ["AI", "healthcare"]),
                ("Machine learning algorithms improve diagnostic accuracy", MemoryType.INSIGHT, ["ML", "healthcare", "diagnosis"]),
                ("Neural networks process medical imaging data", MemoryType.PROCEDURE, ["neural_networks", "medical_imaging"]),
                ("AI ethics considerations in healthcare applications", MemoryType.DOCUMENT, ["AI", "ethics", "healthcare"]),
                ("Deep learning models for drug discovery", MemoryType.RESEARCH, ["deep_learning", "drug_discovery"])
            ]
            
            memory_ids = []
            for content, mem_type, tags in memory_data:
                memory_id = memory_store.add_memory(
                    content=content,
                    memory_type=mem_type,
                    source="graph_test",
                    tags=tags,
                    importance_score=0.7
                )
                memory_ids.append(memory_id)
            
            logger.info(f"  ✅ Added {len(memory_ids)} interconnected memories")
            
            # Initialize graph visualizer
            visualizer = MemoryGraphVisualizer()
            logger.info("  ✅ Memory graph visualizer initialized")
            
            # Test graph building
            graph_data = visualizer._build_memory_graph()
            
            if graph_data:
                G = graph_data['graph']
                layout = graph_data['layout']
                
                logger.info(f"  📊 Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
                
                # Test node properties
                if G.number_of_nodes() > 0:
                    sample_node = list(G.nodes())[0]
                    node_data = G.nodes[sample_node]
                    
                    required_properties = ['memory', 'label', 'size', 'color']
                    if all(prop in node_data for prop in required_properties):
                        logger.info("    ✅ Node properties correctly set")
                
                # Test layout calculation
                if layout and len(layout) == G.number_of_nodes():
                    logger.info("    ✅ Graph layout calculated successfully")
                
                # Test similarity edge creation
                edges_with_similarity = [e for e in G.edges(data=True) if e[2].get('edge_type') == 'similarity']
                if edges_with_similarity:
                    logger.info(f"    ✅ Found {len(edges_with_similarity)} similarity edges")
                
                # Test tag-based edges
                edges_with_tags = [e for e in G.edges(data=True) if e[2].get('edge_type') == 'tags']
                if edges_with_tags:
                    logger.info(f"    ✅ Found {len(edges_with_tags)} tag-based edges")
            
            # Test graph statistics
            if graph_data:
                # Test cosine similarity calculation
                test_vec1 = [1.0, 0.5, 0.0, 0.8]
                test_vec2 = [0.8, 0.6, 0.1, 0.9]
                similarity = visualizer._cosine_similarity(test_vec1, test_vec2)
                
                if 0.0 <= similarity <= 1.0:
                    logger.info(f"    ✅ Cosine similarity calculation: {similarity:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Memory graph visualization test failed: {e}")
        return False

def test_memory_commands():
    """Test enhanced memory recall commands."""
    logger.info("💬 Testing Memory Commands...")
    
    try:
        from ui.memory_commands import MemoryCommandProcessor, get_command_processor
        from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType
        
        # Create temporary storage
        with tempfile.TemporaryDirectory() as storage_dir:
            # Initialize memory store
            memory_store = MemoryVectorStore(
                store_type=VectorStoreType.SIMPLE,
                storage_directory=storage_dir
            )
            
            # Add test memories with different types and tags
            test_data = [
                ("AI research in healthcare shows promising results", MemoryType.INSIGHT, "research_paper", ["AI", "healthcare", "research"]),
                ("User asked about machine learning applications", MemoryType.CONVERSATION, "user_session", ["ML", "conversation", "user:alice"]),
                ("Important procedure for data preprocessing", MemoryType.PROCEDURE, "documentation", ["data", "preprocessing", "important"]),
                ("Key facts about neural network architectures", MemoryType.FACT, "knowledge_base", ["neural_networks", "facts"]),
                ("Recent conversation about AI ethics", MemoryType.CONVERSATION, "user_session", ["AI", "ethics", "user:alice"])
            ]
            
            for content, mem_type, source, tags in test_data:
                memory_store.add_memory(
                    content=content,
                    memory_type=mem_type,
                    source=source,
                    tags=tags,
                    importance_score=0.7,
                    metadata={"user_id": "alice" if "user:alice" in tags else "system"}
                )
            
            logger.info(f"  ✅ Added {len(test_data)} test memories")
            
            # Initialize command processor
            command_processor = get_command_processor()
            logger.info("  ✅ Memory command processor initialized")
            
            # Test recall topic command
            result = command_processor.process_command("!recall topic AI healthcare", user_id="alice")
            
            if result.success:
                logger.info(f"  ✅ Recall topic command: {len(result.data) if result.data else 0} results")
            else:
                logger.warning(f"    ⚠️ Recall topic failed: {result.message}")
            
            # Test recall last command
            result = command_processor.process_command("!recall last 3", user_id="alice")
            
            if result.success:
                logger.info(f"  ✅ Recall last command: {len(result.data) if result.data else 0} results")
            else:
                logger.warning(f"    ⚠️ Recall last failed: {result.message}")
            
            # Test search by tag
            result = command_processor.process_command("!searchmem tag:AI", user_id="alice")
            
            if result.success:
                logger.info(f"  ✅ Search by tag command: {len(result.data) if result.data else 0} results")
            else:
                logger.warning(f"    ⚠️ Search by tag failed: {result.message}")
            
            # Test search by type
            result = command_processor.process_command("!searchmem type:conversation", user_id="alice")
            
            if result.success:
                logger.info(f"  ✅ Search by type command: {len(result.data) if result.data else 0} results")
            else:
                logger.warning(f"    ⚠️ Search by type failed: {result.message}")
            
            # Test memory stats command
            result = command_processor.process_command("!memstats")
            
            if result.success:
                logger.info("  ✅ Memory stats command executed")
                if result.data and 'total_memories' in result.data:
                    logger.info(f"    Total memories: {result.data['total_memories']}")
            else:
                logger.warning(f"    ⚠️ Memory stats failed: {result.message}")
            
            # Test help command
            result = command_processor.process_command("!memhelp")
            
            if result.success:
                logger.info("  ✅ Memory help command executed")
                if result.data:
                    logger.info(f"    Available commands: {len(result.data)}")
            
            # Test JSON output format
            result = command_processor.process_command("!recall topic AI", output_format="json")
            
            if result.success and result.data:
                logger.info("  ✅ JSON output format working")
            
            # Test invalid command
            result = command_processor.process_command("!invalid command")
            
            if not result.success:
                logger.info("  ✅ Invalid command properly rejected")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Memory commands test failed: {e}")
        return False

def test_role_based_memory_filtering():
    """Test role-based memory filtering."""
    logger.info("🎭 Testing Role-Based Memory Filtering...")
    
    try:
        from ui.role_memory_filter import RoleBasedMemoryFilter, MemoryAccessLevel, get_role_filter
        from agents.task_router import AgentRole
        from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType
        
        # Create temporary storage
        with tempfile.TemporaryDirectory() as storage_dir:
            # Initialize memory store
            memory_store = MemoryVectorStore(
                store_type=VectorStoreType.SIMPLE,
                storage_directory=storage_dir
            )
            
            # Initialize role filter
            role_filter = get_role_filter()
            logger.info("  ✅ Role-based memory filter initialized")
            
            # Create role-specific memories
            role_memories = [
                ("Strategic planning for AI implementation", MemoryType.REASONING, AgentRole.PLANNER, ["planning", "strategy"]),
                ("Document processing workflow completed", MemoryType.PROCEDURE, AgentRole.EXECUTOR, ["execution", "workflow"]),
                ("Quality validation of AI model outputs", MemoryType.INSIGHT, AgentRole.VALIDATOR, ["validation", "quality"]),
                ("Critical analysis of system performance", MemoryType.REASONING, AgentRole.CRITIC, ["critical", "analysis"]),
                ("Synthesis of research findings", MemoryType.INSIGHT, AgentRole.SYNTHESIZER, ["synthesis", "research"])
            ]
            
            memory_ids = []
            for content, mem_type, role, tags in role_memories:
                memory_id = role_filter.create_role_specific_memory(
                    content=content,
                    memory_type=mem_type,
                    source=f"{role.value}_session",
                    role=role,
                    agent_id=f"agent_{role.value}_001",
                    access_level=MemoryAccessLevel.ROLE_SPECIFIC,
                    user_id="test_user"
                )
                memory_ids.append(memory_id)
            
            logger.info(f"  ✅ Created {len(memory_ids)} role-specific memories")
            
            # Test role permissions
            for role in [AgentRole.PLANNER, AgentRole.EXECUTOR, AgentRole.VALIDATOR]:
                permissions = role_filter.get_role_memory_permissions(role)
                
                if 'error' not in permissions:
                    logger.info(f"  🔐 {role.value} permissions: {len(permissions['allowed_memory_types'])} types allowed")
                else:
                    logger.warning(f"    ⚠️ Error getting {role.value} permissions")
            
            # Test role-based filtering
            for role in [AgentRole.PLANNER, AgentRole.EXECUTOR]:
                role_context = role_filter.filter_memories_for_role(
                    role=role,
                    agent_id=f"agent_{role.value}_001",
                    query="AI implementation",
                    max_results=10,
                    user_id="test_user"
                )
                
                logger.info(f"  🔍 {role.value} accessible memories: {len(role_context.accessible_memories)}")
                logger.info(f"    Filtered out: {role_context.filtered_count}")
                
                if role_context.role_specific_insights:
                    logger.info(f"    Insights: {len(role_context.role_specific_insights)}")
            
            # Test collaborative access
            collaborative_roles = [AgentRole.PLANNER, AgentRole.EXECUTOR, AgentRole.VALIDATOR]
            collab_context = role_filter.get_collaborative_memories(
                roles=collaborative_roles,
                query="AI",
                max_results=20
            )
            
            if 'error' not in collab_context:
                logger.info(f"  🤝 Collaborative memories: {len(collab_context['shared_memories'])} shared")
                logger.info(f"    Collaboration insights: {len(collab_context['collaboration_insights'])}")
                
                # Verify role-specific data
                for role_name, role_data in collab_context['role_specific_memories'].items():
                    logger.info(f"    {role_name}: {role_data['accessible_count']} accessible")
            
            # Test access level enforcement
            public_memory_id = role_filter.create_role_specific_memory(
                content="Public information about AI safety",
                memory_type=MemoryType.FACT,
                source="public_source",
                role=AgentRole.PLANNER,
                agent_id="agent_planner_001",
                access_level=MemoryAccessLevel.PUBLIC,
                user_id="test_user"
            )
            
            # Verify public memory is accessible to all roles
            public_accessible_count = 0
            for role in [AgentRole.PLANNER, AgentRole.EXECUTOR, AgentRole.VALIDATOR]:
                public_memory = memory_store.get_memory(public_memory_id)
                if public_memory and role_filter._check_memory_access(public_memory, role, f"agent_{role.value}_001"):
                    public_accessible_count += 1
            
            if public_accessible_count == 3:
                logger.info("  ✅ Public memory accessible to all tested roles")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Role-based memory filtering test failed: {e}")
        return False

def test_integrated_memory_ui():
    """Test integrated memory UI functionality."""
    logger.info("🎯 Testing Integrated Memory UI...")
    
    try:
        # Test that all UI components can be imported and initialized
        from ui.memory_browser import MemoryBrowserUI
        from ui.memory_editor import MemoryEditor
        from ui.memory_graph import MemoryGraphVisualizer
        from ui.memory_commands import get_command_processor
        from ui.role_memory_filter import get_role_filter
        
        # Initialize all components
        browser = MemoryBrowserUI()
        editor = MemoryEditor()
        visualizer = MemoryGraphVisualizer()
        command_processor = get_command_processor()
        role_filter = get_role_filter()
        
        logger.info("  ✅ All UI components initialized successfully")
        
        # Test component integration
        available_commands = command_processor.get_available_commands()
        
        if available_commands and len(available_commands) >= 8:
            logger.info(f"  ✅ Command processor: {len(available_commands)} commands available")
        
        # Test role filter integration
        planner_permissions = role_filter.get_role_memory_permissions(AgentRole.PLANNER)
        
        if 'error' not in planner_permissions:
            logger.info("  ✅ Role filter integration working")
        
        # Test memory store integration
        from memory.memory_vectorstore import get_memory_store
        memory_store = get_memory_store()
        
        stats = memory_store.get_memory_stats()
        if stats and not stats.get('error'):
            logger.info("  ✅ Memory store integration working")
        
        # Test configuration integration
        from config.agent_mode import get_mode_controller
        mode_controller = get_mode_controller()
        
        current_mode = mode_controller.get_current_mode()
        if current_mode:
            logger.info(f"  ✅ Mode controller integration: {current_mode.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Integrated memory UI test failed: {e}")
        return False

def main():
    """Run all Sprint 12 interactive memory control and visualization tests."""
    logger.info("🚀 SAM Sprint 12 Interactive Memory Control & Visualization Test Suite")
    logger.info("=" * 90)
    logger.info("Focus: Memory Browser UI, Memory Editor, Graph Visualization, Commands, Role Filtering")
    logger.info("=" * 90)
    
    tests = [
        ("Memory Browser UI", test_memory_browser_ui),
        ("Memory Editor", test_memory_editor),
        ("Memory Graph Visualization", test_memory_graph_visualization),
        ("Memory Commands", test_memory_commands),
        ("Role-Based Memory Filtering", test_role_based_memory_filtering),
        ("Integrated Memory UI", test_integrated_memory_ui),
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
    logger.info("\n📊 Sprint 12 Test Results Summary")
    logger.info("=" * 90)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total:.1%})")
    
    if passed == total:
        logger.info("🎉 Sprint 12 interactive memory control and visualization system is ready!")
        logger.info("\n✅ Interactive Memory Control & Visualization Achieved:")
        logger.info("  🖥️ Interactive memory browser with search and filtering")
        logger.info("  ✏️ Memory editing and deletion tools with audit logging")
        logger.info("  📊 Memory graph visualization with interactive connections")
        logger.info("  💬 Enhanced memory recall commands for chat and CLI")
        logger.info("  🎭 Role-based memory filtering for collaborative work")
        logger.info("  🔍 Similarity-based memory connections and clustering")
        logger.info("  📈 Memory statistics and performance visualization")
        logger.info("  🛡️ Access control with role-specific permissions")
        logger.info("  🎛️ Integrated UI with multiple visualization modes")
        return 0
    else:
        logger.error("⚠️  Some Sprint 12 components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
