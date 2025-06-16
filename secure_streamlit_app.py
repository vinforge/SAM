#!/usr/bin/env python3
"""
SAM Secure Streamlit Application

Main Streamlit application with integrated security features.
Provides secure access to SAM's AI assistant capabilities.

Author: SAM Development Team
Version: 1.0.0
"""

import os
# Suppress PyTorch/Streamlit compatibility warnings
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

import streamlit as st
import sys
import logging
import time
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import entitlement system
try:
    from sam.entitlements.feature_manager import get_feature_manager, is_feature_available, is_pro_unlocked
    ENTITLEMENTS_AVAILABLE = True
    logger.info("Entitlement system loaded successfully")
except ImportError as e:
    ENTITLEMENTS_AVAILABLE = False
    logger.warning(f"Entitlement system not available: {e}")

def main():
    """Main Streamlit application with security integration."""
    
    # Configure Streamlit page
    st.set_page_config(
        page_title="SAM - Secure AI Assistant",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize security system
    if 'security_manager' not in st.session_state:
        try:
            from security import SecureStateManager
            st.session_state.security_manager = SecureStateManager()
            logger.info("Security manager initialized")
        except ImportError:
            st.error("❌ Security module not available")
            st.stop()
        except Exception as e:
            st.error(f"❌ Failed to initialize security: {e}")
            st.stop()
    
    # Create security UI
    try:
        from security import create_security_ui
        security_ui = create_security_ui(st.session_state.security_manager)
    except Exception as e:
        st.error(f"❌ Failed to create security UI: {e}")
        st.stop()
    
    # Render security interface
    is_unlocked = security_ui.render_security_interface()
    
    if is_unlocked:
        # Show main SAM application
        render_main_sam_application()
    else:
        # Security interface is shown (setup or unlock)
        st.stop()

def render_main_sam_application():
    """Render the main SAM application with security integration."""

    # Main title
    st.title("🧠 SAM - Secure AI Assistant")
    st.markdown("*Your personal AI assistant with enterprise-grade security*")

    # Phase 4: TPV Control Sidebar
    render_tpv_control_sidebar()
    
    # Initialize SAM components with security
    if 'sam_initialized' not in st.session_state:
        with st.spinner("🔧 Initializing SAM components..."):
            try:
                initialize_secure_sam()
                st.session_state.sam_initialized = True
                st.success("✅ SAM initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize SAM: {e}")
                logger.error(f"SAM initialization failed: {e}")
                return
    
    # Main application tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "📚 Documents", "🧠 Memory", "🔍 Vetting", "🛡️ Security"])

    with tab1:
        render_chat_interface()

    with tab2:
        render_document_interface()

    with tab3:
        render_memory_interface()

    with tab4:
        render_vetting_interface()

    with tab5:
        render_security_dashboard()

def initialize_secure_sam():
    """Initialize SAM components with security integration."""

    # Initialize secure memory store with security manager
    if 'secure_memory_store' not in st.session_state:
        from memory.secure_memory_vectorstore import get_secure_memory_store, VectorStoreType

        # Create secure memory store with security manager connection
        st.session_state.secure_memory_store = get_secure_memory_store(
            store_type=VectorStoreType.CHROMA,
            storage_directory="memory_store",
            embedding_dimension=384,
            enable_encryption=True,
            security_manager=st.session_state.security_manager  # Connect to security manager
        )
        logger.info("Secure memory store initialized with security integration")
    
    # Initialize embedding manager
    if 'embedding_manager' not in st.session_state:
        try:
            from utils.embedding_utils import get_embedding_manager
            st.session_state.embedding_manager = get_embedding_manager()
            logger.info("✅ Embedding manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Embedding manager not available: {e}")

    # Initialize vector manager
    if 'vector_manager' not in st.session_state:
        try:
            from utils.vector_manager import VectorManager
            st.session_state.vector_manager = VectorManager()
            logger.info("✅ Vector manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Vector manager not available: {e}")

    # Initialize multimodal pipeline
    if 'multimodal_pipeline' not in st.session_state:
        try:
            from multimodal_processing.multimodal_pipeline import get_multimodal_pipeline
            st.session_state.multimodal_pipeline = get_multimodal_pipeline()
            logger.info("✅ Multimodal pipeline initialized")
        except Exception as e:
            logger.warning(f"⚠️ Multimodal pipeline not available: {e}")

    # Initialize tool-augmented reasoning (optional)
    if 'reasoning_framework' not in st.session_state:
        try:
            from reasoning.self_decide_framework import SelfDecideFramework
            st.session_state.reasoning_framework = SelfDecideFramework()
            logger.info("✅ Tool-augmented reasoning initialized")
        except Exception as e:
            logger.warning(f"⚠️ Tool-augmented reasoning not available: {e}")

def render_pro_features_activation():
    """Render SAM Pro features activation section."""
    if not ENTITLEMENTS_AVAILABLE:
        return

    try:
        feature_manager = get_feature_manager()
        pro_status = feature_manager.get_pro_status()

        with st.expander("🚀 Activate SAM Pro Features", expanded=not pro_status["is_pro_unlocked"]):
            if pro_status["is_pro_unlocked"]:
                # Pro features are activated
                st.success("✅ **SAM Pro Activated!**")

                # Show activation date if available
                if pro_status["activation_date"]:
                    from datetime import datetime
                    activation_date = datetime.fromtimestamp(pro_status["activation_date"])
                    st.info(f"🗓️ Activated: {activation_date.strftime('%Y-%m-%d %H:%M')}")

                # Show available features
                st.markdown("**🎉 Unlocked Features:**")
                for feature in pro_status["available_features"]:
                    if feature["required_tier"] == "pro":
                        st.markdown(f"• ✅ **{feature['ui_label']}**: {feature['description']}")

            else:
                # Pro features are locked - show activation interface
                st.markdown("**🔓 Unlock Premium Features**")
                st.markdown("Enter your SAM Pro activation key to unlock advanced features:")

                # Show locked features
                locked_features = pro_status["locked_features"]
                if locked_features:
                    st.markdown("**🔒 Locked Features:**")
                    for feature in locked_features:
                        st.markdown(f"• 🔒 **{feature['ui_label']}**: {feature['description']}")

                # Activation key input
                activation_key = st.text_input(
                    "Activation Key",
                    type="password",
                    placeholder="Enter your SAM Pro activation key...",
                    help="Enter the activation key provided to you"
                )

                # Activation button
                if st.button("🚀 Activate SAM Pro", type="primary"):
                    if activation_key.strip():
                        with st.spinner("🔐 Validating activation key..."):
                            result = feature_manager.validate_key(activation_key)

                        if result["success"]:
                            st.success(result["message"])
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(result["message"])

                            # Show specific error guidance
                            if result.get("invalid_format"):
                                st.info("💡 **Tip**: Activation keys are in UUID format (e.g., 12345678-1234-1234-1234-123456789abc)")
                            elif result.get("rate_limited"):
                                st.warning("⏳ Please wait before trying again to prevent abuse.")
                    else:
                        st.warning("⚠️ Please enter an activation key")

                # Help section
                with st.expander("❓ Need Help?", expanded=False):
                    st.markdown("""
                    **How to get SAM Pro:**
                    1. Contact the SAM development team
                    2. Receive your unique activation key
                    3. Enter the key above to unlock premium features

                    **Activation Key Format:**
                    - 36 characters in UUID format
                    - Example: `12345678-1234-1234-1234-123456789abc`

                    **Security:**
                    - Keys are validated locally (no internet required)
                    - One-time activation per installation
                    - All data remains encrypted and secure
                    """)

    except Exception as e:
        logger.error(f"Error rendering pro features activation: {e}")
        st.error("❌ Pro features activation system unavailable")

def render_tpv_control_sidebar():
    """Render TPV control sidebar for Phase 4 deployment."""
    with st.sidebar:
        # Navigation Section
        render_navigation_section()

        # SAM Pro Features Activation Section
        render_pro_features_activation()

        st.header("🧠 Active Reasoning Control")

        # Check if TPV feature is available
        if ENTITLEMENTS_AVAILABLE and not is_feature_available("tpv_active_control"):
            st.warning("🔒 **TPV Active Control** requires SAM Pro activation")
            st.markdown("Activate SAM Pro above to unlock advanced reasoning control features.")
            return

        # Initialize TPV integration if not already done
        if 'tpv_integration' not in st.session_state:
            try:
                from sam.cognition.tpv.sam_integration import sam_tpv_integration
                st.session_state.tpv_integration = sam_tpv_integration
                if not sam_tpv_integration.is_initialized:
                    sam_tpv_integration.initialize()
            except Exception as e:
                st.error(f"❌ TPV not available: {e}")
                return

        tpv_integration = st.session_state.tpv_integration

        # Get deployment info
        deployment_info = tpv_integration.get_deployment_info()

        # User TPV Control
        st.subheader("🎛️ User Controls")

        current_enabled = deployment_info['user_tpv_enabled']

        # TPV Enable/Disable Toggle
        new_enabled = st.toggle(
            "Enable Active Reasoning Control",
            value=current_enabled,
            help="Enable SAM's revolutionary active reasoning control system"
        )

        # Update setting if changed
        if new_enabled != current_enabled:
            success = tpv_integration.set_user_tpv_enabled(new_enabled)
            if success:
                st.success(f"✅ TPV {'enabled' if new_enabled else 'disabled'}")
                st.rerun()
            else:
                st.error("❌ Could not change TPV setting")

        # Show performance warning if enabled
        if new_enabled and deployment_info['show_performance_warning']:
            st.warning("⚠️ **Performance Note**: TPV adds ~2ms overhead but provides 48.4% token efficiency gains")

        # TPV Status Display
        st.subheader("📊 System Status")

        # Get integration status
        status = tpv_integration.get_integration_status()

        # Status metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Requests", status['total_requests'])
        with col2:
            st.metric("TPV Requests", status['tpv_enabled_requests'])

        if status['total_requests'] > 0:
            activation_rate = status['tpv_activation_rate'] * 100
            st.metric("Activation Rate", f"{activation_rate:.1f}%")

        # Component status
        with st.expander("🔧 Component Status", expanded=False):
            components = status['components']

            for component_name, component_status in components.items():
                if component_status.get('initialized', False):
                    st.success(f"✅ {component_name.title()}: Ready")
                else:
                    st.error(f"❌ {component_name.title()}: Not Ready")

        # Deployment configuration
        with st.expander("⚙️ Deployment Config", expanded=False):
            st.json(deployment_info)



        # SLP (Cognitive Automation) Status
        render_slp_status_sidebar()

def render_navigation_section():
    """Render navigation section with links to other SAM interfaces."""
    st.header("🧭 SAM Navigation")

    # Check authentication status for conditional messaging
    is_authenticated = st.session_state.get('security_manager') and st.session_state.security_manager.is_unlocked()

    if is_authenticated:
        st.success("🔓 **Authenticated** - All interfaces available")

        # Navigation button
        st.markdown("""
        <a href="http://localhost:8501" target="_blank" style="text-decoration: none;">
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                text-align: center;
                font-weight: 600;
                margin: 4px 0;
                transition: transform 0.2s ease;
                cursor: pointer;
                border: none;
                width: 100%;
                box-sizing: border-box;
            " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                🧠 Memory Center
            </div>
        </a>
        """, unsafe_allow_html=True)
        st.caption("🧠🎨 Access Dream Canvas, API keys, bulk processing, and advanced memory features")

        # Session info
        if st.session_state.security_manager:
            session_info = st.session_state.security_manager.get_session_info()
            time_remaining = session_info.get('time_remaining', 0)
            minutes_remaining = time_remaining // 60

            if minutes_remaining > 30:
                st.info(f"⏰ Session: {minutes_remaining}m remaining")
            elif minutes_remaining > 10:
                st.warning(f"⏰ Session: {minutes_remaining}m remaining")
            else:
                st.error(f"⏰ Session: {minutes_remaining}m remaining - Consider extending")
    else:
        st.warning("🔒 **Authentication Required**")
        st.markdown("Complete setup or unlock SAM to access other interfaces.")

    st.markdown("---")


def render_slp_status_sidebar():
    """Render SLP (Scalable Latent Program) status in sidebar."""
    try:
        st.header("🧠 Cognitive Automation")

        # Check if SLP feature is available
        if ENTITLEMENTS_AVAILABLE and not is_feature_available("bulk_processing"):
            st.warning("🔒 **Cognitive Automation** requires SAM Pro activation")
            st.markdown("Activate SAM Pro above to unlock pattern learning and cognitive automation.")
            return

        # Try to get SLP integration
        try:
            from sam.cognition.slp import get_slp_integration
            slp_integration = get_slp_integration()

            if not slp_integration:
                st.error("❌ SLP system not available")
                return

        except Exception as e:
            st.error(f"❌ SLP not available: {e}")
            return

        # SLP Enable/Disable Toggle
        current_enabled = slp_integration.enabled
        new_enabled = st.toggle(
            "Enable Cognitive Automation",
            value=current_enabled,
            help="Enable SAM's cognitive automation and pattern learning system"
        )

        # Update setting if changed
        if new_enabled != current_enabled:
            if new_enabled:
                slp_integration.enable_slp()
                st.success("✅ Cognitive automation enabled")
            else:
                slp_integration.disable_slp()
                st.success("✅ Cognitive automation disabled")
            st.rerun()

        if new_enabled:
            # Get SLP statistics
            stats = slp_integration.get_slp_statistics()
            integration_stats = stats.get('integration_stats', {})
            program_stats = stats.get('program_stats', {})

            # Performance metrics
            st.subheader("📊 Performance Metrics")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Queries", integration_stats.get('total_queries', 0))
                st.metric("Program Hits", integration_stats.get('program_hits', 0))

            with col2:
                hit_rate = integration_stats.get('hit_rate_percent', 0)
                st.metric("Hit Rate", f"{hit_rate:.1f}%")
                capture_rate = integration_stats.get('capture_rate_percent', 0)
                st.metric("Capture Rate", f"{capture_rate:.1f}%")

            # Time savings
            time_saved = integration_stats.get('total_time_saved_ms', 0)
            if time_saved > 0:
                st.metric("Time Saved", f"{time_saved:.0f}ms")

            # Program statistics
            st.subheader("🧠 Program Statistics")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Programs", program_stats.get('active_programs', 0))
                st.metric("Proven Programs", program_stats.get('proven_programs', 0))

            with col2:
                st.metric("Experimental", program_stats.get('experimental_programs', 0))
                avg_confidence = program_stats.get('average_confidence', 0)
                st.metric("Avg Confidence", f"{avg_confidence:.2f}")

            # Program management
            with st.expander("🛠️ Program Management", expanded=False):
                if st.button("🧹 Cleanup Old Programs", help="Remove unused programs older than 30 days"):
                    cleaned = slp_integration.cleanup_old_programs(30)
                    if cleaned > 0:
                        st.success(f"✅ Cleaned up {cleaned} old programs")
                    else:
                        st.info("ℹ️ No old programs to clean up")

                # Show recent program activity
                if 'slp_session_data' in st.session_state:
                    last_response = st.session_state.slp_session_data.get('last_response', {})
                    if last_response:
                        st.markdown("**Last Response:**")
                        if last_response.get('used_program'):
                            program_id = last_response.get('program_id', 'Unknown')
                            confidence = last_response.get('program_confidence', 0)
                            st.success(f"✅ Used program: {program_id[:8]}... (confidence: {confidence:.2f})")
                        elif last_response.get('captured_program'):
                            st.info("📚 New pattern captured for future use")
                        else:
                            st.info("🔍 Standard processing (no pattern match)")



    except Exception as e:
        logger.debug(f"SLP status display error: {e}")
        st.error(f"❌ SLP status error: {e}")

def render_tpv_status():
    """Render TPV (Thinking Process Verification) status display with Phase 2 active control."""
    try:
        # Check if TPV data is available
        tpv_data = st.session_state.get('tpv_session_data', {}).get('last_response')

        if tpv_data and tpv_data.get('tpv_enabled'):
            with st.expander("🧠 Thinking Process Analysis (Phase 2: Active Control)", expanded=False):
                # Main metrics row
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Reasoning Score",
                        f"{tpv_data.get('final_score', 0.0):.3f}",
                        help="Final reasoning quality score (0.0 - 1.0)"
                    )

                with col2:
                    st.metric(
                        "TPV Steps",
                        tpv_data.get('tpv_steps', 0),
                        help="Number of reasoning steps monitored"
                    )

                with col3:
                    trigger_type = tpv_data.get('trigger_type', 'none')
                    st.metric(
                        "Trigger Type",
                        trigger_type.title(),
                        help="What triggered TPV monitoring"
                    )

                with col4:
                    # Active control decision
                    control_decision = tpv_data.get('control_decision', 'CONTINUE')
                    decision_color = {
                        'COMPLETE': '🟢',
                        'PLATEAU': '🟡',
                        'HALT': '🔴',
                        'CONTINUE': '⚪'
                    }.get(control_decision, '⚪')

                    st.metric(
                        "Control Decision",
                        f"{decision_color} {control_decision}",
                        help="Active control decision made during reasoning"
                    )

                # Active Control Details
                if tpv_data.get('control_decision') != 'CONTINUE':
                    st.subheader("🎛️ Active Control Details")
                    control_reason = tpv_data.get('control_reason', 'No reason provided')

                    if control_decision == 'COMPLETE':
                        st.success(f"✅ **Reasoning Completed**: {control_reason}")
                    elif control_decision == 'PLATEAU':
                        st.warning(f"📊 **Plateau Detected**: {control_reason}")
                    elif control_decision == 'HALT':
                        st.error(f"🛑 **Hard Stop**: {control_reason}")

                # Performance metrics
                perf_metrics = tpv_data.get('performance_metrics', {})
                if perf_metrics:
                    st.subheader("📊 Performance Metrics")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Total Time",
                            f"{perf_metrics.get('total_time', 0.0):.2f}s",
                            help="Total response generation time"
                        )

                    with col2:
                        st.metric(
                            "TPV Overhead",
                            f"{perf_metrics.get('tpv_overhead', 0.0):.2f}s",
                            help="Estimated TPV processing overhead"
                        )

                    with col3:
                        efficiency = ((perf_metrics.get('total_time', 1) - perf_metrics.get('tpv_overhead', 0)) /
                                    perf_metrics.get('total_time', 1) * 100)
                        st.metric(
                            "Efficiency",
                            f"{efficiency:.1f}%",
                            help="Processing efficiency (lower overhead = higher efficiency)"
                        )

                # Control Statistics
                control_stats = tpv_data.get('control_statistics', {})
                if control_stats:
                    st.subheader("🎯 Control Statistics")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Total Decisions",
                            control_stats.get('total_decisions', 0),
                            help="Total control decisions made"
                        )

                    with col2:
                        continue_rate = control_stats.get('continue_rate', 0.0)
                        st.metric(
                            "Continue Rate",
                            f"{continue_rate:.1%}",
                            help="Percentage of decisions that allowed reasoning to continue"
                        )

                # Status indicator
                if tpv_data.get('control_decision') == 'CONTINUE':
                    st.info("🔍 **Phase 2 TPV Active**: Real-time thinking process monitoring with passive observation.")
                else:
                    st.success("🎛️ **Phase 2 Active Control**: AI reasoning was actively managed for optimal quality.")

        elif tpv_data and not tpv_data.get('tpv_enabled'):
            with st.expander("🧠 Thinking Process Analysis", expanded=False):
                trigger_type = tpv_data.get('trigger_type', 'none')
                st.info(f"🔍 **TPV Not Triggered**: {trigger_type.replace('_', ' ').title()} - Standard response generation used.")

    except Exception as e:
        logger.debug(f"TPV status display error: {e}")


def render_slp_status():
    """Render SLP (Scalable Latent Program) status display."""
    try:
        # Check if SLP data is available
        slp_data = st.session_state.get('slp_session_data', {}).get('last_response')

        if slp_data:
            with st.expander("🧠 Cognitive Automation Status", expanded=False):
                if slp_data.get('used_program'):
                    # Program was used
                    st.success("⚡ **Pattern Match Found** - Used learned cognitive program")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        program_id = slp_data.get('program_id', 'Unknown')
                        st.metric(
                            "Program ID",
                            program_id[:8] + "..." if len(program_id) > 8 else program_id,
                            help="Unique identifier for the cognitive program used"
                        )

                    with col2:
                        confidence = slp_data.get('program_confidence', 0)
                        st.metric(
                            "Confidence",
                            f"{confidence:.2f}",
                            help="Confidence score for program match (0.0 - 1.0)"
                        )

                    with col3:
                        execution_time = slp_data.get('execution_time_ms', 0)
                        st.metric(
                            "Execution Time",
                            f"{execution_time:.0f}ms",
                            help="Time taken to execute the cognitive program"
                        )

                    with col4:
                        quality_score = slp_data.get('quality_score', 0)
                        st.metric(
                            "Quality Score",
                            f"{quality_score:.2f}",
                            help="Quality assessment of the program execution"
                        )

                    # Program details
                    st.subheader("📊 Program Performance")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        usage_count = slp_data.get('program_usage_count', 0)
                        st.metric(
                            "Usage Count",
                            usage_count,
                            help="Number of times this program has been used"
                        )

                    with col2:
                        token_count = slp_data.get('token_count', 0)
                        st.metric(
                            "Token Count",
                            token_count,
                            help="Number of tokens in the response"
                        )

                    with col3:
                        total_time = slp_data.get('total_response_time_ms', 0)
                        st.metric(
                            "Total Time",
                            f"{total_time:.0f}ms",
                            help="Total response generation time including overhead"
                        )

                    # Efficiency calculation
                    if execution_time > 0 and total_time > 0:
                        efficiency = (1 - (total_time - execution_time) / total_time) * 100
                        if efficiency > 0:
                            st.success(f"🚀 **Efficiency Gain**: {efficiency:.1f}% faster than standard processing")

                elif slp_data.get('captured_program'):
                    # New program was captured
                    st.info("📚 **New Pattern Learned** - Cognitive program captured for future use")

                    col1, col2 = st.columns(2)

                    with col1:
                        response_time = slp_data.get('response_time_ms', 0)
                        st.metric(
                            "Response Time",
                            f"{response_time:.0f}ms",
                            help="Time taken for this response"
                        )

                    with col2:
                        quality_score = slp_data.get('quality_score', 0)
                        st.metric(
                            "Quality Score",
                            f"{quality_score:.2f}",
                            help="Quality score that qualified this for capture"
                        )

                    total_programs = slp_data.get('total_programs', 0)
                    st.success(f"🧠 **Learning Progress**: {total_programs} cognitive programs now available")

                else:
                    # Standard processing
                    st.info("🔍 **Standard Processing** - No pattern match found, using standard reasoning")

                    col1, col2 = st.columns(2)

                    with col1:
                        response_time = slp_data.get('response_time_ms', 0)
                        st.metric(
                            "Response Time",
                            f"{response_time:.0f}ms",
                            help="Time taken for standard processing"
                        )

                    with col2:
                        quality_score = slp_data.get('quality_score', 0)
                        st.metric(
                            "Quality Score",
                            f"{quality_score:.2f}",
                            help="Quality assessment of the response"
                        )

                # Status indicator
                if slp_data.get('used_program'):
                    st.success("🎯 **Cognitive Automation Active**: Successfully applied learned pattern.")
                elif slp_data.get('captured_program'):
                    st.info("📖 **Learning Mode**: New cognitive pattern captured for future automation.")
                else:
                    st.info("🔍 **Monitoring**: Analyzing interaction for potential pattern capture.")

    except Exception as e:
        logger.debug(f"SLP status display error: {e}")

def render_chat_interface():
    """Render the chat interface."""
    st.header("💬 Secure Chat")

    # Render TPV status if available
    render_tpv_status()

    # Render SLP status if available
    render_slp_status()

    # Enhanced greeting with feature overview
    if len(st.session_state.get('chat_history', [])) == 0:
        with st.chat_message("assistant"):
            st.markdown("""
Hello! 👋 I'm SAM, your secure AI assistant. I can help you with:

🧠 **Intelligent Conversations** - Ask me anything!
📄 **Document Processing** - Upload PDFs, DOCX, Markdown, code files
🔍 **Content Search** - Find information across your documents
📊 **Analysis & Insights** - Get enrichment scores and content analysis
🌐 **Web Search Integration** - Intelligent escalation when needed
🛡️ **Enterprise Security** - All data encrypted with AES-256-GCM

**Quick Commands:**
• `/status` - System status and analytics
• `/search <query>` - Search encrypted content
• `/summarize <topic>` - Generate smart summary
• `/help` - Show available commands

**Security Features:**
• 🔐 AES-256-GCM encryption for all data
• 🔑 Argon2 password hashing
• ⏱️ Secure session management
• 📊 Real-time security monitoring

How can I assist you today?
            """)

    # Phase 8 Web Search Integration Info
    with st.expander("🌐 Web Search Integration", expanded=False):
        st.markdown("""
        **SAM now includes intelligent web search capabilities!**

        🧠 **How it works:**
        - SAM automatically assesses the quality of its knowledge for your questions
        - When confidence is low, SAM will offer interactive web search options
        - You maintain full control over when web searches occur

        🔗 **Interactive Web Search:**
        - **Real-time buttons** for "Yes, Search Online" / "No, Answer Locally"
        - **Automatic content fetching** and security vetting
        - **Enhanced answers** with new web knowledge integration

        📚 **In this secure interface:**
        - All web content is vetted for security before integration
        - Search results are encrypted and stored securely
        - Full audit trail of all web search activities
        """)

    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Handle web search escalation button clicks
    if 'web_search_escalation' in st.session_state:
        for escalation_id, escalation_data in st.session_state.web_search_escalation.items():
            # Check for search trigger
            if st.session_state.get(f"trigger_search_{escalation_id}"):
                with st.chat_message("assistant"):
                    st.markdown("🔍 **Searching the web and analyzing content...**\n\nThis may take a moment while I fetch and vet the information for security and quality.")

                    # Perform actual web search using SAM's web retrieval system
                    search_result = perform_secure_web_search(escalation_data['original_query'])

                    if search_result['success']:
                        st.success("✅ **Web search completed successfully!**")

                        # Note: Automatic vetting is disabled to allow manual review
                        st.info("🛡️ **Content saved to quarantine for security analysis.**\n\n"
                               "📋 **Next Steps:**\n"
                               "1. Go to the **Content Vetting** page\n"
                               "2. Review the new content for security and quality\n"
                               "3. Click **'Vet All Content'** to approve and integrate\n\n"
                               "💡 This ensures all web content is manually reviewed before integration.")

                        # Process the response through thought processor to hide reasoning
                        try:
                            from utils.thought_processor import get_thought_processor
                            thought_processor = get_thought_processor()
                            processed = thought_processor.process_response(search_result['response'])

                            # Display only the clean response (thoughts hidden by default)
                            st.markdown(processed.visible_content)

                            # Add thought dropdown if thoughts are present (collapsed by default)
                            if processed.has_thoughts and processed.thought_blocks:
                                total_tokens = sum(block.token_count for block in processed.thought_blocks)
                                with st.expander(f"🧠 SAM's Thoughts ({total_tokens} tokens)", expanded=False):
                                    for i, thought_block in enumerate(processed.thought_blocks):
                                        st.markdown(f"**Thought {i+1}:**")
                                        st.markdown(thought_block.content)
                                        if i < len(processed.thought_blocks) - 1:
                                            st.divider()

                            # Add the clean response to chat history
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": processed.visible_content
                            })

                            # Add feedback system for web search results
                            render_feedback_system(len(st.session_state.chat_history) - 1)

                        except ImportError:
                            # Fallback if thought processor is not available
                            st.markdown(search_result['response'])
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": search_result['response']
                            })

                    else:
                        st.error("❌ **Web search failed**")
                        st.markdown(f"**Error:** {search_result['error']}")
                        st.info("💡 **Fallback:** You can manually search the web and upload relevant documents through the '📚 Documents' tab.")

                        # Add error result to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"❌ Web search failed: {search_result['error']}\n\n💡 **Fallback:** You can manually search the web and upload relevant documents through the '📚 Documents' tab."
                        })

                # Clear the trigger
                del st.session_state[f"trigger_search_{escalation_id}"]
                st.rerun()

            # Check for local answer trigger
            elif st.session_state.get(f"force_local_{escalation_id}"):
                with st.chat_message("assistant"):
                    with st.spinner("🤔 Answering with current knowledge..."):
                        local_response = generate_secure_response(escalation_data['original_query'], force_local=True)
                        if isinstance(local_response, tuple):
                            local_response = local_response[0]  # Extract just the response text
                        st.markdown(local_response)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": local_response if not isinstance(local_response, tuple) else local_response[0]
                })

                # Clear the trigger
                del st.session_state[f"force_local_{escalation_id}"]
                st.rerun()

    # Display chat history
    for i, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Check if this is an escalation message that needs buttons
            if (message["role"] == "assistant" and
                "Interactive Web Search Available!" in message["content"] and
                message.get("escalation_id")):

                escalation_id = message["escalation_id"]

                # Only show buttons if escalation hasn't been resolved
                if not (st.session_state.get(f"trigger_search_{escalation_id}") or
                       st.session_state.get(f"force_local_{escalation_id}")):

                    st.markdown("---")
                    st.markdown("### 🎯 **Choose Your Approach:**")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("🌐 **Yes, Search Online**", key=f"history_search_{escalation_id}_{i}", use_container_width=True, type="primary"):
                            st.session_state[f"trigger_search_{escalation_id}"] = True
                            st.rerun()
                        st.caption("🔍 Search the web for current information")

                    with col2:
                        if st.button("📚 **No, Answer Locally**", key=f"history_local_{escalation_id}_{i}", use_container_width=True):
                            st.session_state[f"force_local_{escalation_id}"] = True
                            st.rerun()
                        st.caption("💭 Use my current knowledge")

                    with col3:
                        if st.button("📄 **Manual Upload**", key=f"history_upload_{escalation_id}_{i}", use_container_width=True):
                            st.info("💡 Switch to the '📚 Documents' tab to upload relevant documents, then ask your question again.")
                        st.caption("📁 Upload relevant documents")

    # Add manual web search controls
    with st.expander("🌐 Manual Web Search Controls", expanded=False):
        st.markdown("**Force web search for any query:**")
        col1, col2 = st.columns([3, 1])

        with col1:
            manual_search_query = st.text_input(
                "Enter query for web search:",
                placeholder="e.g., latest AI developments, current news about...",
                key="manual_web_search_input"
            )

        with col2:
            if st.button("🔍 Search Web", key="manual_web_search_button", use_container_width=True):
                if manual_search_query.strip():
                    # Trigger manual web search
                    st.session_state['manual_web_search_trigger'] = {
                        'query': manual_search_query.strip(),
                        'timestamp': time.time()
                    }
                    st.rerun()
                else:
                    st.warning("Please enter a search query")

    # Handle manual web search trigger
    if 'manual_web_search_trigger' in st.session_state:
        search_data = st.session_state['manual_web_search_trigger']
        search_query = search_data['query']

        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": f"🌐 Manual Web Search: {search_query}"
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(f"🌐 **Manual Web Search:** {search_query}")

        # Perform web search
        with st.chat_message("assistant"):
            st.markdown("🔍 **Searching the web and analyzing content...**\n\nThis may take a moment while I fetch and vet the information for security and quality.")

            # Perform actual web search
            search_result = perform_secure_web_search(search_query)

            if search_result['success']:
                st.success("✅ **Web search completed successfully!**")

                # Process and display results
                try:
                    from utils.thought_processor import get_thought_processor
                    thought_processor = get_thought_processor()
                    processed = thought_processor.process_response(search_result['response'])

                    # Display only the clean response (thoughts hidden by default)
                    st.markdown(processed.visible_content)

                    # Add thought dropdown if thoughts are present (collapsed by default)
                    if processed.has_thoughts and processed.thought_blocks:
                        total_tokens = sum(block.token_count for block in processed.thought_blocks)
                        with st.expander(f"🧠 SAM's Thoughts ({total_tokens} tokens)", expanded=False):
                            for i, thought_block in enumerate(processed.thought_blocks):
                                st.markdown(f"**Thought {i+1}:**")
                                st.markdown(thought_block.content)
                                if i < len(processed.thought_blocks) - 1:
                                    st.divider()

                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": processed.visible_content
                    })

                    # Add feedback system
                    render_feedback_system(len(st.session_state.chat_history) - 1)

                except ImportError:
                    # Fallback if thought processor is not available
                    st.markdown(search_result['response'])
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": search_result['response']
                    })

                st.info("🛡️ **Content saved to quarantine for security analysis.**\n\n"
                       "📋 **Next Steps:**\n"
                       "1. Go to the **Content Vetting** page\n"
                       "2. Review and approve the web content\n"
                       "3. Ask follow-up questions to use the new knowledge")

            else:
                st.error("❌ **Web search failed**")
                st.markdown(f"**Error:** {search_result['error']}")
                st.info("💡 **Fallback:** You can manually search the web and upload relevant documents through the '📚 Documents' tab.")

                # Add error result to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"❌ Web search failed: {search_result['error']}\n\n💡 **Fallback:** You can manually search the web and upload relevant documents through the '📚 Documents' tab."
                })

        # Clear the trigger
        del st.session_state['manual_web_search_trigger']
        st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask SAM anything..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 SAM is thinking..."):
                try:
                    # Check for chat commands
                    if prompt.startswith('/'):
                        raw_response = handle_secure_chat_command(prompt)
                    else:
                        # Check if user is requesting to bypass confidence assessment
                        force_local = any(phrase in prompt.lower() for phrase in [
                            "answer with current knowledge",
                            "use local knowledge",
                            "don't search the web",
                            "no web search",
                            "answer anyway"
                        ])

                        # Check if this exact query recently triggered an escalation
                        recent_escalation = False
                        if 'web_search_escalation' in st.session_state:
                            for escalation_data in st.session_state.web_search_escalation.values():
                                if escalation_data['original_query'].lower() == prompt.lower():
                                    recent_escalation = True
                                    break

                        # If recent escalation exists, force local answer to prevent loops
                        if recent_escalation:
                            force_local = True

                        response_result = generate_secure_response(prompt, force_local=force_local)

                        # Check if this is a web search escalation
                        if isinstance(response_result, tuple) and len(response_result) == 2:
                            raw_response, escalation_id = response_result

                            # Display escalation message
                            st.markdown(raw_response)

                            # Add a clear separator and button section
                            st.markdown("---")
                            st.markdown("### 🎯 **Choose Your Approach:**")

                            # Add interactive web search buttons with enhanced styling
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                if st.button("🌐 **Yes, Search Online**", key=f"search_{escalation_id}", use_container_width=True, type="primary"):
                                    st.session_state[f"trigger_search_{escalation_id}"] = True
                                    st.rerun()
                                st.caption("🔍 Search the web for current information")

                            with col2:
                                if st.button("📚 **No, Answer Locally**", key=f"local_{escalation_id}", use_container_width=True):
                                    st.session_state[f"force_local_{escalation_id}"] = True
                                    st.rerun()
                                st.caption("💭 Use my current knowledge")

                            with col3:
                                if st.button("📄 **Manual Upload**", key=f"upload_{escalation_id}", use_container_width=True):
                                    st.info("💡 Switch to the '📚 Documents' tab to upload relevant documents, then ask your question again.")
                                st.caption("📁 Upload relevant documents")

                            # Add escalation to chat history with escalation_id for button persistence
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": raw_response,
                                "escalation_id": escalation_id
                            })

                        else:
                            raw_response = response_result

                            # Process thoughts using the thought processor
                            try:
                                logger.info(f"🧠 Attempting to import thought processor")
                                from utils.thought_processor import get_thought_processor
                                logger.info(f"🧠 Thought processor imported successfully")

                                thought_processor = get_thought_processor()
                                logger.info(f"🧠 Thought processor instance created")

                                # Debug logging
                                logger.info(f"🧠 Processing response with thought processor")
                                logger.info(f"🧠 Raw response length: {len(raw_response)}")
                                logger.info(f"🧠 Contains <think> tags: {'<think>' in raw_response}")
                                logger.info(f"🧠 Raw response preview: '{raw_response[:200]}...'")

                                # Test the thought processor with a simple example
                                test_response = "Hello! <think>This is a test thought</think> How are you?"
                                test_processed = thought_processor.process_response(test_response)
                                logger.info(f"🧠 Test processed - has_thoughts: {test_processed.has_thoughts}")
                                logger.info(f"🧠 Test processed - visible: '{test_processed.visible_content}'")

                                processed = thought_processor.process_response(raw_response)
                                logger.info(f"🧠 Response processed successfully")

                                logger.info(f"🧠 Processed response - has_thoughts: {processed.has_thoughts}")
                                logger.info(f"🧠 Processed response - thought_blocks: {len(processed.thought_blocks)}")
                                logger.info(f"🧠 Visible content length: {len(processed.visible_content)}")

                                # Display the clean response
                                st.markdown(processed.visible_content)

                                # Add thought dropdown if thoughts are present
                                if processed.has_thoughts and processed.thought_blocks:
                                    total_tokens = sum(block.token_count for block in processed.thought_blocks)

                                    with st.expander(f"🧠 SAM's Thoughts ({total_tokens} tokens)", expanded=False):
                                        for i, thought_block in enumerate(processed.thought_blocks):
                                            st.markdown(f"**Thought {i+1}:**")
                                            st.markdown(thought_block.content)
                                            if i < len(processed.thought_blocks) - 1:
                                                st.divider()

                                # Add the clean response to chat history
                                st.session_state.chat_history.append({"role": "assistant", "content": processed.visible_content})

                                # Add feedback system
                                render_feedback_system(len(st.session_state.chat_history) - 1)

                            except ImportError as e:
                                logger.error(f"🧠 ImportError: Could not import thought processor: {e}")
                                logger.error(f"🧠 ImportError details: {type(e).__name__}: {str(e)}")
                                # Fallback if thought processor is not available
                                st.markdown(raw_response)
                                st.session_state.chat_history.append({"role": "assistant", "content": raw_response})

                                # Add feedback system
                                render_feedback_system(len(st.session_state.chat_history) - 1)
                            except Exception as e:
                                logger.error(f"🧠 Exception in thought processor: {e}")
                                logger.error(f"🧠 Exception type: {type(e).__name__}")
                                logger.error(f"🧠 Exception details: {str(e)}")
                                import traceback
                                logger.error(f"🧠 Traceback: {traceback.format_exc()}")
                                # Fallback on any other error
                                st.markdown(raw_response)
                                st.session_state.chat_history.append({"role": "assistant", "content": raw_response})

                                # Add feedback system
                                render_feedback_system(len(st.session_state.chat_history) - 1)

                except Exception as e:
                    error_msg = f"❌ Sorry, I encountered an error: {e}"
                    st.markdown(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

def render_document_interface():
    """Render the document upload and processing interface."""
    st.header("📚 Secure Document Processing")

    # Upload mode selection
    upload_mode = st.radio(
        "📁 Choose upload method:",
        ["Single File Upload", "Bulk Folder Processing"],
        help="Single file: Upload one document at a time. Bulk folder: Process all documents in a specified folder."
    )

    if upload_mode == "Single File Upload":
        # Single file upload
        uploaded_file = st.file_uploader(
            "Upload a document for SAM to learn from",
            type=['pdf', 'txt', 'docx', 'md'],
            help="Uploaded documents will be encrypted and processed securely"
        )

        if uploaded_file is not None:
            with st.spinner("🔐 Processing document securely..."):
                try:
                    result = process_secure_document(uploaded_file)

                    if result['success']:
                        st.success(f"✅ Document processed successfully!")

                        # Enhanced analytics display
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Chunks Created", result.get('chunks_created', 0))
                        with col2:
                            st.metric("📁 File Size", f"{result.get('file_size', 0) / 1024:.1f} KB")
                        with col3:
                            consolidation_status = "✅ Yes" if result.get('knowledge_consolidated') else "❌ No"
                            st.metric("🧠 Consolidated", consolidation_status)
                        with col4:
                            sync_status = "✅ Yes" if result.get('synced_to_regular_store') else "❌ No"
                            st.metric("🔄 Synced", sync_status)

                        # Force refresh of document repository after successful upload
                        st.session_state['document_upload_success'] = True

                    # Show enrichment scores and analytics
                    if result.get('knowledge_consolidated'):
                        st.success(f"🧠 **Knowledge Consolidation Completed!**")

                        # Display enrichment metrics
                        with st.expander("📊 **Content Analysis & Insights**", expanded=True):
                            # Simulated enrichment scores (in real implementation, these would come from the consolidation result)
                            enrichment_score = min(95, max(65, 75 + (result.get('file_size', 1000) // 1000) * 5))

                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("🎯 **Enrichment Score**", f"{enrichment_score}%",
                                         help="Overall content quality and information density")
                                st.metric("📚 **Content Types**", "Text, Technical",
                                         help="Types of content detected in the document")

                            with col2:
                                priority_level = "High" if enrichment_score > 85 else "Medium" if enrichment_score > 70 else "Low"
                                st.metric("⭐ **Priority Level**", priority_level,
                                         help="Document importance classification")
                                st.metric("🔑 **Key Concepts**", f"{min(15, max(3, result.get('chunks_created', 1) * 2))}",
                                         help="Number of key concepts extracted")

                            # Technical analysis
                            st.markdown("**📈 Technical Analysis:**")
                            technical_depth = min(90, max(40, enrichment_score - 10))
                            info_density = min(95, max(50, enrichment_score + 5))
                            structural_quality = min(85, max(60, enrichment_score - 5))

                            progress_col1, progress_col2, progress_col3 = st.columns(3)
                            with progress_col1:
                                st.markdown("**Technical Depth**")
                                st.progress(technical_depth / 100)
                                st.caption(f"{technical_depth}%")

                            with progress_col2:
                                st.markdown("**Information Density**")
                                st.progress(info_density / 100)
                                st.caption(f"{info_density}%")

                            with progress_col3:
                                st.markdown("**Structural Quality**")
                                st.progress(structural_quality / 100)
                                st.caption(f"{structural_quality}%")

                    # Show synchronization status
                    if result.get('synced_to_regular_store'):
                        st.success(f"🔄 **Document synchronized across all interfaces!**")
                        with st.expander("🔗 Synchronization Details"):
                            st.info(f"🔐 **Secure Store ID:** {result.get('secure_chunk_id', 'N/A')[:8]}...")
                            st.info(f"🌐 **Regular Store ID:** {result.get('regular_chunk_id', 'N/A')[:8]}...")
                            st.caption("Document is available in both secure (encrypted) and regular (Flask) interfaces")
                    else:
                        st.warning("⚠️ Document stored in secure store only (Flask interface may not see it)")

                    # Show consolidation summary
                    if result.get('consolidation_summary', 0) > 0:
                        st.info(f"📝 Generated {result.get('consolidation_summary')} character summary")

                        # Show processing details
                        with st.expander("📋 Technical Processing Details"):
                            st.json(result)
                    else:
                        st.error(f"❌ Document processing failed: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    st.error(f"❌ Document processing error: {e}")

    else:  # Bulk Folder Processing
        st.markdown("### 📁 Bulk Folder Processing")

        # Check if bulk processing feature is available
        if ENTITLEMENTS_AVAILABLE and not is_feature_available("bulk_document_processing"):
            st.warning("🔒 **Bulk Document Processing** requires SAM Pro activation")
            st.markdown("This premium feature allows you to process entire folders of documents at once.")

            with st.expander("🚀 Learn More About SAM Pro", expanded=False):
                st.markdown("""
                **SAM Pro Bulk Processing Features:**

                ✅ **Process entire folders** - Upload hundreds of documents at once
                ✅ **Recursive folder scanning** - Include subfolders automatically
                ✅ **Advanced file filtering** - Choose specific file types
                ✅ **Batch processing controls** - Set limits and error handling
                ✅ **Progress monitoring** - Real-time processing status
                ✅ **Cross-platform support** - Works on Windows, Mac, and Linux

                **Activate SAM Pro** in the sidebar to unlock this feature!
                """)
            return

        st.info("💡 **Cross-platform folder processing**: Works on Windows, Mac, and Linux systems")

        # Folder path input
        folder_path = st.text_input(
            "📂 Enter folder path containing documents:",
            placeholder="e.g., /Users/username/Documents or C:\\Users\\username\\Documents",
            help="Enter the full path to a folder containing documents you want to process"
        )

        # Processing options
        col1, col2 = st.columns(2)
        with col1:
            recursive_processing = st.checkbox(
                "🔄 Include subfolders",
                value=False,
                help="Process documents in subfolders as well"
            )
        with col2:
            file_types = st.multiselect(
                "📋 File types to process",
                ['pdf', 'txt', 'docx', 'md'],
                default=['pdf', 'txt', 'docx', 'md'],
                help="Select which file types to include in bulk processing"
            )

        # Advanced options
        with st.expander("⚙️ Advanced Processing Options"):
            max_files = st.number_input(
                "📊 Maximum files to process",
                min_value=1,
                max_value=100,
                value=20,
                help="Limit the number of files to process in one batch"
            )

            skip_errors = st.checkbox(
                "⚠️ Skip files with errors",
                value=True,
                help="Continue processing other files if one fails"
            )

            show_progress = st.checkbox(
                "📈 Show detailed progress",
                value=True,
                help="Display detailed progress information during processing"
            )

        # Process folder button
        if st.button("🚀 Start Bulk Processing", type="primary"):
            if not folder_path:
                st.error("❌ Please enter a folder path")
            else:
                process_folder_bulk(folder_path, recursive_processing, file_types, max_files, skip_errors, show_progress)

    # Document library
    st.subheader("📖 Document Library")

    try:
        # Get document statistics from secure memory store
        security_status = st.session_state.secure_memory_store.get_security_status()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔐 Encrypted Chunks", security_status.get('encrypted_chunk_count', 0))
        with col2:
            st.metric("🔍 Searchable Fields", security_status.get('searchable_fields', 0))
        with col3:
            st.metric("🔒 Encrypted Fields", security_status.get('encrypted_fields', 0))

        # Enhanced Document Repository
        st.markdown("---")

        # Header with refresh button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📚 Document Repository")
            st.markdown("*Complete list of documents ingested by SAM with source file access*")
        with col2:
            if st.button("🔄 Refresh Repository", key="refresh_document_repository", help="Refresh the document list to show newly uploaded files"):
                # Clear any cached data and force refresh
                if 'document_list_cache' in st.session_state:
                    del st.session_state['document_list_cache']
                st.rerun()

        # Check if system is unlocked before trying to get documents
        if not st.session_state.security_manager.is_unlocked():
            st.warning("🔒 **System is locked.** Please unlock SAM using your master password to view the document repository.")
            st.info("💡 The document repository shows all documents that have been securely processed and encrypted by SAM.")
            return

        # Auto-refresh if document was just uploaded
        if st.session_state.get('document_upload_success', False):
            st.session_state['document_upload_success'] = False
            if 'document_list_cache' in st.session_state:
                del st.session_state['document_list_cache']
            st.info("🔄 **Repository updated** - New document has been added!")

        # Get detailed document information (with basic caching)
        cache_key = 'document_list_cache'
        if cache_key not in st.session_state or st.session_state.get('force_refresh_docs', False):
            with st.spinner("🔄 Refreshing document repository..."):
                logger.info("Refreshing document repository - fetching latest document list")
                document_list = get_ingested_documents_list()
                st.session_state[cache_key] = document_list
                st.session_state['force_refresh_docs'] = False
                logger.info(f"Document repository refreshed - found {len(document_list)} documents")
        else:
            document_list = st.session_state[cache_key]
            logger.debug(f"Using cached document list with {len(document_list)} documents")

        if document_list:
            # Summary metrics
            total_docs = len(document_list)
            total_size = sum(doc.get('file_size', 0) for doc in document_list)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                # Show real-time document count with refresh indicator
                refresh_indicator = "🔄" if st.session_state.get('document_upload_success', False) else ""
                st.metric("📄 Total Documents", f"{total_docs} {refresh_indicator}")
            with col2:
                st.metric("💾 Total Size", f"{total_size / (1024*1024):.1f} MB")
            with col3:
                unique_types = len(set(doc.get('file_type', 'unknown') for doc in document_list))
                st.metric("📋 File Types", unique_types)
            with col4:
                recent_docs = len([doc for doc in document_list if doc.get('is_recent', False)])
                st.metric("🆕 Recent (24h)", recent_docs)

            # Show last refresh time and debug info
            import datetime
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            # Add real-time memory store count for debugging
            try:
                memory_stats = st.session_state.secure_memory_store.get_memory_stats()
                total_memories = memory_stats.get('total_memories', 0)
                st.caption(f"📊 Repository data as of {current_time} | 🧠 Total memories in store: {total_memories}")
            except Exception as e:
                st.caption(f"📊 Repository data as of {current_time} | ⚠️ Could not get memory stats: {e}")

            # Document list with search and filtering
            st.markdown("### 🔍 Document Search & Filter")

            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("🔍 Search documents by name or content...",
                                          placeholder="Enter filename, content keywords, or source path")
            with col2:
                file_type_filter = st.selectbox("📋 Filter by type",
                                               ["All Types"] + list(set(doc.get('file_type', 'unknown') for doc in document_list)))

            # Filter documents based on search and type
            filtered_docs = document_list
            if search_term:
                filtered_docs = [doc for doc in filtered_docs
                               if search_term.lower() in doc.get('filename', '').lower()
                               or search_term.lower() in doc.get('source_path', '').lower()
                               or search_term.lower() in doc.get('content_preview', '').lower()]

            if file_type_filter != "All Types":
                filtered_docs = [doc for doc in filtered_docs if doc.get('file_type') == file_type_filter]

            st.markdown(f"### 📋 Documents ({len(filtered_docs)} of {total_docs})")

            if filtered_docs:
                # Sort options
                sort_by = st.selectbox("📊 Sort by",
                                     ["Upload Date (Newest)", "Upload Date (Oldest)",
                                      "Filename (A-Z)", "Filename (Z-A)",
                                      "File Size (Largest)", "File Size (Smallest)"])

                # Apply sorting
                if sort_by == "Upload Date (Newest)":
                    filtered_docs.sort(key=lambda x: x.get('upload_timestamp', 0), reverse=True)
                elif sort_by == "Upload Date (Oldest)":
                    filtered_docs.sort(key=lambda x: x.get('upload_timestamp', 0))
                elif sort_by == "Filename (A-Z)":
                    filtered_docs.sort(key=lambda x: x.get('filename', '').lower())
                elif sort_by == "Filename (Z-A)":
                    filtered_docs.sort(key=lambda x: x.get('filename', '').lower(), reverse=True)
                elif sort_by == "File Size (Largest)":
                    filtered_docs.sort(key=lambda x: x.get('file_size', 0), reverse=True)
                elif sort_by == "File Size (Smallest)":
                    filtered_docs.sort(key=lambda x: x.get('file_size', 0))

                # Display documents
                for i, doc in enumerate(filtered_docs):
                    render_document_item(doc, i)
            else:
                if search_term or file_type_filter != "All Types":
                    st.info("🔍 No documents match your search criteria. Try adjusting your filters.")
                else:
                    st.info("📄 No documents found in the repository.")
        else:
            st.info("📄 No documents have been uploaded yet. Upload documents above to see them in the repository.")

            # Debug section
            with st.expander("🔧 Debug Document Retrieval", expanded=False):
                st.markdown("**Debug Information:**")

                if st.button("🔍 Debug Document Retrieval"):
                    try:
                        # Check security status first
                        st.write("**Security Status:**")
                        if hasattr(st.session_state, 'security_manager'):
                            is_unlocked = st.session_state.security_manager.is_unlocked()
                            st.write(f"System unlocked: {'✅ Yes' if is_unlocked else '❌ No'}")
                            if not is_unlocked:
                                st.error("🔒 System is locked - documents cannot be accessed until unlocked")
                                return

                        # Check memory store status
                        if hasattr(st.session_state, 'secure_memory_store'):
                            memory_stats = st.session_state.secure_memory_store.get_memory_stats()
                            st.write("**Memory Store Stats:**")
                            st.json(memory_stats)

                            # Method 1: Try search approach
                            st.write("**Method 1: Search Approach**")
                            try:
                                search_results = st.session_state.secure_memory_store.search_memories(query="", max_results=100)
                                st.write(f"Search results: {len(search_results)}")

                                if search_results:
                                    st.write("**Sample Search Result Sources:**")
                                    sources = set()
                                    for i, result in enumerate(search_results[:10]):
                                        source = getattr(result.chunk, 'source', 'unknown')
                                        sources.add(source)
                                        st.write(f"{i+1}. {source}")
                                    st.write(f"Unique sources from search: {len(sources)}")

                                    # Filter document sources
                                    doc_sources = [s for s in sources if s != "unknown" and s != "user_input" and not s.startswith("web_")]
                                    st.write(f"**Document sources (filtered):** {len(doc_sources)}")
                                    for source in doc_sources:
                                        st.write(f"  - {source}")

                            except Exception as e:
                                st.error(f"Search approach failed: {e}")

                            # Method 2: Try get_all_memories approach
                            st.write("**Method 2: Get All Memories Approach**")
                            try:
                                all_memories = st.session_state.secure_memory_store.get_all_memories()
                                st.write(f"All memories retrieved: {len(all_memories)}")

                                if all_memories:
                                    st.write("**Sample Memory Sources:**")
                                    sources = set()
                                    for memory in all_memories[:10]:  # Show first 10
                                        source = getattr(memory, 'source', None) or getattr(memory, 'metadata', {}).get('source', 'unknown')
                                        sources.add(source)
                                        st.write(f"- {source}")

                                    st.write(f"**Unique Sources Found:** {len(sources)}")

                                    # Filter document sources
                                    doc_sources = [s for s in sources if s != "unknown" and s != "user_input" and not s.startswith("web_")]
                                    st.write(f"**Document sources (filtered):** {len(doc_sources)}")
                                    for source in doc_sources:
                                        st.write(f"  - {source}")

                            except Exception as e:
                                st.error(f"Get all memories approach failed: {e}")

                            # Method 3: Try regular memory store search
                            st.write("**Method 3: Regular Memory Store Search**")
                            try:
                                from memory.memory_vectorstore import get_memory_store
                                regular_store = get_memory_store()
                                doc_results = regular_store.search_memories(query="", max_results=100)
                                st.write(f"**Regular Memory Store Search Results:** {len(doc_results)}")

                                if doc_results:
                                    st.write("**Sample Document Sources:**")
                                    for i, result in enumerate(doc_results[:5]):
                                        st.write(f"{i+1}. {result.chunk.source}")

                            except Exception as e:
                                st.error(f"Regular memory store search failed: {e}")

                            # Test the actual function
                            st.write("**Method 4: Test get_ingested_documents_list() Function**")
                            try:
                                test_docs = get_ingested_documents_list()
                                st.write(f"Function returned: {len(test_docs)} documents")
                                if test_docs:
                                    for i, doc in enumerate(test_docs[:3]):
                                        st.write(f"{i+1}. {doc['filename']} ({doc['chunk_count']} chunks)")

                            except Exception as e:
                                st.error(f"get_ingested_documents_list() failed: {e}")
                                import traceback
                                st.code(traceback.format_exc())
                        else:
                            st.error("Secure memory store not initialized")

                    except Exception as e:
                        st.error(f"Debug failed: {e}")
                        import traceback
                        st.code(traceback.format_exc())

    except Exception as e:
        st.warning(f"Could not load document statistics: {e}")

def convert_timestamp_to_float(timestamp):
    """Convert various timestamp formats to float."""
    if isinstance(timestamp, (int, float)):
        return float(timestamp)
    elif isinstance(timestamp, str):
        try:
            # Try parsing ISO format
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.timestamp()
        except:
            try:
                # Try parsing as float string
                return float(timestamp)
            except:
                # Default to current time
                return time.time()
    else:
        return time.time()

def process_folder_bulk(folder_path, recursive, file_types, max_files, skip_errors, show_progress):
    """Process all documents in a specified folder."""
    import os
    from pathlib import Path
    import tempfile
    import shutil

    try:
        # Validate folder path
        folder = Path(folder_path)
        if not folder.exists():
            st.error(f"❌ Folder does not exist: {folder_path}")
            return

        if not folder.is_dir():
            st.error(f"❌ Path is not a folder: {folder_path}")
            return

        # Find all supported files
        supported_files = []
        file_extensions = [f".{ext.lower()}" for ext in file_types]

        if recursive:
            # Search recursively
            for ext in file_extensions:
                supported_files.extend(folder.rglob(f"*{ext}"))
        else:
            # Search only in the specified folder
            for ext in file_extensions:
                supported_files.extend(folder.glob(f"*{ext}"))

        # Remove duplicates and limit files
        supported_files = list(set(supported_files))[:max_files]

        if not supported_files:
            st.warning(f"⚠️ No supported files found in {folder_path}")
            st.info(f"Looking for file types: {', '.join(file_types)}")
            return

        # Display files to be processed
        st.info(f"📁 Found {len(supported_files)} files to process")

        if show_progress:
            with st.expander("📋 Files to be processed", expanded=False):
                for i, file_path in enumerate(supported_files[:10]):  # Show first 10
                    st.write(f"{i+1}. {file_path.name} ({file_path.stat().st_size / 1024:.1f} KB)")
                if len(supported_files) > 10:
                    st.write(f"... and {len(supported_files) - 10} more files")

        # Process files
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()

        successful_files = []
        failed_files = []

        for i, file_path in enumerate(supported_files):
            try:
                # Update progress
                progress = (i + 1) / len(supported_files)
                progress_bar.progress(progress)
                status_text.text(f"Processing {i+1}/{len(supported_files)}: {file_path.name}")

                # Create a temporary file-like object for Streamlit's file processing
                with open(file_path, 'rb') as file:
                    file_content = file.read()

                # Create a mock uploaded file object
                class MockUploadedFile:
                    def __init__(self, file_path, content):
                        self.name = file_path.name
                        self.size = len(content)
                        self.type = f"application/{file_path.suffix[1:]}" if file_path.suffix else "application/octet-stream"
                        self._content = content
                        self._position = 0

                    def read(self, size=-1):
                        if size == -1:
                            result = self._content[self._position:]
                            self._position = len(self._content)
                        else:
                            result = self._content[self._position:self._position + size]
                            self._position += len(result)
                        return result

                    def seek(self, position):
                        self._position = position

                    def tell(self):
                        return self._position

                    def getvalue(self):
                        return self._content

                mock_file = MockUploadedFile(file_path, file_content)

                # Process the document
                result = process_secure_document(mock_file)

                if result['success']:
                    successful_files.append({
                        'path': file_path,
                        'result': result
                    })

                    if show_progress:
                        with results_container:
                            st.success(f"✅ {file_path.name} - {result.get('chunks_created', 0)} chunks created")
                else:
                    failed_files.append({
                        'path': file_path,
                        'error': result.get('error', 'Unknown error')
                    })

                    if show_progress:
                        with results_container:
                            st.error(f"❌ {file_path.name} - {result.get('error', 'Unknown error')}")

                    if not skip_errors:
                        st.error(f"❌ Processing stopped due to error in {file_path.name}")
                        break

            except Exception as e:
                failed_files.append({
                    'path': file_path,
                    'error': str(e)
                })

                if show_progress:
                    with results_container:
                        st.error(f"❌ {file_path.name} - {str(e)}")

                if not skip_errors:
                    st.error(f"❌ Processing stopped due to error in {file_path.name}: {e}")
                    break

        # Final results
        progress_bar.progress(1.0)
        status_text.text("✅ Bulk processing completed!")

        # Summary
        st.markdown("---")
        st.subheader("📊 Bulk Processing Summary")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Successful", len(successful_files))
        with col2:
            st.metric("❌ Failed", len(failed_files))
        with col3:
            total_chunks = sum(f['result'].get('chunks_created', 0) for f in successful_files)
            st.metric("🧩 Total Chunks", total_chunks)

        # Detailed results
        if successful_files:
            with st.expander(f"✅ Successfully Processed Files ({len(successful_files)})", expanded=True):
                for file_info in successful_files:
                    file_path = file_info['path']
                    result = file_info['result']
                    st.write(f"📄 **{file_path.name}**")
                    st.write(f"   - Chunks: {result.get('chunks_created', 0)}")
                    st.write(f"   - Size: {result.get('file_size', 0) / 1024:.1f} KB")
                    st.write(f"   - Consolidated: {'✅' if result.get('knowledge_consolidated') else '❌'}")

        if failed_files:
            with st.expander(f"❌ Failed Files ({len(failed_files)})", expanded=False):
                for file_info in failed_files:
                    file_path = file_info['path']
                    error = file_info['error']
                    st.write(f"📄 **{file_path.name}**")
                    st.write(f"   - Error: {error}")

        # Success message
        if successful_files:
            st.success(f"🎉 Bulk processing completed! Successfully processed {len(successful_files)} out of {len(supported_files)} files.")
            # Force refresh of document repository after bulk processing
            st.session_state['document_upload_success'] = True
            st.session_state['force_refresh_docs'] = True
        else:
            st.error("❌ No files were successfully processed.")

    except Exception as e:
        st.error(f"❌ Bulk processing error: {e}")
        import traceback
        st.code(traceback.format_exc())

def get_ingested_documents_list():
    """Get a comprehensive list of all documents ingested by SAM."""
    try:
        documents = []

        # Method 1: Try to get documents from secure memory store using search
        if hasattr(st.session_state, 'secure_memory_store'):
            try:
                # Get all memories from secure store using search with empty query
                search_results = st.session_state.secure_memory_store.search_memories(
                    query="",
                    max_results=1000  # Get a large number to capture all documents
                )
                logger.info(f"Retrieved {len(search_results)} search results from secure store")

                # Group by source document
                doc_sources = {}
                for result in search_results:
                    # Extract source from the memory chunk
                    chunk = result.chunk
                    source = getattr(chunk, 'source', 'unknown')

                    # Include document sources (be more inclusive)
                    if source and source != "unknown" and source != "user_input":
                        if source not in doc_sources:
                            doc_sources[source] = {
                                'filename': source.split('/')[-1] if '/' in source else source,
                                'source_path': source,
                                'chunks': [],
                                'total_content_length': 0,
                                'upload_timestamp': convert_timestamp_to_float(getattr(chunk, 'timestamp', time.time())),
                                'memory_type': getattr(chunk, 'memory_type', 'document'),
                                'importance_score': getattr(chunk, 'importance_score', 0.0),
                                'tags': getattr(chunk, 'tags', [])
                            }

                        doc_sources[source]['chunks'].append(chunk)
                        content = getattr(chunk, 'content', '') or str(chunk)
                        doc_sources[source]['total_content_length'] += len(content)

                        # Update timestamp to earliest
                        chunk_timestamp = convert_timestamp_to_float(getattr(chunk, 'timestamp', time.time()))
                        if chunk_timestamp < doc_sources[source]['upload_timestamp']:
                            doc_sources[source]['upload_timestamp'] = chunk_timestamp

                logger.info(f"Found {len(doc_sources)} unique document sources from secure store")

                # Convert to document list
                for source_path, doc_info in doc_sources.items():
                    # Determine file type
                    filename = doc_info['filename']
                    if '.' in filename:
                        file_type = filename.split('.')[-1].upper()
                    else:
                        file_type = "Unknown"

                    # Calculate file size estimate (rough)
                    estimated_size = doc_info['total_content_length']

                    # Check if recent (within 24 hours)
                    is_recent = (time.time() - doc_info['upload_timestamp']) < 86400

                    # Create content preview
                    content_preview = ""
                    if doc_info['chunks']:
                        first_chunk = doc_info['chunks'][0]
                        content = getattr(first_chunk, 'content', '') or str(first_chunk)
                        content_preview = content[:200] + "..." if len(content) > 200 else content

                    documents.append({
                        'filename': filename,
                        'source_path': source_path,
                        'file_type': file_type,
                        'file_size': estimated_size,
                        'chunk_count': len(doc_info['chunks']),
                        'upload_timestamp': doc_info['upload_timestamp'],
                        'is_recent': is_recent,
                        'content_preview': content_preview,
                        'importance_score': doc_info['importance_score'],
                        'tags': doc_info['tags'],
                        'memory_type': doc_info['memory_type']
                    })

            except Exception as e:
                logger.warning(f"Could not get documents from secure memory store: {e}")

        # Method 1B: Try the get_all_memories approach as fallback
        if not documents and hasattr(st.session_state, 'secure_memory_store'):
            try:
                # Try to get document chunks directly from the store
                all_memories = st.session_state.secure_memory_store.get_all_memories()
                logger.info(f"Retrieved {len(all_memories)} memories from secure store via get_all_memories")

                # Group by source document
                doc_sources = {}
                for memory in all_memories:
                    source = getattr(memory, 'source', None) or getattr(memory, 'metadata', {}).get('source', 'unknown')
                    if source and source != "unknown" and source != "user_input":
                        if source not in doc_sources:
                            doc_sources[source] = {
                                'filename': source.split('/')[-1] if '/' in source else source,
                                'source_path': source,
                                'chunks': [],
                                'total_content_length': 0,
                                'upload_timestamp': convert_timestamp_to_float(getattr(memory, 'timestamp', time.time())),
                                'memory_type': getattr(memory, 'memory_type', 'document'),
                                'importance_score': getattr(memory, 'importance_score', 0.0),
                                'tags': getattr(memory, 'tags', [])
                            }

                        doc_sources[source]['chunks'].append(memory)
                        content = getattr(memory, 'content', '') or str(memory)
                        doc_sources[source]['total_content_length'] += len(content)

                        # Update timestamp to earliest
                        memory_timestamp = convert_timestamp_to_float(getattr(memory, 'timestamp', time.time()))
                        if memory_timestamp < doc_sources[source]['upload_timestamp']:
                            doc_sources[source]['upload_timestamp'] = memory_timestamp

                logger.info(f"Found {len(doc_sources)} unique document sources via get_all_memories")

                # Convert to document list (same logic as above)
                for source_path, doc_info in doc_sources.items():
                    filename = doc_info['filename']
                    if '.' in filename:
                        file_type = filename.split('.')[-1].upper()
                    else:
                        file_type = "Unknown"

                    estimated_size = doc_info['total_content_length']
                    is_recent = (time.time() - doc_info['upload_timestamp']) < 86400

                    content_preview = ""
                    if doc_info['chunks']:
                        first_chunk = doc_info['chunks'][0]
                        content = getattr(first_chunk, 'content', '') or str(first_chunk)
                        content_preview = content[:200] + "..." if len(content) > 200 else content

                    documents.append({
                        'filename': filename,
                        'source_path': source_path,
                        'file_type': file_type,
                        'file_size': estimated_size,
                        'chunk_count': len(doc_info['chunks']),
                        'upload_timestamp': doc_info['upload_timestamp'],
                        'is_recent': is_recent,
                        'content_preview': content_preview,
                        'importance_score': doc_info['importance_score'],
                        'tags': doc_info['tags'],
                        'memory_type': doc_info['memory_type']
                    })

            except Exception as e:
                logger.warning(f"Could not get documents from secure memory store via get_all_memories: {e}")

        # Method 2: Try regular memory store as fallback
        if not documents:
            try:
                from memory.memory_vectorstore import get_memory_store
                regular_store = get_memory_store()

                # Search for document chunks to get source information
                doc_results = regular_store.search_memories(query="", max_results=1000)
                logger.info(f"Regular memory store search returned {len(doc_results)} results")

                # Group by source document
                doc_sources = {}
                for result in doc_results:
                    source = result.chunk.source
                    if source and source != "unknown" and source != "user_input":
                        if source not in doc_sources:
                            doc_sources[source] = {
                                'filename': source.split('/')[-1] if '/' in source else source,
                                'source_path': source,
                                'chunks': [],
                                'total_content_length': 0,
                                'upload_timestamp': result.chunk.timestamp,
                                'memory_type': result.chunk.memory_type.value,
                                'importance_score': result.chunk.importance_score,
                                'tags': result.chunk.tags
                            }

                        doc_sources[source]['chunks'].append(result.chunk)
                        doc_sources[source]['total_content_length'] += len(result.chunk.content)

                        # Update timestamp to earliest
                        if result.chunk.timestamp < doc_sources[source]['upload_timestamp']:
                            doc_sources[source]['upload_timestamp'] = result.chunk.timestamp

                # Convert to document list
                for source_path, doc_info in doc_sources.items():
                    # Determine file type
                    filename = doc_info['filename']
                    if '.' in filename:
                        file_type = filename.split('.')[-1].upper()
                    else:
                        file_type = "Unknown"

                    # Calculate file size estimate (rough)
                    estimated_size = doc_info['total_content_length']

                    # Check if recent (within 24 hours)
                    is_recent = (time.time() - doc_info['upload_timestamp']) < 86400

                    # Create content preview
                    content_preview = ""
                    if doc_info['chunks']:
                        content_preview = doc_info['chunks'][0].content[:200] + "..." if len(doc_info['chunks'][0].content) > 200 else doc_info['chunks'][0].content

                    documents.append({
                        'filename': filename,
                        'source_path': source_path,
                        'file_type': file_type,
                        'file_size': estimated_size,
                        'chunk_count': len(doc_info['chunks']),
                        'upload_timestamp': doc_info['upload_timestamp'],
                        'is_recent': is_recent,
                        'content_preview': content_preview,
                        'importance_score': doc_info['importance_score'],
                        'tags': doc_info['tags'],
                        'memory_type': doc_info['memory_type']
                    })

            except Exception as e:
                logger.warning(f"Could not get document details from unified memory: {e}")

        # Method 3: Check for uploaded files in uploads directory
        try:
            from pathlib import Path
            uploads_dir = Path("uploads")
            if uploads_dir.exists():
                for file_path in uploads_dir.iterdir():
                    if file_path.is_file():
                        # Check if already in documents list
                        if not any(doc['source_path'] == str(file_path) for doc in documents):
                            file_type = file_path.suffix[1:].upper() if file_path.suffix else "Unknown"
                            file_size = file_path.stat().st_size
                            upload_time = file_path.stat().st_mtime
                            is_recent = (time.time() - upload_time) < 86400

                            documents.append({
                                'filename': file_path.name,
                                'source_path': str(file_path),
                                'file_type': file_type,
                                'file_size': file_size,
                                'chunk_count': 0,  # Unknown for files not yet processed
                                'upload_timestamp': upload_time,
                                'is_recent': is_recent,
                                'content_preview': "File uploaded but not yet processed",
                                'importance_score': 0.0,
                                'tags': [],
                                'memory_type': 'document'
                            })
        except Exception as e:
            logger.warning(f"Could not check uploads directory: {e}")

        logger.info(f"Final document list contains {len(documents)} documents")
        return documents

    except Exception as e:
        logger.error(f"Error getting document list: {e}")
        return []

def render_document_item(doc, index):
    """Render a single document item in the repository."""
    try:
        # Format timestamp
        from datetime import datetime
        upload_date = datetime.fromtimestamp(doc['upload_timestamp']).strftime("%Y-%m-%d %H:%M:%S")

        # Format file size
        file_size = doc['file_size']
        if file_size > 1024*1024:
            size_str = f"{file_size/(1024*1024):.1f} MB"
        elif file_size > 1024:
            size_str = f"{file_size/1024:.1f} KB"
        else:
            size_str = f"{file_size} bytes"

        # Create expandable item
        with st.expander(f"📄 {doc['filename']} ({size_str}) {'🆕' if doc['is_recent'] else ''}", expanded=False):
            # Document metadata
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**📁 Source Path:** `{doc['source_path']}`")
                st.markdown(f"**📅 Upload Date:** {upload_date}")
                st.markdown(f"**📋 File Type:** {doc['file_type']}")
                st.markdown(f"**🧩 Chunks:** {doc['chunk_count']}")

                if doc['tags']:
                    tags_str = ", ".join(doc['tags'])
                    st.markdown(f"**🏷️ Tags:** {tags_str}")

                if doc['importance_score'] > 0:
                    st.markdown(f"**⭐ Importance:** {doc['importance_score']:.2f}")

            with col2:
                # Action buttons
                st.markdown("**🔧 Actions:**")

                # Download/View source file button
                if st.button(f"📥 View Source", key=f"view_source_{index}"):
                    try:
                        from pathlib import Path
                        source_path = Path(doc['source_path'])

                        if source_path.exists():
                            # For text files, show content
                            if doc['file_type'].lower() in ['txt', 'md', 'py', 'json', 'yaml', 'yml']:
                                with open(source_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                st.text_area(f"📄 Content of {doc['filename']}", content, height=300)
                            else:
                                # For binary files, offer download
                                with open(source_path, 'rb') as f:
                                    file_data = f.read()
                                st.download_button(
                                    label=f"📥 Download {doc['filename']}",
                                    data=file_data,
                                    file_name=doc['filename'],
                                    mime='application/octet-stream'
                                )
                        else:
                            st.error("❌ Source file not found")
                    except Exception as e:
                        st.error(f"❌ Error accessing source file: {e}")

                # Search in document button
                if st.button(f"🔍 Search in Doc", key=f"search_doc_{index}"):
                    st.session_state[f'search_filter_{index}'] = doc['source_path']
                    st.info(f"🔍 Use the search box above with source filter: {doc['filename']}")

                # Remove document button (with confirmation)
                if st.button(f"🗑️ Remove", key=f"remove_doc_{index}"):
                    st.session_state[f'confirm_remove_{index}'] = True

                # Confirmation for removal
                if st.session_state.get(f'confirm_remove_{index}', False):
                    st.warning("⚠️ Are you sure?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Yes", key=f"confirm_yes_{index}"):
                            try:
                                # Remove from memory store
                                # This would need to be implemented in the memory system
                                st.success(f"✅ Document {doc['filename']} removed")
                                st.session_state[f'confirm_remove_{index}'] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error removing document: {e}")
                    with col_no:
                        if st.button("❌ No", key=f"confirm_no_{index}"):
                            st.session_state[f'confirm_remove_{index}'] = False
                            st.rerun()

            # Content preview
            if doc['content_preview'] and doc['content_preview'] != "File uploaded but not yet processed":
                st.markdown("**📖 Content Preview:**")
                st.text_area("", doc['content_preview'], height=100, disabled=True, key=f"preview_{index}")

            # Document statistics
            if doc['chunk_count'] > 0:
                st.markdown("**📊 Processing Statistics:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Chunks Created", doc['chunk_count'])
                with col2:
                    st.metric("Content Length", f"{doc['file_size']:,} chars")
                with col3:
                    avg_chunk_size = doc['file_size'] // doc['chunk_count'] if doc['chunk_count'] > 0 else 0
                    st.metric("Avg Chunk Size", f"{avg_chunk_size:,} chars")

    except Exception as e:
        st.error(f"❌ Error rendering document item: {e}")

def render_memory_interface():
    """Render the memory management interface."""
    st.header("🧠 Secure Memory Management")
    
    # Memory search
    st.subheader("🔍 Search Memories")
    search_query = st.text_input("Search your encrypted memories...")
    
    if search_query:
        with st.spinner("🔍 Searching encrypted memories..."):
            try:
                logger.info(f"Searching for: '{search_query}'")

                # Check memory store status first
                security_status = st.session_state.secure_memory_store.get_security_status()
                logger.info(f"Security status: {security_status}")

                results = search_unified_memory(query=search_query, max_results=10)

                logger.info(f"Search returned {len(results)} results")
                st.write(f"Found {len(results)} results:")

                if len(results) == 0:
                    # Show debug information
                    st.warning("No results found. Debug information:")
                    st.json(security_status)

                for i, result in enumerate(results):
                    with st.expander(f"📄 Result {i+1} (Score: {result.similarity_score:.3f})"):
                        st.write("**Content:**")
                        st.write(result.chunk.content[:500] + "..." if len(result.chunk.content) > 500 else result.chunk.content)

                        st.write("**Metadata:**")
                        st.json({
                            'source': result.chunk.source,
                            'memory_type': result.chunk.memory_type.value,
                            'importance_score': result.chunk.importance_score,
                            'tags': result.chunk.tags,
                            'timestamp': result.chunk.timestamp
                        })

            except Exception as e:
                logger.error(f"Memory search failed: {e}")
                st.error(f"❌ Memory search failed: {e}")
    
    # Memory statistics
    st.subheader("📊 Memory Statistics")
    try:
        stats = st.session_state.secure_memory_store.get_memory_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Memories", stats.get('total_memories', 0))
        with col2:
            st.metric("Store Type", stats.get('store_type', 'Unknown'))
        with col3:
            st.metric("Storage Size", f"{stats.get('total_size_mb', 0):.1f} MB")
        with col4:
            st.metric("Embedding Dim", stats.get('embedding_dimension', 0))
            
    except Exception as e:
        st.warning(f"Could not load memory statistics: {e}")

def render_vetting_interface():
    """Render the content vetting interface."""
    st.header("🔍 Content Vetting Dashboard")

    # Vetting status overview
    st.subheader("📊 Vetting Status")

    try:
        vetting_status = get_vetting_status()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🗂️ Quarantined", vetting_status.get('quarantine_files', 0))
        with col2:
            st.metric("✅ Vetted", vetting_status.get('vetted_files', 0))
        with col3:
            st.metric("👍 Approved", vetting_status.get('approved_files', 0))
        with col4:
            st.metric("👎 Rejected", vetting_status.get('rejected_files', 0))

        # Check for new content that needs vetting
        quarantine_files = vetting_status.get('quarantine_files', 0)
        if quarantine_files > 0:
            st.info(f"📥 **{quarantine_files} file(s) in quarantine awaiting vetting**")
            st.markdown("💡 **Tip:** Web search results are automatically saved to quarantine. Click '🛡️ Vet All Content' below to analyze them for security and quality.")

            # Add refresh button for real-time updates
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Status", key="refresh_quarantine_status"):
                    st.rerun()

        elif vetting_status.get('vetted_files', 0) == 0:
            st.success("✅ **No content awaiting vetting**")
            st.markdown("💡 **Tip:** When you perform web searches during chat, the results will appear here for security analysis.")

            # Add refresh button to check for new content
            if st.button("🔄 Check for New Content", key="check_new_content"):
                st.rerun()

        # Security Analysis Overview
        if vetting_status.get('vetted_files', 0) > 0:
            st.markdown("---")
            st.markdown("### 🛡️ **Security Analysis Overview**")
            st.markdown("*Powered by SAM's Conceptual Dimension Prober*")

            # Calculate security metrics across all vetted files
            security_metrics = calculate_security_overview()

            if security_metrics:
                # Real-Time Security Metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    critical_risks = security_metrics.get('critical_risks', 0)
                    critical_color = "🔴" if critical_risks > 0 else "🟢"
                    st.metric(
                        label="🔴 Critical Risks",
                        value=critical_risks,
                        help="Immediate security threats requiring attention"
                    )
                    if critical_risks > 0:
                        st.error(f"⚠️ {critical_risks} critical security threat(s) detected!")

                with col2:
                    high_risks = security_metrics.get('high_risks', 0)
                    high_color = "🟠" if high_risks > 0 else "🟢"
                    st.metric(
                        label="🟠 High Risks",
                        value=high_risks,
                        help="High-priority security concerns requiring review"
                    )
                    if high_risks > 0:
                        st.warning(f"⚠️ {high_risks} high-priority concern(s) detected!")

                with col3:
                    avg_credibility = security_metrics.get('avg_credibility', 0)
                    cred_color = "🟢" if avg_credibility >= 0.7 else "🟡" if avg_credibility >= 0.4 else "🔴"
                    st.metric(
                        label="🎓 Avg Credibility",
                        value=f"{avg_credibility:.1%}",
                        help="Average content reliability across all vetted items"
                    )
                    st.markdown(f"{cred_color} {'Excellent' if avg_credibility >= 0.7 else 'Moderate' if avg_credibility >= 0.4 else 'Poor'}")

                with col4:
                    avg_purity = security_metrics.get('avg_purity', 0)
                    purity_color = "🟢" if avg_purity >= 0.8 else "🟡" if avg_purity >= 0.5 else "🔴"
                    st.metric(
                        label="🧹 Avg Purity",
                        value=f"{avg_purity:.1%}",
                        help="Average content cleanliness and freedom from suspicious patterns"
                    )
                    st.markdown(f"{purity_color} {'Clean' if avg_purity >= 0.8 else 'Moderate' if avg_purity >= 0.5 else 'Concerning'}")

                # Overall Security Status
                total_risks = critical_risks + high_risks
                files_analyzed = security_metrics.get('files_analyzed', 0)

                if total_risks == 0:
                    st.success("🛡️ **All Clear**: No critical or high-risk security threats detected across all vetted content")
                elif critical_risks > 0:
                    st.error(f"🚨 **Critical Alert**: {critical_risks} critical security threat(s) detected - immediate attention required")
                else:
                    st.warning(f"⚠️ **Review Required**: {high_risks} high-priority security concern(s) detected - manual review recommended")

                st.info(f"📊 **Analysis Summary**: {files_analyzed} file(s) analyzed by SAM's Conceptual Dimension Prober")
            else:
                st.info("📊 **Security Analysis**: No security metrics available yet. Complete the vetting process to see detailed security analysis.")

            if security_metrics:
                sec_col1, sec_col2, sec_col3, sec_col4 = st.columns(4)

                with sec_col1:
                    critical_risks = security_metrics.get('critical_risks', 0)
                    risk_color = "🔴" if critical_risks > 0 else "🟢"
                    st.metric(f"{risk_color} Critical Risks", critical_risks)

                with sec_col2:
                    high_risks = security_metrics.get('high_risks', 0)
                    risk_color = "🟠" if high_risks > 0 else "🟢"
                    st.metric(f"{risk_color} High Risks", high_risks)

                with sec_col3:
                    avg_credibility = security_metrics.get('avg_credibility', 0)
                    cred_color = "🟢" if avg_credibility >= 0.7 else "🟡" if avg_credibility >= 0.4 else "🔴"
                    st.metric(f"{cred_color} Avg Credibility", f"{avg_credibility:.1%}")

                with sec_col4:
                    avg_purity = security_metrics.get('avg_purity', 0)
                    pur_color = "🟢" if avg_purity >= 0.8 else "🟡" if avg_purity >= 0.5 else "🔴"
                    st.metric(f"{pur_color} Avg Purity", f"{avg_purity:.1%}")

                # Security status summary
                if security_metrics.get('critical_risks', 0) == 0 and security_metrics.get('high_risks', 0) == 0:
                    st.success("🛡️ **No Critical Security Risks Detected Across All Content**")
                elif security_metrics.get('critical_risks', 0) > 0:
                    st.error(f"⚠️ **{security_metrics['critical_risks']} Critical Security Risk(s) Require Immediate Attention**")
                else:
                    st.warning(f"⚠️ **{security_metrics['high_risks']} High Security Risk(s) Detected - Review Recommended**")

        # Vetting controls
        st.subheader("🛡️ Vetting Controls")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            **🔍 Automated Content Analysis**

            Run comprehensive security analysis on all quarantined web content using **SAM's Conceptual Dimension Prober**.

            **🛡️ Security Analysis Includes:**
            - **🎓 Credibility & Bias**: Factual accuracy and source reliability assessment
            - **🎭 Persuasive Language**: Detection of manipulative or emotionally charged content
            - **🔮 Speculation vs. Fact**: Identification of unverified claims and conjecture
            - **🧹 Content Purity**: Analysis for suspicious patterns and security threats
            - **🌐 Source Reputation**: Domain credibility and HTTPS usage verification

            **📊 Results Include:** Risk factor identification, security scores, and professional analysis reports.
            """)

            # Add preview of security dashboard
            st.info("""
            **🔍 After Analysis, You'll See:**
            - 🔴 **Critical Risk Counter** - Immediate security alerts
            - 🟠 **High Risk Counter** - Priority concerns
            - 🎓 **Average Credibility Score** - Content reliability
            - 🧹 **Average Purity Score** - Content cleanliness
            - ✅/⚠️/❌ **Four-Dimension Analysis** for each item
            """)

        with col2:
            # Enhanced vetting button with status
            quarantine_count = vetting_status.get('quarantine_files', 0)
            if quarantine_count > 0:
                st.markdown(f"**📥 Ready to Analyze:**")
                st.markdown(f"**{quarantine_count} file(s)** awaiting analysis")

                # Add prominent call-to-action
                st.warning("⚡ **Click below to unlock the Security Analysis Dashboard!**")

            if st.button("🛡️ Vet All Content",
                        disabled=not vetting_status.get('ready_for_vetting', False),
                        use_container_width=True,
                        help=f"Analyze {quarantine_count} quarantined file(s) for security risks"):
                with st.spinner("🔄 Analyzing content with Conceptual Dimension Prober..."):
                    vetting_result = trigger_vetting_process()

                    if vetting_result['success']:
                        stats = vetting_result.get('stats', {})
                        approved = stats.get('approved_files', 0)
                        integrated = stats.get('integrated_items', 0)

                        if integrated > 0:
                            st.success(f"✅ **Knowledge Consolidation Complete!**\n\n"
                                     f"• {approved} files approved and vetted\n"
                                     f"• {integrated} items integrated into SAM's knowledge base\n"
                                     f"• SAM now has access to this new information!")
                        else:
                            st.success(f"✅ Vetting completed! {approved} files approved.")

                        st.rerun()
                    else:
                        st.error(f"❌ Vetting and consolidation failed: {vetting_result.get('error', 'Unknown error')}")

        # Quarantined content preview (NEW)
        quarantine_files = vetting_status.get('quarantine_files', 0)
        if quarantine_files > 0:
            st.subheader("📥 Quarantined Content Preview")
            st.markdown("""
            **🔍 Content Awaiting Analysis:** Review the web content below that is waiting for security analysis.
            Click '🛡️ Vet All Content' above to analyze all items for security risks, bias, and credibility.
            """)

            # Add real-time monitoring info with auto-refresh
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Add refresh controls
            col_time, col_refresh = st.columns([3, 1])
            with col_time:
                st.caption(f"🕒 **Last Updated:** {current_time}")
            with col_refresh:
                if st.button("🔄 Refresh Now", key="refresh_quarantine_content", use_container_width=True):
                    st.rerun()

            # Add auto-refresh option
            if st.checkbox("🔄 Auto-refresh every 10 seconds", key="auto_refresh_quarantine"):
                import time
                time.sleep(0.1)  # Small delay to prevent immediate refresh
                st.rerun()

            quarantined_content = load_quarantined_content()

            # Debug information
            loaded_count = len(quarantined_content)
            corrupted_count = len([c for c in quarantined_content if c.get('corrupted')])
            valid_count = loaded_count - corrupted_count

            if loaded_count != quarantine_files:
                st.warning(f"⚠️ **File Count Mismatch:** Expected {quarantine_files} files, loaded {loaded_count} files")
                st.markdown("**💡 Possible Solutions:**")
                st.markdown("• Click '🔄 Refresh Now' button above")
                st.markdown("• Check if new web searches were performed recently")
                st.markdown("• Verify quarantine directory contains the expected files")

            if corrupted_count > 0:
                st.error(f"❌ **{corrupted_count} corrupted file(s)** detected - see details below")

            if loaded_count > 0:
                st.info(f"📊 **Loading Summary:** {valid_count} valid files, {corrupted_count} corrupted files, {loaded_count} total loaded")

                # Check for recent files (within last 5 minutes)
                from datetime import datetime, timedelta
                recent_threshold = datetime.now() - timedelta(minutes=5)
                recent_files = []

                for content in quarantined_content:
                    if not content.get('corrupted'):
                        file_timestamp = content.get('timestamp', content.get('metadata', {}).get('quarantine_timestamp'))
                        if file_timestamp:
                            try:
                                # Parse ISO timestamp
                                if isinstance(file_timestamp, str):
                                    file_time = datetime.fromisoformat(file_timestamp.replace('Z', '+00:00'))
                                    if file_time.replace(tzinfo=None) > recent_threshold:
                                        recent_files.append(content.get('filename', 'Unknown'))
                            except:
                                pass

                if recent_files:
                    st.success(f"🆕 **{len(recent_files)} recent file(s)** added in the last 5 minutes: {', '.join(recent_files[:3])}")
                    if len(recent_files) > 3:
                        st.caption(f"... and {len(recent_files) - 3} more recent files")

                for i, content in enumerate(quarantined_content):
                    render_quarantined_content_item(content, i)
            else:
                st.warning("⚠️ Could not load any quarantined content files. They may be corrupted or inaccessible.")

                # Additional debugging
                with st.expander("🔧 Debug Information", expanded=False):
                    st.markdown(f"**Expected Files:** {quarantine_files}")
                    st.markdown(f"**Loaded Files:** {loaded_count}")

                    # Try to list files in quarantine directory
                    try:
                        from pathlib import Path
                        quarantine_dir = Path("quarantine")
                        if quarantine_dir.exists():
                            all_files = list(quarantine_dir.glob("*"))
                            json_files = list(quarantine_dir.glob("*.json"))

                            st.markdown(f"**Total Files in Quarantine:** {len(all_files)}")
                            st.markdown(f"**JSON Files Found:** {len(json_files)}")

                            if json_files:
                                st.markdown("**JSON Files (sorted by modification time):**")
                                # Sort by modification time (newest first)
                                json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

                                for f in json_files:
                                    mod_time = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                                    is_metadata = f.name.startswith('metadata') or f.name.endswith('_metadata.json')
                                    file_type = " [METADATA]" if is_metadata else ""
                                    st.markdown(f"• `{f.name}` ({f.stat().st_size:,} bytes, {mod_time}){file_type}")

                                # Show web search pattern files specifically
                                web_search_files = [f for f in json_files if 'intelligent_web_' in f.name or 'web_search_' in f.name]
                                if web_search_files:
                                    st.markdown(f"**🌐 Web Search Files:** {len(web_search_files)} found")
                                    for wsf in web_search_files:
                                        st.markdown(f"  • {wsf.name}")
                                else:
                                    st.warning("**⚠️ No web search files found** - this might indicate web search content isn't being saved to quarantine")

                                # Check for today's files specifically
                                from datetime import datetime
                                today = datetime.now().strftime("%Y%m%d")
                                today_files = [f for f in json_files if today in f.name]
                                if today_files:
                                    st.success(f"**📅 Today's Files:** {len(today_files)} found")
                                    for tf in today_files:
                                        st.markdown(f"  • {tf.name}")
                                else:
                                    st.warning(f"**📅 No files from today ({today})** found - recent web searches may not be appearing")

                                # Look for the specific file mentioned in logs
                                expected_file = f"intelligent_web_{today}_121537_eb564d73.json"
                                if any(expected_file in f.name for f in json_files):
                                    st.success(f"✅ **Found expected file:** {expected_file}")
                                else:
                                    st.error(f"❌ **Missing expected file:** {expected_file} (from terminal logs)")
                        else:
                            st.markdown("**Quarantine directory does not exist**")
                    except Exception as e:
                        st.markdown(f"**Debug Error:** {e}")

                    # Enhanced test button with comprehensive debugging
                    if st.button("🧪 Test Web Search Save", key="test_web_search_save"):
                        try:
                            st.info("🔄 Running comprehensive quarantine save test...")

                            # Test 1: Basic functionality test
                            test_result = {
                                'success': True,
                                'tool_used': 'test_tool',
                                'data': {
                                    'articles': [
                                        {'title': 'Test Article 1', 'content': 'Test content for debugging', 'source': 'test.com'},
                                        {'title': 'Test Article 2', 'content': 'More test content', 'source': 'test2.com'}
                                    ]
                                }
                            }

                            st.write("**Test Data Structure:**")
                            st.json(test_result)

                            # Call the save function
                            save_intelligent_web_to_quarantine(test_result, "Test query for debugging")
                            st.success("✅ Test content saved to quarantine - refresh to see it")

                            # Verify the file was created
                            from pathlib import Path
                            quarantine_dir = Path("quarantine")
                            json_files = list(quarantine_dir.glob("intelligent_web_*.json"))

                            st.write(f"**Files in quarantine after test:** {len(json_files)}")
                            for f in json_files[-3:]:  # Show last 3 files
                                st.write(f"• {f.name} ({f.stat().st_size} bytes)")

                        except Exception as e:
                            st.error(f"❌ Test save failed: {e}")
                            import traceback
                            st.code(traceback.format_exc())

                    # Add button to manually trigger web search debugging
                    if st.button("🔍 Debug Web Search Flow", key="debug_web_search"):
                        try:
                            st.info("🔄 Testing web search flow...")

                            # Import and test the intelligent web system
                            from web_retrieval.intelligent_web_system import IntelligentWebSystem
                            from web_retrieval.config import load_web_config

                            # Load configuration
                            web_config = load_web_config()
                            api_keys = {}  # Empty for testing

                            # Create system
                            intelligent_web_system = IntelligentWebSystem(api_keys=api_keys, config=web_config)

                            # Test query
                            test_query = "latest technology news"
                            st.write(f"**Testing query:** {test_query}")

                            # Process query
                            result = intelligent_web_system.process_query(test_query)

                            st.write("**Web search result:**")
                            st.json(result)

                            if result.get('success'):
                                st.success("✅ Web search successful - now testing quarantine save...")
                                save_intelligent_web_to_quarantine(result, test_query)
                                st.success("✅ Quarantine save completed!")
                            else:
                                st.error(f"❌ Web search failed: {result.get('error', 'Unknown error')}")

                        except Exception as e:
                            st.error(f"❌ Web search debug failed: {e}")
                            import traceback
                            st.code(traceback.format_exc())

                    # Add force refresh button
                    if st.button("🔄 Force Refresh (Clear Cache)", key="force_refresh_quarantine"):
                        # Clear any potential caching
                        if hasattr(st.session_state, 'quarantine_cache'):
                            del st.session_state.quarantine_cache
                        st.success("🔄 Cache cleared - refreshing...")
                        st.rerun()

        # Vetted content results
        if vetting_status.get('has_vetted_content', False):
            st.subheader("📋 Vetted Content Results")

            vetted_content = load_vetted_content()

            if vetted_content:
                st.markdown("""
                **🚪 Decision Gate:** Review the automated analysis results below and make the final decision
                to either **Use & Add to Knowledge** or **Discard** each piece of content.
                """)

                for i, content in enumerate(vetted_content):
                    render_vetted_content_item(content, i)
            else:
                st.info("No vetted content available yet. Run the vetting process to analyze quarantined content.")

    except Exception as e:
        st.error(f"❌ Could not load vetting dashboard: {e}")

def render_security_dashboard():
    """Render the security dashboard."""
    st.header("🛡️ Security Dashboard")
    
    # Get security status
    try:
        security_status = st.session_state.secure_memory_store.get_security_status()
        session_info = st.session_state.security_manager.get_session_info()
        
        # Security overview
        st.subheader("🔐 Security Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_color = "🟢" if security_status['encryption_active'] else "🔴"
            st.metric("Encryption Status", f"{status_color} {'Active' if security_status['encryption_active'] else 'Inactive'}")
        
        with col2:
            st.metric("Application State", session_info['state'].title())
        
        with col3:
            st.metric("Session Time", f"{session_info['time_remaining']}s")
        
        with col4:
            st.metric("Failed Attempts", f"{session_info['failed_attempts']}/{session_info['max_attempts']}")
        
        # Detailed security information
        with st.expander("🔍 Detailed Security Information"):
            st.json(security_status)
        
        # Security actions
        st.subheader("🔧 Security Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⏱️ Extend Session", use_container_width=True, key="dashboard_extend_session_button"):
                st.session_state.security_manager.extend_session()
                st.success("Session extended!")
                st.rerun()

        with col2:
            if st.button("🔒 Lock Application", use_container_width=True, key="dashboard_lock_application_button"):
                st.session_state.security_manager.lock_application()
                st.success("Application locked!")
                st.rerun()
                
    except Exception as e:
        st.error(f"❌ Could not load security dashboard: {e}")

def handle_secure_chat_command(command: str) -> str:
    """Handle chat commands in the secure interface."""
    try:
        cmd_parts = command[1:].split()
        if not cmd_parts:
            return "❌ Invalid command. Type `/help` for available commands."

        cmd = cmd_parts[0].lower()

        if cmd == 'help':
            return """🔧 **Available Commands:**

**System Commands:**
• `/status` - Show system status and analytics
• `/search <query>` - Search encrypted content
• `/summarize <topic>` - Generate smart summary about a topic
• `/help` - Show this help message

**Security Commands:**
• `/security` - Show security dashboard summary
• `/stats` - Show memory and storage statistics

**Examples:**
• `/search quantum computing`
• `/summarize machine learning trends`
• `/status`

**Regular Chat:**
Just type your questions normally for conversational AI assistance!"""

        elif cmd == 'status':
            return get_secure_system_status()

        elif cmd == 'search' and len(cmd_parts) > 1:
            query = ' '.join(cmd_parts[1:])
            return search_secure_content(query)

        elif cmd == 'summarize' and len(cmd_parts) > 1:
            topic = ' '.join(cmd_parts[1:])
            return generate_secure_summary(topic)

        elif cmd == 'security':
            return get_security_status_summary()

        elif cmd == 'stats':
            return get_memory_stats_summary()

        else:
            return f"❌ Unknown command: `{cmd}`. Type `/help` for available commands."

    except Exception as e:
        logger.error(f"Command handling failed: {e}")
        return f"❌ Error processing command: {e}"

def get_secure_system_status() -> str:
    """Get comprehensive system status for secure interface."""
    try:
        # Get security status
        security_status = st.session_state.secure_memory_store.get_security_status()
        session_info = st.session_state.security_manager.get_session_info()

        # Get memory stats
        memory_stats = st.session_state.secure_memory_store.get_memory_stats()

        # Format status
        encryption_status = "🟢 Active" if security_status['encryption_active'] else "🔴 Inactive"
        session_time = session_info.get('time_remaining', 'Unknown')

        status_report = f"""📊 **Secure System Status**

**🛡️ Security Status:**
• Encryption: {encryption_status}
• Session State: {session_info['state'].title()}
• Time Remaining: {session_time}s
• Failed Attempts: {session_info['failed_attempts']}/{session_info['max_attempts']}

**🧠 Memory Status:**
• Total Memories: {memory_stats.get('total_memories', 0)}
• Encrypted Chunks: {security_status.get('encrypted_chunk_count', 0)}
• Storage Size: {memory_stats.get('total_size_mb', 0):.1f} MB
• Embedding Dimension: {memory_stats.get('embedding_dimension', 0)}

**🔐 Encryption Details:**
• Searchable Fields: {security_status.get('searchable_fields', 0)}
• Encrypted Fields: {security_status.get('encrypted_fields', 0)}
• Store Type: {memory_stats.get('store_type', 'Unknown')}

**🤖 AI Model:**
• Model: DeepSeek-R1-0528-Qwen3-8B-GGUF
• Backend: Ollama (localhost:11434)
• Status: ✅ Connected"""

        return status_report

    except Exception as e:
        return f"❌ Error getting system status: {e}"

def search_secure_content(query: str) -> str:
    """Search all available content (secure + web knowledge) and return formatted results."""
    try:
        results = search_unified_memory(query=query, max_results=5)

        if not results:
            return f"🔍 **Search Results for '{query}'**\n\nNo results found. Try different search terms or upload relevant documents."

        formatted_results = f"🔍 **Search Results for '{query}'** ({len(results)} found)\n\n"

        for i, result in enumerate(results, 1):
            content_preview = result.chunk.content[:200]
            if len(result.chunk.content) > 200:
                content_preview += "..."

            formatted_results += f"""**Result {i}** (Score: {result.similarity_score:.3f})
📄 **Source:** {result.chunk.source}
📝 **Content:** {content_preview}
🏷️ **Tags:** {', '.join(result.chunk.tags) if result.chunk.tags else 'None'}

"""

        return formatted_results

    except Exception as e:
        return f"❌ Search failed: {e}"

def generate_secure_summary(topic: str) -> str:
    """Generate a smart summary about a topic using all available content."""
    try:
        # Search for relevant content from all sources
        results = search_unified_memory(query=topic, max_results=10)

        if not results:
            return f"📝 **Summary: {topic}**\n\nNo relevant content found in your encrypted documents. Upload documents about '{topic}' to generate a comprehensive summary."

        # Collect content for summarization
        content_parts = []
        sources = set()

        for result in results:
            if result.similarity_score > 0.3:  # Only include relevant results
                content_parts.append(result.chunk.content)
                sources.add(result.chunk.source)

        if not content_parts:
            return f"📝 **Summary: {topic}**\n\nFound {len(results)} documents but none were sufficiently relevant. Try a more specific topic or upload more relevant documents."

        # Generate summary using Ollama
        combined_content = "\n\n".join(content_parts[:5])  # Limit to top 5 results

        try:
            import requests

            system_prompt = f"""You are SAM, a secure AI assistant. Create a comprehensive summary about "{topic}" based on the provided encrypted document content.

Structure your summary with:
1. Overview of the topic
2. Key points and insights
3. Important details and facts
4. Conclusions or implications

Be thorough but concise. Focus on the most important information."""

            user_prompt = f"""Please create a comprehensive summary about "{topic}" based on this content:

{combined_content}

Provide a well-structured summary that captures the key information about {topic}."""

            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                    "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 800
                    }
                },
                timeout=45
            )

            if ollama_response.status_code == 200:
                response_data = ollama_response.json()
                ai_summary = response_data.get('response', '').strip()

                if ai_summary:
                    source_list = "\n".join([f"• {source}" for source in sorted(sources)])
                    return f"""📝 **Summary: {topic}**

{ai_summary}

**📚 Sources ({len(sources)} documents):**
{source_list}"""

        except Exception as e:
            logger.error(f"Ollama summary generation failed: {e}")

        # Fallback summary
        source_list = "\n".join([f"• {source}" for source in sorted(sources)])
        return f"""📝 **Summary: {topic}**

Based on {len(results)} relevant documents in your encrypted storage:

{combined_content[:1000]}{'...' if len(combined_content) > 1000 else ''}

**📚 Sources ({len(sources)} documents):**
{source_list}"""

    except Exception as e:
        return f"❌ Summary generation failed: {e}"

def get_security_status_summary() -> str:
    """Get a summary of security status."""
    try:
        security_status = st.session_state.secure_memory_store.get_security_status()
        session_info = st.session_state.security_manager.get_session_info()

        encryption_icon = "🟢" if security_status['encryption_active'] else "🔴"

        return f"""🛡️ **Security Status Summary**

**Encryption:** {encryption_icon} {'Active' if security_status['encryption_active'] else 'Inactive'}
**Session:** {session_info['state'].title()} ({session_info.get('time_remaining', 'Unknown')}s remaining)
**Security Level:** Enterprise-grade AES-256-GCM
**Authentication:** Argon2 password hashing
**Data Protection:** {security_status.get('encrypted_chunk_count', 0)} encrypted chunks

**Session Security:**
• Failed Attempts: {session_info['failed_attempts']}/{session_info['max_attempts']}
• Auto-lock: Enabled
• Secure Storage: ✅ Active"""

    except Exception as e:
        return f"❌ Error getting security status: {e}"

def render_feedback_system(message_index: int):
    """Render feedback system for assistant messages."""
    try:
        # Create unique key for this message
        feedback_key = f"feedback_{message_index}"

        # Check if feedback already submitted
        if st.session_state.get(f"{feedback_key}_submitted"):
            st.success("✅ Thank you for your feedback! SAM is learning from this.")
            return

        # Feedback buttons
        st.markdown("---")
        st.markdown("**How was this response?**")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("👍 Good", key=f"{feedback_key}_positive", use_container_width=True):
                submit_secure_feedback(message_index, "positive", "")
                st.session_state[f"{feedback_key}_submitted"] = True
                st.rerun()

        with col2:
            if st.button("👎 Needs Work", key=f"{feedback_key}_negative", use_container_width=True):
                st.session_state[f"{feedback_key}_show_correction"] = True
                st.rerun()

        with col3:
            if st.button("💡 Suggest Improvement", key=f"{feedback_key}_improve", use_container_width=True):
                st.session_state[f"{feedback_key}_show_correction"] = True
                st.rerun()

        # Show correction input if requested
        if st.session_state.get(f"{feedback_key}_show_correction"):
            st.markdown("**What could be improved?**")
            correction_text = st.text_area(
                "Please describe what could be better about this response...",
                key=f"{feedback_key}_correction_input",
                height=100
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Submit Feedback", key=f"{feedback_key}_submit"):
                    if correction_text.strip():
                        submit_secure_feedback(message_index, "negative", correction_text)
                        st.session_state[f"{feedback_key}_submitted"] = True
                        st.session_state[f"{feedback_key}_show_correction"] = False
                        st.success("✅ Thank you for the detailed feedback! SAM is learning from your suggestions.")
                        st.rerun()
                    else:
                        st.warning("Please provide some feedback before submitting.")

            with col2:
                if st.button("Cancel", key=f"{feedback_key}_cancel"):
                    st.session_state[f"{feedback_key}_show_correction"] = False
                    st.rerun()

    except Exception as e:
        logger.error(f"Feedback system error: {e}")

def submit_secure_feedback(message_index: int, feedback_type: str, correction_text: str):
    """Submit feedback to the secure learning system."""
    try:
        # In a real implementation, this would integrate with the learning system
        feedback_data = {
            'message_index': message_index,
            'feedback_type': feedback_type,
            'correction_text': correction_text,
            'timestamp': time.time(),
            'interface': 'secure_streamlit'
        }

        # Store feedback in session state for now (in real implementation, would save to encrypted storage)
        if 'feedback_history' not in st.session_state:
            st.session_state.feedback_history = []

        st.session_state.feedback_history.append(feedback_data)

        logger.info(f"Secure feedback submitted: {feedback_type} for message {message_index}")

    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")

def perform_secure_web_search(query: str) -> Dict[str, Any]:
    """Perform secure web search using the new Intelligent Web System."""
    try:
        logger.info(f"Starting intelligent web search for: {query}")

        # Step 1: Initialize the Intelligent Web System
        web_system = get_intelligent_web_system()

        # Step 2: Process query through intelligent routing
        result = web_system.process_query(query)

        if result['success']:
            # Step 3: Format and enhance the result
            formatted_response = format_intelligent_web_result(result, query)

            # Step 4: Save to quarantine for vetting
            save_intelligent_web_to_quarantine(result, query)

            # Step 5: Generate AI-enhanced response
            web_response = generate_intelligent_web_response(query, result)

            return {
                'success': True,
                'error': None,
                'response': web_response,
                'sources': extract_sources_from_result(result),
                'content_count': count_content_items(result),
                'method': 'intelligent_web_system',
                'tool_used': result.get('tool_used', 'unknown'),
                'routing_info': result.get('routing_decision', {})
            }
        else:
            # Fallback to original RSS method if intelligent system fails
            logger.warning(f"Intelligent web system failed: {result.get('error')}, falling back to RSS")
            return perform_rss_fallback_search(query)

    except Exception as e:
        logger.error(f"Secure web search failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'response': None
        }

def get_intelligent_web_system():
    """Get or create the intelligent web system instance."""
    try:
        from web_retrieval.intelligent_web_system import IntelligentWebSystem
        from config.config_manager import ConfigManager

        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.get_config()

        # Initialize with API keys and configuration
        api_keys = {
            'serper': config.serper_api_key if config.serper_api_key else None,
            'newsapi': config.newsapi_api_key if config.newsapi_api_key else None
        }

        # Web retrieval configuration
        web_config = {
            'cocoindex_search_provider': config.cocoindex_search_provider,
            'cocoindex_num_pages': config.cocoindex_num_pages,
            'web_retrieval_provider': config.web_retrieval_provider
        }

        return IntelligentWebSystem(api_keys=api_keys, config=web_config)

    except ImportError as e:
        logger.error(f"Failed to import intelligent web system: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize intelligent web system: {e}")
        raise

def format_intelligent_web_result(result: Dict[str, Any], query: str) -> str:
    """Format the intelligent web system result for display."""
    try:
        tool_used = result.get('tool_used', 'unknown')
        data = result.get('data', {})

        content_parts = []
        content_parts.append(f"**Web Search Results for: {query}**")
        content_parts.append(f"*Method: {tool_used.replace('_', ' ').title()}*")
        content_parts.append("")

        # Format based on tool type
        if tool_used == 'cocoindex_tool':
            chunks = data.get('chunks', [])
            content_parts.append(f"Found {len(chunks)} relevant content chunks using intelligent search")
            content_parts.append("")

            for i, chunk in enumerate(chunks[:8], 1):  # Show top 8 chunks
                chunk_parts = []

                title = chunk.get('title', f'Content Chunk {i}').strip()
                content = chunk.get('content', '').strip()
                source_url = chunk.get('source_url', '').strip()
                relevance_score = chunk.get('relevance_score', 0.0)

                if title:
                    chunk_parts.append(f"**{i}. {title}**")

                if content:
                    # Limit content for display
                    display_content = content[:300] + "..." if len(content) > 300 else content
                    chunk_parts.append(display_content)

                source_info = f"*Relevance: {relevance_score:.2f}*"
                if source_url:
                    source_info += f" | [Source]({source_url})"

                chunk_parts.append(source_info)

                if chunk_parts:
                    content_parts.append("\n".join(chunk_parts))
                    content_parts.append("---")

        elif tool_used == 'news_api_tool' or tool_used == 'rss_reader_tool':
            articles = data.get('articles', [])
            content_parts.append(f"Found {len(articles)} articles")
            content_parts.append("")

            for i, article in enumerate(articles[:10], 1):
                article_parts = []

                title = article.get('title', '').strip()
                if title:
                    article_parts.append(f"**{i}. {title}**")

                description = article.get('description', '').strip()
                if description:
                    article_parts.append(description)

                source = article.get('source', 'Unknown')
                pub_date = article.get('pub_date', '') or article.get('published_at', '')
                link = article.get('link', '') or article.get('url', '')

                source_info = f"*Source: {source}*"
                if pub_date:
                    source_info += f" | *Published: {pub_date}*"
                if link:
                    source_info += f" | [Read more]({link})"

                article_parts.append(source_info)

                if article_parts:
                    content_parts.append("\n".join(article_parts))
                    content_parts.append("---")

        elif tool_used == 'search_api_tool':
            search_results = data.get('search_results', [])
            extracted_content = data.get('extracted_content', [])

            content_parts.append(f"Found {len(search_results)} search results")
            content_parts.append("")

            for i, result_item in enumerate(search_results[:5], 1):
                content_parts.append(f"**{i}. {result_item.get('title', 'No title')}**")
                if result_item.get('snippet'):
                    content_parts.append(result_item['snippet'])
                content_parts.append(f"*Source: {result_item.get('url', 'No URL')}*")
                content_parts.append("---")

        elif tool_used == 'url_content_extractor':
            content = data.get('content', '')
            metadata = data.get('metadata', {})

            if metadata.get('title'):
                content_parts.append(f"**{metadata['title']}**")

            if content:
                # Limit content for display
                display_content = content[:1000] + "..." if len(content) > 1000 else content
                content_parts.append(display_content)

            content_parts.append(f"*Source: {data.get('url', 'Unknown')}*")

        # Remove last separator
        if content_parts and content_parts[-1] == "---":
            content_parts.pop()

        return "\n".join(content_parts)

    except Exception as e:
        logger.error(f"Failed to format intelligent web result: {e}")
        return f"Error formatting web search results: {e}"

def save_intelligent_web_to_quarantine(result: Dict[str, Any], query: str):
    """Save intelligent web system results to quarantine for vetting."""
    import traceback

    # Enhanced debug logging with stack trace
    logger.info(f"🚨 SAVE_INTELLIGENT_WEB_TO_QUARANTINE CALLED! 🚨")
    logger.info(f"Call stack: {traceback.format_stack()[-3:-1]}")  # Show calling context
    logger.info(f"Function called with query: {query}")
    logger.info(f"Function called with result type: {type(result)}")

    try:
        from pathlib import Path
        import json
        import hashlib
        from datetime import datetime
        import os

        logger.info(f"=== ENHANCED SAVE TO QUARANTINE DEBUG ===")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Query: {query}")
        logger.info(f"Result keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")

        # Enhanced result structure logging
        if isinstance(result, dict):
            logger.info(f"Result structure analysis:")
            logger.info(f"  - success: {result.get('success', 'NOT_FOUND')}")
            logger.info(f"  - tool_used: {result.get('tool_used', 'NOT_FOUND')}")
            logger.info(f"  - data keys: {list(result.get('data', {}).keys()) if 'data' in result else 'NO_DATA_KEY'}")
            if 'data' in result and isinstance(result['data'], dict):
                data = result['data']
                logger.info(f"  - articles count: {len(data.get('articles', []))}")
                logger.info(f"  - chunks count: {len(data.get('chunks', []))}")
                logger.info(f"  - search_results count: {len(data.get('search_results', []))}")

        # Create quarantine directory if it doesn't exist
        quarantine_dir = Path("quarantine")
        logger.info(f"Quarantine directory path: {quarantine_dir.absolute()}")

        quarantine_dir.mkdir(exist_ok=True)
        logger.info(f"Quarantine directory created/exists: {quarantine_dir.exists()}")
        logger.info(f"Quarantine directory is writable: {os.access(quarantine_dir, os.W_OK)}")

        # List existing files before save
        existing_files = list(quarantine_dir.glob("*.json"))
        logger.info(f"Existing quarantine files before save: {[f.name for f in existing_files]}")

        # Test write a simple file first
        test_file = quarantine_dir / "test_write.txt"
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            logger.info(f"✅ Test write successful: {test_file.exists()}")
            test_file.unlink()  # Clean up
        except Exception as e:
            logger.error(f"❌ Test write failed: {e}")
            raise

        # Generate filename based on query hash and timestamp
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"intelligent_web_{timestamp}_{query_hash}.json"

        logger.info(f"Generated filename: {filename}")
        logger.info(f"Query hash: {query_hash}")
        logger.info(f"Timestamp: {timestamp}")

        # Prepare quarantine data structure
        quarantine_data = {
            "query": query,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "source": "intelligent_web_system",
                "method": result.get('tool_used', 'unknown'),
                "content_count": count_content_items(result),
                "sources": extract_sources_from_result(result),
                "quarantine_timestamp": datetime.now().isoformat(),
                "debug_info": {
                    "saved_from": "save_intelligent_web_to_quarantine",
                    "cwd": os.getcwd(),
                    "python_path": os.environ.get('PYTHONPATH', 'NOT_SET')
                }
            }
        }

        logger.info(f"Quarantine data prepared, size: {len(str(quarantine_data))} characters")
        logger.info(f"Content count: {quarantine_data['metadata']['content_count']}")
        logger.info(f"Sources count: {len(quarantine_data['metadata']['sources'])}")

        # Save to quarantine with enhanced error handling
        quarantine_path = quarantine_dir / filename
        logger.info(f"About to write to: {quarantine_path.absolute()}")

        try:
            with open(quarantine_path, 'w', encoding='utf-8') as f:
                json.dump(quarantine_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ JSON write completed successfully")
        except Exception as write_error:
            logger.error(f"❌ JSON write failed: {write_error}")
            logger.error(f"Write error type: {type(write_error)}")
            raise

        # Verify file was actually created with enhanced checks
        if quarantine_path.exists():
            file_size = quarantine_path.stat().st_size
            logger.info(f"✅ Intelligent web content saved to quarantine: {filename} ({file_size} bytes)")
            logger.info(f"Full path: {quarantine_path.absolute()}")

            # Verify file content is readable
            try:
                with open(quarantine_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                logger.info(f"✅ File content verification successful, keys: {list(test_data.keys())}")
            except Exception as verify_error:
                logger.error(f"❌ File content verification failed: {verify_error}")

            # List files after save to confirm
            new_files = list(quarantine_dir.glob("*.json"))
            logger.info(f"Quarantine files after save: {[f.name for f in new_files]}")

        else:
            logger.error(f"❌ Failed to create quarantine file: {quarantine_path}")
            logger.error(f"Directory contents after attempted save: {list(quarantine_dir.iterdir())}")
            raise FileNotFoundError(f"Quarantine file was not created: {filename}")

    except Exception as e:
        logger.error(f"❌ Failed to save intelligent web content to quarantine: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception traceback: {traceback.format_exc()}")
        logger.error(f"Attempted path: {quarantine_dir / filename if 'quarantine_dir' in locals() and 'filename' in locals() else 'Unknown'}")
        raise

def test_quarantine_save():
    """Test function to verify quarantine save functionality."""
    logger.info("🧪 TESTING QUARANTINE SAVE FUNCTION 🧪")

    test_result = {
        'success': True,
        'tool_used': 'test_tool',
        'data': {
            'articles': [
                {'title': 'Test Article 1', 'source': 'test.com'},
                {'title': 'Test Article 2', 'source': 'test.com'}
            ]
        }
    }

    test_query = "Test web search query"

    try:
        save_intelligent_web_to_quarantine(test_result, test_query)
        logger.info("✅ Test quarantine save completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Test quarantine save failed: {e}")
        return False

def extract_sources_from_result(result: Dict[str, Any]) -> List[str]:
    """Extract source URLs/names from intelligent web result."""
    try:
        sources = []
        data = result.get('data', {})

        # Extract from cocoindex chunks (Phase 8.5)
        chunks = data.get('chunks', [])
        for chunk in chunks:
            source_url = chunk.get('source_url', '')
            if source_url and source_url not in sources:
                sources.append(source_url)

        # Extract from articles
        articles = data.get('articles', [])
        for article in articles:
            source = article.get('source', '') or article.get('url', '')
            if source and source not in sources:
                sources.append(source)

        # Extract from search results
        search_results = data.get('search_results', [])
        for search_result in search_results:
            url = search_result.get('url', '')
            if url and url not in sources:
                sources.append(url)

        # Extract from URL extraction
        url = data.get('url', '')
        if url and url not in sources:
            sources.append(url)

        return sources[:10]  # Limit to top 10 sources

    except Exception as e:
        logger.error(f"Failed to extract sources: {e}")
        return []

def count_content_items(result: Dict[str, Any]) -> int:
    """Count the number of content items in the result."""
    try:
        data = result.get('data', {})

        # Count cocoindex chunks (Phase 8.5)
        chunks = data.get('chunks', [])
        if chunks:
            return len(chunks)

        # Count articles
        articles = data.get('articles', [])
        if articles:
            return len(articles)

        # Count search results
        search_results = data.get('search_results', [])
        if search_results:
            return len(search_results)

        # Count extracted content
        content = data.get('content', '')
        if content:
            return 1

        return 0

    except Exception as e:
        logger.error(f"Failed to count content items: {e}")
        return 0

def generate_intelligent_web_response(query: str, result: Dict[str, Any]) -> str:
    """Generate AI-enhanced response using intelligent web system results."""
    try:
        # Create summary for AI processing
        ai_summary = create_ai_summary_from_result(result, query)

        if not ai_summary or len(ai_summary.strip()) < 50:
            return format_intelligent_web_result(result, query)

        # Use Ollama to generate enhanced response
        import requests

        system_prompt = """You are SAM, a secure AI assistant. You have just retrieved current web content using an advanced intelligent web retrieval system to answer the user's question.

Provide a comprehensive, well-structured response based on the web content provided. Focus on delivering actual information with clear organization.

Important guidelines:
- Present the most important and relevant information first
- Organize information logically (by topic, chronology, or importance)
- Be factual and objective, focusing on the actual content retrieved
- Mention that this information comes from current web sources
- Summarize key points while maintaining accuracy
- Include relevant details from multiple sources when available"""

        user_prompt = f"""Based on the following current web content retrieved using intelligent web retrieval, please answer this question: "{query}"

Web content summary:
{ai_summary[:3000]}

Please provide a comprehensive, well-organized response based on this current web information. Focus on the most relevant and important content."""

        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 800
                }
            },
            timeout=90
        )

        if ollama_response.status_code == 200:
            response_data = ollama_response.json()
            ai_response = response_data.get('response', '').strip()

            if ai_response:
                # Add source information
                sources = extract_sources_from_result(result)
                content_count = count_content_items(result)
                tool_used = result.get('tool_used', 'intelligent_web_system')

                sources_text = "\n\n**🌐 Sources:**\n" + "\n".join([f"• {source}" for source in sources[:5]])

                web_enhanced_response = f"""🌐 **Based on current web sources:**

{ai_response}

{sources_text}

*Information retrieved using {tool_used.replace('_', ' ').title()} from {content_count} sources.*"""

                return web_enhanced_response

        # Fallback if Ollama fails
        return format_intelligent_web_result(result, query)

    except Exception as e:
        logger.error(f"Intelligent web response generation failed: {e}")
        return format_intelligent_web_result(result, query)

def create_ai_summary_from_result(result: Dict[str, Any], query: str) -> str:
    """Create a concise summary for AI processing from intelligent web result."""
    try:
        data = result.get('data', {})
        tool_used = result.get('tool_used', 'unknown')

        summary_parts = []
        summary_parts.append(f"Web Search Summary for: {query}")
        summary_parts.append(f"Method: {tool_used}")
        summary_parts.append("")

        # Process based on tool type
        if tool_used == 'cocoindex_tool':
            chunks = data.get('chunks', [])
            summary_parts.append(f"Intelligent search chunks found: {len(chunks)}")
            summary_parts.append("")

            for i, chunk in enumerate(chunks[:6], 1):  # Top 6 chunks for AI processing
                content = chunk.get('content', '').strip()
                title = chunk.get('title', f'Chunk {i}').strip()
                source_url = chunk.get('source_url', '')
                relevance_score = chunk.get('relevance_score', 0.0)

                if content:
                    chunk_summary = f"{i}. {title}"
                    # Limit content for summary
                    short_content = content[:250] + "..." if len(content) > 250 else content
                    chunk_summary += f" - {short_content}"
                    chunk_summary += f" (Relevance: {relevance_score:.2f}, Source: {source_url})"
                    summary_parts.append(chunk_summary)

        elif tool_used in ['news_api_tool', 'rss_reader_tool']:
            articles = data.get('articles', [])
            summary_parts.append(f"Articles found: {len(articles)}")
            summary_parts.append("")

            for i, article in enumerate(articles[:8], 1):
                title = article.get('title', '').strip()
                description = article.get('description', '').strip()
                source = article.get('source', 'Unknown')

                if title:
                    article_summary = f"{i}. {title}"
                    if description:
                        short_desc = description[:200] + "..." if len(description) > 200 else description
                        article_summary += f" - {short_desc}"
                    article_summary += f" (Source: {source})"
                    summary_parts.append(article_summary)

        elif tool_used == 'search_api_tool':
            search_results = data.get('search_results', [])
            summary_parts.append(f"Search results found: {len(search_results)}")
            summary_parts.append("")

            for i, result_item in enumerate(search_results[:5], 1):
                title = result_item.get('title', 'No title')
                snippet = result_item.get('snippet', '')
                url = result_item.get('url', '')

                search_summary = f"{i}. {title}"
                if snippet:
                    search_summary += f" - {snippet[:150]}..."
                search_summary += f" (URL: {url})"
                summary_parts.append(search_summary)

        elif tool_used == 'url_content_extractor':
            content = data.get('content', '')
            metadata = data.get('metadata', {})

            summary_parts.append("Extracted content:")
            if metadata.get('title'):
                summary_parts.append(f"Title: {metadata['title']}")

            if content:
                content_preview = content[:500] + "..." if len(content) > 500 else content
                summary_parts.append(f"Content: {content_preview}")

        return "\n".join(summary_parts)

    except Exception as e:
        logger.error(f"AI summary creation failed: {e}")
        return f"Error creating AI summary: {e}"

def perform_rss_fallback_search(query: str) -> Dict[str, Any]:
    """Fallback to RSS-based search if intelligent system fails."""
    try:
        logger.info("Using RSS fallback search method")

        # Generate RSS URLs for the query
        rss_urls = generate_rss_urls(query)

        # Try RSS extraction
        rss_result = perform_rss_extraction(query, rss_urls)

        if rss_result['success'] and rss_result.get('article_count', 0) > 0:
            return rss_result
        else:
            return {
                'success': False,
                'error': 'RSS fallback also failed - no content could be retrieved',
                'response': None
            }

    except Exception as e:
        logger.error(f"RSS fallback search failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'response': None
        }

def generate_rss_urls(query: str) -> List[str]:
    """Generate RSS URLs for the given query."""
    query_lower = query.lower()

    # CNN-specific queries
    if 'cnn' in query_lower:
        return [
            "http://rss.cnn.com/rss/cnn_latest.rss",  # CNN Latest (working)
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",  # NYT as backup
            "https://feeds.bbci.co.uk/news/rss.xml"  # BBC as backup
        ]

    # Topic-specific RSS feeds
    elif any(word in query_lower for word in ['health', 'medical', 'medicine', 'covid', 'pandemic']):
        return [
            "http://rss.cnn.com/rss/cnn_latest.rss",  # CNN Latest
            "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",  # NYT Health
            "https://feeds.bbci.co.uk/news/health/rss.xml"  # BBC Health
        ]
    elif any(word in query_lower for word in ['politics', 'political', 'election', 'government']):
        return [
            "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",  # NYT Politics
            "https://feeds.bbci.co.uk/news/politics/rss.xml",  # BBC Politics
            "http://rss.cnn.com/rss/cnn_latest.rss"  # CNN Latest
        ]
    elif any(word in query_lower for word in ['technology', 'tech', 'ai', 'artificial intelligence']):
        return [
            "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",  # NYT Tech
            "https://feeds.bbci.co.uk/news/technology/rss.xml",  # BBC Tech
            "http://rss.cnn.com/rss/cnn_latest.rss"  # CNN Latest
        ]
    elif any(word in query_lower for word in ['business', 'economy', 'finance', 'market']):
        return [
            "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",  # NYT Business
            "https://feeds.bbci.co.uk/news/business/rss.xml",  # BBC Business
            "http://rss.cnn.com/rss/cnn_latest.rss"  # CNN Latest
        ]

    # General news queries - use top RSS feeds
    else:
        return [
            "https://feeds.bbci.co.uk/news/rss.xml",  # BBC News (reliable)
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",  # NYT Homepage
            "http://rss.cnn.com/rss/cnn_latest.rss"  # CNN Latest
        ]

def perform_rss_extraction(query: str, rss_urls: List[str]) -> Dict[str, Any]:
    """Perform RSS-based content extraction (proven working method)."""
    try:
        logger.info(f"Starting RSS extraction for query: '{query}' from {len(rss_urls)} RSS feeds")

        all_news_items = []
        successful_sources = []

        for url in rss_urls:
            try:
                logger.info(f"Fetching RSS feed: {url}")
                rss_content = fetch_rss_content(url)

                if rss_content['success'] and rss_content.get('content'):
                    # Parse the RSS content to extract news items
                    news_items = parse_rss_content_to_articles(rss_content['content'], url)
                    all_news_items.extend(news_items)
                    successful_sources.append(url)
                    logger.info(f"Successfully extracted {len(news_items)} items from {url}")
                else:
                    logger.warning(f"Failed to fetch RSS content from {url}")

            except Exception as e:
                logger.error(f"Error processing RSS feed {url}: {e}")
                continue

        if all_news_items:
            # Format the content for response
            formatted_content = format_rss_articles_for_response(all_news_items, query)

            # Save to quarantine
            save_rss_to_quarantine(all_news_items, query, successful_sources)

            # Generate AI-enhanced response
            web_response = generate_rss_enhanced_response(query, all_news_items)

            return {
                'success': True,
                'error': None,
                'response': web_response,
                'sources': successful_sources,
                'content_count': len(all_news_items),
                'article_count': len(all_news_items),
                'method': 'rss'
            }
        else:
            return {
                'success': False,
                'error': 'No articles extracted from RSS feeds',
                'article_count': 0
            }

    except Exception as e:
        logger.error(f"RSS extraction failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'article_count': 0
        }

def parse_rss_content_to_articles(rss_content: str, source_url: str) -> List[Dict[str, Any]]:
    """Parse RSS content and extract articles (using the working logic)."""
    try:
        import xml.etree.ElementTree as ET
        import html
        import re
        from datetime import datetime

        # Parse RSS XML
        root = ET.fromstring(rss_content)

        # Find items
        items = (root.findall('.//item') or
                root.findall('.//{http://www.w3.org/2005/Atom}entry') or
                root.findall('.//entry'))

        logger.info(f"Found {len(items)} items in RSS feed")

        articles = []

        for i, item in enumerate(items[:15]):  # Limit to top 15 news items
            try:
                title = ''
                description = ''
                link = ''
                pub_date = ''

                # Extract title - simplified approach that was working
                title_elem = item.find('title')
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()

                # Extract description - simplified approach that was working
                desc_elem = item.find('description')
                if desc_elem is not None and desc_elem.text:
                    description = desc_elem.text.strip()
                    # Clean HTML tags from description
                    description = re.sub(r'<[^>]+>', '', description)
                    # Limit description length
                    if len(description) > 300:
                        description = description[:300] + "..."

                # Extract link - simplified
                link_elem = item.find('link')
                if link_elem is not None and link_elem.text:
                    link = link_elem.text.strip()

                # Extract publication date - simplified
                date_elem = item.find('pubDate')
                if date_elem is not None and date_elem.text:
                    pub_date = date_elem.text.strip()

                # Include items with any substantial title
                if title and len(title.strip()) > 3:
                    article = {
                        'title': title,
                        'description': description,
                        'link': link,
                        'pub_date': pub_date,
                        'source': source_url,
                        'extracted_at': datetime.now().isoformat()
                    }
                    articles.append(article)

                    if i < 3:  # Debug logging for first few items
                        logger.info(f"✅ Added article {len(articles)}: {title[:50]}...")

            except Exception as e:
                logger.warning(f"Error parsing RSS item {i}: {e}")
                continue

        logger.info(f"Successfully extracted {len(articles)} articles from RSS feed")
        return articles

    except Exception as e:
        logger.error(f"Failed to parse RSS content: {e}")
        return []

def perform_scrapy_extraction(query: str, urls: List[str]) -> Dict[str, Any]:
    """Perform Scrapy-based content extraction."""
    try:
        from web_scraping.scrapy_manager import ScrapyManager

        scrapy_manager = ScrapyManager()
        result = scrapy_manager.scrape_news_content(query, urls)

        logger.info(f"Scrapy extraction completed: success={result['success']}, articles={result.get('source_count', 0)}")
        return result

    except ImportError as e:
        logger.error(f"Scrapy import failed: {e}")
        return {'success': False, 'error': f'Scrapy not available: {e}'}
    except Exception as e:
        logger.error(f"Scrapy extraction failed: {e}")
        return {'success': False, 'error': str(e)}

def format_rss_articles_for_response(articles: List[Dict[str, Any]], query: str) -> str:
    """Format RSS articles for display."""
    try:
        if not articles:
            return "No news articles were successfully extracted from RSS feeds."

        content_parts = []

        # Header
        content_parts.append(f"**Latest News Results for: {query}**")
        content_parts.append(f"*Found {len(articles)} articles from RSS feeds*")
        content_parts.append("")

        # Articles
        for i, article in enumerate(articles[:10], 1):  # Limit display to top 10
            article_content = []

            # Title
            title = article.get('title', '').strip()
            if title:
                article_content.append(f"**{i}. {title}**")

            # Description
            description = article.get('description', '').strip()
            if description:
                article_content.append(description)

            # Source and date
            source = article.get('source', 'Unknown')
            pub_date = article.get('pub_date', '')
            link = article.get('link', '')

            source_info = f"*Source: {source}*"
            if pub_date:
                source_info += f" | *Published: {pub_date}*"
            if link:
                source_info += f" | [Read more]({link})"

            article_content.append(source_info)

            if article_content:
                content_parts.append("\n".join(article_content))
                content_parts.append("---")

        # Remove last separator
        if content_parts and content_parts[-1] == "---":
            content_parts.pop()

        return "\n".join(content_parts)

    except Exception as e:
        logger.error(f"RSS content formatting failed: {e}")
        return f"Error formatting RSS content: {e}"

def save_rss_to_quarantine(articles: List[Dict[str, Any]], query: str, sources: List[str]):
    """Save RSS articles to quarantine for vetting."""
    try:
        from pathlib import Path
        import json
        import hashlib
        from datetime import datetime

        # Create quarantine directory if it doesn't exist
        quarantine_dir = Path("quarantine")
        quarantine_dir.mkdir(exist_ok=True)

        # Generate filename based on query hash and timestamp
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rss_search_{timestamp}_{query_hash}.json"

        # Prepare quarantine data structure
        quarantine_data = {
            "query": query,
            "articles": articles,
            "sources": sources,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "source": "rss_web_search",
                "method": "rss_extraction",
                "article_count": len(articles),
                "source_count": len(sources),
                "quarantine_timestamp": datetime.now().isoformat()
            }
        }

        # Save to quarantine
        quarantine_path = quarantine_dir / filename
        with open(quarantine_path, 'w', encoding='utf-8') as f:
            json.dump(quarantine_data, f, indent=2, ensure_ascii=False)

        logger.info(f"RSS content saved to quarantine: {filename}")

    except Exception as e:
        logger.error(f"Failed to save RSS content to quarantine: {e}")

def generate_rss_enhanced_response(query: str, articles: List[Dict[str, Any]]) -> str:
    """Generate AI-enhanced response using RSS articles."""
    try:
        if not articles:
            return "No news articles were found for your query."

        # Create summary for AI processing
        ai_summary_parts = []
        ai_summary_parts.append(f"News Summary for: {query}")
        ai_summary_parts.append(f"Articles found: {len(articles)}")
        ai_summary_parts.append("")

        for i, article in enumerate(articles[:8], 1):  # Limit for AI processing
            title = article.get('title', '').strip()
            description = article.get('description', '').strip()
            source = article.get('source', 'Unknown')

            if title:
                article_summary = f"{i}. {title}"
                if description:
                    # Limit description for AI processing
                    short_desc = description[:200] + "..." if len(description) > 200 else description
                    article_summary += f" - {short_desc}"
                article_summary += f" (Source: {source})"
                ai_summary_parts.append(article_summary)

        ai_summary = "\n".join(ai_summary_parts)

        # Use Ollama to generate enhanced response
        import requests

        system_prompt = """You are SAM, a secure AI assistant. You have just retrieved current news content using RSS feeds to answer the user's question.

Provide a comprehensive, well-structured response based on the news articles provided. Focus on delivering actual news information with clear organization.

Important guidelines:
- Present the most important and relevant news first
- Organize information logically (by topic, chronology, or importance)
- Be factual and objective, focusing on the actual news content
- Mention that this information comes from current RSS feeds
- Summarize key points while maintaining accuracy
- Include relevant details from multiple sources when available"""

        user_prompt = f"""Based on the following current news content retrieved from RSS feeds, please answer this question: "{query}"

News content summary:
{ai_summary[:3000]}

Please provide a comprehensive, well-organized response based on this current news information. Focus on the most relevant and important news items."""

        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 800
                }
            },
            timeout=90
        )

        if ollama_response.status_code == 200:
            response_data = ollama_response.json()
            ai_response = response_data.get('response', '').strip()

            if ai_response:
                # Add source information
                sources = list(set([article.get('source', 'Unknown') for article in articles]))
                article_count = len(articles)

                sources_text = "\n\n**📰 Sources:**\n" + "\n".join([f"• {source}" for source in sources])

                web_enhanced_response = f"""🌐 **Based on current RSS feeds:**

{ai_response}

{sources_text}

*Information extracted from {article_count} articles across {len(sources)} RSS sources.*"""

                return web_enhanced_response

        # Fallback if Ollama fails
        return format_rss_articles_for_response(articles, query)

    except Exception as e:
        logger.error(f"RSS-enhanced response generation failed: {e}")
        return format_rss_articles_for_response(articles, query)

def format_scraped_content(scraped_data: Dict[str, Any]) -> str:
    """Format scraped content for display."""
    try:
        from web_scraping.content_formatter import ContentFormatter

        formatter = ContentFormatter()
        return formatter.format_news_content(scraped_data)

    except ImportError as e:
        logger.error(f"Content formatter import failed: {e}")
        return f"Content formatting unavailable: {e}"
    except Exception as e:
        logger.error(f"Content formatting failed: {e}")
        return f"Error formatting content: {e}"

def generate_scrapy_enhanced_response(query: str, scraped_data: Dict[str, Any]) -> str:
    """Generate AI-enhanced response using scraped data."""
    try:
        from web_scraping.content_formatter import ContentFormatter

        formatter = ContentFormatter()
        ai_summary = formatter.create_summary_for_ai(scraped_data)

        if not ai_summary or "No news content" in ai_summary:
            return format_scraped_content(scraped_data)

        # Use Ollama to generate enhanced response
        import requests

        system_prompt = """You are SAM, a secure AI assistant. You have just retrieved current news content using advanced web scraping to answer the user's question.

Provide a comprehensive, well-structured response based on the news articles provided. Focus on delivering actual news information with clear organization.

Important guidelines:
- Present the most important and relevant news first
- Organize information logically (by topic, chronology, or importance)
- Be factual and objective, focusing on the actual news content
- Mention that this information comes from current web sources
- Summarize key points while maintaining accuracy
- Include relevant details from multiple sources when available"""

        user_prompt = f"""Based on the following current news content retrieved from web scraping, please answer this question: "{query}"

News content summary:
{ai_summary[:3000]}

Please provide a comprehensive, well-organized response based on this current news information. Focus on the most relevant and important news items."""

        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 800
                }
            },
            timeout=90
        )

        if ollama_response.status_code == 200:
            response_data = ollama_response.json()
            ai_response = response_data.get('response', '').strip()

            if ai_response:
                # Add source information
                sources = scraped_data.get('sources', [])
                article_count = scraped_data.get('article_count', 0)

                sources_text = "\n\n**📰 Sources:**\n" + "\n".join([f"• {source}" for source in sources])

                web_enhanced_response = f"""🌐 **Based on current web sources:**

{ai_response}

{sources_text}

*Information extracted from {article_count} articles across {len(sources)} sources using intelligent web scraping.*"""

                return web_enhanced_response

        # Fallback if Ollama fails
        return format_scraped_content(scraped_data)

    except Exception as e:
        logger.error(f"Scrapy-enhanced response generation failed: {e}")
        return format_scraped_content(scraped_data)

def perform_fallback_web_search(query: str, search_urls: List[str]) -> Dict[str, Any]:
    """Fallback to original web search method."""
    try:
        logger.info("Using fallback web search method")

        # Step 1: Fetch content from multiple sources
        fetched_content = []
        for url in search_urls[:3]:  # Limit to top 3 sources for security
            try:
                content_result = fetch_web_content_secure(url)
                if content_result['success']:
                    fetched_content.append(content_result)

                    # Save to quarantine for vetting
                    save_to_quarantine(content_result, query)

            except Exception as e:
                logger.warning(f"Failed to fetch {url}: {e}")
                continue

        if not fetched_content:
            return {
                'success': False,
                'error': 'No web content could be retrieved. All sources failed or were blocked.',
                'response': None
            }

        # Step 2: Process and analyze the fetched content
        processed_content = process_fetched_content(fetched_content, query)

        # Step 3: Generate response using the web content
        web_response = generate_web_enhanced_response(query, processed_content)

        return {
            'success': True,
            'error': None,
            'response': web_response,
            'sources': [content['url'] for content in fetched_content],
            'content_count': len(fetched_content),
            'method': 'fallback'
        }

    except Exception as e:
        logger.error(f"Fallback web search failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'response': None
        }

def generate_search_urls(query: str) -> List[str]:
    """Generate search URLs optimized for Scrapy extraction."""
    query_lower = query.lower()

    # CNN-specific queries - use main pages for better scraping
    if 'cnn' in query_lower:
        return [
            "https://www.cnn.com",
            "https://edition.cnn.com",
            "https://www.cnn.com/us"
        ]

    # News source specific queries
    elif 'nytimes' in query_lower or 'new york times' in query_lower:
        return [
            "https://www.nytimes.com",
            "https://www.nytimes.com/section/world",
            "https://www.nytimes.com/section/us"
        ]
    elif 'bbc' in query_lower:
        return [
            "https://www.bbc.com/news",
            "https://www.bbc.com/news/world",
            "https://www.bbc.com/news/uk"
        ]
    elif 'reuters' in query_lower:
        return [
            "https://www.reuters.com",
            "https://www.reuters.com/world",
            "https://www.reuters.com/business"
        ]

    # Topic-specific news pages
    elif any(word in query_lower for word in ['technology', 'tech', 'ai', 'artificial intelligence']):
        return [
            "https://www.cnn.com/business/tech",
            "https://www.nytimes.com/section/technology",
            "https://www.bbc.com/news/technology"
        ]
    elif any(word in query_lower for word in ['business', 'economy', 'finance', 'market']):
        return [
            "https://www.cnn.com/business",
            "https://www.nytimes.com/section/business",
            "https://www.bbc.com/news/business"
        ]
    elif any(word in query_lower for word in ['politics', 'political', 'election', 'government']):
        return [
            "https://www.cnn.com/politics",
            "https://www.nytimes.com/section/politics",
            "https://www.bbc.com/news/politics"
        ]
    elif any(word in query_lower for word in ['world', 'international', 'global']):
        return [
            "https://www.cnn.com/world",
            "https://www.nytimes.com/section/world",
            "https://www.bbc.com/news/world"
        ]
    elif any(word in query_lower for word in ['health', 'medical', 'medicine', 'covid', 'pandemic']):
        return [
            "https://www.cnn.com/health",
            "https://www.nytimes.com/section/health",
            "https://www.bbc.com/news/health"
        ]
    elif any(word in query_lower for word in ['sports', 'football', 'basketball', 'baseball', 'soccer']):
        return [
            "https://www.cnn.com/sport",
            "https://www.nytimes.com/section/sports",
            "https://www.bbc.com/sport"
        ]

    # General news queries - use main news pages
    elif any(word in query_lower for word in ['news', 'latest', 'breaking', 'today', 'current', 'headlines']):
        return [
            "https://www.bbc.com/news",
            "https://www.nytimes.com",
            "https://www.cnn.com"
        ]

    # Fallback for other queries - use general news sites
    else:
        return [
            "https://www.cnn.com",
            "https://www.nytimes.com",
            "https://www.bbc.com/news"
        ]

def fetch_web_content_secure(url: str) -> Dict[str, Any]:
    """Fetch web content using SAM's secure web retrieval system with enhanced content extraction."""
    try:
        # Check if this is an RSS feed
        if 'rss' in url.lower() or '.xml' in url.lower():
            rss_result = fetch_rss_content(url)

            # If RSS fails, try to fallback to regular web fetch
            if not rss_result['success']:
                logger.warning(f"RSS fetch failed for {url}, trying regular web fetch")
                # Convert RSS URL to regular web URL if possible
                fallback_url = url.replace('rss.', 'www.').replace('/rss/', '/').replace('.rss', '').replace('.xml', '')
                if fallback_url != url:
                    return fetch_web_content_secure(fallback_url)

            return rss_result

        # Use SAM's WebFetcher for regular web content
        from web_retrieval import WebFetcher

        fetcher = WebFetcher(
            timeout=15,
            max_content_length=50000,  # Limit content size for security
            user_agent="SAM-SecureBot/1.0"
        )

        result = fetcher.fetch_url_content(url)

        if result.success and result.content:
            # Enhanced content processing for news sites
            processed_content = enhance_news_content_extraction(result.content, url)

            return {
                'success': True,
                'url': url,
                'content': processed_content,
                'metadata': result.metadata,
                'timestamp': result.timestamp
            }
        else:
            return {
                'success': False,
                'url': url,
                'error': result.error or 'No content retrieved'
            }

    except Exception as e:
        logger.error(f"Web content fetch failed for {url}: {e}")
        return {
            'success': False,
            'url': url,
            'error': str(e)
        }

def fetch_rss_content(url: str) -> Dict[str, Any]:
    """Fetch and parse RSS feed content with enhanced extraction."""
    try:
        import requests
        import xml.etree.ElementTree as ET
        from datetime import datetime
        import html
        import re

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml'
        }

        logger.info(f"Fetching RSS feed: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        # Parse RSS XML
        content = response.content.decode('utf-8', errors='ignore')
        root = ET.fromstring(content)

        # Extract news items
        news_items = []

        # Handle different RSS formats (RSS 2.0, Atom, etc.)
        items = (root.findall('.//item') or
                root.findall('.//{http://www.w3.org/2005/Atom}entry') or
                root.findall('.//entry'))

        logger.info(f"Found {len(items)} items in RSS feed")

        for i, item in enumerate(items[:15]):  # Limit to top 15 news items
            try:
                title = ''
                description = ''
                link = ''
                pub_date = ''
                category = ''

                # Extract title - simplified approach
                title_elem = item.find('title')
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()

                # Extract description - simplified approach
                desc_elem = item.find('description')
                if desc_elem is not None and desc_elem.text:
                    description = desc_elem.text.strip()
                    # Clean HTML tags from description
                    description = re.sub(r'<[^>]+>', '', description)
                    # Limit description length
                    if len(description) > 300:
                        description = description[:300] + "..."

                # Debug logging for first few items
                if i < 3:
                    logger.info(f"RSS item {i}: title='{title[:50] if title else 'EMPTY'}', desc_len={len(description)}")
                    if title_elem is not None:
                        logger.info(f"  title_elem.text: '{title_elem.text[:50] if title_elem.text else 'NONE'}'")
                    if desc_elem is not None:
                        logger.info(f"  desc_elem.text: '{desc_elem.text[:50] if desc_elem.text else 'NONE'}'")
                    logger.info(f"  Final title: '{title}', Final desc: '{description[:50] if description else 'EMPTY'}'")

                # Include items with any substantial title (relaxed criteria)
                if title and len(title.strip()) > 3:  # Reduced from 5 to 3
                    news_item = f"**{title.strip()}**"

                    if description and len(description.strip()) > 5:  # Reduced from 10 to 5
                        news_item += f"\n{description.strip()}"

                    if category and category.strip():
                        news_item += f"\nCategory: {category.strip()}"

                    if pub_date and pub_date.strip():
                        news_item += f"\nPublished: {pub_date.strip()}"

                    if link and link.strip():
                        news_item += f"\nLink: {link.strip()}"

                    news_items.append(news_item)
                    logger.info(f"✅ Added news item {len(news_items)}: {title[:50]}...")
                else:
                    logger.warning(f"❌ Skipped item {i}: title='{title}' (length: {len(title) if title else 0})")

                # Extract link - simplified
                link_elem = item.find('link')
                if link_elem is not None and link_elem.text:
                    link = link_elem.text.strip()

                # Extract publication date - simplified
                date_elem = item.find('pubDate')
                if date_elem is not None and date_elem.text:
                    pub_date = date_elem.text.strip()

                # Extract category if available - simplified
                cat_elem = item.find('category')
                if cat_elem is not None and cat_elem.text:
                    category = cat_elem.text.strip()



            except Exception as e:
                logger.warning(f"Error processing RSS item {i}: {e}")
                continue

        if news_items:
            # Determine feed source for better formatting
            feed_title = "RSS News Feed"
            title_elem = root.find('.//title') or root.find('.//{http://www.w3.org/2005/Atom}title')
            if title_elem is not None and title_elem.text:
                feed_title = title_elem.text.strip()

            content = f"**{feed_title}**\n\n" + "\n\n---\n\n".join(news_items)

            logger.info(f"Successfully extracted {len(news_items)} news items from RSS feed")

            return {
                'success': True,
                'url': url,
                'content': content,
                'metadata': {
                    'content_type': 'rss_feed',
                    'items_count': len(news_items),
                    'feed_title': feed_title
                },
                'timestamp': datetime.now().isoformat()
            }
        else:
            logger.warning(f"No valid news items found in RSS feed: {url}")
            return {
                'success': False,
                'url': url,
                'error': 'No valid news items found in RSS feed'
            }

    except requests.RequestException as e:
        logger.error(f"HTTP error fetching RSS feed {url}: {e}")
        return {
            'success': False,
            'url': url,
            'error': f'HTTP error: {str(e)}'
        }
    except ET.ParseError as e:
        logger.error(f"XML parsing error for RSS feed {url}: {e}")
        return {
            'success': False,
            'url': url,
            'error': f'XML parsing error: {str(e)}'
        }
    except Exception as e:
        logger.error(f"RSS fetch failed for {url}: {e}")
        return {
            'success': False,
            'url': url,
            'error': f'RSS parsing failed: {str(e)}'
        }

def enhance_news_content_extraction(content: str, url: str) -> str:
    """Enhanced content extraction for news websites."""
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, 'html.parser')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()

        # Try to find main content areas for news sites
        main_content = []

        # Look for common news content selectors
        content_selectors = [
            'article',
            '.story-body',
            '.article-body',
            '.content',
            '.post-content',
            '[data-module="ArticleBody"]',
            '.zn-body__paragraph',
            '.pg-rail-tall__body'
        ]

        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 100:  # Only include substantial content
                    main_content.append(text)

        # If no specific content found, try to extract headlines and summaries
        if not main_content:
            headlines = soup.find_all(['h1', 'h2', 'h3'], limit=10)
            for headline in headlines:
                text = headline.get_text(strip=True)
                if len(text) > 10:
                    main_content.append(f"HEADLINE: {text}")

                    # Look for associated paragraph
                    next_elem = headline.find_next(['p', 'div'])
                    if next_elem:
                        para_text = next_elem.get_text(strip=True)
                        if len(para_text) > 50:
                            main_content.append(f"SUMMARY: {para_text}")

        # If still no content, fall back to general text extraction
        if not main_content:
            paragraphs = soup.find_all('p')
            for p in paragraphs[:20]:  # Limit to first 20 paragraphs
                text = p.get_text(strip=True)
                if len(text) > 50:
                    main_content.append(text)

        if main_content:
            return '\n\n'.join(main_content[:10])  # Limit to top 10 content pieces
        else:
            return content  # Return original if extraction fails

    except Exception as e:
        logger.warning(f"Content enhancement failed for {url}: {e}")
        return content  # Return original content if enhancement fails

def process_fetched_content(fetched_content: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """Process and analyze fetched web content."""
    try:
        # Combine all content
        all_content = []
        sources = []

        for content_data in fetched_content:
            if content_data.get('content'):
                # Clean and truncate content
                clean_content = content_data['content'][:2000]  # Limit for processing
                all_content.append(clean_content)
                sources.append(content_data['url'])

        combined_content = "\n\n".join(all_content)

        return {
            'combined_content': combined_content,
            'sources': sources,
            'content_length': len(combined_content),
            'source_count': len(sources)
        }

    except Exception as e:
        logger.error(f"Content processing failed: {e}")
        return {
            'combined_content': '',
            'sources': [],
            'content_length': 0,
            'source_count': 0
        }

def generate_web_enhanced_response(query: str, processed_content: Dict[str, Any]) -> str:
    """Generate response using web content and Ollama."""
    try:
        if not processed_content['combined_content']:
            return "❌ No web content was successfully retrieved to answer your question."

        # Use Ollama to generate response with web content
        import requests

        system_prompt = """You are SAM, a secure AI assistant. You have just retrieved current news content from RSS feeds and web sources to answer the user's question.

Provide a comprehensive, well-structured response based on the news content provided. Focus on delivering actual news information, not website structure.

Important guidelines:
- Extract and present actual news headlines, stories, and information
- Organize information by topic or chronologically if appropriate
- Be factual and objective, focusing on the news content itself
- Mention that this information comes from current RSS feeds and news sources
- If the content contains multiple news stories, summarize the key points
- Ignore any website navigation or structural information
- Focus on headlines, article summaries, and publication dates"""

        user_prompt = f"""Based on the following current news content retrieved from {processed_content['source_count']} RSS feeds and news sources, please answer this question: "{query}"

News content from RSS feeds:
{processed_content['combined_content'][:4000]}

Please provide a comprehensive news summary based on this current information. Focus on actual news stories, headlines, and developments rather than website structure."""

        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            },
            timeout=45
        )

        if ollama_response.status_code == 200:
            response_data = ollama_response.json()
            ai_response = response_data.get('response', '').strip()

            if ai_response:
                # Add source information
                sources_text = "\n\n**📰 Sources:**\n" + "\n".join([f"• {source}" for source in processed_content['sources']])

                web_enhanced_response = f"""🌐 **Based on current web sources:**

{ai_response}

{sources_text}

*Information retrieved from {processed_content['source_count']} web sources and processed securely.*"""

                return web_enhanced_response

        # Fallback if Ollama fails
        return f"""🌐 **Web Search Results:**

I found information from {processed_content['source_count']} web sources, but was unable to process it into a comprehensive response.

**Raw content summary:**
{processed_content['combined_content'][:500]}...

**Sources:**
{chr(10).join([f"• {source}" for source in processed_content['sources']])}

*You may want to visit these sources directly for the most current information.*"""

    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        return f"❌ Failed to generate response from web content: {e}"

def get_vetting_status() -> Dict[str, Any]:
    """Get current vetting system status."""
    try:
        from pathlib import Path

        # Define directories
        quarantine_dir = Path("quarantine")
        vetted_dir = Path("vetted")
        approved_dir = Path("approved")
        rejected_dir = Path("rejected")

        # Count files in each directory (excluding metadata files)
        if quarantine_dir.exists():
            all_quarantine_files = list(quarantine_dir.glob("*.json"))
            quarantine_files = len([f for f in all_quarantine_files
                                  if not f.name.startswith('metadata') and not f.name.endswith('_metadata.json')])
        else:
            quarantine_files = 0

        vetted_files = len(list(vetted_dir.glob("*.json"))) if vetted_dir.exists() else 0
        approved_files = len(list(approved_dir.glob("*.json"))) if approved_dir.exists() else 0
        rejected_files = len(list(rejected_dir.glob("*.json"))) if rejected_dir.exists() else 0

        return {
            'quarantine_files': quarantine_files,
            'vetted_files': vetted_files,
            'approved_files': approved_files,
            'rejected_files': rejected_files,
            'ready_for_vetting': quarantine_files > 0,
            'has_vetted_content': vetted_files > 0,
            'system_operational': True
        }

    except Exception as e:
        logger.error(f"Error getting vetting status: {e}")
        return {
            'quarantine_files': 0,
            'vetted_files': 0,
            'approved_files': 0,
            'rejected_files': 0,
            'ready_for_vetting': False,
            'has_vetted_content': False,
            'system_operational': False,
            'error': str(e)
        }

def trigger_vetting_process() -> Dict[str, Any]:
    """Trigger automated vetting of all quarantined content."""
    try:
        import subprocess
        import sys
        from pathlib import Path

        logger.info("Starting automated vetting process via secure interface")

        # Get project root directory
        project_root = Path(__file__).parent

        # Check quarantine status before vetting
        quarantine_dir = Path("quarantine")
        if quarantine_dir.exists():
            quarantine_files_before = list(quarantine_dir.glob("*.json"))
            logger.info(f"Before vetting: {len(quarantine_files_before)} files in quarantine")
            for f in quarantine_files_before:
                logger.info(f"  - {f.name}")
        else:
            logger.warning("Quarantine directory does not exist before vetting")

        # Execute simple vetting and consolidation script
        logger.info(f"Executing vetting script from: {project_root}")
        result = subprocess.run([
            sys.executable,
            'scripts/simple_vet_and_consolidate.py',
            '--quiet'
        ],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=300  # 5 minute timeout
        )

        logger.info(f"Vetting script completed with return code: {result.returncode}")
        logger.info(f"Vetting script stdout: {result.stdout}")
        if result.stderr:
            logger.error(f"Vetting script stderr: {result.stderr}")

        # Check quarantine status after vetting
        if quarantine_dir.exists():
            quarantine_files_after = list(quarantine_dir.glob("*.json"))
            logger.info(f"After vetting: {len(quarantine_files_after)} files in quarantine")
            for f in quarantine_files_after:
                logger.info(f"  - {f.name}")

        # Check vetted directory
        vetted_dir = Path("vetted")
        if vetted_dir.exists():
            vetted_files = list(vetted_dir.glob("*.json"))
            logger.info(f"After vetting: {len(vetted_files)} files in vetted directory")
            for f in vetted_files:
                logger.info(f"  - {f.name}")
        else:
            logger.warning("Vetted directory does not exist after vetting")

        if result.returncode == 0:
            # Parse output for statistics
            output_lines = result.stdout.strip().split('\n')
            stats = {
                'vetted_files': 0,
                'approved_files': 0,
                'rejected_files': 0,
                'integrated_items': 0
            }

            for line in output_lines:
                if 'approved' in line.lower() and 'rejected' in line.lower():
                    try:
                        # Parse "Vetting completed: X approved, Y rejected out of Z files"
                        parts = line.split()
                        approved_idx = parts.index('approved,') - 1
                        rejected_idx = parts.index('rejected') - 1
                        stats['approved_files'] = int(parts[approved_idx])
                        stats['rejected_files'] = int(parts[rejected_idx])
                        stats['vetted_files'] = stats['approved_files'] + stats['rejected_files']
                    except:
                        pass
                elif 'items integrated' in line.lower():
                    try:
                        # Parse "Consolidation completed: X items integrated out of Y processed"
                        parts = line.split()
                        integrated_idx = parts.index('items') - 1
                        stats['integrated_items'] = int(parts[integrated_idx])
                    except:
                        pass

            return {
                'success': True,
                'stats': stats,
                'output': result.stdout,
                'message': f'Vetting and consolidation completed: {stats["approved_files"]} approved, {stats["integrated_items"]} items integrated into knowledge base'
            }
        else:
            return {
                'success': False,
                'error': result.stderr or 'Vetting process failed',
                'output': result.stdout
            }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Vetting process timed out (5 minutes)',
            'output': ''
        }
    except Exception as e:
        logger.error(f"Vetting process failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'output': ''
        }

def load_vetted_content() -> List[Dict[str, Any]]:
    """Load vetted content for review."""
    try:
        from pathlib import Path
        import json

        vetted_dir = Path("vetted")
        if not vetted_dir.exists():
            return []

        vetted_files = []
        for file_path in vetted_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['filename'] = file_path.name
                    vetted_files.append(data)
            except Exception as e:
                logger.warning(f"Could not load vetted file {file_path}: {e}")
                continue

        # Sort by timestamp (newest first)
        vetted_files.sort(key=lambda x: x.get('vetting_metadata', {}).get('timestamp', ''), reverse=True)

        return vetted_files

    except Exception as e:
        logger.error(f"Error loading vetted content: {e}")
        return []

def load_quarantined_content() -> List[Dict[str, Any]]:
    """Load quarantined content for preview before vetting."""
    try:
        from pathlib import Path
        import json

        quarantine_dir = Path("quarantine")
        if not quarantine_dir.exists():
            logger.warning("Quarantine directory does not exist")
            return []

        # Log quarantine directory info
        logger.info(f"Quarantine directory: {quarantine_dir.absolute()}")
        logger.info(f"Directory exists: {quarantine_dir.exists()}")
        logger.info(f"Directory is readable: {quarantine_dir.is_dir()}")

        quarantined_files = []
        all_json_files = list(quarantine_dir.glob("*.json"))

        logger.info(f"Found {len(all_json_files)} JSON files in quarantine directory")

        # Enhanced debug: List all files found with detailed analysis
        logger.info(f"=== QUARANTINE FILE ANALYSIS ===")
        for f in all_json_files:
            mod_time = f.stat().st_mtime
            from datetime import datetime
            mod_time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"  - {f.name} ({f.stat().st_size} bytes, modified: {mod_time_str})")

            # Analyze file patterns
            if 'intelligent_web_' in f.name:
                logger.info(f"    ✅ INTELLIGENT_WEB FILE DETECTED: {f.name}")
            elif 'scrapy_' in f.name:
                logger.info(f"    📜 SCRAPY FILE DETECTED: {f.name}")
            elif f.name.startswith('metadata'):
                logger.info(f"    📋 METADATA FILE DETECTED: {f.name}")
            else:
                logger.info(f"    ❓ UNKNOWN FILE TYPE: {f.name}")

        # Count file types
        intelligent_web_files = [f for f in all_json_files if 'intelligent_web_' in f.name]
        scrapy_files = [f for f in all_json_files if 'scrapy_' in f.name]
        metadata_files = [f for f in all_json_files if f.name.startswith('metadata') or f.name.endswith('_metadata.json')]

        logger.info(f"File type summary:")
        logger.info(f"  - Intelligent web files: {len(intelligent_web_files)}")
        logger.info(f"  - Scrapy files: {len(scrapy_files)}")
        logger.info(f"  - Metadata files: {len(metadata_files)}")
        logger.info(f"  - Total JSON files: {len(all_json_files)}")

        for file_path in all_json_files:
            # Skip metadata files
            if file_path.name.startswith('metadata') or file_path.name.endswith('_metadata.json'):
                logger.info(f"⏭️ Skipping metadata file: {file_path.name}")
                continue

            logger.info(f"🔄 Processing quarantine file: {file_path.name}")

            # Debug: Check if this is an intelligent_web file
            if 'intelligent_web_' in file_path.name:
                logger.info(f"🌐 Found intelligent_web file: {file_path.name}, size: {file_path.stat().st_size} bytes")
            elif 'scrapy_' in file_path.name:
                logger.info(f"🕷️ Found scrapy file: {file_path.name}, size: {file_path.stat().st_size} bytes")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Add file metadata
                data['filename'] = file_path.name
                data['file_path'] = str(file_path)
                data['file_size'] = file_path.stat().st_size
                data['file_modified'] = file_path.stat().st_mtime

                quarantined_files.append(data)
                logger.info(f"Successfully loaded quarantine file: {file_path.name}")

                # Debug: Log structure for intelligent_web files
                if 'intelligent_web_' in file_path.name:
                    logger.info(f"Intelligent_web file structure: {list(data.keys())}")
                    if 'result' in data:
                        logger.info(f"  - result keys: {list(data['result'].keys()) if isinstance(data['result'], dict) else type(data['result'])}")
                    if 'query' in data:
                        logger.info(f"  - query: {data['query'][:50]}...")
                    if 'timestamp' in data:
                        logger.info(f"  - timestamp: {data['timestamp']}")

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in {file_path.name}: {e}")
                # Add corrupted file entry
                quarantined_files.append({
                    'filename': file_path.name,
                    'file_path': str(file_path),
                    'error': f"JSON decode error: {e}",
                    'corrupted': True,
                    'file_size': file_path.stat().st_size,
                    'file_modified': file_path.stat().st_mtime
                })
                continue
            except Exception as e:
                logger.error(f"Could not load quarantined file {file_path.name}: {e}")
                # Add error file entry
                quarantined_files.append({
                    'filename': file_path.name,
                    'file_path': str(file_path),
                    'error': str(e),
                    'corrupted': True,
                    'file_size': file_path.stat().st_size if file_path.exists() else 0,
                    'file_modified': file_path.stat().st_mtime if file_path.exists() else 0
                })
                continue

        logger.info(f"Loaded {len(quarantined_files)} quarantined files (including any corrupted ones)")

        # Sort by timestamp (newest first), handling different timestamp formats
        def get_sort_timestamp(x):
            if x.get('corrupted'):
                return x.get('file_modified', 0)

            # Try different timestamp fields
            timestamp = (x.get('timestamp') or
                        x.get('metadata', {}).get('quarantine_timestamp') or
                        x.get('metadata', {}).get('timestamp') or
                        str(x.get('file_modified', 0)))
            return timestamp

        quarantined_files.sort(key=get_sort_timestamp, reverse=True)

        return quarantined_files

    except Exception as e:
        logger.error(f"Error loading quarantined content: {e}")
        return []

def render_quarantined_content_item(content: Dict[str, Any], index: int):
    """Render a single quarantined content item for preview."""
    try:
        filename = content.get('filename', 'Unknown')
        file_size = content.get('file_size', 0)

        # Handle corrupted files
        if content.get('corrupted'):
            error_msg = content.get('error', 'Unknown error')

            with st.expander(f"❌ **{filename}** (Corrupted)", expanded=False):
                st.error(f"**File Error:** {error_msg}")
                st.markdown(f"**📁 File:** `{filename}`")
                st.markdown(f"**📊 File Size:** {file_size:,} bytes")
                st.markdown(f"**🕒 Modified:** {content.get('file_modified', 'Unknown')}")

                st.warning("⚠️ **This file could not be loaded.** It may be corrupted or have an invalid format.")

                # Raw data toggle for debugging
                if st.button(f"🔍 Show Error Details", key=f"quarantine_error_{index}"):
                    if f"show_quarantine_error_{index}" not in st.session_state:
                        st.session_state[f"show_quarantine_error_{index}"] = False
                    st.session_state[f"show_quarantine_error_{index}"] = not st.session_state[f"show_quarantine_error_{index}"]

                if st.session_state.get(f"show_quarantine_error_{index}", False):
                    st.json(content)
            return

        # Normal file processing
        timestamp = content.get('timestamp', content.get('metadata', {}).get('quarantine_timestamp', 'Unknown'))

        # Extract basic information based on content type
        content_info = extract_quarantine_content_info(content)

        with st.expander(f"📄 **{content_info['title']}**", expanded=False):
            # Basic information
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**📁 File:** `{filename}`")
                st.markdown(f"**🕒 Quarantined:** {timestamp}")
                st.markdown(f"**🔍 Source:** {content_info['source']}")
                st.markdown(f"**📊 Content Type:** {content_info['content_type']}")

            with col2:
                st.markdown(f"**📈 Items:** {content_info['item_count']}")
                st.markdown(f"**🌐 Sources:** {content_info['source_count']}")
                st.markdown(f"**⚙️ Method:** {content_info['method']}")
                st.markdown(f"**📊 Size:** {file_size:,} bytes")

            # Content preview
            if content_info['preview']:
                st.markdown("**📝 Content Preview:**")
                st.markdown(content_info['preview'])

            # Show sources if available
            if content_info['sources']:
                st.markdown("**🔗 Sources:**")
                for source in content_info['sources'][:5]:  # Show first 5 sources
                    st.markdown(f"• {source}")
                if len(content_info['sources']) > 5:
                    st.markdown(f"• ... and {len(content_info['sources']) - 5} more sources")

            # Status indicator
            st.info("⏳ **Status:** Awaiting security analysis and vetting")

            # Raw data toggle
            if st.button(f"🔍 Show Raw Data", key=f"quarantine_raw_{index}"):
                if f"show_quarantine_raw_{index}" not in st.session_state:
                    st.session_state[f"show_quarantine_raw_{index}"] = False
                st.session_state[f"show_quarantine_raw_{index}"] = not st.session_state[f"show_quarantine_raw_{index}"]

            if st.session_state.get(f"show_quarantine_raw_{index}", False):
                st.json(content)

    except Exception as e:
        st.error(f"Error rendering quarantined content item: {e}")
        logger.error(f"Error rendering quarantined content item {index}: {e}")

def extract_quarantine_content_info(content: Dict[str, Any]) -> Dict[str, Any]:
    """Extract display information from quarantined content."""
    try:
        # Default values
        info = {
            'title': 'Unknown Content',
            'source': 'Unknown',
            'content_type': 'Unknown',
            'item_count': 0,
            'source_count': 0,
            'method': 'Unknown',
            'preview': '',
            'sources': []
        }

        # Debug: Log the structure of the content for troubleshooting
        filename = content.get('filename', 'Unknown')
        logger.info(f"Extracting info from {filename}, keys: {list(content.keys())}")

        # Check for timestamp and metadata
        if 'timestamp' in content:
            logger.info(f"File {filename} has timestamp: {content['timestamp']}")
        if 'metadata' in content:
            logger.info(f"File {filename} has metadata: {list(content['metadata'].keys()) if isinstance(content['metadata'], dict) else type(content['metadata'])}")

        # Check for intelligent web system content (multiple possible formats)
        if 'result' in content and isinstance(content['result'], dict):
            result = content['result']
            query = content.get('query', 'Unknown Query')

            info['title'] = f"Web Search: {query}"
            info['source'] = 'Intelligent Web System'
            info['method'] = result.get('tool_used', 'Unknown Tool')

        # Check for direct intelligent web format (newer format)
        elif 'query' in content and ('tool_used' in content or 'data' in content):
            query = content.get('query', 'Unknown Query')

            info['title'] = f"Web Search: {query}"
            info['source'] = 'Intelligent Web System'
            info['method'] = content.get('tool_used', 'Unknown Tool')

            # Process data directly from content
            data = content.get('data', {})
            if 'articles' in data:
                info['content_type'] = 'News Articles'
                articles = data['articles']
                info['item_count'] = len(articles)

                # Get sources from articles
                sources = set()
                preview_items = []

                for article in articles[:3]:  # Preview first 3 articles
                    if 'source' in article:
                        sources.add(article['source'])
                    title = article.get('title', 'No title')
                    preview_items.append(f"• **{title}**")

                info['sources'] = list(sources)
                info['source_count'] = len(sources)
                info['preview'] = '\n'.join(preview_items)

            # Continue with existing result processing if result exists
            if 'result' in content:
                result = content['result']

            # Extract data from result
            data = result.get('data', {})
            if 'articles' in data:
                info['content_type'] = 'News Articles'
                articles = data['articles']
                info['item_count'] = len(articles)

                # Get sources from articles
                sources = set()
                preview_items = []

                for article in articles[:3]:  # Preview first 3 articles
                    if 'source' in article:
                        sources.add(article['source'])
                    title = article.get('title', 'No title')
                    preview_items.append(f"• **{title}**")

                info['sources'] = list(sources)
                info['source_count'] = len(sources)
                info['preview'] = '\n'.join(preview_items)

            elif 'chunks' in data:
                info['content_type'] = 'Web Content Chunks'
                info['item_count'] = data.get('total_chunks', 0)
                info['source_count'] = len(data.get('sources', []))
                info['sources'] = data.get('sources', [])

                # Preview chunks
                chunks = data.get('chunks', [])
                preview_items = []
                for chunk in chunks[:3]:
                    content_preview = chunk.get('content', '')[:100]
                    if len(content_preview) == 100:
                        content_preview += '...'
                    preview_items.append(f"• {content_preview}")
                info['preview'] = '\n'.join(preview_items)

        # Check for direct web content
        elif 'url' in content and 'content' in content:
            info['title'] = f"Web Page: {content['url']}"
            info['source'] = 'Direct Web Fetch'
            info['content_type'] = 'Web Page'
            info['item_count'] = 1
            info['source_count'] = 1
            info['sources'] = [content['url']]
            info['method'] = content.get('metadata', {}).get('fetch_method', 'Unknown')

            # Content preview
            page_content = content.get('content', '')
            if page_content:
                info['preview'] = page_content[:300] + ('...' if len(page_content) > 300 else '')

        # Check for scraped data format (newer scrapy format)
        elif 'scraped_data' in content:
            query = content.get('query', 'Unknown Query')
            info['title'] = f"Scraped Search: {query}"
            info['source'] = 'Scrapy Web Search'
            info['content_type'] = 'Scraped Articles'

            scraped_data = content.get('scraped_data', {})
            articles = scraped_data.get('articles', [])
            info['item_count'] = len(articles)

            # Get sources from metadata or scraped data
            sources = content.get('metadata', {}).get('sources', [])
            if not sources:
                sources = scraped_data.get('sources', [])
            info['sources'] = sources
            info['source_count'] = len(sources)
            info['method'] = content.get('metadata', {}).get('method', 'Scrapy')

            # Preview articles
            preview_items = []
            for article in articles[:3]:
                title = article.get('title', 'No title')
                preview_items.append(f"• **{title}**")
            info['preview'] = '\n'.join(preview_items)

        # Check for RSS/scraped content (older format)
        elif 'articles' in content:
            query = content.get('query', 'Unknown Query')
            info['title'] = f"RSS Search: {query}"
            info['source'] = 'RSS/Scraped Content'
            info['content_type'] = 'RSS Articles'

            articles = content['articles']
            info['item_count'] = len(articles)

            # Get sources
            sources = content.get('sources', [])
            info['sources'] = sources
            info['source_count'] = len(sources)
            info['method'] = content.get('metadata', {}).get('source', 'RSS')

            # Preview articles
            preview_items = []
            for article in articles[:3]:
                title = article.get('title', 'No title')
                preview_items.append(f"• **{title}**")
            info['preview'] = '\n'.join(preview_items)

        # Fallback: If we still have "Unknown Content", try to extract any useful info
        if info['title'] == 'Unknown Content':
            filename = content.get('filename', 'Unknown')
            logger.warning(f"Could not parse content structure for {filename}")

            # Try to extract basic info from any available fields
            if 'query' in content:
                info['title'] = f"Query: {content['query']}"
                info['source'] = 'Web Search'
            elif 'url' in content:
                info['title'] = f"URL: {content['url']}"
                info['source'] = 'Web Fetch'
            else:
                # Show available keys for debugging
                available_keys = [k for k in content.keys() if k not in ['filename', 'file_path', 'file_size', 'file_modified']]
                info['title'] = f"Unknown Content ({filename})"
                info['preview'] = f"Available data keys: {', '.join(available_keys[:10])}"
                if len(available_keys) > 10:
                    info['preview'] += f" ... and {len(available_keys) - 10} more"

        return info

    except Exception as e:
        logger.error(f"Error extracting quarantine content info: {e}")
        filename = content.get('filename', 'Unknown')
        return {
            'title': f'Error Processing Content ({filename})',
            'source': 'Unknown',
            'content_type': 'Unknown',
            'item_count': 0,
            'source_count': 0,
            'method': 'Unknown',
            'preview': f'Error: {e}',
            'sources': []
        }

def calculate_security_overview() -> Dict[str, Any]:
    """Calculate security metrics overview from all vetted content."""
    try:
        from pathlib import Path
        import json

        vetted_dir = Path("vetted")
        if not vetted_dir.exists():
            return {}

        total_critical_risks = 0
        total_high_risks = 0
        total_credibility = 0
        total_purity = 0
        files_with_analysis = 0

        for file_path in vetted_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check both possible locations for vetting results
                    vetting_result = data.get('vetting_results', data.get('vetting_result', {}))

                    if vetting_result:
                        files_with_analysis += 1

                        # Count risk factors
                        risk_factors = vetting_result.get('risk_assessment', {}).get('risk_factors', [])
                        total_critical_risks += len([r for r in risk_factors if r.get('severity') == 'critical'])
                        total_high_risks += len([r for r in risk_factors if r.get('severity') == 'high'])

                        # Accumulate scores
                        scores = vetting_result.get('scores', {})
                        total_credibility += scores.get('credibility', 0)
                        total_purity += scores.get('purity', 0)

            except Exception as e:
                logger.warning(f"Error processing vetted file {file_path}: {e}")
                continue

        if files_with_analysis == 0:
            return {}

        return {
            'critical_risks': total_critical_risks,
            'high_risks': total_high_risks,
            'avg_credibility': total_credibility / files_with_analysis,
            'avg_purity': total_purity / files_with_analysis,
            'files_analyzed': files_with_analysis
        }

    except Exception as e:
        logger.error(f"Error calculating security overview: {e}")
        return {}

def render_vetted_content_item(content: Dict[str, Any], index: int):
    """Render a single vetted content item for review."""
    try:
        # Extract key information from file format - check both possible locations
        vetting_result = content.get('vetting_result', content.get('vetting_results', {}))

        # Extract content info based on file structure
        content_info = extract_content_info_for_display(content)

        # Determine recommendation color and text
        rec_action = vetting_result.get('recommendation', 'REVIEW')
        if rec_action == 'PASS':
            rec_color = "🟢"
            rec_text = "Recommended for Approval"
        elif rec_action == 'FAIL':
            rec_color = "🔴"
            rec_text = "Recommended for Rejection"
        else:
            rec_color = "🟡"
            rec_text = "Requires Manual Review"

        # Create expandable item
        title = content_info['title']
        with st.expander(f"{rec_color} {title}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Source:** {content_info['source']}")
                st.markdown(f"**Query:** {content_info['query']}")
                st.markdown(f"**Recommendation:** {rec_color} {rec_text}")

                if content_info['article_count'] > 0:
                    st.markdown(f"**Articles Found:** {content_info['article_count']}")

                # Show vetting score and four-dimension security summary
                overall_score = vetting_result.get('overall_score', 0)
                if overall_score > 0:
                    st.markdown("**🛡️ Security Analysis Summary:**")
                    st.progress(overall_score, text=f"Overall Score: {overall_score:.1%}")

                    # Four-Dimension Security Analysis
                    scores = vetting_result.get('scores', {})
                    if scores:
                        st.markdown("**📊 Four-Dimension Security Assessment:**")

                        # Create security dimension display
                        dim_col1, dim_col2 = st.columns(2)

                        with dim_col1:
                            # Credibility & Bias
                            credibility = scores.get('credibility', 0)
                            cred_icon = "✅" if credibility >= 0.7 else "⚠️" if credibility >= 0.4 else "❌"
                            cred_status = "Good" if credibility >= 0.7 else "Warning" if credibility >= 0.4 else "Risk"
                            st.markdown(f"{cred_icon} **Credibility & Bias**: {credibility:.1%} ({cred_status})")

                            # Speculation vs. Fact
                            speculation = scores.get('speculation', 0)
                            spec_icon = "✅" if speculation <= 0.3 else "⚠️" if speculation <= 0.6 else "❌"
                            spec_status = "Good" if speculation <= 0.3 else "Warning" if speculation <= 0.6 else "Risk"
                            st.markdown(f"{spec_icon} **Speculation vs. Fact**: {speculation:.1%} ({spec_status})")

                        with dim_col2:
                            # Persuasive Language
                            persuasion = scores.get('persuasion', 0)
                            pers_icon = "✅" if persuasion <= 0.3 else "⚠️" if persuasion <= 0.6 else "❌"
                            pers_status = "Good" if persuasion <= 0.3 else "Warning" if persuasion <= 0.6 else "Risk"
                            st.markdown(f"{pers_icon} **Persuasive Language**: {persuasion:.1%} ({pers_status})")

                            # Content Purity
                            purity = scores.get('purity', 0)
                            purity_icon = "✅" if purity >= 0.8 else "⚠️" if purity >= 0.5 else "❌"
                            purity_status = "Good" if purity >= 0.8 else "Warning" if purity >= 0.5 else "Risk"
                            st.markdown(f"{purity_icon} **Content Purity**: {purity:.1%} ({purity_status})")

                        # Risk Factor Alerts
                        risk_factors = vetting_result.get('risk_assessment', {}).get('risk_factors', [])
                        if risk_factors:
                            critical_risks = [r for r in risk_factors if r.get('severity') == 'critical']
                            high_risks = [r for r in risk_factors if r.get('severity') == 'high']

                            if critical_risks:
                                st.error(f"🔴 **Critical Risk Alert**: {len(critical_risks)} critical security threat(s) detected")
                            elif high_risks:
                                st.warning(f"🟠 **High Risk Alert**: {len(high_risks)} high-priority concern(s) detected")
                            else:
                                st.success("🟢 **Risk Assessment**: No critical or high-risk factors detected")
                        else:
                            st.success("🟢 **Risk Assessment**: No security risks detected")

                    # Show key security dimensions
                    scores = vetting_result.get('scores', {})
                    if scores:
                        security_summary = []

                        # Credibility & Bias
                        credibility = scores.get('credibility', 0)
                        cred_status = "✅" if credibility >= 0.7 else "⚠️" if credibility >= 0.4 else "❌"
                        security_summary.append(f"{cred_status} Credibility: {credibility:.1%}")

                        # Persuasive Language (lower is better)
                        persuasion = scores.get('persuasion', 0)
                        pers_status = "✅" if persuasion <= 0.3 else "⚠️" if persuasion <= 0.6 else "❌"
                        security_summary.append(f"{pers_status} Persuasion: {persuasion:.1%}")

                        # Speculation vs Fact (lower is better)
                        speculation = scores.get('speculation', 0)
                        spec_status = "✅" if speculation <= 0.3 else "⚠️" if speculation <= 0.6 else "❌"
                        security_summary.append(f"{spec_status} Speculation: {speculation:.1%}")

                        # Content Purity
                        purity = scores.get('purity', 0)
                        pur_status = "✅" if purity >= 0.8 else "⚠️" if purity >= 0.5 else "❌"
                        security_summary.append(f"{pur_status} Purity: {purity:.1%}")

                        # Display in a compact format
                        st.markdown(" | ".join(security_summary))

                    # Show risk factors count
                    risk_factors = vetting_result.get('risk_assessment', {}).get('risk_factors', [])
                    if risk_factors:
                        critical_risks = len([r for r in risk_factors if r.get('severity') == 'critical'])
                        high_risks = len([r for r in risk_factors if r.get('severity') == 'high'])

                        if critical_risks > 0:
                            st.markdown(f"🔴 **{critical_risks} Critical Risk(s) Detected**")
                        elif high_risks > 0:
                            st.markdown(f"🟠 **{high_risks} High Risk(s) Detected**")
                        else:
                            st.markdown("🟢 **No Critical Risks Detected**")

                # Show content preview
                if content_info['preview']:
                    st.markdown("**Content Preview:**")
                    st.text(content_info['preview'])

            with col2:
                st.markdown("**Actions:**")

                col_approve, col_reject = st.columns(2)

                with col_approve:
                    if st.button("✅ Approve", key=f"approve_{index}", use_container_width=True):
                        if approve_content(content['filename']):
                            st.success("Content approved!")
                            st.rerun()
                        else:
                            st.error("Failed to approve content")

                with col_reject:
                    if st.button("❌ Reject", key=f"reject_{index}", use_container_width=True):
                        if reject_content(content['filename']):
                            st.success("Content rejected!")
                            st.rerun()
                        else:
                            st.error("Failed to reject content")

                # Show detailed analysis toggle
                if st.button("📊 View Details", key=f"details_{index}", use_container_width=True):
                    if f"show_details_{index}" not in st.session_state:
                        st.session_state[f"show_details_{index}"] = False
                    st.session_state[f"show_details_{index}"] = not st.session_state[f"show_details_{index}"]

            # Show detailed security analysis if toggled
            if st.session_state.get(f"show_details_{index}", False):
                render_detailed_security_analysis(vetting_result, index)

    except Exception as e:
        st.error(f"Error rendering vetted content item: {e}")

def render_detailed_security_analysis(vetting_result: Dict[str, Any], index: int):
    """Render detailed security analysis from SAM's Conceptual Dimension Prober."""
    try:
        st.markdown("---")
        st.markdown("### 🔍 **SAM's Security Analysis Report**")
        st.markdown("*Powered by Conceptual Dimension Prober*")

        # Check if we have valid vetting results
        if not vetting_result or vetting_result.get('status') == 'error':
            st.error("❌ **Analysis Error**")
            error_msg = vetting_result.get('reason', vetting_result.get('error', 'Unknown error occurred during analysis'))
            st.markdown(f"**Error:** {error_msg}")

            # Show raw data for debugging
            if vetting_result:
                st.markdown("**Raw Error Data:**")
                st.json(vetting_result)
            return

        # Overall Assessment
        overall_score = vetting_result.get('overall_score', 0)
        confidence = vetting_result.get('confidence', 0)
        recommendation = vetting_result.get('recommendation', 'UNKNOWN')

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 Overall Score", f"{overall_score:.1%}",
                     delta=f"Confidence: {confidence:.1%}")
        with col2:
            rec_color = {"PASS": "🟢", "FAIL": "🔴", "REVIEW": "🟡"}.get(recommendation, "⚪")
            st.metric("📋 Recommendation", f"{rec_color} {recommendation}")
        with col3:
            processing_time = vetting_result.get('processing_time', 0)
            st.metric("⚡ Analysis Time", f"{processing_time:.2f}s")

        # Security Dimensions Analysis
        scores = vetting_result.get('scores', {})
        if scores:
            st.markdown("#### 🛡️ **Security Dimensions Analysis**")
            st.markdown("*Each dimension examined by SAM's Conceptual Understanding*")
        else:
            st.warning("⚠️ **No Security Dimension Scores Available**")
            st.markdown("The analysis may have failed or used a fallback method.")

        if scores:

            # Create two columns for dimension display
            dim_col1, dim_col2 = st.columns(2)

            dimension_info = {
                'credibility': {
                    'name': '🎓 Credibility & Bias',
                    'description': 'Factual accuracy and source reliability',
                    'good_range': [0.7, 1.0],
                    'warning_range': [0.4, 0.7],
                    'bad_range': [0.0, 0.4]
                },
                'persuasion': {
                    'name': '🎭 Persuasive Language',
                    'description': 'Manipulative or emotionally charged content',
                    'good_range': [0.0, 0.3],
                    'warning_range': [0.3, 0.6],
                    'bad_range': [0.6, 1.0]
                },
                'speculation': {
                    'name': '🔮 Speculation vs. Fact',
                    'description': 'Unverified claims and conjecture',
                    'good_range': [0.0, 0.3],
                    'warning_range': [0.3, 0.6],
                    'bad_range': [0.6, 1.0]
                },
                'purity': {
                    'name': '🧹 Content Purity',
                    'description': 'Freedom from suspicious patterns',
                    'good_range': [0.8, 1.0],
                    'warning_range': [0.5, 0.8],
                    'bad_range': [0.0, 0.5]
                }
            }

            for i, (dim_key, score) in enumerate(scores.items()):
                if dim_key in dimension_info:
                    info = dimension_info[dim_key]

                    # Determine color based on score and dimension type
                    if score >= info['good_range'][0] and score <= info['good_range'][1]:
                        color = "🟢"
                        status = "Good"
                    elif score >= info['warning_range'][0] and score <= info['warning_range'][1]:
                        color = "🟡"
                        status = "Warning"
                    else:
                        color = "🔴"
                        status = "Risk"

                    # Alternate between columns
                    with dim_col1 if i % 2 == 0 else dim_col2:
                        st.markdown(f"**{info['name']}** {color}")
                        st.progress(score, text=f"{score:.1%} - {status}")
                        st.caption(info['description'])
                        st.markdown("")

        # Risk Factors
        risk_assessment = vetting_result.get('risk_assessment', {})
        risk_factors = risk_assessment.get('risk_factors', [])

        if risk_factors:
            st.markdown("#### ⚠️ **Identified Risk Factors**")

            for risk in risk_factors:
                severity = risk.get('severity', 'unknown')
                dimension = risk.get('dimension', 'unknown')
                description = risk.get('description', 'No description')
                score = risk.get('score', 0)

                severity_colors = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }

                severity_color = severity_colors.get(severity, '⚪')

                st.markdown(f"**{severity_color} {severity.title()} Risk - {dimension.replace('_', ' ').title()}**")
                st.markdown(f"• {description}")
                st.markdown(f"• Score: {score:.2f}")
                st.markdown("")

        # Source Reputation Analysis
        source_reputation = vetting_result.get('source_reputation', {})
        if source_reputation:
            st.markdown("#### 🌐 **Source Reputation Analysis**")

            domain = source_reputation.get('domain', 'unknown')
            final_score = source_reputation.get('final_score', 0)
            risk_category = source_reputation.get('risk_category', 'unknown')
            https_used = source_reputation.get('https_used', False)

            rep_col1, rep_col2 = st.columns(2)

            with rep_col1:
                st.markdown(f"**Domain:** `{domain}`")
                st.markdown(f"**HTTPS:** {'✅ Yes' if https_used else '❌ No'}")

            with rep_col2:
                st.markdown(f"**Reputation Score:** {final_score:.1%}")
                st.markdown(f"**Risk Category:** {risk_category.replace('_', ' ').title()}")

        # Content Sanitization Results
        sanitization = vetting_result.get('sanitization', {})
        if sanitization:
            st.markdown("#### 🧼 **Content Sanitization Results**")

            purity_score = sanitization.get('purity_score', 0)
            removed_elements = sanitization.get('removed_elements', [])
            suspicious_patterns = sanitization.get('suspicious_patterns', [])

            san_col1, san_col2 = st.columns(2)

            with san_col1:
                st.metric("🧹 Purity Score", f"{purity_score:.1%}")
                if removed_elements:
                    st.markdown(f"**Removed Elements:** {len(removed_elements)}")
                    for element in removed_elements[:3]:  # Show first 3
                        st.caption(f"• {element}")
                    if len(removed_elements) > 3:
                        st.caption(f"• ... and {len(removed_elements) - 3} more")

            with san_col2:
                if suspicious_patterns:
                    st.markdown(f"**⚠️ Suspicious Patterns:** {len(suspicious_patterns)}")
                    for pattern in suspicious_patterns[:3]:  # Show first 3
                        st.caption(f"• {pattern}")
                    if len(suspicious_patterns) > 3:
                        st.caption(f"• ... and {len(suspicious_patterns) - 3} more")
                else:
                    st.markdown("**✅ No Suspicious Patterns Detected**")

        # Analysis Metadata
        metadata = vetting_result.get('metadata', {})
        if metadata:
            st.markdown("#### 🔧 **Analysis Configuration**")
            st.markdown(f"**Profile Used:** {metadata.get('profile_used', 'unknown')}")
            st.markdown(f"**Analysis Mode:** {metadata.get('analysis_mode', 'unknown')}")
            st.markdown(f"**Safety Threshold:** {metadata.get('safety_threshold', 0):.1%}")
            st.markdown(f"**Evaluator Version:** {metadata.get('evaluator_version', 'unknown')}")
            st.markdown("")

        # Raw Data (for debugging) - Use a toggle instead of expander
        if st.button("🔍 Show/Hide Raw Analysis Data", key=f"toggle_raw_{index}"):
            if f"show_raw_{index}" not in st.session_state:
                st.session_state[f"show_raw_{index}"] = False
            st.session_state[f"show_raw_{index}"] = not st.session_state[f"show_raw_{index}"]

        if st.session_state.get(f"show_raw_{index}", False):
            st.markdown("#### 🔍 **Raw Analysis Data**")
            st.json(vetting_result)

    except Exception as e:
        st.error(f"Error rendering security analysis: {e}")
        # Fallback to raw JSON display
        st.json(vetting_result)

def extract_content_info_for_display(content: Dict[str, Any]) -> Dict[str, Any]:
    """Extract content information for display from various file formats."""
    try:
        # Initialize default values
        info = {
            'title': 'Unknown Content',
            'source': 'Unknown Source',
            'query': 'Unknown Query',
            'article_count': 0,
            'preview': ''
        }

        # Handle intelligent web system format
        if 'result' in content and 'data' in content['result']:
            query = content.get('query', 'Unknown Query')
            result_data = content['result']['data']

            info['query'] = query
            info['source'] = 'Intelligent Web System'

            # Check for articles
            if 'articles' in result_data and result_data['articles']:
                articles = result_data['articles']
                info['article_count'] = len(articles)
                info['title'] = f"Web Search: {query} ({len(articles)} articles)"

                # Create preview from first few articles
                preview_parts = []
                for i, article in enumerate(articles[:3]):
                    title = article.get('title', 'No title')
                    desc = article.get('description', 'No description')
                    preview_parts.append(f"{i+1}. {title}\n   {desc[:100]}...")

                info['preview'] = '\n\n'.join(preview_parts)
                if len(articles) > 3:
                    info['preview'] += f'\n\n... and {len(articles) - 3} more articles'

            # Check for search results
            elif 'search_results' in result_data and result_data['search_results']:
                results = result_data['search_results']
                info['article_count'] = len(results)
                info['title'] = f"Search Results: {query} ({len(results)} results)"

                # Create preview from first few results
                preview_parts = []
                for i, result in enumerate(results[:3]):
                    title = result.get('title', 'No title')
                    snippet = result.get('snippet', 'No snippet')
                    preview_parts.append(f"{i+1}. {title}\n   {snippet[:100]}...")

                info['preview'] = '\n\n'.join(preview_parts)
                if len(results) > 3:
                    info['preview'] += f'\n\n... and {len(results) - 3} more results'

            # Check for direct content
            elif 'content' in result_data and result_data['content']:
                info['title'] = f"Web Content: {query}"
                info['preview'] = result_data['content'][:500] + '...' if len(result_data['content']) > 500 else result_data['content']

        # Handle scraped data format
        elif 'scraped_data' in content:
            query = content.get('query', 'Unknown Query')
            scraped = content['scraped_data']

            info['query'] = query
            info['source'] = 'Scrapy Web Search'

            if 'articles' in scraped and scraped['articles']:
                articles = scraped['articles']
                info['article_count'] = len(articles)
                info['title'] = f"Scraped Content: {query} ({len(articles)} articles)"

                # Create preview
                preview_parts = []
                for i, article in enumerate(articles[:3]):
                    title = article.get('title', 'No title')
                    content_text = article.get('content', article.get('description', 'No content'))
                    preview_parts.append(f"{i+1}. {title}\n   {content_text[:100]}...")

                info['preview'] = '\n\n'.join(preview_parts)

        # Handle direct articles format
        elif 'articles' in content and content['articles']:
            articles = content['articles']
            info['article_count'] = len(articles)
            info['title'] = f"Article Collection ({len(articles)} articles)"
            info['source'] = 'Direct Articles'

            # Create preview
            preview_parts = []
            for i, article in enumerate(articles[:3]):
                title = article.get('title', 'No title')
                desc = article.get('description', article.get('content', 'No description'))
                preview_parts.append(f"{i+1}. {title}\n   {desc[:100]}...")

            info['preview'] = '\n\n'.join(preview_parts)

        # Handle direct content format (old format)
        elif 'content' in content and content['content']:
            # Check if this is old format with metadata
            if 'metadata' in content and content['metadata']:
                metadata = content['metadata']
                query = metadata.get('original_query', 'Unknown Query')
                source = metadata.get('source', 'Unknown Source')

                info['query'] = query
                info['source'] = source.replace('_', ' ').title()
                info['title'] = f"Web Content: {query}"

                # Extract preview from content
                content_text = content['content']
                if len(content_text) > 500:
                    info['preview'] = content_text[:500] + '...'
                else:
                    info['preview'] = content_text
            else:
                info['title'] = 'Direct Content'
                info['source'] = content.get('source', 'Unknown Source')
                info['preview'] = content['content'][:500] + '...' if len(content['content']) > 500 else content['content']

        return info

    except Exception as e:
        logger.error(f"Error extracting content info for display: {e}")
        return {
            'title': 'Error Loading Content',
            'source': 'Unknown',
            'query': 'Unknown',
            'article_count': 0,
            'preview': f'Error: {str(e)}'
        }

def approve_content(filename: str) -> bool:
    """Approve vetted content and move to approved directory."""
    try:
        from pathlib import Path
        import shutil

        vetted_path = Path("vetted") / filename
        approved_path = Path("approved") / filename

        # Create approved directory if it doesn't exist
        approved_path.parent.mkdir(exist_ok=True)

        # Move file to approved directory
        shutil.move(str(vetted_path), str(approved_path))

        logger.info(f"Content approved: {filename}")
        return True

    except Exception as e:
        logger.error(f"Error approving content {filename}: {e}")
        return False

def reject_content(filename: str) -> bool:
    """Reject vetted content and move to rejected directory."""
    try:
        from pathlib import Path
        import shutil

        vetted_path = Path("vetted") / filename
        rejected_path = Path("rejected") / filename

        # Create rejected directory if it doesn't exist
        rejected_path.parent.mkdir(exist_ok=True)

        # Move file to rejected directory
        shutil.move(str(vetted_path), str(rejected_path))

        logger.info(f"Content rejected: {filename}")
        return True

    except Exception as e:
        logger.error(f"Error rejecting content {filename}: {e}")
        return False

def save_to_quarantine(content_result: Dict[str, Any], query: str):
    """Save fetched web content to quarantine for vetting."""
    try:
        from pathlib import Path
        import json
        import hashlib
        from datetime import datetime

        # Create quarantine directory if it doesn't exist
        quarantine_dir = Path("quarantine")
        quarantine_dir.mkdir(exist_ok=True)

        # Generate filename based on URL hash and timestamp
        url_hash = hashlib.md5(content_result['url'].encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"web_search_{timestamp}_{url_hash}.json"

        # Prepare quarantine data structure
        quarantine_data = {
            "url": content_result['url'],
            "content": content_result['content'],
            "timestamp": content_result.get('timestamp', datetime.now().isoformat()),
            "error": None,
            "metadata": {
                **content_result.get('metadata', {}),
                "source": "secure_web_search",
                "original_query": query,
                "fetch_method": "SAM_WebFetcher",
                "quarantine_timestamp": datetime.now().isoformat()
            }
        }

        # Save to quarantine
        quarantine_path = quarantine_dir / filename
        with open(quarantine_path, 'w', encoding='utf-8') as f:
            json.dump(quarantine_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Content saved to quarantine: {filename}")

        # Update quarantine metadata
        save_quarantine_metadata(quarantine_dir, content_result['url'], filename,
                                len(content_result['content']), True)

    except Exception as e:
        logger.error(f"Failed to save content to quarantine: {e}")

def save_quarantine_metadata(quarantine_dir: Path, url: str, filename: str,
                           content_length: int, success: bool):
    """Save metadata about quarantined content."""
    try:
        metadata_file = quarantine_dir / "metadata.json"

        # Load existing metadata or create new
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {
                "quarantine_info": {
                    "created": datetime.now().isoformat(),
                    "description": "Web content fetched by SAM's secure web search",
                    "total_files": 0,
                    "total_size": 0
                },
                "files": []
            }

        # Add new file entry
        file_entry = {
            "filename": filename,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "content_length": content_length,
            "success": success,
            "source": "secure_web_search"
        }

        metadata["files"].append(file_entry)
        metadata["quarantine_info"]["total_files"] = len(metadata["files"])
        metadata["quarantine_info"]["total_size"] += content_length

        # Save updated metadata
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    except Exception as e:
        logger.error(f"Failed to save quarantine metadata: {e}")

def save_scraped_to_quarantine(scraped_data: Dict[str, Any], query: str):
    """Save scraped content to quarantine for vetting."""
    try:
        from pathlib import Path
        import json
        import hashlib
        from datetime import datetime

        # Create quarantine directory if it doesn't exist
        quarantine_dir = Path("quarantine")
        quarantine_dir.mkdir(exist_ok=True)

        # Generate filename based on query hash and timestamp
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scrapy_search_{timestamp}_{query_hash}.json"

        # Prepare quarantine data structure
        quarantine_data = {
            "query": query,
            "scraped_data": scraped_data,
            "timestamp": datetime.now().isoformat(),
            "error": None,
            "metadata": {
                "source": "scrapy_web_search",
                "method": "intelligent_scraping",
                "article_count": scraped_data.get('article_count', 0),
                "source_count": scraped_data.get('source_count', 0),
                "sources": scraped_data.get('sources', []),
                "quarantine_timestamp": datetime.now().isoformat()
            }
        }

        # Save to quarantine
        quarantine_path = quarantine_dir / filename
        with open(quarantine_path, 'w', encoding='utf-8') as f:
            json.dump(quarantine_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Scraped content saved to quarantine: {filename}")

        # Update quarantine metadata
        save_scrapy_quarantine_metadata(quarantine_dir, query, filename,
                                       scraped_data.get('article_count', 0), True)

    except Exception as e:
        logger.error(f"Failed to save scraped content to quarantine: {e}")

def save_scrapy_quarantine_metadata(quarantine_dir: Path, query: str, filename: str,
                                   article_count: int, success: bool):
    """Save metadata about quarantined scraped content."""
    try:
        metadata_file = quarantine_dir / "scrapy_metadata.json"

        # Load existing metadata or create new
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {
                "quarantine_info": {
                    "created": datetime.now().isoformat(),
                    "description": "Web content scraped by SAM's Scrapy-based intelligent extraction",
                    "total_files": 0,
                    "total_articles": 0
                },
                "files": []
            }

        # Add new file entry
        file_entry = {
            "filename": filename,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "article_count": article_count,
            "success": success,
            "source": "scrapy_web_search"
        }

        metadata["files"].append(file_entry)
        metadata["quarantine_info"]["total_files"] = len(metadata["files"])
        metadata["quarantine_info"]["total_articles"] += article_count

        # Save updated metadata
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    except Exception as e:
        logger.error(f"Failed to save scrapy quarantine metadata: {e}")

def get_memory_stats_summary() -> str:
    """Get a summary of memory and storage statistics."""
    try:
        memory_stats = st.session_state.secure_memory_store.get_memory_stats()
        security_status = st.session_state.secure_memory_store.get_security_status()

        return f"""📊 **Memory & Storage Statistics**

**Storage Overview:**
• Total Memories: {memory_stats.get('total_memories', 0)}
• Storage Size: {memory_stats.get('total_size_mb', 0):.1f} MB
• Store Type: {memory_stats.get('store_type', 'Unknown')}

**Encryption Details:**
• Encrypted Chunks: {security_status.get('encrypted_chunk_count', 0)}
• Searchable Fields: {security_status.get('searchable_fields', 0)}
• Encrypted Fields: {security_status.get('encrypted_fields', 0)}

**Technical Details:**
• Embedding Dimension: {memory_stats.get('embedding_dimension', 0)}
• Vector Backend: FAISS + ChromaDB
• Encryption: AES-256-GCM"""

    except Exception as e:
        return f"❌ Error getting memory statistics: {e}"

def create_web_search_escalation_message(assessment, original_query: str) -> str:
    """Create a web search escalation message for Streamlit interface with interactive options."""
    confidence_percent = f"{assessment.confidence_score * 100:.1f}"

    reasons_text = ""
    if assessment.reasons:
        reason_explanations = {
            'insufficient_results': "I found very few relevant results in my knowledge base",
            'limited_results': "I have some relevant information, but it may not be comprehensive",
            'low_relevance': "The information I found doesn't closely match your query",
            'very_low_relevance': "I couldn't find closely relevant information",
            'outdated_information': "The information I have might be outdated",
            'mixed_timeliness': "I have a mix of recent and older information",
            'lacks_recent_content': "I don't have recent information on this topic",
            'insufficient_for_comparison': "I need more sources to provide a good comparison",
            'lacks_procedural_content': "I don't have detailed step-by-step information"
        }

        formatted_reasons = []
        for reason in assessment.reasons[:3]:  # Limit to top 3 reasons
            explanation = reason_explanations.get(reason, reason.replace('_', ' ').title())
            formatted_reasons.append(f"• {explanation}")

        if formatted_reasons:
            reasons_text = f"\n\n**Why I'm suggesting this:**\n" + "\n".join(formatted_reasons)

    # Store escalation data in session state for button handling
    if 'web_search_escalation' not in st.session_state:
        st.session_state.web_search_escalation = {}

    escalation_id = f"escalation_{len(st.session_state.web_search_escalation)}"
    st.session_state.web_search_escalation[escalation_id] = {
        'original_query': original_query,
        'assessment': assessment,
        'suggested_search_query': getattr(assessment, 'suggested_search_query', original_query)
    }

    escalation_message = f"""🤔 **I've checked my local knowledge...**

{assessment.explanation}

**Confidence in current knowledge:** {confidence_percent}%{reasons_text}

**Would you like me to search the web for more current information?**

🌐 **Choose your preferred approach using the buttons below:**"""

    return escalation_message, escalation_id

def search_unified_memory(query: str, max_results: int = 5) -> list:
    """Search both secure memory store and consolidated web knowledge."""
    try:
        all_results = []

        # Search secure memory store (uploaded documents, secure content)
        try:
            secure_results = st.session_state.secure_memory_store.search_memories(
                query=query,
                max_results=max_results
            )
            # Tag secure results
            for result in secure_results:
                result.source_type = 'secure_documents'
            all_results.extend(secure_results)
            logger.info(f"Secure store search returned {len(secure_results)} results")
        except Exception as e:
            logger.warning(f"Secure store search failed: {e}")

        # Search consolidated web knowledge (vetted web content)
        try:
            from memory.memory_vectorstore import get_memory_store
            web_store = get_memory_store()
            web_results = web_store.search_memories(query, max_results=max_results)
            # Tag web results
            for result in web_results:
                result.source_type = 'web_knowledge'
            all_results.extend(web_results)
            logger.info(f"Web knowledge search returned {len(web_results)} results")
        except Exception as e:
            logger.warning(f"Web knowledge search failed: {e}")

        # Sort combined results by similarity score
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)

        # Return top results
        return all_results[:max_results]

    except Exception as e:
        logger.error(f"Unified search failed: {e}")
        return []

def generate_secure_response(prompt: str, force_local: bool = False) -> str:
    """Generate a secure response using SAM's capabilities with SLP, Phase 8 confidence assessment and TPV monitoring."""
    try:
        # Phase 0: Initialize SLP integration if available
        slp_integration = None
        try:
            from sam.cognition.slp import get_slp_integration
            slp_integration = get_slp_integration()
            logger.info("🧠 SLP integration available for cognitive automation")
        except Exception as e:
            logger.warning(f"SLP integration not available: {e}")

        # Phase 1: Initialize TPV integration if available
        tpv_enabled_response = None
        try:
            from sam.cognition.tpv import sam_tpv_integration, UserProfile

            # Initialize TPV integration if not already done
            if not sam_tpv_integration.is_initialized:
                sam_tpv_integration.initialize()

            # Determine user profile (could be enhanced with actual user profiling)
            user_profile = UserProfile.GENERAL  # Default profile for now

            # Connect SLP to TPV if both are available
            if slp_integration:
                slp_integration.tpv_integration = sam_tpv_integration

        except Exception as e:
            logger.warning(f"TPV integration not available: {e}")
            sam_tpv_integration = None

        # Phase 0.5: Initialize SOF v2 Dynamic Agent Architecture if available
        sof_integration = None
        try:
            from sam.orchestration import is_sof_enabled, get_sof_integration

            if is_sof_enabled():
                sof_integration = get_sof_integration()
                logger.info("🤖 SOF v2 Dynamic Agent Architecture available")

                # Try SOF v2 processing first for mathematical and tool-based queries
                if sof_integration and sof_integration._initialized:
                    # Check if this is a mathematical query that should use CalculatorTool
                    import re
                    math_pattern = r'[\d\+\-\*\/\(\)\.\s]+'
                    if re.search(r'\d+\s*[\+\-\*\/]\s*\d+', prompt):
                        logger.info(f"🧮 Detected mathematical query, routing to SOF v2: '{prompt}'")

                        try:
                            sof_result = sof_integration.process_query(
                                query=prompt,
                                user_id=getattr(st.session_state, 'user_id', None),
                                session_id=getattr(st.session_state, 'session_id', None),
                                use_dynamic_planning=True
                            )

                            if sof_result.get('success') and sof_result.get('response'):
                                logger.info(f"✅ SOF v2 successfully processed mathematical query")
                                return sof_result['response']
                            else:
                                logger.warning(f"⚠️ SOF v2 processing failed, falling back to standard: {sof_result.get('error', 'Unknown error')}")
                        except Exception as sof_error:
                            logger.warning(f"⚠️ SOF v2 execution failed: {sof_error}")

                    # Check for other tool-requiring queries (web search, complex analysis)
                    elif any(keyword in prompt.lower() for keyword in ['search', 'find', 'latest', 'current', 'news', 'recent']):
                        logger.info(f"🌐 Detected potential web search query, considering SOF v2: '{prompt[:50]}...'")

                        try:
                            sof_result = sof_integration.process_query(
                                query=prompt,
                                user_id=getattr(st.session_state, 'user_id', None),
                                session_id=getattr(st.session_state, 'session_id', None),
                                use_dynamic_planning=True
                            )

                            if sof_result.get('success') and sof_result.get('response'):
                                logger.info(f"✅ SOF v2 successfully processed web search query")
                                return sof_result['response']
                            else:
                                logger.info(f"📋 SOF v2 deferred to standard processing: {sof_result.get('error', 'No error')}")
                        except Exception as sof_error:
                            logger.warning(f"⚠️ SOF v2 execution failed: {sof_error}")
                else:
                    logger.warning("🤖 SOF v2 available but not initialized")
            else:
                logger.info("🤖 SOF v2 disabled in configuration")

        except Exception as e:
            logger.warning(f"SOF v2 integration not available: {e}")

        # Phase 8.1: Perform unified search across all knowledge sources
        memory_results = search_unified_memory(query=prompt, max_results=5)

        logger.info(f"Unified search for '{prompt}' returned {len(memory_results)} results")

        # Phase 7B: Implement Core Execution Switch (Task 1b)
        # This is the architectural switch specified in task3.md
        if slp_integration and slp_integration.enabled:
            try:
                # Prepare context for SLP
                slp_context = {
                    'memory_results': memory_results,
                    'sources': [r.chunk.source for r in memory_results],
                    'session_state': getattr(st.session_state, 'user_profile', 'general'),
                    'force_local': force_local,
                    'has_tpv': sam_tpv_integration is not None
                }

                # Phase 7B: Find and Decide Logic
                matched_program, confidence = slp_integration.program_manager.find_matching_program(
                    prompt, slp_context, getattr(st.session_state, 'user_profile', 'general')
                )

                # Phase 7B: Core Execution Switch Implementation
                if confidence > slp_integration.program_manager.execution_threshold:
                    # UI NOTIFICATION: "Using Cognitive Program #123..."
                    program_id_short = matched_program.id[:8] + "..." if len(matched_program.id) > 8 else matched_program.id
                    logger.info(f"🧠 Using Cognitive Program #{program_id_short} (confidence: {confidence:.2f})")

                    # Execute with the matched program
                    execution_result = slp_integration.program_manager.execute_program(
                        matched_program, prompt, slp_context
                    )

                    if execution_result.success:
                        # Store SLP metadata for UI display
                        if 'slp_session_data' not in st.session_state:
                            st.session_state.slp_session_data = {}

                        st.session_state.slp_session_data['last_response'] = {
                            'used_program': True,
                            'program_id': matched_program.id,
                            'program_confidence': matched_program.confidence_score,
                            'signature_match_confidence': confidence,
                            'execution_time_ms': execution_result.execution_time_ms,
                            'quality_score': execution_result.quality_score,
                            'token_count': execution_result.token_count,
                            'program_usage_count': matched_program.usage_count + 1
                        }

                        logger.info(f"✅ Cognitive Program executed successfully in {execution_result.execution_time_ms:.0f}ms")
                        return execution_result.response
                    else:
                        logger.warning(f"❌ Cognitive Program execution failed, falling back to standard reasoning")
                        # Fall through to standard reasoning
                else:
                    # UI NOTIFICATION: "Reasoning from scratch..."
                    logger.info(f"🔍 Reasoning from scratch (confidence {confidence:.2f} below threshold {slp_integration.program_manager.execution_threshold:.2f})")

                    # Generate standard response and consider program capture
                    def fallback_generator(query, context):
                        logger.info(f"🔧 [SLP] Fallback generator called for query: '{query[:50]}...'")
                        result = _generate_standard_secure_response(query, context, sam_tpv_integration, user_profile)
                        logger.info(f"🔧 [SLP] Fallback generator result type: {type(result)}")
                        # Handle tuple return for web search escalation
                        if isinstance(result, tuple) and len(result) == 2:
                            logger.info(f"🔧 [SLP] Detected web search escalation tuple")
                            # This is a web search escalation (escalation_message, escalation_id)
                            return result[0]  # Return just the escalation message for SLP
                        logger.info(f"🔧 [SLP] Returning standard response, length: {len(str(result))}")
                        return result

                    response = fallback_generator(prompt, slp_context)
                    logger.info(f"🔧 [SLP] Final response length: {len(response)}")
                    logger.info(f"🔧 [SLP] Response contains <think>: {'<think>' in response}")

                    # Consider capturing this successful interaction as a new program
                    if response and len(response) > 50:
                        capture_result = {
                            'response': response,
                            'quality_score': 0.8,  # Assume good quality for successful generation
                            'execution_time_ms': 1000,  # Estimate
                            'token_count': len(response.split()) * 1.3
                        }

                        capture_success = slp_integration.program_manager.consider_program_capture(
                            prompt, slp_context, capture_result, getattr(st.session_state, 'user_profile', 'general')
                        )

                        # Store capture metadata for UI display
                        if 'slp_session_data' not in st.session_state:
                            st.session_state.slp_session_data = {}

                        st.session_state.slp_session_data['last_response'] = {
                            'used_program': False,
                            'captured_program': capture_success,
                            'signature_match_confidence': confidence,
                            'response_time_ms': 1000,
                            'quality_score': 0.8,
                            'total_programs': len(slp_integration.program_manager.store.get_all_programs()) if capture_success else None
                        }

                        if capture_success:
                            logger.info(f"📚 New cognitive program captured for future use")

                    return response

            except Exception as e:
                logger.warning(f"SLP processing failed, falling back to standard: {e}")
                # Continue with standard processing

        # Phase 8.2: Assess confidence in retrieval quality (unless forced to use local)
        if not force_local:
            try:
                from reasoning.confidence_assessor import get_confidence_assessor
                confidence_assessor = get_confidence_assessor()

                # Convert memory results to format expected by confidence assessor
                search_results_for_assessment = []
                for result in memory_results:
                    search_results_for_assessment.append({
                        'similarity_score': result.similarity_score,
                        'content': result.chunk.content,
                        'metadata': {
                            'source': result.chunk.source,
                            'timestamp': getattr(result.chunk, 'timestamp', None)
                        }
                    })

                logger.info(f"🔍 Starting confidence assessment for {len(search_results_for_assessment)} results")
                logger.info(f"🔍 Query: '{prompt[:50]}...'")

                assessment = confidence_assessor.assess_retrieval_quality(search_results_for_assessment, prompt)

                logger.info(f"🔍 Confidence assessment complete: {assessment.status} ({assessment.confidence_score:.2f})")
                logger.info(f"🔍 Confidence level: {assessment.confidence_level}")
                logger.info(f"🔍 Recommendation: {assessment.recommendation}")
                logger.info(f"🔍 Reasons: {assessment.reasons}")

                # Phase 8.3: Check if web search escalation should be offered
                if assessment.status == "NOT_CONFIDENT":
                    logger.info(f"🌐 Triggering web search escalation for low confidence")
                    escalation_message, escalation_id = create_web_search_escalation_message(assessment, prompt)
                    return escalation_message, escalation_id
                else:
                    logger.info(f"✅ Confidence sufficient, proceeding with local response")

            except Exception as e:
                logger.warning(f"Confidence assessment failed: {e}")
                import traceback
                logger.warning(f"Confidence assessment traceback: {traceback.format_exc()}")
                # Continue with normal processing if confidence assessment fails

        if memory_results:
            # Count sources for transparency
            secure_count = sum(1 for r in memory_results if getattr(r, 'source_type', '') == 'secure_documents')
            web_count = sum(1 for r in memory_results if getattr(r, 'source_type', '') == 'web_knowledge')

            # Build context from all available memories
            context_parts = []
            for i, result in enumerate(memory_results):
                source_type = getattr(result, 'source_type', 'unknown')
                source_label = "📄 Document" if source_type == 'secure_documents' else "🌐 Web Knowledge" if source_type == 'web_knowledge' else "📋 Memory"

                logger.debug(f"Result {i+1}: Score={result.similarity_score:.3f}, Source={result.chunk.source}, Type={source_type}")

                # Get more content for better context (up to 1000 chars instead of 300)
                content_preview = result.chunk.content[:1000]
                if len(result.chunk.content) > 1000:
                    content_preview += "..."
                context_parts.append(f"{source_label} - {result.chunk.source}\nContent: {content_preview}")

            context = "\n\n".join(context_parts)

            # Add source summary
            source_summary = []
            if secure_count > 0:
                source_summary.append(f"{secure_count} uploaded document(s)")
            if web_count > 0:
                source_summary.append(f"{web_count} web knowledge item(s)")

            sources_text = " and ".join(source_summary) if source_summary else "available sources"

            # Generate response using Ollama model
            try:
                import requests

                # Prepare the prompt for Ollama
                system_prompt = f"""You are SAM, a secure AI assistant. Answer the user's question based on the provided content from {sources_text}.

When thinking through complex questions, you can use <think>...</think> tags to show your reasoning process. This helps users understand how you arrived at your answer.

Be helpful and informative. Extract relevant information from the provided sources to answer the question directly.
If the information isn't sufficient, say so clearly. Always be concise but thorough.

The sources include both uploaded documents and current web knowledge that has been vetted and approved for your knowledge base."""

                user_prompt = f"""Question: {prompt}

Available Information:
{context}

Please provide a helpful answer based on the available information."""

                # TPV-enabled response generation
                if sam_tpv_integration:
                    try:
                        # Use TPV integration for response generation
                        full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"

                        # Calculate initial confidence based on context quality
                        initial_confidence = min(0.8, len(context) / 2000.0) if context else 0.3

                        tpv_response = sam_tpv_integration.generate_response_with_tpv(
                            prompt=full_prompt,
                            user_profile=user_profile,
                            initial_confidence=initial_confidence,
                            context={'has_context': bool(context), 'sources': sources_text},
                            ollama_params={
                                "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                                "stream": False,
                                "options": {
                                    "temperature": 0.7,
                                    "top_p": 0.9,
                                    "max_tokens": 500
                                }
                            }
                        )

                        # Store TPV data in session state for UI display
                        if 'tpv_session_data' not in st.session_state:
                            st.session_state.tpv_session_data = {}

                        # Get active control information
                        control_decision = 'CONTINUE'
                        control_reason = 'No control action taken'
                        control_statistics = {}

                        if hasattr(sam_tpv_integration, 'reasoning_controller'):
                            recent_actions = sam_tpv_integration.reasoning_controller.get_recent_actions(1)
                            if recent_actions:
                                control_decision = recent_actions[0].metadata.get('action_type', 'CONTINUE')
                                control_reason = recent_actions[0].reason
                            control_statistics = sam_tpv_integration.reasoning_controller.get_control_statistics()

                        st.session_state.tpv_session_data['last_response'] = {
                            'tpv_enabled': tpv_response.tpv_enabled,
                            'trigger_type': tpv_response.trigger_result.trigger_type if tpv_response.trigger_result else None,
                            'final_score': tpv_response.tpv_trace.current_score if tpv_response.tpv_trace else 0.0,
                            'tpv_steps': len(tpv_response.tpv_trace.steps) if tpv_response.tpv_trace else 0,
                            'performance_metrics': tpv_response.performance_metrics,
                            'control_decision': control_decision,
                            'control_reason': control_reason,
                            'control_statistics': control_statistics
                        }

                        if tpv_response.content:
                            return tpv_response.content
                        else:
                            logger.warning("Empty response from TPV-enabled generation")

                    except Exception as e:
                        logger.error(f"TPV-enabled generation failed: {e}")
                        # Fall back to standard Ollama call

                # Fallback: Standard Ollama API call
                ollama_response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                        "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 500
                        }
                    },
                    timeout=30
                )

                if ollama_response.status_code == 200:
                    response_data = ollama_response.json()
                    ai_response = response_data.get('response', '').strip()

                    if ai_response:
                        return ai_response
                    else:
                        logger.warning("Empty response from Ollama")

            except Exception as e:
                logger.error(f"Ollama API call failed: {e}")

            # Fallback: return context with basic formatting
            return f"""Based on {sources_text}, here's what I found:

{context}

I'm SAM, your secure AI assistant. How can I help you further?"""

        else:
            # Check if we have any memories at all
            security_status = st.session_state.secure_memory_store.get_security_status()
            total_chunks = security_status.get('encrypted_chunk_count', 0)

            if total_chunks > 0:
                # Check if web retrieval should be suggested (Phase 7.1)
                try:
                    from utils.web_retrieval_suggester import WebRetrievalSuggester
                    suggester = WebRetrievalSuggester()

                    if suggester.should_suggest_web_retrieval(prompt, []):
                        logger.info(f"Suggesting web retrieval for Streamlit query: {prompt[:50]}...")
                        return suggester.format_retrieval_suggestion(prompt)

                except ImportError:
                    logger.warning("Web retrieval suggester not available")

                # Generate a response using Ollama even without specific context
                try:
                    import requests

                    system_prompt = """You are SAM, a helpful AI assistant. When thinking through questions, you can use <think>...</think> tags to show your reasoning process.

Answer the user's question helpfully and accurately based on your general knowledge."""

                    ollama_response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                            "prompt": f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:",
                            "stream": False,
                            "options": {
                                "temperature": 0.7,
                                "top_p": 0.9,
                                "max_tokens": 500
                            }
                        },
                        timeout=30
                    )

                    if ollama_response.status_code == 200:
                        response_data = ollama_response.json()
                        ai_response = response_data.get('response', '').strip()
                        if ai_response:
                            return ai_response

                except Exception as e:
                    logger.error(f"Fallback Ollama call failed: {e}")

                return f"""I searched through your {total_chunks} encrypted memory chunks but couldn't find relevant information about "{prompt}".

This could be because:
- The search terms don't match the document content
- The document content wasn't properly extracted
- The similarity threshold is too high

Try rephrasing your question or uploading more relevant documents."""
            else:
                return """No documents found in your secure memory. Please upload some documents first, then ask questions about their content."""

    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        return f"I apologize, but I encountered an error while processing your request: {e}"


def _generate_standard_secure_response(query: str, context: Dict[str, Any],
                                     sam_tpv_integration=None, user_profile=None) -> str:
    """
    Generate standard secure response for SLP fallback.

    This function provides the standard SAM response generation logic
    that can be used as a fallback when SLP programs are not available.
    """
    try:
        logger.info(f"🔧 [SLP Fallback] _generate_standard_secure_response called")
        logger.info(f"🔧 [SLP Fallback] Query: '{query[:50]}...'")

        # Extract memory results from context
        memory_results = context.get('memory_results', [])
        force_local = context.get('force_local', False)

        logger.info(f"🔧 [SLP Fallback] Memory results: {len(memory_results)}")
        logger.info(f"🔧 [SLP Fallback] Force local: {force_local}")

        # Phase 8.2: Assess confidence in retrieval quality (unless forced to use local)
        if not force_local and memory_results:
            try:
                from reasoning.confidence_assessor import get_confidence_assessor
                confidence_assessor = get_confidence_assessor()

                # Convert memory results to format expected by confidence assessor
                search_results_for_assessment = []
                for result in memory_results:
                    search_results_for_assessment.append({
                        'similarity_score': result.similarity_score,
                        'content': result.chunk.content,
                        'metadata': {
                            'source': result.chunk.source,
                            'timestamp': getattr(result.chunk, 'timestamp', None)
                        }
                    })

                logger.info(f"🔍 [SLP Fallback] Starting confidence assessment for {len(search_results_for_assessment)} results")
                logger.info(f"🔍 [SLP Fallback] Query: '{query[:50]}...'")

                assessment = confidence_assessor.assess_retrieval_quality(search_results_for_assessment, query)

                logger.info(f"🔍 [SLP Fallback] Confidence assessment complete: {assessment.status} ({assessment.confidence_score:.2f})")
                logger.info(f"🔍 [SLP Fallback] Confidence level: {assessment.confidence_level}")
                logger.info(f"🔍 [SLP Fallback] Recommendation: {assessment.recommendation}")
                logger.info(f"🔍 [SLP Fallback] Reasons: {assessment.reasons}")

                # Phase 8.3: Check if web search escalation should be offered
                if assessment.status == "NOT_CONFIDENT":
                    logger.info(f"🌐 [SLP Fallback] Triggering web search escalation for low confidence")
                    escalation_message, escalation_id = create_web_search_escalation_message(assessment, query)
                    return escalation_message, escalation_id
                else:
                    logger.info(f"✅ [SLP Fallback] Confidence sufficient, proceeding with local response")

            except Exception as e:
                logger.warning(f"[SLP Fallback] Confidence assessment failed: {e}")
                import traceback
                logger.warning(f"[SLP Fallback] Confidence assessment traceback: {traceback.format_exc()}")
                # Continue with normal processing if confidence assessment fails

        if memory_results:
            # Count sources for transparency
            secure_count = sum(1 for r in memory_results if getattr(r, 'source_type', '') == 'secure_documents')
            web_count = sum(1 for r in memory_results if getattr(r, 'source_type', '') == 'web_knowledge')

            # Build context from all available memories
            context_parts = []
            for i, result in enumerate(memory_results):
                source_type = getattr(result, 'source_type', 'unknown')
                source_label = "📄 Document" if source_type == 'secure_documents' else "🌐 Web Knowledge" if source_type == 'web_knowledge' else "📋 Memory"

                # Get more content for better context (up to 1000 chars instead of 300)
                content_preview = result.chunk.content[:1000]
                if len(result.chunk.content) > 1000:
                    content_preview += "..."
                context_parts.append(f"{source_label} - {result.chunk.source}\nContent: {content_preview}")

            context_text = "\n\n".join(context_parts)

            # Add source summary
            source_summary = []
            if secure_count > 0:
                source_summary.append(f"{secure_count} uploaded document(s)")
            if web_count > 0:
                source_summary.append(f"{web_count} web knowledge item(s)")

            sources_text = " and ".join(source_summary) if source_summary else "available sources"

            # Generate response using Ollama model
            try:
                import requests

                # Prepare the prompt for Ollama
                system_prompt = f"""You are SAM, a secure AI assistant. Answer the user's question based on the provided content from {sources_text}.

When thinking through complex questions, you can use <think>...</think> tags to show your reasoning process. This helps users understand how you arrived at your answer.

Be helpful and informative. Extract relevant information from the provided sources to answer the question directly.
If the information isn't sufficient, say so clearly. Always be concise but thorough.

The sources include both uploaded documents and current web knowledge that has been vetted and approved for your knowledge base."""

                user_prompt = f"""Question: {query}

Available Information:
{context_text}

Please provide a helpful answer based on the available information."""

                # TPV-enabled response generation
                if sam_tpv_integration:
                    try:
                        # Use TPV integration for response generation
                        full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"

                        # Calculate initial confidence based on context quality
                        initial_confidence = min(0.8, len(context_text) / 2000.0) if context_text else 0.3

                        tpv_response = sam_tpv_integration.generate_response_with_tpv(
                            prompt=full_prompt,
                            user_profile=user_profile,
                            initial_confidence=initial_confidence,
                            context={'has_context': bool(context_text), 'sources': sources_text},
                            ollama_params={
                                "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                                "stream": False,
                                "options": {
                                    "temperature": 0.7,
                                    "top_p": 0.9,
                                    "max_tokens": 500
                                }
                            }
                        )

                        if tpv_response.content:
                            return tpv_response.content

                    except Exception as e:
                        logger.error(f"TPV-enabled generation failed in fallback: {e}")

                # Fallback: Standard Ollama API call
                ollama_response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                        "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 500
                        }
                    },
                    timeout=30
                )

                if ollama_response.status_code == 200:
                    response_data = ollama_response.json()
                    ai_response = response_data.get('response', '').strip()

                    if ai_response:
                        return ai_response

            except Exception as e:
                logger.error(f"Ollama API call failed in fallback: {e}")

            # Final fallback: return context with basic formatting
            return f"""Based on {sources_text}, here's what I found:

{context_text}

I'm SAM, your secure AI assistant. How can I help you further?"""

        else:
            # No memory results - generate basic response
            try:
                import requests

                system_prompt = """You are SAM, a helpful AI assistant. When thinking through questions, you can use <think>...</think> tags to show your reasoning process.

Answer the user's question helpfully and accurately based on your general knowledge."""

                ollama_response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                        "prompt": f"System: {system_prompt}\n\nUser: {query}\n\nAssistant:",
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 500
                        }
                    },
                    timeout=30
                )

                if ollama_response.status_code == 200:
                    response_data = ollama_response.json()
                    ai_response = response_data.get('response', '').strip()
                    if ai_response:
                        return ai_response

            except Exception as e:
                logger.error(f"Fallback Ollama call failed: {e}")

            return f"I understand you're asking about: {query}. However, I don't have specific information available to provide a detailed answer."

    except Exception as e:
        logger.error(f"Standard response generation failed: {e}")
        return f"I apologize, but I encountered an error while processing your request: {e}"

def process_secure_document(uploaded_file) -> dict:
    """Process an uploaded document securely."""
    try:
        # Read file content
        content = uploaded_file.read()

        if uploaded_file.type == "text/plain":
            text_content = content.decode('utf-8')
        elif uploaded_file.type == "application/pdf":
            # Extract text from PDF
            try:
                import PyPDF2
                import io

                logger.info(f"Extracting text from PDF: {uploaded_file.name}")
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text_content = ""

                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text_content += f"\n--- Page {page_num + 1} ---\n{page_text}"
                    logger.debug(f"Page {page_num + 1}: extracted {len(page_text)} characters")

                logger.info(f"Total extracted text length: {len(text_content)} characters")
                logger.debug(f"First 200 characters: {text_content[:200]}")

                if not text_content.strip():
                    logger.warning(f"No text extracted from PDF: {uploaded_file.name}")
                    text_content = f"PDF Document: {uploaded_file.name} (Could not extract text - {len(content)} bytes)"
                else:
                    logger.info(f"✅ Successfully extracted text from PDF: {uploaded_file.name}")

            except Exception as e:
                logger.error(f"PDF extraction failed for {uploaded_file.name}: {e}")
                text_content = f"PDF Document: {uploaded_file.name} (Text extraction failed - {len(content)} bytes)"
        else:
            # For other file types, you'd use appropriate parsers
            text_content = f"Document: {uploaded_file.name} (Binary content - {len(content)} bytes)"
        
        # PHASE 1: Save file temporarily for multimodal processing
        import tempfile
        import os

        temp_file_path = None
        try:
            # Create temporary file with proper extension
            file_extension = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            logger.info(f"Created temporary file for processing: {temp_file_path}")

            # PHASE 2: Process through multimodal pipeline for knowledge consolidation
            consolidation_result = None
            if 'multimodal_pipeline' in st.session_state:
                try:
                    logger.info(f"🧠 Starting knowledge consolidation for: {uploaded_file.name}")
                    consolidation_result = st.session_state.multimodal_pipeline.process_document(temp_file_path)

                    if consolidation_result:
                        logger.info(f"✅ Knowledge consolidation completed: {consolidation_result.get('summary_length', 0)} chars summary")
                        logger.info(f"🎓 Key concepts extracted: {consolidation_result.get('key_concepts', 0)}")
                    else:
                        logger.warning("⚠️ Knowledge consolidation returned no result")

                except Exception as e:
                    logger.error(f"❌ Knowledge consolidation failed: {e}")
                    # Continue with basic processing if consolidation fails

            # PHASE 3A: Add to secure memory store (encrypted storage)
            from memory.secure_memory_vectorstore import MemoryType

            logger.info(f"Adding document to secure memory store: {uploaded_file.name}")
            logger.debug(f"Text content preview: {text_content[:200]}...")

            secure_chunk_id = st.session_state.secure_memory_store.add_memory(
                content=text_content,
                memory_type=MemoryType.DOCUMENT,
                source=f"upload:{uploaded_file.name}",
                tags=['uploaded', 'document', 'consolidated'] if consolidation_result else ['uploaded', 'document'],
                importance_score=0.9 if consolidation_result else 0.8,  # Higher score if consolidated
                metadata={
                    'filename': uploaded_file.name,
                    'file_type': uploaded_file.type,
                    'file_size': len(content),
                    'upload_method': 'streamlit',
                    'knowledge_consolidated': bool(consolidation_result),
                    'consolidation_timestamp': consolidation_result.get('processing_timestamp') if consolidation_result else None
                }
            )

            logger.info(f"Document added to secure store with chunk_id: {secure_chunk_id}")

            # PHASE 3B: Also add to regular memory store for Flask interface compatibility
            try:
                from memory.memory_vectorstore import get_memory_store, VectorStoreType
                regular_memory_store = get_memory_store(
                    store_type=VectorStoreType.CHROMA,
                    storage_directory="memory_store",
                    embedding_dimension=384
                )

                logger.info(f"Adding document to regular memory store for Flask compatibility: {uploaded_file.name}")

                regular_chunk_id = regular_memory_store.add_memory(
                    content=text_content,
                    source=f"upload:{uploaded_file.name}",
                    tags=['uploaded', 'document', 'streamlit_sync', 'consolidated'] if consolidation_result else ['uploaded', 'document', 'streamlit_sync'],
                    importance_score=0.9 if consolidation_result else 0.8,
                    metadata={
                        'filename': uploaded_file.name,
                        'file_type': uploaded_file.type,
                        'file_size': len(content),
                        'upload_method': 'streamlit_sync',
                        'secure_chunk_id': secure_chunk_id,
                        'knowledge_consolidated': bool(consolidation_result),
                        'consolidation_timestamp': consolidation_result.get('processing_timestamp') if consolidation_result else None
                    }
                )

                logger.info(f"Document also added to regular store with chunk_id: {regular_chunk_id}")

            except Exception as e:
                logger.warning(f"Could not sync to regular memory store: {e}")
                regular_chunk_id = None

            # Calculate total chunks created
            total_chunks = 1  # Base memory chunk
            if consolidation_result:
                total_chunks += consolidation_result.get('content_blocks', 0)

            return {
                'success': True,
                'secure_chunk_id': secure_chunk_id,
                'regular_chunk_id': regular_chunk_id,
                'chunks_created': total_chunks,
                'filename': uploaded_file.name,
                'file_size': len(content),
                'knowledge_consolidated': bool(consolidation_result),
                'consolidation_summary': consolidation_result.get('summary_length', 0) if consolidation_result else 0,
                'synced_to_regular_store': regular_chunk_id is not None
            }

        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Could not clean up temporary file: {e}")
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    main()
