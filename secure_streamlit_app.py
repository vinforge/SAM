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
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📚 Documents", "🧠 Memory", "🛡️ Security"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_document_interface()
    
    with tab3:
        render_memory_interface()
    
    with tab4:
        render_security_dashboard()

def initialize_secure_sam():
    """Initialize SAM components with security integration."""

    # Initialize secure memory store with security manager
    if 'secure_memory_store' not in st.session_state:
        from memory.secure_memory_vectorstore import get_secure_memory_store, VectorStoreType

        # Create secure memory store with security manager connection
        st.session_state.secure_memory_store = get_secure_memory_store(
            store_type=VectorStoreType.CHROMA,
            storage_directory="streamlit_data",
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

def render_chat_interface():
    """Render the chat interface."""
    st.header("💬 Secure Chat")
    
    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
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
                    response = generate_secure_response(prompt)
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"❌ Sorry, I encountered an error: {e}"
                    st.markdown(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

def render_document_interface():
    """Render the document upload and processing interface."""
    st.header("📚 Secure Document Processing")
    
    # File upload
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
                    st.info(f"📊 {result.get('chunks_created', 0)} encrypted memory chunks created")
                    
                    # Show processing details
                    with st.expander("📋 Processing Details"):
                        st.json(result)
                else:
                    st.error(f"❌ Document processing failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Document processing error: {e}")
    
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
            
    except Exception as e:
        st.warning(f"Could not load document statistics: {e}")

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

                results = st.session_state.secure_memory_store.search_memories(
                    query=search_query,
                    max_results=10
                )

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

def generate_secure_response(prompt: str) -> str:
    """Generate a secure response using SAM's capabilities with Ollama model."""
    try:
        # Use secure memory store for context
        memory_results = st.session_state.secure_memory_store.search_memories(
            query=prompt,
            max_results=5
        )

        logger.info(f"Search for '{prompt}' returned {len(memory_results)} results")

        if memory_results:
            # Build context from encrypted memories
            context_parts = []
            for i, result in enumerate(memory_results):
                logger.debug(f"Result {i+1}: Score={result.similarity_score:.3f}, Source={result.chunk.source}")
                # Get more content for better context (up to 1000 chars instead of 300)
                content_preview = result.chunk.content[:1000]
                if len(result.chunk.content) > 1000:
                    content_preview += "..."
                context_parts.append(f"Source: {result.chunk.source}\nContent: {content_preview}")

            context = "\n\n".join(context_parts)

            # Generate response using Ollama model
            try:
                import requests

                # Prepare the prompt for Ollama
                system_prompt = """You are SAM, a secure AI assistant. Answer the user's question based on the provided encrypted memory content.

Be helpful and informative. Extract relevant information from the provided sources to answer the question directly.
If the information isn't sufficient, say so clearly. Always be concise but thorough.

Do not mention that the data is encrypted or from memory - just answer naturally based on the content."""

                user_prompt = f"""Question: {prompt}

Available Information:
{context}

Please provide a helpful answer based on the available information."""

                # Call Ollama API
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
            return f"""Based on your documents, here's what I found:

{context}

I'm SAM, your secure AI assistant. How can I help you further?"""

        else:
            # Check if we have any memories at all
            security_status = st.session_state.secure_memory_store.get_security_status()
            total_chunks = security_status.get('encrypted_chunk_count', 0)

            if total_chunks > 0:
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
        
        # Add to secure memory store
        from memory.secure_memory_vectorstore import MemoryType

        logger.info(f"Adding document to secure memory store: {uploaded_file.name}")
        logger.debug(f"Text content preview: {text_content[:200]}...")

        chunk_id = st.session_state.secure_memory_store.add_memory(
            content=text_content,
            memory_type=MemoryType.DOCUMENT,
            source=f"upload:{uploaded_file.name}",
            tags=['uploaded', 'document'],
            importance_score=0.8,
            metadata={
                'filename': uploaded_file.name,
                'file_type': uploaded_file.type,
                'file_size': len(content),
                'upload_method': 'streamlit'
            }
        )

        logger.info(f"Document added with chunk_id: {chunk_id}")
        
        return {
            'success': True,
            'chunk_id': chunk_id,
            'chunks_created': 1,
            'filename': uploaded_file.name,
            'file_size': len(content)
        }
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    main()
