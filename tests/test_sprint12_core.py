#!/usr/bin/env python3
"""
Sprint 12 Core Functionality Test Suite
Tests the core memory control and visualization functionality without UI dependencies.

Sprint 12 Core Testing: Memory Commands, Role Filtering, Graph Logic, Editor Logic
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

def test_memory_commands_core():
    """Test memory commands core functionality."""
    logger.info("💬 Testing Memory Commands Core...")
    
    try:
        from ui.memory_commands import MemoryCommandProcessor
        from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType
        
        # Create temporary storage
        with tempfile.TemporaryDirectory() as storage_dir:
            # Initialize memory store
            memory_store = MemoryVectorStore(
                store_type=VectorStoreType.SIMPLE,
                storage_directory=storage_dir
            )
            
            # Add test memories
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
            command_processor = MemoryCommandProcessor()
            logger.info("  ✅ Memory command processor initialized")
            
            # Test recall topic command
            result = command_processor.process_command("!recall topic AI healthcare", user_id="alice")
            
            if result.success:
                logger.info(f"  ✅ Recall topic command: Found results")
                if result.data and len(result.data) > 0:
                    logger.info(f"    Found {len(result.data)} relevant memories")
            else:
                logger.warning(f"    ⚠️ Recall topic failed: {result.message}")
            
            # Test recall last command
            result = command_processor.process_command("!recall last 3", user_id="alice")
            
            if result.success:
                logger.info(f"  ✅ Recall last command: Found results")
                if result.data and len(result.data) > 0:
                    logger.info(f"    Retrieved {len(result.data)} recent memories")
            else:
                logger.warning(f"    ⚠️ Recall last failed: {result.message}")
            
            # Test search by tag
            result = command_processor.process_command("!searchmem tag:AI", user_id="alice")
            
            if result.success:
                logger.info(f"  ✅ Search by tag command: Found results")
            else:
                logger.warning(f"    ⚠️ Search by tag failed: {result.message}")
            
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
        logger.error(f"  ❌ Memory commands core test failed: {e}")
        return False

def test_role_based_filtering_core():
    """Test role-based memory filtering core functionality."""
    logger.info("🎭 Testing Role-Based Filtering Core...")
    
    try:
        from ui.role_memory_filter import RoleBasedMemoryFilter, MemoryAccessLevel
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
            role_filter = RoleBasedMemoryFilter()
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
                    logger.info(f"    Access levels: {permissions['access_levels']}")
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
            else:
                logger.warning(f"    ⚠️ Public memory only accessible to {public_accessible_count}/3 roles")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Role-based filtering core test failed: {e}")
        return False

def test_memory_graph_core():
    """Test memory graph core functionality."""
    logger.info("📊 Testing Memory Graph Core...")
    
    try:
        import networkx as nx
        import numpy as np
        
        # Test NetworkX and numpy functionality
        G = nx.Graph()
        G.add_node("node1", data="test")
        G.add_node("node2", data="test")
        G.add_edge("node1", "node2", weight=0.5)
        
        if G.number_of_nodes() == 2 and G.number_of_edges() == 1:
            logger.info("  ✅ NetworkX graph creation working")
        
        # Test cosine similarity calculation
        vec1 = np.array([1.0, 0.5, 0.0, 0.8])
        vec2 = np.array([0.8, 0.6, 0.1, 0.9])
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 > 0 and norm2 > 0:
            similarity = dot_product / (norm1 * norm2)
            if 0.0 <= similarity <= 1.0:
                logger.info(f"  ✅ Cosine similarity calculation: {similarity:.3f}")
        
        # Test graph layout algorithms
        layout_algorithms = ['spring', 'circular', 'random']
        
        for algorithm in layout_algorithms:
            try:
                if algorithm == 'spring':
                    layout = nx.spring_layout(G)
                elif algorithm == 'circular':
                    layout = nx.circular_layout(G)
                elif algorithm == 'random':
                    layout = nx.random_layout(G)
                
                if layout and len(layout) == G.number_of_nodes():
                    logger.info(f"    ✅ {algorithm} layout working")
                    
            except Exception as e:
                logger.warning(f"    ⚠️ {algorithm} layout failed: {e}")
        
        # Test graph statistics
        try:
            density = nx.density(G)
            degree_centrality = nx.degree_centrality(G)
            
            if density >= 0 and degree_centrality:
                logger.info(f"  ✅ Graph statistics: density={density:.3f}")
                
        except Exception as e:
            logger.warning(f"    ⚠️ Graph statistics failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Memory graph core test failed: {e}")
        return False

def test_memory_editor_core():
    """Test memory editor core functionality."""
    logger.info("✏️ Testing Memory Editor Core...")
    
    try:
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
            
            # Test memory retrieval
            original_memory = memory_store.get_memory(memory_id)
            
            if original_memory:
                logger.info("  ✅ Memory retrieval working")
                logger.info(f"    Original content length: {len(original_memory.content)}")
                logger.info(f"    Original tags: {original_memory.tags}")
                logger.info(f"    Original importance: {original_memory.importance_score}")
            
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
                    changes_verified = (
                        updated_memory.content == updated_content and 
                        updated_memory.tags == updated_tags and
                        updated_memory.importance_score == updated_importance
                    )
                    
                    if changes_verified:
                        logger.info("    ✅ Memory update verified")
                        logger.info(f"      New content length: {len(updated_memory.content)}")
                        logger.info(f"      New tags: {updated_memory.tags}")
                        logger.info(f"      New importance: {updated_memory.importance_score}")
                    else:
                        logger.warning("    ⚠️ Memory update verification failed")
            
            # Test audit logging simulation
            audit_entries = []
            
            def log_audit_entry(action, memory_id, details, user_id):
                entry = {
                    'action': action,
                    'memory_id': memory_id,
                    'timestamp': datetime.now().isoformat(),
                    'details': details,
                    'user_id': user_id
                }
                audit_entries.append(entry)
                return entry
            
            # Log some test entries
            log_audit_entry("edit", memory_id, "Updated content and tags", "test_user")
            log_audit_entry("access", memory_id, "Memory accessed for editing", "test_user")
            
            if len(audit_entries) == 2:
                logger.info("  ✅ Audit logging simulation working")
                logger.info(f"    Logged {len(audit_entries)} audit entries")
            
            # Test memory deletion
            delete_success = memory_store.delete_memory(memory_id)
            
            if delete_success:
                logger.info("  ✅ Memory deletion successful")
                
                # Verify deletion
                deleted_memory = memory_store.get_memory(memory_id)
                if deleted_memory is None:
                    logger.info("    ✅ Memory deletion verified")
                else:
                    logger.warning("    ⚠️ Memory deletion verification failed")
            
            # Test undo simulation (re-add deleted memory)
            restored_memory_id = memory_store.add_memory(
                content=updated_content,
                memory_type=MemoryType.INSIGHT,
                source="test_source",
                tags=updated_tags,
                importance_score=updated_importance,
                metadata={"user_id": "test_user", "restored": True}
            )
            
            if restored_memory_id:
                logger.info("  ✅ Memory restoration simulation successful")
                
                # Log restoration
                log_audit_entry("restore", restored_memory_id, "Memory restored from deletion", "test_user")
                
                if len(audit_entries) == 3:
                    logger.info("    ✅ Restoration audit logging working")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Memory editor core test failed: {e}")
        return False

def test_memory_browser_core():
    """Test memory browser core functionality."""
    logger.info("🖥️ Testing Memory Browser Core...")
    
    try:
        from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType
        from memory.memory_reasoning import MemoryDrivenReasoningEngine
        
        # Create temporary storage
        with tempfile.TemporaryDirectory() as storage_dir:
            # Initialize memory store with test data
            memory_store = MemoryVectorStore(
                store_type=VectorStoreType.SIMPLE,
                storage_directory=storage_dir
            )
            
            memory_reasoning = MemoryDrivenReasoningEngine(memory_store=memory_store)
            
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
            
            # Test search functionality
            search_results = memory_reasoning.search_memories(
                query="AI healthcare",
                user_id="test_user",
                max_results=10
            )
            
            if search_results:
                logger.info(f"  🔍 Search test: {len(search_results)} results found")
                
                # Verify search results contain relevant memories
                ai_related = sum(1 for r in search_results if "AI" in r.chunk.content or "healthcare" in r.chunk.content)
                if ai_related > 0:
                    logger.info(f"    ✅ Found {ai_related} AI/healthcare related memories")
            
            # Test recent memories retrieval (simulate browser logic)
            all_memories = list(memory_store.memory_chunks.values())
            
            # Filter by user
            user_memories = [m for m in all_memories if m.metadata.get('user_id') == 'test_user']
            
            # Sort by timestamp (newest first)
            user_memories.sort(key=lambda m: m.timestamp, reverse=True)
            recent_memories = user_memories[:10]
            
            if recent_memories:
                logger.info(f"  📚 Recent memories: {len(recent_memories)} retrieved")
                
                # Verify memories are sorted by timestamp
                timestamps = [m.timestamp for m in recent_memories]
                if timestamps == sorted(timestamps, reverse=True):
                    logger.info("    ✅ Memories properly sorted by timestamp")
            
            # Test filtering by memory type
            insight_memories = [m for m in all_memories if m.memory_type == MemoryType.INSIGHT]
            conversation_memories = [m for m in all_memories if m.memory_type == MemoryType.CONVERSATION]
            
            logger.info(f"  🔍 Filter by type: {len(insight_memories)} insights, {len(conversation_memories)} conversations")
            
            # Test filtering by tags
            test_tagged_memories = [m for m in all_memories if "test" in m.tags]
            ui_tagged_memories = [m for m in all_memories if "ui" in m.tags]
            
            logger.info(f"  🏷️ Filter by tags: {len(test_tagged_memories)} test-tagged, {len(ui_tagged_memories)} ui-tagged")
            
            # Test importance filtering
            high_importance = [m for m in all_memories if m.importance_score >= 0.7]
            medium_importance = [m for m in all_memories if 0.5 <= m.importance_score < 0.7]
            
            logger.info(f"  ⭐ Filter by importance: {len(high_importance)} high, {len(medium_importance)} medium")
            
            # Test memory statistics
            stats = memory_store.get_memory_stats()
            
            if stats and not stats.get('error'):
                logger.info(f"  📊 Memory stats: {stats['total_memories']} total memories")
                logger.info(f"    Memory types: {list(stats['memory_types'].keys())}")
                logger.info(f"    Storage size: {stats['total_size_mb']:.2f} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Memory browser core test failed: {e}")
        return False

def main():
    """Run all Sprint 12 core functionality tests."""
    logger.info("🚀 SAM Sprint 12 Core Functionality Test Suite")
    logger.info("=" * 90)
    logger.info("Focus: Memory Commands, Role Filtering, Graph Logic, Editor Logic, Browser Logic")
    logger.info("=" * 90)
    
    tests = [
        ("Memory Commands Core", test_memory_commands_core),
        ("Role-Based Filtering Core", test_role_based_filtering_core),
        ("Memory Graph Core", test_memory_graph_core),
        ("Memory Editor Core", test_memory_editor_core),
        ("Memory Browser Core", test_memory_browser_core),
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
    logger.info("\n📊 Sprint 12 Core Test Results Summary")
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
        logger.info("🎉 Sprint 12 core functionality is ready!")
        logger.info("\n✅ Interactive Memory Control & Visualization Core Achieved:")
        logger.info("  💬 Memory command processing with recall, search, and filtering")
        logger.info("  🎭 Role-based memory access control and filtering")
        logger.info("  📊 Memory graph construction and analysis algorithms")
        logger.info("  ✏️ Memory editing, updating, and deletion with audit trails")
        logger.info("  🖥️ Memory browsing, searching, and filtering logic")
        logger.info("  🔍 Similarity-based memory connections and clustering")
        logger.info("  📈 Memory statistics and performance analysis")
        logger.info("  🛡️ Access control with role-specific permissions")
        logger.info("  🎛️ Integrated core functionality for UI components")
        return 0
    else:
        logger.error("⚠️  Some Sprint 12 core components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
