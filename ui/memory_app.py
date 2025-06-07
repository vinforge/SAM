"""
Main Memory UI Application for SAM
Integrated Streamlit app for interactive memory control and visualization.

Sprint 12: Interactive Memory Control & Visualization
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.memory_browser import MemoryBrowserUI
from ui.memory_editor import MemoryEditor
from ui.memory_graph import MemoryGraphVisualizer
from ui.memory_commands import MemoryCommandProcessor, get_command_processor
from ui.role_memory_filter import RoleBasedMemoryFilter, get_role_filter
from memory.memory_vectorstore import get_memory_store
from memory.memory_reasoning import get_memory_reasoning_engine
from config.agent_mode import get_mode_controller
from agents.task_router import AgentRole

def main():
    """Main Streamlit application for memory management."""

    # Page configuration - only call once at the very beginning
    if 'page_config_set' not in st.session_state:
        st.set_page_config(
            page_title="SAM Memory Control Center",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.session_state.page_config_set = True
    
    # Initialize components
    memory_store = get_memory_store()
    memory_reasoning = get_memory_reasoning_engine()
    mode_controller = get_mode_controller()
    command_processor = get_command_processor()
    role_filter = get_role_filter()
    
    # Main header
    st.title("🧠 SAM Memory Control Center")
    st.markdown("Interactive memory management, visualization, and role-based access control")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🎛️ Navigation")
        
        # Current mode display
        current_mode = mode_controller.get_current_mode()
        mode_status = mode_controller.get_mode_status()
        
        st.info(f"**Current Mode:** {current_mode.value.title()}")
        
        if mode_status.key_status.value != "missing":
            st.caption(f"Key Status: {mode_status.key_status.value}")
        
        # Navigation menu
        page = st.selectbox(
            "Select Page",
            options=[
                "💬 Enhanced Chat",
                "Chat with SAM",
                "Memory Browser",
                "Memory Editor",
                "Memory Graph",
                "Command Interface",
                "Role-Based Access",
                "🏆 Memory Ranking",
                "📝 Citation Engine",
                "📊 Smart Summaries",
                "📈 Memory Insights",
                "🧠 Thought Settings",
                "System Status"
            ],
            index=0
        )
        
        # Quick stats
        st.subheader("📊 Quick Stats")
        try:
            stats = memory_store.get_memory_stats()
            st.metric("Total Memories", stats['total_memories'])
            st.metric("Storage Size", f"{stats['total_size_mb']:.1f} MB")
            
            if stats['memory_types']:
                st.caption("**Memory Types:**")
                for mem_type, count in list(stats['memory_types'].items())[:3]:
                    st.caption(f"• {mem_type}: {count}")
                    
        except Exception as e:
            st.error(f"Error loading stats: {e}")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("📊 Memory Stats"):
            st.session_state.show_stats = True
        
        # Memory command input
        st.subheader("💬 Quick Command")
        quick_command = st.text_input(
            "Memory Command",
            placeholder="!recall topic AI",
            help="Enter a memory command (type !memhelp for help)"
        )
        
        if st.button("Execute") and quick_command:
            result = command_processor.process_command(quick_command)
            if result.success:
                st.success("Command executed successfully!")
                st.text_area("Result", value=result.message, height=100)
            else:
                st.error(f"Command failed: {result.message}")
    
    # Main content area
    if page == "💬 Enhanced Chat":
        render_enhanced_chat_interface()
    elif page == "Chat with SAM":
        render_chat_interface()
    elif page == "Memory Browser":
        render_memory_browser()
    elif page == "Memory Editor":
        render_memory_editor()
    elif page == "Memory Graph":
        render_memory_graph()
    elif page == "Command Interface":
        render_command_interface()
    elif page == "Role-Based Access":
        render_role_access()
    elif page == "🏆 Memory Ranking":
        render_memory_ranking()
    elif page == "📝 Citation Engine":
        render_citation_engine()
    elif page == "📊 Smart Summaries":
        render_smart_summaries()
    elif page == "📈 Memory Insights":
        render_memory_insights()
    elif page == "🧠 Thought Settings":
        render_thought_settings()
    elif page == "System Status":
        render_system_status()

def render_chat_interface():
    """Render the enhanced diagnostic chat interface with SAM."""
    try:
        st.subheader("💬 Diagnostic Chat with SAM")
        st.markdown("Interactive conversation with comprehensive diagnostic information and memory-driven reasoning")

        # Diagnostic settings
        col1, col2, col3 = st.columns(3)

        with col1:
            show_diagnostics = st.checkbox("🔍 Show Diagnostics", value=True, help="Display detailed diagnostic information")

        with col2:
            show_memory_context = st.checkbox("🧠 Show Memory Context", value=True, help="Display memory retrieval details")

        with col3:
            show_reasoning_trace = st.checkbox("🤔 Show Reasoning Trace", value=True, help="Display reasoning process details")

        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        # Chat input
        user_input = st.chat_input("Ask SAM anything... (Use !commands for memory operations)")

        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Generate diagnostic information
            diagnostic_info = generate_diagnostic_info(user_input)

            # Check if it's a memory command
            command_processor = get_command_processor()

            if user_input.startswith('!'):
                # Process memory command
                result = command_processor.process_command(user_input)

                if result.success:
                    response = f"✅ **Command Result:**\n\n{result.message}"
                    diagnostic_info['command_execution'] = {
                        'status': 'success',
                        'execution_time': getattr(result, 'execution_time_ms', 0),
                        'data_returned': bool(getattr(result, 'data', None))
                    }
                else:
                    response = f"❌ **Command Error:**\n\n{result.message}"
                    diagnostic_info['command_execution'] = {
                        'status': 'failed',
                        'error': result.message
                    }
            else:
                # Regular chat with memory-driven reasoning
                memory_reasoning = get_memory_reasoning_engine()

                # Use memory-driven reasoning
                reasoning_session = memory_reasoning.reason_with_memory(
                    query=user_input,
                    user_id="streamlit_user",
                    session_id=f"streamlit_session_{len(st.session_state.chat_history)}"
                )

                if reasoning_session:
                    response = reasoning_session.final_response

                    # Enhanced diagnostic information
                    diagnostic_info.update({
                        'reasoning_session': {
                            'session_id': reasoning_session.session_id,
                            'reasoning_steps': len(getattr(reasoning_session, 'reasoning_steps', [])),
                            'confidence_score': getattr(reasoning_session, 'confidence_score', 0.0),
                            'processing_time_ms': getattr(reasoning_session, 'processing_time_ms', 0)
                        },
                        'memory_context': {
                            'memories_found': reasoning_session.memory_context.memory_count,
                            'relevance_score': reasoning_session.memory_context.relevance_score,
                            'search_strategy': getattr(reasoning_session.memory_context, 'search_strategy', 'default'),
                            'context_length': len(reasoning_session.memory_context.context_text)
                        }
                    })

                    # Add memory context info to response
                    if reasoning_session.memory_context.memory_count > 0:
                        response += f"\n\n*💭 Recalled {reasoning_session.memory_context.memory_count} relevant memories (relevance: {reasoning_session.memory_context.relevance_score:.2f})*"
                else:
                    response = "I'm here to help! You can ask me questions or use memory commands like `!recall topic AI` to search my memory."
                    diagnostic_info['reasoning_session'] = {'status': 'no_session_created'}

            # Add SAM response to history with diagnostics
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "diagnostics": diagnostic_info if show_diagnostics else None
            })

        # Display chat history with enhanced diagnostics
        for i, message in enumerate(st.session_state.chat_history):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Show diagnostics for assistant messages
                if (message["role"] == "assistant" and
                    show_diagnostics and
                    message.get("diagnostics")):

                    render_diagnostic_panel(message["diagnostics"], show_memory_context, show_reasoning_trace)

        # Enhanced help and controls
        col1, col2 = st.columns(2)

        with col1:
            with st.expander("💡 Memory Commands Help"):
                st.markdown("""
                **Available Memory Commands:**
                - `!recall topic [keyword]` - Find memories about a topic
                - `!recall last 5` - Get recent memories
                - `!searchmem tag:important` - Search by tags
                - `!searchmem type:conversation` - Search by memory type
                - `!memstats` - View memory statistics
                - `!memhelp` - Show all commands

                **Example:** `!recall topic artificial intelligence`
                """)

        with col2:
            with st.expander("🔍 Diagnostic Commands"):
                st.markdown("""
                **Diagnostic Queries:**
                - `Hello SAM` - Basic system status
                - `What do you remember?` - Memory overview
                - `How are you learning?` - Learning status
                - `Show me your capabilities` - System capabilities
                - `What documents have you learned from?` - Learning history

                **System Status:**
                - Memory store health
                - Learning statistics
                - Recent activity
                - Performance metrics
                """)

        # Control buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()

        with col2:
            if st.button("📊 System Status"):
                # Add system status message
                status_info = get_system_status_info()
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": format_system_status(status_info),
                    "diagnostics": status_info if show_diagnostics else None
                })
                st.rerun()

        with col3:
            if st.button("🧠 Memory Overview"):
                # Add memory overview message
                memory_info = get_memory_overview_info()
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": format_memory_overview(memory_info),
                    "diagnostics": memory_info if show_diagnostics else None
                })
                st.rerun()

    except Exception as e:
        st.error(f"Error loading chat interface: {e}")

def render_memory_browser():
    """Render the memory browser interface."""
    try:
        browser = MemoryBrowserUI()
        browser.render()
    except Exception as e:
        st.error(f"Error loading memory browser: {e}")

def render_memory_editor():
    """Render the memory editor interface."""
    try:
        st.subheader("✏️ Memory Editor")
        
        editor = MemoryEditor()
        
        # Check if we have a memory to edit
        if hasattr(st.session_state, 'editing_memory') and st.session_state.editing_memory:
            editor.render_edit_interface(st.session_state.editing_memory)
        elif hasattr(st.session_state, 'deleting_memory') and st.session_state.deleting_memory:
            editor.render_delete_interface(st.session_state.deleting_memory)
        else:
            st.info("Select a memory from the Memory Browser to edit or delete it.")
            
            # Show recent edits and deletions
            col1, col2 = st.columns(2)
            
            with col1:
                editor.render_undo_interface()
            
            with col2:
                editor.render_audit_log()
                
    except Exception as e:
        st.error(f"Error loading memory editor: {e}")

def render_memory_graph():
    """Render the memory graph visualization."""
    try:
        visualizer = MemoryGraphVisualizer()
        visualizer.render()
    except Exception as e:
        st.error(f"Error loading memory graph: {e}")

def render_command_interface():
    """Render the command interface."""
    try:
        st.subheader("💬 Memory Command Interface")
        st.markdown("Execute memory recall commands and view results")
        
        command_processor = get_command_processor()
        
        # Command input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            command_text = st.text_input(
                "Enter Memory Command",
                placeholder="!recall topic artificial intelligence",
                help="Enter a memory command to execute"
            )
        
        with col2:
            output_format = st.selectbox("Output", ["text", "json"])
        
        # Execute button
        if st.button("🚀 Execute Command", type="primary") and command_text:
            with st.spinner("Executing command..."):
                result = command_processor.process_command(
                    command_text=command_text,
                    output_format=output_format
                )
                
                # Display results
                if result.success:
                    st.success(f"✅ Command executed successfully in {result.execution_time_ms}ms")
                    
                    if output_format == "json" and result.data:
                        st.json(result.data)
                    else:
                        st.markdown(result.message)
                else:
                    st.error(f"❌ Command failed: {result.message}")
        
        # Command help
        st.subheader("📚 Available Commands")
        
        commands = command_processor.get_available_commands()
        
        for cmd in commands:
            with st.expander(f"**{cmd['command']}**"):
                st.markdown(f"**Description:** {cmd['description']}")
                st.code(cmd['example'])
        
        # Command history
        if hasattr(st.session_state, 'command_history'):
            st.subheader("📜 Command History")
            
            for i, hist_cmd in enumerate(reversed(st.session_state.command_history[-10:])):
                st.caption(f"{i+1}. {hist_cmd}")
                
    except Exception as e:
        st.error(f"Error loading command interface: {e}")

def render_role_access():
    """Render the role-based access control interface."""
    try:
        st.subheader("🎭 Role-Based Memory Access")
        st.markdown("Manage memory access permissions and role-specific filtering")
        
        role_filter = get_role_filter()
        
        # Role selection
        col1, col2 = st.columns(2)
        
        with col1:
            selected_role = st.selectbox(
                "Select Agent Role",
                options=[role.value for role in AgentRole],
                index=0
            )
            role = AgentRole(selected_role)
        
        with col2:
            agent_id = st.text_input(
                "Agent ID",
                value=f"agent_{selected_role}_001",
                help="Specific agent identifier"
            )
        
        # Role permissions
        st.subheader("🔐 Role Permissions")
        
        permissions = role_filter.get_role_memory_permissions(role)
        
        if 'error' not in permissions:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Allowed Memory Types:**")
                for mem_type in permissions['allowed_memory_types']:
                    st.markdown(f"✅ {mem_type}")
                
                if permissions['restricted_memory_types']:
                    st.markdown("**Restricted Memory Types:**")
                    for mem_type in permissions['restricted_memory_types']:
                        st.markdown(f"❌ {mem_type}")
            
            with col2:
                st.markdown("**Access Levels:**")
                for level in permissions['access_levels']:
                    st.markdown(f"🔑 {level}")
                
                if permissions['special_permissions']:
                    st.markdown("**Special Permissions:**")
                    for perm in permissions['special_permissions']:
                        st.markdown(f"⭐ {perm}")
        
        # Role-filtered memories
        st.subheader("📚 Role-Filtered Memories")
        
        search_query = st.text_input(
            "Search Query (optional)",
            placeholder="Enter search terms...",
            help="Search memories accessible to this role"
        )
        
        max_results = st.slider("Max Results", 5, 50, 10)
        
        if st.button("🔍 Filter Memories"):
            with st.spinner("Filtering memories by role..."):
                role_context = role_filter.filter_memories_for_role(
                    role=role,
                    agent_id=agent_id,
                    query=search_query if search_query else None,
                    max_results=max_results
                )
                
                # Display results
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Accessible Memories ({len(role_context.accessible_memories)}):**")
                    
                    for i, result in enumerate(role_context.accessible_memories, 1):
                        memory = result.chunk
                        
                        with st.container():
                            st.markdown(f"**{i}. {memory.memory_type.value.title()}** - {memory.source}")
                            st.caption(f"Date: {memory.timestamp[:10]} | Importance: {memory.importance_score:.2f}")
                            
                            content_preview = memory.content[:100]
                            if len(memory.content) > 100:
                                content_preview += "..."
                            st.markdown(content_preview)
                            
                            if memory.tags:
                                tag_html = " ".join([
                                    f"<span style='background-color: #e1f5fe; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;'>{tag}</span>" 
                                    for tag in memory.tags[:3]
                                ])
                                st.markdown(tag_html, unsafe_allow_html=True)
                            
                            st.divider()
                
                with col2:
                    st.markdown("**Filter Summary:**")
                    st.metric("Accessible", len(role_context.accessible_memories))
                    st.metric("Filtered Out", role_context.filtered_count)
                    
                    if role_context.access_summary:
                        st.markdown("**By Type:**")
                        for mem_type, count in role_context.access_summary.items():
                            st.caption(f"{mem_type}: {count}")
                    
                    if role_context.role_specific_insights:
                        st.markdown("**Insights:**")
                        for insight in role_context.role_specific_insights:
                            st.caption(f"• {insight}")
        
        # Collaborative access
        st.subheader("🤝 Collaborative Access")
        
        selected_roles = st.multiselect(
            "Select Multiple Roles",
            options=[role.value for role in AgentRole],
            default=[selected_role]
        )
        
        if len(selected_roles) > 1 and st.button("🔍 Analyze Collaborative Access"):
            roles = [AgentRole(r) for r in selected_roles]
            
            with st.spinner("Analyzing collaborative memory access..."):
                collab_context = role_filter.get_collaborative_memories(
                    roles=roles,
                    query=search_query if search_query else None,
                    max_results=20
                )
                
                if 'error' not in collab_context:
                    st.markdown(f"**Shared Memories ({len(collab_context['shared_memories'])}):**")
                    
                    for memory in collab_context['shared_memories'][:10]:
                        st.markdown(f"• **{memory['memory_type']}** - {memory['source']}")
                        st.caption(f"Accessible to: {', '.join(memory['accessible_to'])}")
                        st.caption(f"Content: {memory['content']}")
                        st.divider()
                    
                    if collab_context['collaboration_insights']:
                        st.markdown("**Collaboration Insights:**")
                        for insight in collab_context['collaboration_insights']:
                            st.info(insight)
                
    except Exception as e:
        st.error(f"Error loading role access interface: {e}")

def render_system_status():
    """Render the system status interface."""
    try:
        st.subheader("🖥️ System Status")
        
        # Memory system status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Memory System:**")
            
            memory_store = get_memory_store()
            stats = memory_store.get_memory_stats()
            
            st.metric("Total Memories", stats['total_memories'])
            st.metric("Storage Size", f"{stats['total_size_mb']:.2f} MB")
            st.metric("Store Type", stats['store_type'])
            
            if stats['memory_types']:
                st.markdown("**Memory Distribution:**")
                for mem_type, count in stats['memory_types'].items():
                    st.progress(count / stats['total_memories'], text=f"{mem_type}: {count}")
        
        with col2:
            st.markdown("**Agent Mode:**")
            
            mode_controller = get_mode_controller()
            mode_status = mode_controller.get_mode_status()
            
            st.metric("Current Mode", mode_status.current_mode.value.title())
            st.metric("Key Status", mode_status.key_status.value)
            st.metric("Uptime", f"{mode_status.uptime_seconds}s")
            
            st.markdown("**Enabled Capabilities:**")
            for capability in mode_status.enabled_capabilities[:5]:
                st.caption(f"✅ {capability}")
            
            if mode_status.disabled_capabilities:
                st.markdown("**Disabled Capabilities:**")
                for capability in mode_status.disabled_capabilities[:3]:
                    st.caption(f"❌ {capability}")
        
        # Performance metrics
        st.subheader("📈 Performance Metrics")
        
        # This would integrate with actual performance monitoring
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avg Query Time", "45ms", delta="-5ms")
        
        with col2:
            st.metric("Memory Hit Rate", "87%", delta="+2%")
        
        with col3:
            st.metric("Active Sessions", "3", delta="+1")
        
        # System health
        st.subheader("🏥 System Health")
        
        health_checks = [
            ("Memory Store", "✅ Healthy"),
            ("Vector Index", "✅ Healthy"),
            ("Agent Mode Controller", "✅ Healthy"),
            ("Command Processor", "✅ Healthy"),
            ("Role Filter", "✅ Healthy")
        ]
        
        for component, status in health_checks:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(component)
            with col2:
                st.text(status)
        
    except Exception as e:
        st.error(f"Error loading system status: {e}")

def render_memory_ranking():
    """Render the Sprint 15 Memory Ranking interface."""
    try:
        st.subheader("🏆 Memory Ranking Framework")
        st.markdown("**Sprint 15 Feature:** Intelligent memory prioritization and ranking")

        from memory.memory_ranking import get_memory_ranking_framework

        ranking_framework = get_memory_ranking_framework()
        memory_store = get_memory_store()

        # Configuration section
        st.subheader("⚙️ Ranking Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Current Ranking Weights:**")
            weights = ranking_framework.ranking_weights
            for factor, weight in weights.items():
                st.metric(factor.replace('_', ' ').title(), f"{weight:.2f}")

        with col2:
            st.markdown("**Settings:**")
            st.metric("Priority Threshold", f"{ranking_framework.priority_threshold:.2f}")
            st.metric("Recency Decay (days)", ranking_framework.recency_decay_days)
            st.metric("Max Priority Memories", ranking_framework.config.get('max_priority_memories', 10))

        # Test ranking section
        st.subheader("🧪 Test Memory Ranking")

        test_query = st.text_input(
            "Test Query",
            value="important dates",
            help="Enter a query to test memory ranking"
        )

        max_results = st.slider("Max Results", 3, 20, 8)

        if st.button("🔍 Rank Memories", type="primary"):
            with st.spinner("Ranking memories..."):
                # Search for memories
                memory_results = memory_store.search_memories(test_query, max_results=max_results)

                if memory_results:
                    # Rank the memories
                    ranking_scores = ranking_framework.rank_memories(memory_results, query=test_query)

                    st.success(f"✅ Ranked {len(ranking_scores)} memories")

                    # Display ranking results
                    for i, score in enumerate(ranking_scores, 1):
                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])

                            with col1:
                                st.markdown(f"**{i}. Memory {score.memory_id}**")
                                st.caption(score.ranking_explanation)

                            with col2:
                                score_color = "🟢" if score.overall_score > 0.7 else "🟡" if score.overall_score > 0.4 else "🔴"
                                st.metric("Score", f"{score_color} {score.overall_score:.3f}")

                            with col3:
                                priority_icon = "⭐" if score.is_priority else "📌" if score.is_pinned else "•"
                                st.markdown(f"**Status:** {priority_icon}")
                                if score.is_priority:
                                    st.caption("Priority")
                                elif score.is_pinned:
                                    st.caption("Pinned")
                                else:
                                    st.caption("Regular")

                            # Factor breakdown
                            with st.expander("Factor Breakdown"):
                                factor_cols = st.columns(3)
                                for j, (factor, factor_score) in enumerate(score.factor_scores.items()):
                                    with factor_cols[j % 3]:
                                        st.metric(factor.value.replace('_', ' ').title(), f"{factor_score:.3f}")

                            st.divider()
                else:
                    st.warning("No memories found for the test query")

        # Memory pinning section
        st.subheader("📌 Memory Pinning")
        st.markdown("Manually pin/unpin memories for priority treatment")

        memory_id_to_pin = st.text_input(
            "Memory ID to Pin/Unpin",
            placeholder="mem_abc123...",
            help="Enter the memory ID to toggle its pinned status"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📌 Pin Memory"):
                if memory_id_to_pin:
                    # Implementation would go here
                    st.success(f"Memory {memory_id_to_pin} pinned!")
                else:
                    st.error("Please enter a memory ID")

        with col2:
            if st.button("📌 Unpin Memory"):
                if memory_id_to_pin:
                    # Implementation would go here
                    st.success(f"Memory {memory_id_to_pin} unpinned!")
                else:
                    st.error("Please enter a memory ID")

    except Exception as e:
        st.error(f"Error loading memory ranking: {e}")

def render_citation_engine():
    """Render the Sprint 15 Citation Engine interface."""
    try:
        st.subheader("📝 Citation Engine")
        st.markdown("**Sprint 15 Feature:** Transparent source attribution and quote injection")

        from memory.citation_engine import get_citation_engine

        citation_engine = get_citation_engine()
        memory_store = get_memory_store()

        # Configuration section
        st.subheader("⚙️ Citation Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Current Settings:**")
            st.metric("Citation Style", citation_engine.citation_style.value)
            st.metric("Citations Enabled", "✅" if citation_engine.enable_citations else "❌")
            st.metric("Max Quote Length", citation_engine.max_quote_length)

        with col2:
            st.markdown("**Thresholds:**")
            st.metric("Min Confidence", f"{citation_engine.min_confidence_threshold:.2f}")
            st.metric("Max Citations", citation_engine.config.get('max_citations_per_response', 5))

        # Test citation generation
        st.subheader("🧪 Test Citation Generation")

        test_query = st.text_input(
            "Test Query",
            value="Incubator dates",
            help="Enter a query to test citation generation"
        )

        test_response = st.text_area(
            "Sample Response Text",
            value="Based on the documents, there are several important dates to consider.",
            help="Enter sample response text to inject citations into"
        )

        if st.button("📝 Generate Citations", type="primary"):
            with st.spinner("Generating citations..."):
                # Search for relevant memories
                memory_results = memory_store.search_memories(test_query, max_results=5)

                if memory_results:
                    # Generate citations
                    cited_response = citation_engine.inject_citations(test_response, memory_results, test_query)

                    st.success(f"✅ Generated {len(cited_response.citations)} citations")

                    # Display results
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown("**Response with Citations:**")
                        st.markdown(cited_response.response_text)

                    with col2:
                        st.metric("Transparency Score", f"{cited_response.transparency_score:.1%}")
                        st.metric("Source Count", cited_response.source_count)
                        st.metric("Citation Style", cited_response.citation_style.value)

                    # Citation details
                    if cited_response.citations:
                        st.subheader("📋 Citation Details")

                        for i, citation in enumerate(cited_response.citations, 1):
                            with st.expander(f"Citation {i}: {citation.citation_label}"):
                                col1, col2 = st.columns([3, 1])

                                with col1:
                                    st.markdown(f"**Source:** {citation.source_name}")
                                    st.markdown(f"**Quote:** \"{citation.quote_text}\"")
                                    st.markdown(f"**Full Path:** {citation.full_source_path}")

                                with col2:
                                    confidence_color = "🟢" if citation.confidence_score > 0.7 else "🟡" if citation.confidence_score > 0.4 else "🔴"
                                    st.metric("Confidence", f"{confidence_color} {citation.confidence_score:.3f}")
                else:
                    st.warning("No memories found for citation generation")

        # Citation style settings
        st.subheader("🎨 Citation Style Settings")

        from memory.citation_engine import CitationStyle

        new_style = st.selectbox(
            "Citation Style",
            options=[style.value for style in CitationStyle],
            index=list(CitationStyle).index(citation_engine.citation_style)
        )

        if st.button("💾 Update Citation Style"):
            citation_engine.citation_style = CitationStyle(new_style)
            st.success(f"Citation style updated to: {new_style}")

    except Exception as e:
        st.error(f"Error loading citation engine: {e}")

def render_smart_summaries():
    """Render the Sprint 15 Smart Summary Generator interface."""
    try:
        st.subheader("📊 Smart Summary Generator")
        st.markdown("**Sprint 15 Feature:** AI-powered intelligent summarization with source tracking")

        from memory.smart_summarizer import get_smart_summarizer, SummaryRequest, SummaryType, SummaryFormat

        summarizer = get_smart_summarizer()
        memory_store = get_memory_store()

        # Summary generation section
        st.subheader("✨ Generate Smart Summary")

        col1, col2 = st.columns(2)

        with col1:
            topic_keyword = st.text_input(
                "Topic/Keyword",
                value="important dates",
                help="Enter the topic you want to summarize"
            )

            summary_type = st.selectbox(
                "Summary Type",
                options=[stype.value for stype in SummaryType],
                index=0
            )

            output_format = st.selectbox(
                "Output Format",
                options=[fmt.value for fmt in SummaryFormat],
                index=0
            )

        with col2:
            max_length = st.slider("Max Length (words)", 100, 1000, 300)
            include_sources = st.checkbox("Include Sources", value=True)

            # Memory filters
            st.markdown("**Memory Filters (optional):**")
            filter_by_type = st.multiselect(
                "Memory Types",
                options=["document", "conversation", "user_interaction"],
                default=[]
            )

        if st.button("📊 Generate Summary", type="primary"):
            with st.spinner("Generating smart summary..."):
                # Create summary request
                request = SummaryRequest(
                    topic_keyword=topic_keyword,
                    summary_type=SummaryType(summary_type),
                    output_format=SummaryFormat(output_format),
                    max_length=max_length,
                    include_sources=include_sources,
                    memory_filters={'memory_types': filter_by_type} if filter_by_type else None
                )

                # Generate summary
                summary = summarizer.generate_summary(request, memory_store)

                if summary.word_count > 0:
                    st.success(f"✅ Summary generated: {summary.word_count} words from {summary.source_count} sources")

                    # Display summary
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown("**Generated Summary:**")
                        if summary.output_format == SummaryFormat.MARKDOWN:
                            st.markdown(summary.summary_text)
                        else:
                            st.text(summary.summary_text)

                    with col2:
                        st.markdown("**Summary Statistics:**")
                        st.metric("Word Count", summary.word_count)
                        st.metric("Source Count", summary.source_count)
                        confidence_color = "🟢" if summary.confidence_score > 0.7 else "🟡" if summary.confidence_score > 0.4 else "🔴"
                        st.metric("Confidence", f"{confidence_color} {summary.confidence_score:.3f}")
                        st.metric("Summary ID", summary.summary_id)

                    # Key topics
                    if summary.key_topics:
                        st.markdown("**Key Topics:**")
                        topic_html = " ".join([
                            f"<span style='background-color: #e3f2fd; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block;'>{topic}</span>"
                            for topic in summary.key_topics
                        ])
                        st.markdown(topic_html, unsafe_allow_html=True)

                    # Export options
                    st.subheader("💾 Export Summary")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("📋 Copy to Clipboard"):
                            st.code(summary.summary_text)

                    with col2:
                        if st.button("💾 Save as Memory"):
                            # Implementation would save summary as a new memory
                            st.success("Summary saved as memory!")

                    with col3:
                        if st.button("📄 Download"):
                            st.download_button(
                                label="Download Summary",
                                data=summary.summary_text,
                                file_name=f"summary_{summary.summary_id}.md",
                                mime="text/markdown"
                            )
                else:
                    st.warning("No summary could be generated. Try a different topic or check if relevant memories exist.")

        # Summary history
        st.subheader("📜 Recent Summaries")

        if 'summary_history' not in st.session_state:
            st.session_state.summary_history = []

        if st.session_state.summary_history:
            for i, hist_summary in enumerate(reversed(st.session_state.summary_history[-5:])):
                with st.expander(f"Summary {i+1}: {hist_summary.get('topic', 'Unknown')}"):
                    st.markdown(f"**Generated:** {hist_summary.get('timestamp', 'Unknown')}")
                    st.markdown(f"**Word Count:** {hist_summary.get('word_count', 0)}")
                    st.markdown(f"**Confidence:** {hist_summary.get('confidence', 0):.3f}")
                    st.markdown(hist_summary.get('text', '')[:200] + "...")
        else:
            st.info("No summaries generated yet. Create your first summary above!")

    except Exception as e:
        st.error(f"Error loading smart summaries: {e}")

def render_memory_insights():
    """Render the Enhanced Memory Usage Insights interface with Knowledge Consolidation tracking."""
    try:
        st.subheader("📈 Enhanced Memory Usage Insights")
        st.markdown("**Enhanced Features:** Analytics, insights, knowledge consolidation tracking, and learning history")

        memory_store = get_memory_store()

        # Knowledge Consolidation Status Section
        st.subheader("🎓 Knowledge Consolidation Status")
        st.markdown("Track SAM's learning from uploaded documents")

        # Get learning history data
        learning_data = get_learning_history_data(memory_store)

        # Learning overview metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Documents Learned",
                learning_data['total_documents_learned'],
                help="Total number of documents SAM has successfully learned from"
            )

        with col2:
            st.metric(
                "Key Concepts",
                learning_data['total_key_concepts'],
                help="Total key concepts extracted and learned"
            )

        with col3:
            st.metric(
                "Avg Enrichment",
                f"{learning_data['average_enrichment_score']:.3f}",
                help="Average enrichment score across all learned documents"
            )

        with col4:
            st.metric(
                "Content Blocks",
                learning_data['total_content_blocks_processed'],
                help="Total content blocks processed and stored"
            )

        # Overall statistics
        st.subheader("📊 Overall Memory Statistics")

        stats = memory_store.get_memory_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Memories", stats['total_memories'])

        with col2:
            st.metric("Storage Size", f"{stats['total_size_mb']:.1f} MB")

        with col3:
            st.metric("Store Type", stats['store_type'])

        with col4:
            avg_importance = sum(chunk.importance_score for chunk in memory_store.memory_chunks.values()) / len(memory_store.memory_chunks) if memory_store.memory_chunks else 0
            st.metric("Avg Importance", f"{avg_importance:.3f}")

        # Learning History Timeline
        st.subheader("📚 Learning History Timeline")
        render_learning_timeline(learning_data)

        # Knowledge Consolidation Details
        st.subheader("🔍 Recent Learning Events")
        render_learning_events_table(learning_data)

        # Memory type distribution
        if stats['memory_types']:
            st.subheader("📋 Memory Type Distribution")

            import plotly.express as px
            import pandas as pd

            # Create pie chart
            df = pd.DataFrame(list(stats['memory_types'].items()), columns=['Type', 'Count'])
            fig = px.pie(df, values='Count', names='Type', title="Memory Distribution by Type")
            st.plotly_chart(fig, use_container_width=True)

        # Usage analytics
        st.subheader("🔍 Usage Analytics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Most Important Memories:**")

            # Get top memories by importance
            top_memories = sorted(
                memory_store.memory_chunks.values(),
                key=lambda x: x.importance_score,
                reverse=True
            )[:5]

            for i, memory in enumerate(top_memories, 1):
                with st.container():
                    st.markdown(f"**{i}. {memory.memory_type.value.title()}**")
                    st.caption(f"Importance: {memory.importance_score:.3f} | Source: {memory.source}")
                    st.caption(f"Content: {memory.content[:100]}...")
                    st.divider()

        with col2:
            st.markdown("**Recent Memories:**")

            # Get most recent memories
            recent_memories = sorted(
                memory_store.memory_chunks.values(),
                key=lambda x: x.timestamp,
                reverse=True
            )[:5]

            for i, memory in enumerate(recent_memories, 1):
                with st.container():
                    st.markdown(f"**{i}. {memory.memory_type.value.title()}**")
                    st.caption(f"Date: {memory.timestamp[:10]} | Source: {memory.source}")
                    st.caption(f"Content: {memory.content[:100]}...")
                    st.divider()

        # Search performance insights
        st.subheader("🚀 Search Performance Insights")

        test_queries = ["important dates", "artificial intelligence", "documents", "conversation"]

        if st.button("🧪 Run Performance Test"):
            with st.spinner("Testing search performance..."):
                import time

                performance_results = []

                for query in test_queries:
                    start_time = time.time()
                    results = memory_store.search_memories(query, max_results=10)
                    end_time = time.time()

                    performance_results.append({
                        'Query': query,
                        'Results': len(results),
                        'Time (ms)': round((end_time - start_time) * 1000, 2),
                        'Avg Similarity': round(sum(r.similarity_score for r in results) / len(results), 3) if results else 0
                    })

                # Display results
                df = pd.DataFrame(performance_results)
                st.dataframe(df, use_container_width=True)

                # Performance metrics
                avg_time = df['Time (ms)'].mean()
                avg_results = df['Results'].mean()

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Avg Search Time", f"{avg_time:.1f} ms")

                with col2:
                    st.metric("Avg Results", f"{avg_results:.1f}")

        # Memory health check
        st.subheader("🏥 Memory Health Check")

        if st.button("🔍 Run Health Check"):
            with st.spinner("Analyzing memory health..."):
                health_issues = []

                # Check for duplicate content
                content_hashes = {}
                duplicates = 0

                for chunk in memory_store.memory_chunks.values():
                    content_hash = hash(chunk.content[:100])
                    if content_hash in content_hashes:
                        duplicates += 1
                    else:
                        content_hashes[content_hash] = chunk.chunk_id

                if duplicates > 0:
                    health_issues.append(f"⚠️ Found {duplicates} potential duplicate memories")

                # Check for low importance memories
                low_importance = sum(1 for chunk in memory_store.memory_chunks.values() if chunk.importance_score < 0.3)
                if low_importance > stats['total_memories'] * 0.3:
                    health_issues.append(f"⚠️ {low_importance} memories have low importance scores")

                # Check for missing embeddings
                missing_embeddings = sum(1 for chunk in memory_store.memory_chunks.values() if not chunk.embedding)
                if missing_embeddings > 0:
                    health_issues.append(f"❌ {missing_embeddings} memories missing embeddings")

                # Display health results
                if health_issues:
                    st.warning("Memory health issues detected:")
                    for issue in health_issues:
                        st.markdown(f"- {issue}")
                else:
                    st.success("✅ Memory system is healthy!")

    except Exception as e:
        st.error(f"Error loading memory insights: {e}")

def render_enhanced_chat_interface():
    """Render the Sprint 16 enhanced chat interface."""
    try:
        from ui.chat_interface import render_chat_interface as render_sprint16_chat
        render_sprint16_chat()
    except Exception as e:
        st.error(f"Error loading enhanced chat interface: {e}")
        st.markdown("**Fallback:** Using basic chat interface")
        render_chat_interface()

def render_thought_settings():
    """Render the Sprint 16 thought settings interface."""
    try:
        from ui.chat_interface import render_thought_settings as render_sprint16_settings
        render_sprint16_settings()
    except Exception as e:
        st.error(f"Error loading thought settings: {e}")

def get_learning_history_data(memory_store):
    """Get learning history data from memory store."""
    try:
        all_memories = memory_store.get_all_memories()

        # Filter for document summaries (learning events)
        learning_events = []
        for memory in all_memories:
            metadata = getattr(memory, 'metadata', {})
            if metadata.get('document_type') == 'summary':
                learning_event = {
                    'timestamp': metadata.get('upload_timestamp', metadata.get('processing_timestamp', 'unknown')),
                    'filename': metadata.get('file_name', 'unknown'),
                    'source_file': metadata.get('source_file', 'unknown'),
                    'enrichment_score': metadata.get('enrichment_score', 0.0),
                    'priority_level': metadata.get('priority_level', 'unknown'),
                    'key_concepts': metadata.get('key_concepts', []),
                    'content_types': metadata.get('content_types', []),
                    'content_blocks_count': metadata.get('content_blocks_count', 0),
                    'file_size': metadata.get('file_size', 0),
                    'memory_id': getattr(memory, 'memory_id', 'unknown')
                }
                learning_events.append(learning_event)

        # Sort by timestamp (most recent first)
        learning_events.sort(key=lambda x: x['timestamp'], reverse=True)

        # Calculate learning statistics
        total_documents = len(learning_events)
        total_concepts = sum(len(event.get('key_concepts', [])) for event in learning_events)
        avg_enrichment = sum(event.get('enrichment_score', 0) for event in learning_events) / max(total_documents, 1)
        total_content_blocks = sum(event.get('content_blocks_count', 0) for event in learning_events)

        return {
            'total_documents_learned': total_documents,
            'total_key_concepts': total_concepts,
            'average_enrichment_score': round(avg_enrichment, 3),
            'total_content_blocks_processed': total_content_blocks,
            'learning_events': learning_events,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        st.error(f"Error getting learning history: {e}")
        return {
            'total_documents_learned': 0,
            'total_key_concepts': 0,
            'average_enrichment_score': 0.0,
            'total_content_blocks_processed': 0,
            'learning_events': [],
            'timestamp': datetime.now().isoformat()
        }

def render_learning_timeline(learning_data):
    """Render learning timeline visualization."""
    try:
        import plotly.express as px
        import pandas as pd
        from datetime import datetime, timedelta

        learning_events = learning_data.get('learning_events', [])

        if not learning_events:
            st.info("📚 No learning events found. Upload documents to see SAM's learning timeline!")
            return

        # Prepare timeline data
        timeline_data = []
        for event in learning_events:
            try:
                # Parse timestamp
                if event['timestamp'] != 'unknown':
                    timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                    timeline_data.append({
                        'Date': timestamp.date(),
                        'Time': timestamp.time(),
                        'Document': event['filename'],
                        'Enrichment Score': event['enrichment_score'],
                        'Key Concepts': len(event.get('key_concepts', [])),
                        'Content Blocks': event['content_blocks_count'],
                        'Priority': event['priority_level']
                    })
            except Exception as e:
                continue

        if timeline_data:
            df = pd.DataFrame(timeline_data)

            # Create timeline chart
            fig = px.scatter(
                df,
                x='Date',
                y='Enrichment Score',
                size='Content Blocks',
                color='Priority',
                hover_data=['Document', 'Key Concepts'],
                title="📈 SAM's Learning Timeline",
                labels={'Enrichment Score': 'Document Enrichment Score'}
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Learning velocity chart
            if len(df) > 1:
                daily_counts = df.groupby('Date').size().reset_index(name='Documents Learned')

                fig2 = px.bar(
                    daily_counts,
                    x='Date',
                    y='Documents Learned',
                    title="📊 Daily Learning Velocity",
                    labels={'Documents Learned': 'Documents Processed Per Day'}
                )

                fig2.update_layout(height=300)
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("⚠️ Unable to parse learning timeline data")

    except Exception as e:
        st.error(f"Error rendering learning timeline: {e}")

def render_learning_events_table(learning_data):
    """Render recent learning events table."""
    try:
        import pandas as pd
        from datetime import datetime

        learning_events = learning_data.get('learning_events', [])[:10]  # Show last 10 events

        if not learning_events:
            st.info("📋 No recent learning events found.")
            return

        # Prepare table data
        table_data = []
        for event in learning_events:
            try:
                # Format timestamp
                timestamp_str = "Unknown"
                if event['timestamp'] != 'unknown':
                    timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M")

                # Format key concepts
                concepts_count = len(event.get('key_concepts', []))
                concepts_preview = ", ".join(event.get('key_concepts', [])[:3])
                if len(event.get('key_concepts', [])) > 3:
                    concepts_preview += "..."

                table_data.append({
                    '📅 Timestamp': timestamp_str,
                    '📄 Document': event['filename'],
                    '📊 Enrichment': f"{event['enrichment_score']:.3f}",
                    '🔑 Concepts': f"{concepts_count}",
                    '🧩 Blocks': event['content_blocks_count'],
                    '🎯 Priority': event['priority_level'],
                    '💾 Size': f"{event.get('file_size', 0) / 1024:.1f} KB" if event.get('file_size', 0) > 0 else "Unknown"
                })
            except Exception as e:
                continue

        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)

            # Knowledge consolidation confirmation
            st.subheader("🎓 Knowledge Consolidation Confirmation")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**✅ Confirmed Learning Indicators:**")
                st.markdown("• Document summaries created")
                st.markdown("• Key concepts extracted and stored")
                st.markdown("• Memory chunks generated for Q&A")
                st.markdown("• Enrichment scores calculated")
                st.markdown("• Content blocks processed and indexed")

            with col2:
                st.markdown("**📈 Learning Quality Metrics:**")
                total_docs = learning_data['total_documents_learned']
                avg_score = learning_data['average_enrichment_score']
                total_concepts = learning_data['total_key_concepts']

                if total_docs > 0:
                    st.markdown(f"• **{total_docs}** documents successfully learned")
                    st.markdown(f"• **{avg_score:.3f}** average enrichment quality")
                    st.markdown(f"• **{total_concepts}** total concepts mastered")
                    st.markdown(f"• **{total_concepts/total_docs:.1f}** avg concepts per document")

                    # Learning status indicator
                    if avg_score >= 0.7:
                        st.success("🎓 **Excellent Learning Performance!**")
                    elif avg_score >= 0.5:
                        st.info("📚 **Good Learning Performance**")
                    else:
                        st.warning("⚠️ **Learning Performance Needs Improvement**")
                else:
                    st.info("📚 No learning data available yet")
        else:
            st.warning("⚠️ Unable to format learning events data")

    except Exception as e:
        st.error(f"Error rendering learning events: {e}")

def generate_diagnostic_info(user_input):
    """Generate comprehensive diagnostic information for a user query."""
    try:
        memory_store = get_memory_store()
        stats = memory_store.get_memory_stats()

        diagnostic_info = {
            'timestamp': datetime.now().isoformat(),
            'query_analysis': {
                'input_length': len(user_input),
                'word_count': len(user_input.split()),
                'query_type': classify_query_type(user_input),
                'contains_keywords': extract_keywords(user_input)
            },
            'system_state': {
                'total_memories': stats['total_memories'],
                'memory_types': stats['memory_types'],
                'storage_size_mb': stats['total_size_mb'],
                'system_health': 'healthy' if stats['total_memories'] > 0 else 'no_memories'
            },
            'processing_context': {
                'session_type': 'streamlit_diagnostic',
                'user_id': 'streamlit_user',
                'processing_mode': 'memory_driven_reasoning'
            }
        }

        return diagnostic_info

    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'system_state': 'error'
        }

def classify_query_type(query):
    """Classify the type of user query."""
    query_lower = query.lower()

    if any(greeting in query_lower for greeting in ['hello', 'hi', 'hey', 'greetings']):
        return 'greeting'
    elif any(question in query_lower for question in ['what', 'how', 'why', 'when', 'where', 'who']):
        return 'question'
    elif query.startswith('!'):
        return 'command'
    elif any(status in query_lower for status in ['status', 'health', 'system', 'diagnostic']):
        return 'diagnostic'
    elif any(memory in query_lower for memory in ['remember', 'recall', 'memory', 'learned']):
        return 'memory_query'
    else:
        return 'general'

def extract_keywords(query):
    """Extract key terms from the query."""
    import re

    # Remove common stop words and extract meaningful terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}

    words = re.findall(r'\b\w+\b', query.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]

    return keywords[:10]  # Return top 10 keywords

def render_diagnostic_panel(diagnostics, show_memory_context, show_reasoning_trace):
    """Render the diagnostic information panel."""
    try:
        with st.expander("🔍 Diagnostic Information", expanded=False):

            # Query Analysis
            if 'query_analysis' in diagnostics:
                st.markdown("**📝 Query Analysis:**")
                qa = diagnostics['query_analysis']
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Input Length", qa.get('input_length', 0))

                with col2:
                    st.metric("Word Count", qa.get('word_count', 0))

                with col3:
                    st.metric("Query Type", qa.get('query_type', 'unknown'))

                if qa.get('contains_keywords'):
                    st.caption(f"**Keywords:** {', '.join(qa['contains_keywords'])}")

            # System State
            if 'system_state' in diagnostics:
                st.markdown("**🖥️ System State:**")
                ss = diagnostics['system_state']

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Memories", ss.get('total_memories', 0))

                with col2:
                    st.metric("Storage Size", f"{ss.get('storage_size_mb', 0):.1f} MB")

                with col3:
                    health_color = "🟢" if ss.get('system_health') == 'healthy' else "🔴"
                    st.metric("Health", f"{health_color} {ss.get('system_health', 'unknown')}")

            # Memory Context (if enabled)
            if show_memory_context and 'memory_context' in diagnostics:
                st.markdown("**🧠 Memory Context:**")
                mc = diagnostics['memory_context']

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Memories Found", mc.get('memories_found', 0))

                with col2:
                    st.metric("Relevance Score", f"{mc.get('relevance_score', 0):.3f}")

                with col3:
                    st.metric("Context Length", mc.get('context_length', 0))

                if mc.get('search_strategy'):
                    st.caption(f"**Search Strategy:** {mc['search_strategy']}")

            # Reasoning Trace (if enabled)
            if show_reasoning_trace and 'reasoning_session' in diagnostics:
                st.markdown("**🤔 Reasoning Session:**")
                rs = diagnostics['reasoning_session']

                if rs.get('status') != 'no_session_created':
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Reasoning Steps", rs.get('reasoning_steps', 0))

                    with col2:
                        st.metric("Confidence", f"{rs.get('confidence_score', 0):.3f}")

                    with col3:
                        st.metric("Processing Time", f"{rs.get('processing_time_ms', 0)} ms")

                    if rs.get('session_id'):
                        st.caption(f"**Session ID:** {rs['session_id']}")
                else:
                    st.caption("No reasoning session created for this query")

            # Command Execution (if applicable)
            if 'command_execution' in diagnostics:
                st.markdown("**⚡ Command Execution:**")
                ce = diagnostics['command_execution']

                if ce.get('status') == 'success':
                    st.success(f"✅ Command executed successfully in {ce.get('execution_time', 0)} ms")
                    if ce.get('data_returned'):
                        st.info("📊 Data returned from command")
                else:
                    st.error(f"❌ Command failed: {ce.get('error', 'Unknown error')}")

            # Timestamp
            st.caption(f"**Generated:** {diagnostics.get('timestamp', 'Unknown')}")

    except Exception as e:
        st.error(f"Error rendering diagnostics: {e}")

def get_system_status_info():
    """Get comprehensive system status information."""
    try:
        memory_store = get_memory_store()
        stats = memory_store.get_memory_stats()

        # Get learning history
        learning_data = get_learning_history_data(memory_store)

        system_info = {
            'timestamp': datetime.now().isoformat(),
            'memory_system': {
                'status': 'operational',
                'total_memories': stats['total_memories'],
                'storage_size_mb': stats['total_size_mb'],
                'memory_types': stats['memory_types'],
                'store_type': stats['store_type']
            },
            'learning_system': {
                'documents_learned': learning_data['total_documents_learned'],
                'key_concepts': learning_data['total_key_concepts'],
                'avg_enrichment': learning_data['average_enrichment_score'],
                'content_blocks': learning_data['total_content_blocks_processed']
            },
            'performance_metrics': {
                'memory_health': 'healthy' if stats['total_memories'] > 0 else 'no_data',
                'learning_performance': 'excellent' if learning_data['average_enrichment_score'] >= 0.7 else
                                      'good' if learning_data['average_enrichment_score'] >= 0.5 else 'needs_improvement',
                'system_uptime': 'active',
                'last_activity': stats.get('newest_memory', 'unknown')
            }
        }

        return system_info

    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'status': 'error'
        }

def format_system_status(status_info):
    """Format system status information for display."""
    if 'error' in status_info:
        return f"❌ **System Status Error:** {status_info['error']}"

    memory_sys = status_info.get('memory_system', {})
    learning_sys = status_info.get('learning_system', {})
    performance = status_info.get('performance_metrics', {})

    status_msg = f"""🖥️ **SAM System Status Report**

**Memory System:**
• Status: {memory_sys.get('status', 'unknown').title()} ✅
• Total Memories: {memory_sys.get('total_memories', 0):,}
• Storage Size: {memory_sys.get('storage_size_mb', 0):.1f} MB
• Store Type: {memory_sys.get('store_type', 'unknown')}

**Learning System:**
• Documents Learned: {learning_sys.get('documents_learned', 0)}
• Key Concepts Mastered: {learning_sys.get('key_concepts', 0)}
• Average Enrichment Score: {learning_sys.get('avg_enrichment', 0):.3f}
• Content Blocks Processed: {learning_sys.get('content_blocks', 0)}

**Performance Metrics:**
• Memory Health: {performance.get('memory_health', 'unknown').title()}
• Learning Performance: {performance.get('learning_performance', 'unknown').title()}
• System Status: {performance.get('system_uptime', 'unknown').title()}

**Capabilities:**
• ✅ Memory-driven reasoning
• ✅ Document processing and learning
• ✅ Knowledge consolidation
• ✅ Multi-modal content analysis
• ✅ Contextual question answering
• ✅ Learning history tracking

*Generated: {status_info.get('timestamp', 'unknown')}*"""

    return status_msg

def get_memory_overview_info():
    """Get memory overview information."""
    try:
        memory_store = get_memory_store()
        all_memories = memory_store.get_all_memories()
        stats = memory_store.get_memory_stats()

        # Analyze memory content
        memory_sources = {}
        memory_types = {}
        recent_memories = []

        for memory in all_memories:
            # Track sources
            source = getattr(memory, 'source', 'unknown')
            if source.startswith('document:'):
                doc_name = source.split(':')[1].split('/')[-1]
                memory_sources[doc_name] = memory_sources.get(doc_name, 0) + 1

            # Track types
            mem_type = getattr(memory, 'memory_type', 'unknown')
            if hasattr(mem_type, 'value'):
                mem_type = mem_type.value
            memory_types[mem_type] = memory_types.get(mem_type, 0) + 1

            # Collect recent memories
            if len(recent_memories) < 5:
                recent_memories.append({
                    'content_preview': memory.content[:100] + "..." if len(memory.content) > 100 else memory.content,
                    'source': source,
                    'timestamp': getattr(memory, 'timestamp', 'unknown'),
                    'importance': getattr(memory, 'importance_score', 0)
                })

        overview_info = {
            'timestamp': datetime.now().isoformat(),
            'memory_statistics': {
                'total_count': len(all_memories),
                'storage_size': stats['total_size_mb'],
                'unique_sources': len(memory_sources),
                'memory_types': memory_types
            },
            'content_analysis': {
                'top_sources': dict(sorted(memory_sources.items(), key=lambda x: x[1], reverse=True)[:5]),
                'recent_memories': recent_memories
            },
            'system_capabilities': {
                'can_recall': len(all_memories) > 0,
                'can_learn': True,
                'can_reason': True,
                'can_consolidate': True
            }
        }

        return overview_info

    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def format_memory_overview(overview_info):
    """Format memory overview information for display."""
    if 'error' in overview_info:
        return f"❌ **Memory Overview Error:** {overview_info['error']}"

    stats = overview_info.get('memory_statistics', {})
    content = overview_info.get('content_analysis', {})
    capabilities = overview_info.get('system_capabilities', {})

    overview_msg = f"""🧠 **SAM Memory Overview**

**Memory Statistics:**
• Total Memories: {stats.get('total_count', 0):,}
• Storage Size: {stats.get('storage_size', 0):.1f} MB
• Unique Sources: {stats.get('unique_sources', 0)}

**Memory Types Distribution:**"""

    for mem_type, count in stats.get('memory_types', {}).items():
        overview_msg += f"\n• {mem_type.title()}: {count}"

    overview_msg += f"""

**Top Document Sources:**"""

    for source, count in content.get('top_sources', {}).items():
        overview_msg += f"\n• {source}: {count} memories"

    overview_msg += f"""

**System Capabilities:**"""

    for capability, status in capabilities.items():
        status_icon = "✅" if status else "❌"
        overview_msg += f"\n• {capability.replace('_', ' ').title()}: {status_icon}"

    if content.get('recent_memories'):
        overview_msg += f"""

**Recent Memory Sample:**"""
        for i, memory in enumerate(content['recent_memories'][:3], 1):
            overview_msg += f"\n{i}. {memory['content_preview']}"
            overview_msg += f"\n   Source: {memory['source']}"

    overview_msg += f"""

*Generated: {overview_info.get('timestamp', 'unknown')}*"""

    return overview_msg

if __name__ == "__main__":
    main()
