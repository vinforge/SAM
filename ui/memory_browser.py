"""
Interactive Memory Browser UI for SAM
Visual interface for memory search, inspection, and management.

Sprint 12 Task 1: Interactive Memory Browser UI
"""

import logging
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.memory_vectorstore import MemoryVectorStore, MemoryType, get_memory_store
from memory.memory_reasoning import MemoryDrivenReasoningEngine, get_memory_reasoning_engine

logger = logging.getLogger(__name__)

class MemoryBrowserUI:
    """
    Interactive memory browser with search, filtering, and visualization.
    """
    
    def __init__(self):
        """Initialize the memory browser UI."""
        self.memory_store = get_memory_store()
        self.memory_reasoning = get_memory_reasoning_engine()
        
        # UI state
        if 'selected_memory' not in st.session_state:
            st.session_state.selected_memory = None
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'filter_settings' not in st.session_state:
            st.session_state.filter_settings = {
                'memory_types': [],
                'tags': [],
                'date_range': None,
                'importance_range': [0.0, 1.0],
                'user_filter': None
            }
    
    def render(self):
        """Render the complete memory browser interface."""
        st.title("🧠 SAM Memory Browser")
        st.markdown("Search, inspect, and manage SAM's long-term memory")
        
        # Sidebar for filters and controls
        self._render_sidebar()
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_search_interface()
            self._render_memory_list()
        
        with col2:
            self._render_memory_details()
            self._render_memory_stats()
    
    def _render_sidebar(self):
        """Render the sidebar with filters and controls."""
        with st.sidebar:
            st.header("🔍 Search & Filters")
            
            # Memory type filter
            memory_types = st.multiselect(
                "Memory Types",
                options=[mt.value for mt in MemoryType],
                default=st.session_state.filter_settings['memory_types'],
                help="Filter by memory type"
            )
            st.session_state.filter_settings['memory_types'] = memory_types
            
            # Date range filter
            st.subheader("📅 Date Range")
            date_filter = st.selectbox(
                "Time Period",
                options=["All Time", "Last 24 Hours", "Last Week", "Last Month", "Custom Range"],
                index=0
            )
            
            if date_filter == "Custom Range":
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                st.session_state.filter_settings['date_range'] = (start_date, end_date)
            elif date_filter != "All Time":
                days_back = {"Last 24 Hours": 1, "Last Week": 7, "Last Month": 30}[date_filter]
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days_back)
                st.session_state.filter_settings['date_range'] = (start_date, end_date)
            else:
                st.session_state.filter_settings['date_range'] = None
            
            # Importance filter
            st.subheader("⭐ Importance")
            importance_range = st.slider(
                "Importance Score",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.filter_settings['importance_range'],
                step=0.1,
                help="Filter by importance score"
            )
            st.session_state.filter_settings['importance_range'] = importance_range
            
            # User filter
            st.subheader("👤 User Filter")
            user_filter = st.text_input(
                "User ID",
                value=st.session_state.filter_settings['user_filter'] or "",
                help="Filter memories by user ID"
            )
            st.session_state.filter_settings['user_filter'] = user_filter if user_filter else None
            
            # Clear filters button
            if st.button("🗑️ Clear All Filters"):
                st.session_state.filter_settings = {
                    'memory_types': [],
                    'tags': [],
                    'date_range': None,
                    'importance_range': [0.0, 1.0],
                    'user_filter': None
                }
                st.rerun()
    
    def _render_search_interface(self):
        """Render the search interface."""
        st.subheader("🔍 Memory Search")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Search memories",
                placeholder="Enter keywords, topics, or questions...",
                help="Search through memory content using semantic similarity"
            )
        
        with col2:
            search_button = st.button("Search", type="primary")
        
        # Perform search
        if search_button and search_query:
            with st.spinner("Searching memories..."):
                results = self._search_memories(search_query)
                st.session_state.search_results = results
                st.success(f"Found {len(results)} memories")
        
        # Quick search buttons
        st.markdown("**Quick Searches:**")
        quick_searches = ["Recent conversations", "Important insights", "AI research", "User feedback"]
        
        cols = st.columns(len(quick_searches))
        for i, quick_search in enumerate(quick_searches):
            with cols[i]:
                if st.button(quick_search, key=f"quick_{i}"):
                    results = self._search_memories(quick_search)
                    st.session_state.search_results = results
    
    def _render_memory_list(self):
        """Render the list of memories."""
        st.subheader("📚 Memory Results")
        
        # Get memories to display
        if st.session_state.search_results:
            memories_to_show = st.session_state.search_results
        else:
            memories_to_show = self._get_recent_memories()
        
        if not memories_to_show:
            st.info("No memories found. Try adjusting your search or filters.")
            return
        
        # Display memories as cards
        for i, memory_result in enumerate(memories_to_show):
            if hasattr(memory_result, 'chunk'):
                memory = memory_result.chunk
                similarity = getattr(memory_result, 'similarity_score', 1.0)
            else:
                memory = memory_result
                similarity = 1.0
            
            with st.container():
                # Memory card
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Memory preview
                    st.markdown(f"**{memory.memory_type.value.title()}** - {memory.source}")
                    
                    # Content preview
                    content_preview = memory.content[:150]
                    if len(memory.content) > 150:
                        content_preview += "..."
                    st.markdown(content_preview)
                    
                    # Tags
                    if memory.tags:
                        tag_html = " ".join([f"<span style='background-color: #e1f5fe; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;'>{tag}</span>" for tag in memory.tags[:5]])
                        st.markdown(tag_html, unsafe_allow_html=True)
                
                with col2:
                    # Metadata
                    st.metric("Importance", f"{memory.importance_score:.2f}")
                    if similarity < 1.0:
                        st.metric("Similarity", f"{similarity:.2f}")
                    st.caption(f"Access: {memory.access_count}")
                
                with col3:
                    # Actions
                    st.caption(memory.timestamp[:10])
                    
                    if st.button("View", key=f"view_{memory.chunk_id}"):
                        st.session_state.selected_memory = memory
                    
                    if st.button("Edit", key=f"edit_{memory.chunk_id}"):
                        self._show_edit_dialog(memory)
                
                st.divider()
    
    def _render_memory_details(self):
        """Render detailed view of selected memory."""
        st.subheader("📄 Memory Details")
        
        if st.session_state.selected_memory is None:
            st.info("Select a memory from the list to view details")
            return
        
        memory = st.session_state.selected_memory
        
        # Memory header
        st.markdown(f"### {memory.memory_type.value.title()}")
        st.markdown(f"**Source:** {memory.source}")
        st.markdown(f"**Created:** {memory.timestamp}")
        st.markdown(f"**Last Accessed:** {memory.last_accessed}")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Importance", f"{memory.importance_score:.2f}")
        with col2:
            st.metric("Access Count", memory.access_count)
        with col3:
            st.metric("Content Length", len(memory.content))
        
        # Full content
        st.markdown("**Content:**")
        st.text_area("", value=memory.content, height=200, disabled=True)
        
        # Tags
        if memory.tags:
            st.markdown("**Tags:**")
            st.write(", ".join(memory.tags))
        
        # Metadata
        if memory.metadata:
            st.markdown("**Metadata:**")
            st.json(memory.metadata)
        
        # Actions
        st.markdown("**Actions:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Edit Memory"):
                self._show_edit_dialog(memory)
        
        with col2:
            if st.button("Delete Memory", type="secondary"):
                self._show_delete_dialog(memory)
        
        with col3:
            if st.button("Find Similar"):
                similar_results = self._search_memories(memory.content[:100])
                st.session_state.search_results = similar_results
                st.rerun()
    
    def _render_memory_stats(self):
        """Render memory statistics panel."""
        st.subheader("📊 Memory Statistics")
        
        try:
            stats = self.memory_store.get_memory_stats()
            
            # Overall stats
            st.metric("Total Memories", stats['total_memories'])
            st.metric("Storage Size", f"{stats['total_size_mb']:.2f} MB")
            
            # Memory types chart
            if stats['memory_types']:
                st.markdown("**Memory Types:**")
                
                # Create pie chart
                fig = px.pie(
                    values=list(stats['memory_types'].values()),
                    names=list(stats['memory_types'].keys()),
                    title="Memory Distribution by Type"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            # Recent activity
            if stats.get('newest_memory'):
                st.markdown("**Recent Activity:**")
                st.caption(f"Newest: {stats['newest_memory'][:10]}")
                if stats.get('oldest_memory'):
                    st.caption(f"Oldest: {stats['oldest_memory'][:10]}")
            
        except Exception as e:
            st.error(f"Error loading statistics: {e}")
    
    def _search_memories(self, query: str) -> List:
        """Search memories with current filters."""
        try:
            # Apply memory type filter
            memory_types = None
            if st.session_state.filter_settings['memory_types']:
                memory_types = [MemoryType(mt) for mt in st.session_state.filter_settings['memory_types']]
            
            # Perform search
            results = self.memory_reasoning.search_memories(
                query=query,
                user_id=st.session_state.filter_settings['user_filter'],
                memory_types=memory_types,
                max_results=50
            )
            
            # Apply additional filters
            filtered_results = []
            for result in results:
                memory = result.chunk
                
                # Date filter
                if st.session_state.filter_settings['date_range']:
                    start_date, end_date = st.session_state.filter_settings['date_range']
                    memory_date = datetime.fromisoformat(memory.timestamp).date()
                    if not (start_date <= memory_date <= end_date):
                        continue
                
                # Importance filter
                importance_min, importance_max = st.session_state.filter_settings['importance_range']
                if not (importance_min <= memory.importance_score <= importance_max):
                    continue
                
                filtered_results.append(result)
            
            return filtered_results
            
        except Exception as e:
            st.error(f"Search error: {e}")
            return []
    
    def _get_recent_memories(self, limit: int = 20) -> List:
        """Get recent memories with filters applied."""
        try:
            # Get all memories and sort by timestamp
            all_memories = list(self.memory_store.memory_chunks.values())
            
            # Apply filters
            filtered_memories = []
            for memory in all_memories:
                # Memory type filter
                if (st.session_state.filter_settings['memory_types'] and 
                    memory.memory_type.value not in st.session_state.filter_settings['memory_types']):
                    continue
                
                # User filter
                if (st.session_state.filter_settings['user_filter'] and 
                    memory.metadata.get('user_id') != st.session_state.filter_settings['user_filter']):
                    continue
                
                # Date filter
                if st.session_state.filter_settings['date_range']:
                    start_date, end_date = st.session_state.filter_settings['date_range']
                    memory_date = datetime.fromisoformat(memory.timestamp).date()
                    if not (start_date <= memory_date <= end_date):
                        continue
                
                # Importance filter
                importance_min, importance_max = st.session_state.filter_settings['importance_range']
                if not (importance_min <= memory.importance_score <= importance_max):
                    continue
                
                filtered_memories.append(memory)
            
            # Sort by timestamp (newest first)
            filtered_memories.sort(key=lambda m: m.timestamp, reverse=True)
            
            return filtered_memories[:limit]
            
        except Exception as e:
            st.error(f"Error loading recent memories: {e}")
            return []
    
    def _show_edit_dialog(self, memory):
        """Show memory editing dialog."""
        st.session_state.editing_memory = memory
        # This would open a modal or separate page for editing
        # For now, we'll use a simple form in the sidebar
        
    def _show_delete_dialog(self, memory):
        """Show memory deletion confirmation."""
        st.session_state.deleting_memory = memory
        # This would show a confirmation dialog

def main():
    """Main function to run the memory browser."""
    browser = MemoryBrowserUI()
    browser.render()

if __name__ == "__main__":
    main()
