#!/usr/bin/env python3
"""
SAM Pro Registration Web Interface

Simple web interface for users to register for SAM Pro activation keys.
Provides a user-friendly form and integrates with the key distribution system.

Author: SAM Development Team
Version: 1.0.0
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add SAM to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the key distribution system
try:
    from scripts.key_distribution_system import KeyDistributionManager
except ImportError:
    st.error("❌ Key distribution system not available")
    st.stop()

def main():
    """Main registration interface."""
    st.set_page_config(
        page_title="SAM Pro Registration",
        page_icon="🧠",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 SAM Pro Registration</h1>
        <p>Get your activation key for the world's most advanced AI memory system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    ## 🎯 **What is SAM Pro?**
    
    SAM Pro unlocks premium features in SAM (Secure AI Memory), including:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h4>🧠 Dream Canvas</h4>
            <p>Interactive memory visualization with cognitive synthesis and UMAP projections</p>
        </div>
        
        <div class="feature-box">
            <h4>🎛️ TPV Active Control</h4>
            <p>Advanced reasoning process monitoring with real-time intervention</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h4>📁 Cognitive Automation</h4>
            <p>Bulk document processing and automated analysis workflows</p>
        </div>
        
        <div class="feature-box">
            <h4>🔬 Dissonance Monitoring</h4>
            <p>Real-time cognitive conflict detection and hallucination prevention</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Registration form
    st.markdown("## 📝 **Register for SAM Pro**")
    
    with st.form("registration_form"):
        st.markdown("### Your Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Full Name *",
                placeholder="John Doe",
                help="Your full name for the activation key"
            )
            
            email = st.text_input(
                "Email Address *",
                placeholder="john@example.com",
                help="We'll send your activation key to this email"
            )
        
        with col2:
            organization = st.text_input(
                "Organization",
                placeholder="Acme Corporation",
                help="Your company or organization (optional)"
            )
            
            use_case = st.selectbox(
                "Primary Use Case",
                [
                    "",
                    "Research & Development",
                    "Business Intelligence",
                    "Educational/Academic",
                    "Personal Knowledge Management",
                    "Content Creation",
                    "Data Analysis",
                    "Software Development",
                    "Other"
                ],
                help="How do you plan to use SAM Pro?"
            )
        
        # Additional use case details
        if use_case == "Other":
            use_case_details = st.text_area(
                "Please describe your use case",
                placeholder="Describe how you plan to use SAM Pro...",
                height=100
            )
        else:
            use_case_details = ""
        
        # Terms and conditions
        st.markdown("### Terms & Conditions")
        
        terms_accepted = st.checkbox(
            "I agree to the SAM Pro terms of use and privacy policy",
            help="By checking this box, you agree to use SAM Pro in accordance with our terms"
        )
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Register for SAM Pro",
            use_container_width=True
        )
        
        if submitted:
            # Validation
            errors = []
            
            if not name.strip():
                errors.append("Name is required")
            
            if not email.strip() or '@' not in email:
                errors.append("Valid email address is required")
            
            if not terms_accepted:
                errors.append("You must accept the terms and conditions")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Process registration
                with st.spinner("🔄 Processing your registration..."):
                    try:
                        manager = KeyDistributionManager()
                        
                        final_use_case = use_case
                        if use_case == "Other" and use_case_details:
                            final_use_case = f"Other: {use_case_details}"
                        
                        result = manager.register_user(
                            email=email.strip(),
                            name=name.strip(),
                            organization=organization.strip(),
                            use_case=final_use_case
                        )
                        
                        if result["success"]:
                            st.markdown("""
                            <div class="success-box">
                                <h3>🎉 Registration Successful!</h3>
                                <p>Your SAM Pro activation key has been sent to your email address.</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            **Registration Details:**
                            - **Email:** {email}
                            - **Registration ID:** `{result.get('registration_id', 'N/A')}`
                            
                            **Next Steps:**
                            1. Check your email for the activation key
                            2. Download SAM from [GitHub](https://github.com/forge-1825/SAM)
                            3. Follow the installation guide
                            4. Enter your activation key in SAM's interface
                            """)
                            
                            st.balloons()
                            
                        else:
                            st.error(f"❌ Registration failed: {result['message']}")
                            
                            if result.get('error_code') == 'ALREADY_REGISTERED':
                                st.info("💡 If you've already registered, check your email for the activation key.")
                    
                    except Exception as e:
                        st.error(f"❌ System error: {str(e)}")
                        st.info("💡 Please try again later or contact support.")
    
    # Footer information
    st.markdown("---")
    
    st.markdown("""
    ## 🔗 **Useful Links**
    
    - **📥 Download SAM:** [github.com/forge-1825/SAM](https://github.com/forge-1825/SAM)
    - **📖 Installation Guide:** Check the README.md in the repository
    - **🔐 Encryption Setup:** ENCRYPTION_SETUP_GUIDE.md
    - **🐛 Support:** [GitHub Issues](https://github.com/forge-1825/SAM/issues)
    
    ## ❓ **Frequently Asked Questions**
    
    **Q: How long does it take to receive my activation key?**  
    A: Activation keys are sent immediately upon registration. Check your spam folder if you don't see it.
    
    **Q: Can I use SAM without a Pro key?**  
    A: Yes! SAM's core features are free. Pro features add advanced capabilities like Dream Canvas and cognitive automation.
    
    **Q: Is my data secure?**  
    A: Absolutely! SAM uses enterprise-grade AES-256 encryption and operates completely locally on your machine.
    
    **Q: Can I use SAM Pro commercially?**  
    A: Yes, SAM Pro can be used for commercial purposes. See our terms of use for details.
    """)
    
    # Contact information
    st.markdown("""
    ---
    
    **Need help?** Contact us at: **sam-pro@forge1825.net**
    
    *SAM Pro - Secure AI Memory | The Future of AI Consciousness*
    """)

if __name__ == "__main__":
    main()
