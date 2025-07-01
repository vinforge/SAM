#!/usr/bin/env python3
"""
SLP Phase 1A+1B Integration Script
=================================

Integrates the enhanced SLP analytics and insights capabilities into the live SAM system.
Preserves 100% of existing functionality while adding advanced analytics.
"""

import sys
import logging
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_enhanced_slp_system():
    """Initialize the enhanced SLP system with Phase 1A+1B capabilities."""
    try:
        # Import enhanced SLP components
        from sam.cognition.slp import (
            SAMSLPIntegration, 
            SLPAnalyticsEngine, 
            SLPMetricsCollector,
            ProgramAnalyzer,
            CognitiveInsightsGenerator,
            ENHANCED_ANALYTICS_AVAILABLE,
            ADVANCED_ANALYSIS_AVAILABLE
        )
        
        logger.info("🧠 Initializing Enhanced SLP System...")
        
        # Check if enhanced components are available
        if not ENHANCED_ANALYTICS_AVAILABLE:
            logger.warning("⚠️ Enhanced analytics not available - using basic SLP")
            return initialize_basic_slp_system()
        
        if not ADVANCED_ANALYSIS_AVAILABLE:
            logger.warning("⚠️ Advanced analysis not available - using Phase 1A only")
        
        # Initialize enhanced SLP integration
        if 'enhanced_slp_integration' not in st.session_state:
            # Get TPV integration if available
            tpv_integration = st.session_state.get('sam_tpv_integration')
            
            # Create enhanced SLP integration
            slp_integration = SAMSLPIntegration(tpv_integration)
            
            # Verify enhanced analytics are working
            if hasattr(slp_integration.program_manager, 'analytics_engine'):
                logger.info("✅ Enhanced analytics engine detected")
                st.session_state.enhanced_slp_integration = slp_integration
                st.session_state.slp_analytics_available = True
                
                # Initialize analytics components separately for direct access
                st.session_state.slp_analytics_engine = slp_integration.program_manager.analytics_engine
                st.session_state.slp_metrics_collector = slp_integration.program_manager.metrics_collector
                
                if ADVANCED_ANALYSIS_AVAILABLE:
                    st.session_state.slp_program_analyzer = ProgramAnalyzer(slp_integration.program_manager.store)
                    st.session_state.slp_cognitive_insights = CognitiveInsightsGenerator(
                        slp_integration.program_manager.store,
                        st.session_state.slp_program_analyzer
                    )
                    logger.info("✅ Advanced analysis components initialized")
                
                logger.info("✅ Enhanced SLP system initialized successfully")
                return slp_integration
            else:
                logger.warning("⚠️ Enhanced analytics not detected - using basic SLP")
                return initialize_basic_slp_system()
        
        return st.session_state.enhanced_slp_integration
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize enhanced SLP system: {e}")
        return initialize_basic_slp_system()

def initialize_basic_slp_system():
    """Initialize basic SLP system as fallback."""
    try:
        from sam.cognition.slp import SAMSLPIntegration
        
        if 'basic_slp_integration' not in st.session_state:
            tpv_integration = st.session_state.get('sam_tpv_integration')
            st.session_state.basic_slp_integration = SAMSLPIntegration(tpv_integration)
            st.session_state.slp_analytics_available = False
            logger.info("✅ Basic SLP system initialized")
        
        return st.session_state.basic_slp_integration
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize basic SLP system: {e}")
        return None

def get_slp_integration():
    """Get the current SLP integration (enhanced or basic)."""
    if 'enhanced_slp_integration' in st.session_state:
        return st.session_state.enhanced_slp_integration
    elif 'basic_slp_integration' in st.session_state:
        return st.session_state.basic_slp_integration
    else:
        return initialize_enhanced_slp_system()

def render_slp_analytics_dashboard():
    """Render the SLP analytics dashboard in the Memory Control Center."""
    st.header("🧠 SLP Cognitive Analytics")
    st.markdown("*Advanced insights into SAM's learning and automation*")
    
    if not st.session_state.get('slp_analytics_available', False):
        st.warning("⚠️ Enhanced SLP analytics not available")
        st.info("💡 **Note:** Enhanced analytics require the Phase 1A+1B components to be properly initialized.")
        return
    
    try:
        # Get analytics components
        analytics_engine = st.session_state.get('slp_analytics_engine')
        program_analyzer = st.session_state.get('slp_program_analyzer')
        cognitive_insights = st.session_state.get('slp_cognitive_insights')
        
        if not analytics_engine:
            st.error("❌ Analytics engine not available")
            return
        
        # Analytics navigation
        analytics_tab = st.selectbox(
            "Analytics View",
            options=[
                "📊 Real-Time Metrics",
                "🔍 Program Analysis", 
                "🧠 Cognitive Insights",
                "📈 Performance Trends",
                "🎯 Automation Opportunities"
            ]
        )
        
        if analytics_tab == "📊 Real-Time Metrics":
            render_real_time_slp_metrics(analytics_engine)
        elif analytics_tab == "🔍 Program Analysis" and program_analyzer:
            render_program_analysis_dashboard(program_analyzer)
        elif analytics_tab == "🧠 Cognitive Insights" and cognitive_insights:
            render_cognitive_insights_dashboard(cognitive_insights)
        elif analytics_tab == "📈 Performance Trends":
            render_performance_trends_dashboard(analytics_engine)
        elif analytics_tab == "🎯 Automation Opportunities" and cognitive_insights:
            render_automation_opportunities_dashboard(cognitive_insights)
        else:
            st.warning(f"⚠️ {analytics_tab} not available - requires advanced analysis components")
            
    except Exception as e:
        st.error(f"❌ Error rendering SLP analytics: {e}")
        logger.error(f"SLP analytics rendering error: {e}")

def render_real_time_slp_metrics(analytics_engine):
    """Render real-time SLP metrics."""
    st.subheader("📊 Real-Time SLP Performance")

    try:
        # Get real-time metrics
        metrics = analytics_engine.get_real_time_metrics()

        if not metrics or all(v == 0 for v in [metrics.get('hit_rate_percent', 0),
                                               metrics.get('avg_execution_time_ms', 0),
                                               metrics.get('time_saved_today_ms', 0)]):
            # Show sample data generation option
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("📊 No real-time metrics available yet. Metrics will appear after SLP usage.")
            with col2:
                if st.button("🎲 Generate Sample Data", help="Generate sample metrics for demonstration"):
                    generate_sample_slp_data(analytics_engine)
                    st.rerun()
            return
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Hit Rate",
                f"{metrics.get('hit_rate_percent', 0):.1f}%",
                help="Percentage of queries using SLP programs"
            )
        
        with col2:
            st.metric(
                "Avg Execution Time",
                f"{metrics.get('avg_execution_time_ms', 0):.0f}ms",
                help="Average program execution time"
            )
        
        with col3:
            st.metric(
                "Time Saved Today",
                f"{metrics.get('time_saved_today_ms', 0)/1000:.1f}s",
                help="Total time saved through automation"
            )
        
        with col4:
            st.metric(
                "Active Programs",
                metrics.get('active_programs', 0),
                help="Number of active SLP programs"
            )
        
        # System status
        status = metrics.get('system_status', 'unknown')
        if status == 'healthy':
            st.success("✅ SLP system is operating normally")
        elif status == 'monitoring':
            st.warning("⚠️ SLP system performance under monitoring")
        else:
            st.info(f"ℹ️ SLP system status: {status}")
        
        # Recent activity
        st.subheader("📈 Recent Activity")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Queries Last Hour",
                metrics.get('total_queries_last_hour', 0),
                help="Total queries processed in the last hour"
            )
        
        with col2:
            st.metric(
                "Program Hits Last Hour", 
                metrics.get('program_hits_last_hour', 0),
                help="Queries that used SLP programs in the last hour"
            )
        
        # Refresh button
        if st.button("🔄 Refresh Metrics"):
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error loading real-time metrics: {e}")

def render_program_analysis_dashboard(program_analyzer):
    """Render program analysis dashboard."""
    st.subheader("🔍 Program Analysis")
    
    try:
        # Analysis options
        analysis_type = st.selectbox(
            "Analysis Type",
            options=[
                "Pattern Similarity",
                "Usage Frequency", 
                "Quality Trends",
                "Program Effectiveness"
            ]
        )
        
        if analysis_type == "Pattern Similarity":
            st.markdown("**🔗 Program Pattern Similarity Analysis**")
            
            with st.spinner("Analyzing program patterns..."):
                similarity_analysis = program_analyzer.analyze_pattern_similarity()
                
                if similarity_analysis:
                    # Display similarity clusters
                    clusters = similarity_analysis.get('similarity_clusters', [])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Programs", similarity_analysis.get('total_programs', 0))
                    with col2:
                        st.metric("Similarity Clusters", len(clusters))
                    with col3:
                        st.metric("Avg Similarity", f"{similarity_analysis.get('average_similarity', 0):.3f}")
                    
                    # Show insights
                    insights = similarity_analysis.get('insights', [])
                    if insights:
                        st.markdown("**💡 Insights:**")
                        for insight in insights:
                            st.info(f"• {insight}")
                    
                    # Show clusters
                    if clusters:
                        st.markdown("**🔗 Similarity Clusters:**")
                        for cluster in clusters:
                            with st.expander(f"Cluster {cluster['cluster_id']} ({cluster['program_count']} programs)"):
                                st.json(cluster)
                else:
                    st.info("No similarity analysis available yet")
        
        elif analysis_type == "Usage Frequency":
            st.markdown("**📊 Program Usage Frequency Analysis**")
            
            time_window = st.slider("Analysis Window (days)", 1, 90, 30)
            
            with st.spinner("Analyzing usage patterns..."):
                frequency_analysis = program_analyzer.analyze_usage_frequency(time_window)
                
                if frequency_analysis and frequency_analysis.get('frequency_distribution'):
                    # Display summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Programs Used", frequency_analysis.get('total_programs_used', 0))
                    with col2:
                        st.metric("Total Executions", frequency_analysis.get('total_executions', 0))
                    with col3:
                        st.metric("Analysis Period", f"{time_window} days")
                    
                    # Show usage distribution
                    st.markdown("**📈 Usage Distribution:**")
                    for program_data in frequency_analysis['frequency_distribution'][:10]:  # Top 10
                        with st.expander(f"Program {program_data['program_id'][:8]}... ({program_data['execution_count']} uses)"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Frequency %", f"{program_data['frequency_percentage']:.1f}%")
                                st.metric("Success Rate", f"{program_data['success_rate']:.1f}%")
                            with col2:
                                st.metric("Avg Quality", f"{program_data['avg_quality_score']:.3f}")
                                st.metric("Category", program_data['usage_category'])
                    
                    # Show insights
                    insights = frequency_analysis.get('insights', [])
                    if insights:
                        st.markdown("**💡 Insights:**")
                        for insight in insights:
                            st.info(f"• {insight}")
                else:
                    st.info("No usage frequency data available yet")
        
        elif analysis_type == "Quality Trends":
            # Quality Trends Analysis Implementation
            st.markdown("**📊 Quality Trends Analysis**")

            # Time window selection
            col1, col2 = st.columns(2)
            with col1:
                time_window = st.selectbox(
                    "Analysis Period",
                    options=[7, 14, 30, 60, 90],
                    index=2,  # Default to 30 days
                    format_func=lambda x: f"Last {x} days"
                )

            with col2:
                program_filter = st.selectbox(
                    "Program Filter",
                    options=["All Programs", "Active Only", "High Usage Only"],
                    index=0
                )

            try:
                # Get quality trends analysis
                if program_filter == "All Programs":
                    quality_trends = program_analyzer.analyze_quality_trends(
                        program_id=None,
                        time_window_days=time_window
                    )
                else:
                    # For now, analyze all programs (can be enhanced later)
                    quality_trends = program_analyzer.analyze_quality_trends(
                        program_id=None,
                        time_window_days=time_window
                    )

                if quality_trends and quality_trends.get('trend_analysis'):
                    trend_analysis = quality_trends['trend_analysis']

                    # Display trend direction
                    trend_direction = trend_analysis.get('trend_direction', 'unknown')
                    trend_strength = trend_analysis.get('trend_strength', 0)

                    # Trend direction indicator
                    if trend_direction == 'improving':
                        st.success(f"📈 **Quality Trend: IMPROVING** (Strength: {trend_strength:.3f})")
                    elif trend_direction == 'declining':
                        st.error(f"📉 **Quality Trend: DECLINING** (Strength: {trend_strength:.3f})")
                    else:
                        st.info(f"📊 **Quality Trend: STABLE** (Strength: {trend_strength:.3f})")

                    # Detailed metrics
                    st.markdown("**📊 Detailed Quality Metrics:**")

                    col1, col2, col3 = st.columns(3)

                    # Quality trend details
                    quality_trend = trend_analysis.get('quality_trend', {})
                    with col1:
                        quality_slope = quality_trend.get('slope', 0)
                        quality_correlation = quality_trend.get('correlation', 0)
                        st.metric(
                            "Quality Score Trend",
                            f"{quality_slope:+.4f}",
                            help=f"Correlation: {quality_correlation:.3f}"
                        )

                    # Efficiency trend details
                    efficiency_trend = trend_analysis.get('efficiency_trend', {})
                    with col2:
                        efficiency_slope = efficiency_trend.get('slope', 0)
                        efficiency_correlation = efficiency_trend.get('correlation', 0)
                        st.metric(
                            "Efficiency Trend",
                            f"{efficiency_slope:+.4f}",
                            help=f"Correlation: {efficiency_correlation:.3f}"
                        )

                    # Success rate trend details
                    success_trend = trend_analysis.get('success_trend', {})
                    with col3:
                        success_slope = success_trend.get('slope', 0)
                        success_correlation = success_trend.get('correlation', 0)
                        st.metric(
                            "Success Rate Trend",
                            f"{success_slope:+.4f}",
                            help=f"Correlation: {success_correlation:.3f}"
                        )

                    # Insights and recommendations
                    insights = quality_trends.get('insights', [])
                    if insights:
                        st.markdown("**💡 Quality Insights:**")
                        for insight in insights:
                            if 'improving' in insight.lower():
                                st.success(f"✅ {insight}")
                            elif 'declining' in insight.lower() or 'attention' in insight.lower():
                                st.warning(f"⚠️ {insight}")
                            else:
                                st.info(f"ℹ️ {insight}")

                    # Data points information
                    data_points = trend_analysis.get('data_points', 0)
                    analysis_period = quality_trends.get('analysis_period_days', time_window)
                    st.caption(f"📊 Analysis based on {data_points} data points over {analysis_period} days")

                else:
                    st.info("📊 No quality trends data available yet. Quality trends will appear after SLP programs have been used over time.")

                    # Show sample data generation option
                    if st.button("🎲 Generate Sample Quality Trends", help="Generate sample quality trend data for demonstration"):
                        generate_sample_quality_trends_data(program_analyzer)
                        st.rerun()

            except Exception as e:
                st.error(f"❌ Error analyzing quality trends: {e}")
                logger.error(f"Quality trends analysis failed: {e}")

        # Add other analysis types as needed
        else:
            st.info(f"📊 {analysis_type} analysis coming soon...")
            
    except Exception as e:
        st.error(f"❌ Error in program analysis: {e}")

def render_cognitive_insights_dashboard(cognitive_insights):
    """Render cognitive insights dashboard."""
    st.subheader("🧠 Cognitive Insights")
    
    try:
        # Insights options
        insight_type = st.selectbox(
            "Insight Type",
            options=[
                "Successful Program Types",
                "Automation Opportunities",
                "Learning Insights", 
                "Cognitive Evolution",
                "Comprehensive Report"
            ]
        )
        
        if insight_type == "Successful Program Types":
            st.markdown("**🏆 Most Successful Program Types**")
            
            with st.spinner("Analyzing successful patterns..."):
                successful_types = cognitive_insights.identify_most_successful_program_types()
                
                if successful_types and successful_types.get('successful_types'):
                    # Display summary
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Programs Analyzed", successful_types.get('total_programs_analyzed', 0))
                    with col2:
                        st.metric("Successful Types", len(successful_types['successful_types']))
                    
                    # Show successful types
                    st.markdown("**🎯 Top Performing Types:**")
                    for type_data in successful_types['successful_types'][:5]:  # Top 5
                        with st.expander(f"{type_data['type_identifier']} (Score: {type_data['success_score']:.3f})"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Program Count", type_data['program_count'])
                                st.metric("Avg Quality", f"{type_data['avg_quality_score']:.3f}")
                            with col2:
                                st.metric("Success Rate", f"{type_data['avg_success_rate']:.3f}")
                                st.metric("Efficiency Gain", f"{type_data['avg_efficiency_gain']:.1f}%")
                            
                            # Show success factors
                            if type_data.get('success_factors'):
                                st.markdown("**Success Factors:**")
                                for factor in type_data['success_factors']:
                                    st.success(f"✅ {factor}")
                else:
                    st.info("No successful program type analysis available yet")
        
        elif insight_type == "Automation Opportunities":
            st.markdown("**🎯 Automation Opportunities**")
            
            with st.spinner("Detecting automation opportunities..."):
                opportunities = cognitive_insights.detect_automation_opportunities()
                
                if opportunities:
                    st.metric("Opportunities Found", len(opportunities))
                    
                    # Show top opportunities
                    st.markdown("**🚀 Top Automation Opportunities:**")
                    for i, opp in enumerate(opportunities[:5]):  # Top 5
                        with st.expander(f"Opportunity {i+1}: {opp.get('pattern_identifier', 'Unknown')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Confidence", f"{opp.get('confidence_score', 0):.3f}")
                                st.metric("Frequency", opp.get('frequency', 0))
                            with col2:
                                st.metric("Impact Score", f"{opp.get('potential_impact_score', 0):.1f}")
                                st.metric("Type", opp.get('type', 'unknown'))
                            
                            # Show detailed analysis if available
                            if opp.get('detailed_analysis'):
                                st.json(opp['detailed_analysis'])
                else:
                    st.info("No automation opportunities detected yet")
        
        # Add other insight types as needed
        else:
            st.info(f"🧠 {insight_type} analysis coming soon...")
            
    except Exception as e:
        st.error(f"❌ Error in cognitive insights: {e}")

def render_performance_trends_dashboard(analytics_engine):
    """Render performance trends dashboard."""
    st.subheader("📈 Performance Trends")
    
    try:
        # Get performance insights
        insights = analytics_engine.generate_performance_insights()
        
        if insights:
            # Display trend information
            st.markdown("**📊 Performance Analysis:**")
            
            # Show execution analytics
            exec_analytics = insights.get('execution_analytics', {})
            if exec_analytics:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Executions", exec_analytics.get('total_executions', 0))
                with col2:
                    st.metric("Avg Quality", f"{exec_analytics.get('avg_quality_score', 0):.3f}")
                with col3:
                    st.metric("Success Rate", f"{exec_analytics.get('success_rate', 0):.1f}%")
            
            # Show efficiency trends
            efficiency_trends = insights.get('efficiency_trends', {})
            if efficiency_trends:
                st.markdown("**⚡ Efficiency Trends:**")
                trend_direction = efficiency_trends.get('trend_direction', 'unknown')
                if trend_direction == 'improving':
                    st.success(f"📈 Performance is improving")
                elif trend_direction == 'declining':
                    st.warning(f"📉 Performance is declining")
                else:
                    st.info(f"📊 Performance is {trend_direction}")
            
            # Show recommendations
            recommendations = insights.get('recommendations', [])
            if recommendations:
                st.markdown("**💡 Recommendations:**")
                for rec in recommendations:
                    st.info(f"• {rec.get('description', 'No description')}")
        else:
            st.info("No performance trends available yet")
            
    except Exception as e:
        st.error(f"❌ Error loading performance trends: {e}")

def render_automation_opportunities_dashboard(cognitive_insights):
    """Render automation opportunities dashboard."""
    st.subheader("🎯 Automation Opportunities")
    
    try:
        # Get automation opportunities
        opportunities = cognitive_insights.detect_automation_opportunities()
        
        if opportunities:
            # Filter by confidence level
            confidence_filter = st.slider("Minimum Confidence", 0.0, 1.0, 0.7, 0.1)
            filtered_opportunities = [opp for opp in opportunities if opp.get('confidence_score', 0) >= confidence_filter]
            
            st.metric("High-Confidence Opportunities", len(filtered_opportunities))
            
            # Display opportunities
            for i, opp in enumerate(filtered_opportunities[:10]):  # Top 10
                with st.expander(f"🎯 {opp.get('pattern_identifier', f'Opportunity {i+1}')}"):
                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        confidence = opp.get('confidence_score', 0)
                        st.metric("Confidence", f"{confidence:.3f}")
                        if confidence >= 0.9:
                            st.success("🟢 Very High")
                        elif confidence >= 0.8:
                            st.success("🟡 High") 
                        else:
                            st.info("🔵 Medium")
                    
                    with col2:
                        st.metric("Frequency", opp.get('frequency', 0))
                        st.metric("Type", opp.get('type', 'unknown'))
                    
                    with col3:
                        impact = opp.get('potential_impact_score', 0)
                        st.metric("Impact Score", f"{impact:.1f}")
                        if impact > 15:
                            st.success("🔥 High Impact")
                        elif impact > 5:
                            st.info("📈 Medium Impact")
                        else:
                            st.info("📊 Low Impact")
                    
                    # Implementation recommendation
                    if confidence >= 0.8 and impact > 10:
                        st.success("✅ **Recommended for immediate implementation**")
                    elif confidence >= 0.7:
                        st.info("💡 **Consider for pilot implementation**")
                    else:
                        st.info("📊 **Monitor for future opportunities**")
        else:
            st.info("🎯 No automation opportunities detected yet. Opportunities will appear as SAM learns from usage patterns.")
            
    except Exception as e:
        st.error(f"❌ Error loading automation opportunities: {e}")

def generate_sample_slp_data(analytics_engine):
    """Generate sample SLP execution data for demonstration purposes."""
    try:
        import random
        from datetime import datetime, timedelta

        # Get the metrics collector if available
        metrics_collector = st.session_state.get('slp_metrics_collector')
        if not metrics_collector:
            st.error("❌ Metrics collector not available")
            return

        # Generate sample execution data
        sample_programs = [
            {"id": "prog_001", "name": "Query Optimization", "type": "performance"},
            {"id": "prog_002", "name": "Response Enhancement", "type": "quality"},
            {"id": "prog_003", "name": "Context Analysis", "type": "understanding"},
            {"id": "prog_004", "name": "Memory Retrieval", "type": "efficiency"},
            {"id": "prog_005", "name": "Pattern Recognition", "type": "learning"}
        ]

        # Generate 20-50 sample executions
        num_executions = random.randint(20, 50)

        for i in range(num_executions):
            program = random.choice(sample_programs)

            # Generate realistic execution metrics
            execution_time_ms = random.uniform(15, 250)  # 15-250ms execution time
            success = random.random() > 0.15  # 85% success rate
            baseline_time_ms = execution_time_ms * random.uniform(1.2, 3.0)  # Baseline is slower

            execution_data = {
                'program_id': program['id'],
                'execution_time_ms': execution_time_ms,
                'success': success,
                'baseline_time_ms': baseline_time_ms,
                'quality_score': random.uniform(0.7, 0.95),
                'context_hash': f"ctx_{random.randint(1000, 9999)}",
                'tpv_enabled': random.random() > 0.6,  # 40% TPV usage
                'timestamp': datetime.utcnow() - timedelta(minutes=random.randint(0, 60))
            }

            # Record the execution
            analytics_engine.collect_execution_metrics(program['id'], execution_data)

        # Generate some pattern discoveries
        for i in range(random.randint(3, 8)):
            pattern_data = {
                'pattern_type': random.choice(['query_optimization', 'response_enhancement', 'context_analysis']),
                'confidence_score': random.uniform(0.6, 0.9),
                'capture_success': random.random() > 0.2,  # 80% capture success
                'timestamp': datetime.utcnow() - timedelta(minutes=random.randint(0, 120))
            }

            if metrics_collector:
                metrics_collector.on_pattern_capture(pattern_data, pattern_data['capture_success'])

        st.success(f"✅ Generated {num_executions} sample executions and pattern discoveries!")
        logger.info(f"Generated {num_executions} sample SLP executions for analytics demonstration")

    except Exception as e:
        st.error(f"❌ Error generating sample data: {e}")
        logger.error(f"Failed to generate sample SLP data: {e}")

def generate_sample_quality_trends_data(program_analyzer):
    """Generate sample quality trends data for demonstration purposes."""
    try:
        import random
        from datetime import datetime, timedelta

        # Get the program store if available
        if not hasattr(program_analyzer, 'store'):
            st.error("❌ Program analyzer store not available")
            return

        store = program_analyzer.store

        # Generate sample quality trend data over the last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        # Create sample programs if none exist
        sample_programs = []
        for i in range(5):
            program_id = f"sample_quality_prog_{i+1}"

            # Generate quality trend data points
            for day in range(30):
                date = start_date + timedelta(days=day)

                # Simulate different quality trend patterns
                if i == 0:  # Improving quality
                    base_quality = 0.6 + (day / 30) * 0.3  # Improves from 0.6 to 0.9
                elif i == 1:  # Declining quality
                    base_quality = 0.9 - (day / 30) * 0.2  # Declines from 0.9 to 0.7
                elif i == 2:  # Stable quality
                    base_quality = 0.8 + random.uniform(-0.05, 0.05)  # Stable around 0.8
                elif i == 3:  # Volatile quality
                    base_quality = 0.7 + random.uniform(-0.2, 0.2)  # Volatile around 0.7
                else:  # Gradual improvement
                    base_quality = 0.5 + (day / 30) * 0.4  # Gradual improvement

                # Add some noise
                quality_score = max(0.1, min(1.0, base_quality + random.uniform(-0.1, 0.1)))

                # Generate corresponding execution data
                execution_data = {
                    'program_id': program_id,
                    'execution_time_ms': random.uniform(50, 200),
                    'success': random.random() > 0.1,  # 90% success rate
                    'quality_score': quality_score,
                    'user_feedback_score': quality_score + random.uniform(-0.1, 0.1),
                    'efficiency_gain': random.uniform(10, 80),
                    'timestamp': date
                }

                # Record the execution (this will create trend data)
                try:
                    store.record_enhanced_execution(program_id, execution_data)
                except Exception as e:
                    # If the method doesn't exist, try alternative approach
                    logger.debug(f"Enhanced execution recording failed: {e}")

        st.success(f"✅ Generated sample quality trends data for {len(sample_programs)} programs over 30 days!")
        logger.info("Generated sample quality trends data for demonstration")

    except Exception as e:
        st.error(f"❌ Error generating sample quality trends data: {e}")
        logger.error(f"Failed to generate sample quality trends data: {e}")

# Integration function to be called from secure_streamlit_app.py
def integrate_enhanced_slp_into_sam():
    """Main integration function to add enhanced SLP to SAM."""
    try:
        # Initialize enhanced SLP system
        slp_integration = initialize_enhanced_slp_system()
        
        if slp_integration:
            logger.info("✅ Enhanced SLP integration successful")
            return slp_integration
        else:
            logger.warning("⚠️ SLP integration failed - using fallback")
            return None
            
    except Exception as e:
        logger.error(f"❌ Enhanced SLP integration failed: {e}")
        return None

if __name__ == "__main__":
    print("🧠 SLP Phase 1A+1B Integration Script")
    print("This script integrates enhanced SLP analytics into the live SAM system.")
    print("Run this from within the SAM Streamlit application.")
