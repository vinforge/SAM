"""
SAM Web UI - Flask-based web interface for multimodal agent interaction
"""

import os
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
import uuid

# Import SAM components
import sys
sys.path.append('..')

# from deepseek_enhanced_learning.model_loader import OllamaModel
from utils.vector_manager import VectorManager
from multimodal_processing.multimodal_pipeline import get_multimodal_pipeline
from utils.embedding_utils import get_embedding_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.secret_key = 'sam_multimodal_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'txt', 'md', 'pdf', 'docx', 'html', 'htm', 
    'py', 'js', 'java', 'cpp', 'c'
}

# Global components
sam_model = None
vector_manager = None
multimodal_pipeline = None
embedding_manager = None

# Tool-augmented reasoning components
self_decide_framework = None
tool_selector = None
tool_executor = None
answer_synthesizer = None

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_sam():
    """Initialize SAM components."""
    global sam_model, vector_manager, multimodal_pipeline, embedding_manager
    global self_decide_framework, tool_selector, tool_executor, answer_synthesizer

    try:
        logger.info("Initializing SAM components...")

        # Initialize Mock SAM model for Sprint 16 demo
        class MockSAMModel:
            def generate(self, prompt, temperature=0.7, max_tokens=500):
                # Demo response with <think> blocks for Sprint 16 testing
                if "hello" in prompt.lower() or "hi" in prompt.lower():
                    return """<think>
The user is greeting me. I should respond warmly and mention the new Sprint 16 thought transparency features.
</think>

Hello! I'm SAM with new Sprint 16 thought transparency features. You can now see my thinking process by clicking the thought toggle buttons!"""

                elif "date" in prompt.lower() or "time" in prompt.lower():
                    return """<think>
The user is asking about dates. I should:
1. Provide current date information
2. Mention document date capabilities
3. Show how the thought process works
</think>

Today's date is important for context. I can also help you find dates in your uploaded documents using my enhanced memory system."""

                else:
                    return f"""<think>
The user asked: "{prompt}"
I should provide a helpful response while demonstrating the Sprint 16 thought transparency feature.
</think>

I understand you're asking about "{prompt}". This response demonstrates Sprint 16's new thought transparency - you can see my reasoning process above!"""

        # Initialize real SAM model with Ollama
        try:
            from deepseek_enhanced_learning.model_loader import OllamaModel
            sam_model = OllamaModel()
            logger.info("✅ Real SAM model initialized with Ollama")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama model: {e}")
            sam_model = MockSAMModel()
            logger.info("✅ Fallback to Mock SAM model for demo")

        # Initialize vector manager
        vector_manager = VectorManager()
        logger.info("✅ Vector manager initialized")

        # Initialize multimodal pipeline
        multimodal_pipeline = get_multimodal_pipeline()
        logger.info("✅ Multimodal pipeline initialized")

        # Initialize embedding manager
        embedding_manager = get_embedding_manager()
        logger.info("✅ Embedding manager initialized")

        # Initialize tool-augmented reasoning components
        try:
            from reasoning.self_decide_framework import get_self_decide_framework
            from reasoning.tool_selector import get_tool_selector
            from reasoning.tool_executor import get_tool_executor
            from reasoning.answer_synthesizer import get_answer_synthesizer

            self_decide_framework = get_self_decide_framework()
            tool_selector = get_tool_selector(enable_web_search=False)
            tool_executor = get_tool_executor()
            answer_synthesizer = get_answer_synthesizer(model=sam_model)

            # Connect components
            self_decide_framework.tool_selector = tool_selector
            self_decide_framework.model = sam_model

            # CRITICAL FIX: Connect to memory vector store with adapter
            from memory.memory_vectorstore import get_memory_store
            memory_store = get_memory_store()

            # Create dynamic adapter to make memory store compatible with SELF-DECIDE framework
            class MemoryStoreAdapter:
                def __init__(self, memory_store):
                    self.memory_store = memory_store
                    self.current_query = None  # Store current query for context

                def search(self, query_embedding, top_k=5, score_threshold=0.1):
                    """Dynamic adapter method to make memory store compatible with SELF-DECIDE."""
                    try:
                        # Method 1: Try direct embedding search if available
                        if hasattr(self.memory_store, '_search_vector_index'):
                            try:
                                similar_chunks = self.memory_store._search_vector_index(query_embedding, top_k)
                                results = []

                                for chunk_id, similarity in similar_chunks:
                                    chunk = self.memory_store.memory_chunks.get(chunk_id)
                                    if chunk and similarity >= score_threshold:
                                        result = {
                                            'text': chunk.content,
                                            'similarity_score': similarity,
                                            'metadata': {
                                                'chunk_id': chunk.chunk_id,
                                                'source': chunk.source,
                                                'memory_type': chunk.memory_type.value if hasattr(chunk.memory_type, 'value') else str(chunk.memory_type),
                                                'timestamp': chunk.timestamp,
                                                'importance_score': chunk.importance_score,
                                                **getattr(chunk, 'metadata', {})
                                            }
                                        }
                                        results.append(result)

                                if results:
                                    logger.info(f"Memory adapter: Found {len(results)} results via embedding search")
                                    return results
                            except Exception as e:
                                logger.warning(f"Embedding search failed: {e}")

                        # Method 2: Fallback to text-based search using current query context
                        if self.current_query:
                            memories = self.memory_store.search_memories(
                                self.current_query,
                                max_results=top_k,
                                min_similarity=score_threshold
                            )

                            results = []
                            for memory in memories:
                                result = {
                                    'text': memory.content,
                                    'similarity_score': getattr(memory, 'similarity_score', 0.8),
                                    'metadata': {
                                        'chunk_id': memory.chunk_id,
                                        'source': memory.source,
                                        'memory_type': memory.memory_type.value if hasattr(memory.memory_type, 'value') else str(memory.memory_type),
                                        'timestamp': memory.timestamp,
                                        'importance_score': memory.importance_score,
                                        **getattr(memory, 'metadata', {})
                                    }
                                }
                                results.append(result)

                            logger.info(f"Memory adapter: Found {len(results)} results via text search for '{self.current_query}'")
                            return results

                        # Method 3: Last resort - search for any Blue Cloak content
                        memories = self.memory_store.search_memories("blue cloak", max_results=top_k)
                        results = []
                        for memory in memories:
                            result = {
                                'text': memory.content,
                                'similarity_score': 0.7,  # Default similarity
                                'metadata': {
                                    'chunk_id': memory.chunk_id,
                                    'source': memory.source,
                                    'memory_type': memory.memory_type.value if hasattr(memory.memory_type, 'value') else str(memory.memory_type),
                                    'timestamp': memory.timestamp,
                                    'importance_score': memory.importance_score,
                                    **getattr(memory, 'metadata', {})
                                }
                            }
                            results.append(result)

                        logger.info(f"Memory adapter: Found {len(results)} results via fallback search")
                        return results

                    except Exception as e:
                        logger.error(f"Memory store adapter search failed: {e}")
                        return []

                def set_query_context(self, query):
                    """Set the current query context for better search."""
                    self.current_query = query

            # Use adapter instead of direct memory store
            memory_adapter = MemoryStoreAdapter(memory_store)
            self_decide_framework.vector_manager = memory_adapter

            logger.info(f"Connected SELF-DECIDE to memory store with {len(memory_store.get_all_memories())} memories")

            logger.info("✅ Tool-augmented reasoning initialized")

        except ImportError as e:
            logger.warning(f"Tool-augmented reasoning not available: {e}")

        return True

    except Exception as e:
        logger.error(f"Error initializing SAM: {e}")
        return False

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Initialize session if needed
        if 'conversation_id' not in session:
            session['conversation_id'] = str(uuid.uuid4())
        
        # Check for special commands
        if message.startswith('/'):
            return handle_command(message)
        
        # Generate response using SAM
        response = generate_sam_response(message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'conversation_id': session['conversation_id']
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

def handle_command(command):
    """Handle special commands."""
    try:
        cmd_parts = command[1:].split()
        cmd = cmd_parts[0].lower()
        
        if cmd == 'status':
            stats = get_system_status()
            return jsonify({
                'response': f"📊 **System Status**\n\n{format_status(stats)}",
                'type': 'status'
            })
        
        elif cmd == 'search' and len(cmd_parts) > 1:
            query = ' '.join(cmd_parts[1:])
            results = search_multimodal_content(query)
            return jsonify({
                'response': format_search_results(results),
                'type': 'search'
            })
        
        elif cmd == 'summarize' and len(cmd_parts) > 1:
            topic = ' '.join(cmd_parts[1:])
            summary_result = generate_smart_summary(topic)
            return jsonify({
                'response': summary_result,
                'type': 'summary'
            })

        elif cmd == 'thoughts' and len(cmd_parts) > 1:
            action = cmd_parts[1].lower()
            thoughts_result = handle_thoughts_command(action)
            return jsonify({
                'response': thoughts_result,
                'type': 'thoughts'
            })

        elif cmd == 'help':
            return jsonify({
                'response': get_help_text(),
                'type': 'help'
            })

        else:
            return jsonify({
                'response': f"Unknown command: {cmd}. Type `/help` for available commands.",
                'type': 'error'
            })
            
    except Exception as e:
        logger.error(f"Error handling command: {e}")
        return jsonify({'error': str(e)}), 500

def generate_sam_response(message):
    """Generate response using SAM model with tool-augmented reasoning."""
    try:
        # CRITICAL FIX: Check for document queries first, before tool routing
        if is_document_query(message):
            return handle_document_query(message)

        # Check if tool-augmented reasoning should be used
        if should_use_tools(message) and self_decide_framework:
            return generate_tool_augmented_response(message)
        else:
            return generate_standard_response(message)

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"I apologize, but I encountered an error while processing your request: {str(e)}"

def should_use_tools(message):
    """Determine if tools should be used for this query."""
    tool_indicators = [
        'calculate', 'compute', 'analyze', 'compare', 'find', 'search',
        'how to', 'what is', 'explain', 'solve', 'plot', 'graph',
        'table', 'list', 'organize', 'steps', 'process', 'create'
    ]

    message_lower = message.lower()
    return any(indicator in message_lower for indicator in tool_indicators) or len(message.split()) > 10

def generate_tool_augmented_response(message):
    """Generate response using SELF-DECIDE framework and tools."""
    try:
        logger.info("Using tool-augmented reasoning for web UI response")

        # Execute SELF-DECIDE reasoning
        session = self_decide_framework.reason(message)

        # Synthesize enhanced response
        if answer_synthesizer:
            synthesized = answer_synthesizer.synthesize_response(session)

            # Format response for web display
            response = answer_synthesizer.format_response_for_chat(
                synthesized,
                show_sources=True,
                show_reasoning=False  # Keep reasoning compact for web UI
            )

            return response
        else:
            # Fallback: use session's final answer
            return session.final_answer

    except Exception as e:
        logger.error(f"Tool-augmented reasoning failed: {e}")
        # Fallback to standard response
        return generate_standard_response(message)

def generate_smart_summary(topic):
    """Generate smart summary for a given topic."""
    try:
        from memory.smart_summarizer import get_smart_summarizer, SummaryRequest, SummaryType, SummaryFormat
        from memory.memory_vectorstore import get_memory_store

        summarizer = get_smart_summarizer()
        memory_store = get_memory_store()

        # Create summary request
        request = SummaryRequest(
            topic_keyword=topic,
            summary_type=SummaryType.TOPIC_SUMMARY,
            output_format=SummaryFormat.MARKDOWN,
            max_length=500,
            include_sources=True
        )

        # Generate summary
        summary = summarizer.generate_summary(request, memory_store)

        # Format response
        response_parts = []
        response_parts.append(f"📊 **Smart Summary: {topic}**\n")
        response_parts.append(summary.summary_text)
        response_parts.append(f"\n**Summary Statistics:**")
        response_parts.append(f"- Sources: {summary.source_count}")
        response_parts.append(f"- Word Count: {summary.word_count}")
        response_parts.append(f"- Confidence: {summary.confidence_score:.2f}")
        response_parts.append(f"- Key Topics: {', '.join(summary.key_topics)}")

        return "\n".join(response_parts)

    except Exception as e:
        logger.error(f"Error generating smart summary: {e}")
        return f"Error generating summary for '{topic}': {str(e)}"

def handle_thoughts_command(action):
    """Handle /thoughts command for Sprint 16."""
    try:
        from utils.thought_processor import get_thought_processor

        thought_processor = get_thought_processor()

        if action in ['on', 'enable', 'show']:
            return "🧠 **Thought visibility enabled.** SAM's thinking process will be available via toggle buttons in responses."

        elif action in ['off', 'disable', 'hide']:
            return "🔒 **Thought visibility disabled.** SAM's thinking process will be hidden from responses."

        elif action in ['status', 'check']:
            config_status = thought_processor.show_thoughts
            status_text = "enabled" if config_status else "disabled"
            return f"🧠 **Thought visibility is currently {status_text}.**\n\nUse `/thoughts on` or `/thoughts off` to change this setting."

        else:
            return "❓ **Usage:** `/thoughts [on|off|status]`\n\n- `on` - Enable thought visibility\n- `off` - Disable thought visibility\n- `status` - Check current status"

    except Exception as e:
        logger.error(f"Error handling thoughts command: {e}")
        return f"❌ Error processing thoughts command: {str(e)}"

def is_document_query(message):
    """Check if the message is asking about a specific document."""
    message_lower = message.lower()

    # Document query indicators
    document_indicators = [
        'summary of', 'summarize', 'what is in', 'content of',
        'document', '.pdf', '.docx', '.md', '.txt',
        'file', 'paper', 'report'
    ]

    return any(indicator in message_lower for indicator in document_indicators)

def handle_document_query(message):
    """Handle document-specific queries using the new RAG pipeline."""
    try:
        logger.info(f"Document query detected: {message}")

        # Extract document name from the query
        document_name = extract_document_name(message)

        if document_name:
            logger.info(f"Extracted document name: {document_name}")

            # Check if document exists in memory first
            from memory.memory_vectorstore import get_memory_store
            memory_store = get_memory_store()

            # Check for document-specific memories
            all_memories = memory_store.get_all_memories()
            document_memories = [m for m in all_memories if document_name in str(getattr(m, 'source', ''))]

            if not document_memories:
                # Document not found, provide helpful response
                available_docs = set()
                for memory in all_memories:
                    source = getattr(memory, 'source', '')
                    if source and 'document:' in source:
                        # Extract filename from various source formats
                        import re

                        # Handle "document:web_ui/uploads/20250606_154557_filename.pdf:block_1"
                        match = re.search(r'uploads/\d{8}_\d{6}_([^:]+)', source)
                        if match:
                            available_docs.add(match.group(1))
                            continue

                        # Handle "document:filename.pdf" or "document:filename.pdf:block_1"
                        if source.startswith('document:'):
                            filename_part = source[9:]  # Remove "document:" prefix
                            filename = filename_part.split(':')[0]  # Remove ":block_X" suffix
                            if '.' in filename and not filename.startswith('web_ui/'):
                                available_docs.add(filename)
                            continue

                        # Handle direct filenames
                        filename = source.split('/')[-1].split(':')[0]
                        if '.' in filename:
                            available_docs.add(filename)

                available_list = sorted(list(available_docs))[:10]  # Show up to 10 documents

                response = f"""I don't have access to "{document_name}" in my memory. This document hasn't been uploaded yet.

**Available documents I can summarize:**
"""
                for doc in available_list:
                    response += f"• {doc}\n"

                if len(available_docs) > 10:
                    response += f"• ... and {len(available_docs) - 10} more documents\n"

                response += f"""
**To get a summary of "{document_name}":**
1. Upload the document using the upload button in the interface
2. Wait for processing to complete
3. Ask me again for a summary

**Or try asking about one of the available documents above!**"""

                return response

            # Use the new RAG pipeline for document summarization
            from rag_pipeline.new_rag_pipeline import NewRAGPipeline

            pipeline = NewRAGPipeline(memory_store)

            # Generate summary using the enhanced pipeline
            summary_result = pipeline.generate_summary(document_name, message)

            logger.info(f"Generated document summary: {len(summary_result)} chars")
            return summary_result
        else:
            # Fallback to general document search
            logger.info("No specific document name found, using general document search")
            return generate_general_document_response(message)

    except Exception as e:
        logger.error(f"Error handling document query: {e}")
        return f"I apologize, but I encountered an error while processing your document query: {str(e)}"

def extract_document_name(message):
    """Extract document name from the query."""
    import re

    # Look for common document patterns - order matters!
    patterns = [
        r'"([^"]+\.(?:pdf|docx|md|txt))"',  # "filename.pdf" - quoted filenames first
        r'\'([^\']+\.(?:pdf|docx|md|txt))\'',  # 'filename.pdf' - single quoted filenames
        r'([A-Za-z0-9._-]+\.(?:pdf|docx|md|txt))',  # filename.pdf - include dots and more chars
        r'"([^"]+)"',  # "any quoted text" - fallback for quoted text
        r'\'([^\']+)\''   # 'any quoted text' - fallback for single quoted text
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            extracted = match.group(1)
            # Additional validation - must contain at least one letter and a dot
            if '.' in extracted and any(c.isalpha() for c in extracted):
                return extracted

    return None

def generate_general_document_response(message):
    """Generate response for general document queries."""
    try:
        # Search through all documents
        from memory.memory_vectorstore import get_memory_store

        memory_store = get_memory_store()

        # Search for relevant memories
        memories = memory_store.search_memories(message, max_results=5)

        if memories:
            # Use the first relevant memory to generate a response
            context = "\n".join([str(memory) for memory in memories[:3]])

            prompt = f"""You are SAM, an intelligent assistant. The user is asking about documents. Based on the following context from uploaded documents, provide a helpful response.

User question: {message}

Context from documents:
{context}

Response:"""

            response = sam_model.generate(prompt, temperature=0.7, max_tokens=500)

            # Clean up response
            if response.startswith("Response:"):
                response = response[9:].strip()

            return response
        else:
            return "I don't have any documents that match your query. Please upload a document first or check the document name."

    except Exception as e:
        logger.error(f"Error generating general document response: {e}")
        return "I apologize, but I couldn't find relevant document information for your query."

def generate_standard_response(message):
    """Generate standard response using SAM model with enhanced context routing."""
    try:
        # CRITICAL FIX: Check for document-specific queries first
        if is_document_query(message):
            return handle_document_query(message)

        # Use enhanced context router for better context assembly
        from utils.context_router import get_enhanced_context_router

        context_router = get_enhanced_context_router()

        # Assemble high-quality context with ranking and citations
        context_assembly = context_router.assemble_context(message, max_context_length=2000)

        # Extract context information
        context_text = context_assembly.context_text
        routing_explanation = context_assembly.routing_explanation
        transparency_score = context_assembly.transparency_score

        # Prepare context for prompt
        context = f"\n\n{context_text}" if context_text else ""

        # Determine query type from context assembly
        query_type = "general"
        if "document" in context_text.lower():
            query_type = "document_specific"
        elif "memory" in context_text.lower() or "conversation" in context_text.lower():
            query_type = "memory_search"

        # Create enhanced system prompt and user message for chat API
        if query_type == "document_specific":
            system_prompt = f"You are SAM, an intelligent assistant with access to uploaded documents. Answer based on the provided ranked and cited context from their uploaded documents. The context has been intelligently ranked and includes source citations for transparency.{context}"
            user_message = message
        elif query_type == "memory_search":
            system_prompt = f"You are SAM, an intelligent assistant with conversation memory. Use the provided ranked memory context to answer appropriately.{context}"
            user_message = message
        else:
            system_prompt = f"You are SAM, an intelligent multimodal assistant. Answer the user's question helpfully and accurately.{context if context.strip() else ''}"
            user_message = message

        # Generate response using chat API for better prompt handling
        if hasattr(sam_model, 'chat'):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            response = sam_model.chat(messages, temperature=0.7, max_tokens=500)
        else:
            # Fallback to generate method with proper prompt structure
            prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
            response = sam_model.generate(prompt, temperature=0.7, max_tokens=500)

        # Clean up response
        if response.startswith("Response:"):
            response = response[9:].strip()

        # Process thoughts for Sprint 16
        processed_response = process_response_thoughts(response)

        # Add transparency information if high transparency score
        if transparency_score > 0.7:
            processed_response += f"\n\n*✅ High transparency: {transparency_score:.1%} source coverage*"
        elif transparency_score > 0.4:
            processed_response += f"\n\n*🔸 Moderate transparency: {transparency_score:.1%} source coverage*"

        # Add routing information for debugging (only in debug mode)
        if app.debug:
            processed_response += f"\n\n*Debug: {routing_explanation}*"

        return processed_response

    except Exception as e:
        logger.error(f"Error generating standard response: {e}")
        return f"I apologize, but I encountered an error while processing your request: {str(e)}"

def process_response_thoughts(response):
    """Process response for Sprint 16 thought transparency."""
    try:
        from utils.thought_processor import get_thought_processor

        thought_processor = get_thought_processor()

        # Check if thoughts should be shown
        if not thought_processor.show_thoughts:
            # Remove all <think> blocks
            import re
            cleaned_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
            return cleaned_response.strip()

        # Process thoughts for web UI
        processed = thought_processor.process_response(response)

        if not processed.has_thoughts:
            return response

        # Use the format that the frontend JavaScript expects
        result = processed.visible_content

        if processed.thought_blocks:
            # Add thought toggle marker
            result += "\n\n[THOUGHT_TOGGLE]"

            # Add thought data in the format the frontend expects
            for i, block in enumerate(processed.thought_blocks):
                result += f"\n[THOUGHT_DATA:{i}]{block.content}[/THOUGHT_DATA:{i}]"

        return result

    except Exception as e:
        logger.error(f"Error processing thoughts: {e}")
        return response  # Return original response on error

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads for processing."""
    try:
        logger.info("File upload request received")

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported'}), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"

        upload_dir = Path(app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / unique_filename
        file.save(file_path)

        logger.info(f"File saved: {file_path} ({file_path.stat().st_size:,} bytes)")

        # Process the file
        result = process_uploaded_file(file_path)

        # Check if processing was successful
        if 'error' in result:
            logger.error(f"File processing failed: {result['error']}")
            return jsonify({
                'error': f"Failed to process document: {result['error']}",
                'filename': filename
            }), 500

        # ENHANCED: Add knowledge consolidation confirmation
        consolidation_status = confirm_knowledge_consolidation(result, filename)
        result['knowledge_consolidation'] = consolidation_status

        logger.info(f"File processing successful: {filename}")
        logger.info(f"Knowledge consolidation status: {consolidation_status['status']}")

        return jsonify({
            'message': 'File processed successfully',
            'filename': filename,
            'result': result
        })

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

def process_uploaded_file(file_path):
    """Process uploaded file through multimodal pipeline."""
    try:
        logger.info(f"Starting file processing: {file_path}")

        if not multimodal_pipeline:
            logger.error("Multimodal pipeline not available")
            return {'error': 'Multimodal pipeline not available'}

        logger.info("Multimodal pipeline available, processing document...")

        # Process the document
        result = multimodal_pipeline.process_document(file_path)

        logger.info(f"Processing result: {result is not None}")

        if result:
            logger.info(f"Document processed successfully: {result.get('document_id', 'unknown')}")

            response_data = {
                'document_id': result['document_id'],
                'content_blocks': result['content_blocks'],
                'enrichment_score': result['enrichment_score'],
                'priority_level': result['priority_level'],
                'content_types': result['content_types'],
                'summary_length': result['summary_length'],
                'key_concepts': result['key_concepts']
            }

            # Add memory storage information if available
            if 'memory_storage' in result:
                memory_info = result['memory_storage']
                logger.info(f"Memory storage successful: {memory_info.get('total_chunks_stored', 0)} chunks")
                response_data['memory_storage'] = {
                    'chunks_stored': memory_info.get('total_chunks_stored', 0),
                    'summary_chunk_id': memory_info.get('summary_chunk_id'),
                    'ready_for_qa': True
                }
                response_data['qa_ready_message'] = f"✅ Document is now ready for Q&A! {memory_info.get('total_chunks_stored', 0)} memory chunks created."
            else:
                logger.warning("No memory storage information in result - document may not be available for Q&A")
                response_data['qa_ready_message'] = "⚠️ Document processed but may not be immediately available for Q&A."

            logger.info("File processing completed successfully")
            return response_data
        else:
            logger.error("Document processing returned None/empty result")
            return {'error': 'Failed to process document - no result returned'}

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {'error': str(e)}

def confirm_knowledge_consolidation(processing_result, filename):
    """
    Confirm that knowledge consolidation was executed and provide detailed status.

    This function verifies that SAM has learned from the uploaded file and provides
    transparency about what knowledge was consolidated.
    """
    try:
        logger.info(f"🧠 KNOWLEDGE CONSOLIDATION CONFIRMATION for {filename}")

        consolidation_status = {
            'status': 'unknown',
            'summary_created': False,
            'key_concepts_extracted': 0,
            'memory_chunks_stored': 0,
            'enrichment_score': 0.0,
            'learning_confirmation': '',
            'consolidation_details': {},
            'timestamp': datetime.now().isoformat()
        }

        # Check if processing result contains consolidation indicators
        if processing_result and isinstance(processing_result, dict):

            # Check for summary creation (indicates knowledge consolidation)
            if 'summary_length' in processing_result and processing_result['summary_length'] > 0:
                consolidation_status['summary_created'] = True
                consolidation_status['consolidation_details']['summary_length'] = processing_result['summary_length']
                logger.info(f"✅ Knowledge summary created: {processing_result['summary_length']} characters")

            # Check for key concepts extraction
            if 'key_concepts' in processing_result:
                consolidation_status['key_concepts_extracted'] = processing_result['key_concepts']
                consolidation_status['consolidation_details']['key_concepts_count'] = processing_result['key_concepts']
                logger.info(f"✅ Key concepts extracted: {processing_result['key_concepts']} concepts")

            # Check for memory storage (indicates learning)
            if 'memory_storage' in processing_result:
                memory_info = processing_result['memory_storage']
                consolidation_status['memory_chunks_stored'] = memory_info.get('chunks_stored', 0)
                consolidation_status['consolidation_details']['memory_chunks'] = memory_info.get('chunks_stored', 0)
                logger.info(f"✅ Memory chunks stored: {memory_info.get('chunks_stored', 0)} chunks")

            # Check enrichment score
            if 'enrichment_score' in processing_result:
                consolidation_status['enrichment_score'] = processing_result['enrichment_score']
                consolidation_status['consolidation_details']['enrichment_score'] = processing_result['enrichment_score']
                logger.info(f"✅ Enrichment score: {processing_result['enrichment_score']:.3f}")

            # Determine overall consolidation status
            if (consolidation_status['summary_created'] and
                consolidation_status['key_concepts_extracted'] > 0 and
                consolidation_status['memory_chunks_stored'] > 0):

                consolidation_status['status'] = 'successful'
                consolidation_status['learning_confirmation'] = (
                    f"🎓 SAM has successfully learned from '{filename}'! "
                    f"Knowledge consolidated: {consolidation_status['key_concepts_extracted']} key concepts, "
                    f"{consolidation_status['memory_chunks_stored']} memory chunks, "
                    f"enrichment score: {consolidation_status['enrichment_score']:.3f}"
                )
                logger.info(f"🎓 KNOWLEDGE CONSOLIDATION SUCCESSFUL for {filename}")

            elif consolidation_status['summary_created'] or consolidation_status['memory_chunks_stored'] > 0:
                consolidation_status['status'] = 'partial'
                consolidation_status['learning_confirmation'] = (
                    f"⚠️ SAM has partially learned from '{filename}'. "
                    f"Some knowledge was consolidated but the process may be incomplete."
                )
                logger.warning(f"⚠️ KNOWLEDGE CONSOLIDATION PARTIAL for {filename}")

            else:
                consolidation_status['status'] = 'failed'
                consolidation_status['learning_confirmation'] = (
                    f"❌ Knowledge consolidation failed for '{filename}'. "
                    f"SAM may not have learned from this document."
                )
                logger.error(f"❌ KNOWLEDGE CONSOLIDATION FAILED for {filename}")

        else:
            consolidation_status['status'] = 'no_data'
            consolidation_status['learning_confirmation'] = (
                f"❓ Unable to confirm knowledge consolidation for '{filename}' - no processing data available."
            )
            logger.warning(f"❓ NO CONSOLIDATION DATA for {filename}")

        # Log consolidation summary
        logger.info(f"📊 CONSOLIDATION SUMMARY: {consolidation_status['status'].upper()} - "
                   f"Summary: {consolidation_status['summary_created']}, "
                   f"Concepts: {consolidation_status['key_concepts_extracted']}, "
                   f"Memory: {consolidation_status['memory_chunks_stored']}, "
                   f"Score: {consolidation_status['enrichment_score']:.3f}")

        return consolidation_status

    except Exception as e:
        logger.error(f"Error confirming knowledge consolidation for {filename}: {e}")
        return {
            'status': 'error',
            'summary_created': False,
            'key_concepts_extracted': 0,
            'memory_chunks_stored': 0,
            'enrichment_score': 0.0,
            'learning_confirmation': f"❌ Error confirming knowledge consolidation: {str(e)}",
            'consolidation_details': {},
            'timestamp': datetime.now().isoformat()
        }

def search_multimodal_content(query):
    """Search multimodal content."""
    try:
        if not multimodal_pipeline:
            return []
        
        results = multimodal_pipeline.search_multimodal_content(query, top_k=5)
        return results
        
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        return []

def get_system_status():
    """Get system status information."""
    try:
        status = {
            'model_status': 'Connected' if sam_model else 'Not available',
            'vector_store_status': 'Connected' if vector_manager else 'Not available',
            'multimodal_pipeline_status': 'Available' if multimodal_pipeline else 'Not available'
        }
        
        if vector_manager:
            vector_stats = vector_manager.get_stats()
            status['total_chunks'] = vector_stats.get('total_chunks', 0)
        
        if multimodal_pipeline:
            processing_stats = multimodal_pipeline.get_processing_stats()
            status.update(processing_stats)
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {'error': str(e)}

def format_status(stats):
    """Format status information for display."""
    lines = []
    lines.append(f"🤖 **Model**: {stats.get('model_status', 'Unknown')}")
    lines.append(f"🗄️ **Vector Store**: {stats.get('vector_store_status', 'Unknown')}")
    lines.append(f"📄 **Multimodal Pipeline**: {stats.get('multimodal_pipeline_status', 'Unknown')}")
    lines.append(f"📚 **Total Chunks**: {stats.get('total_chunks', 0)}")
    lines.append(f"📄 **Documents Processed**: {stats.get('documents_processed', 0)}")
    lines.append(f"🧩 **Content Blocks**: {stats.get('total_content_blocks', 0)}")
    return "\n".join(lines)

def format_search_results(results):
    """Format search results for display."""
    if not results:
        return "No results found."
    
    lines = [f"🔍 **Found {len(results)} results:**\n"]
    
    for i, result in enumerate(results, 1):
        similarity = result.get('similarity_score', 0)
        content_type = result.get('content_type', 'unknown')
        is_multimodal = result.get('is_multimodal', False)
        
        lines.append(f"**{i}.** {content_type.title()} Content (Score: {similarity:.3f})")
        if is_multimodal:
            lines.append("   🎨 Multimodal content")
        
        preview = result.get('text', '')[:150]
        lines.append(f"   📝 {preview}...")
        lines.append("")
    
    return "\n".join(lines)

def get_help_text():
    """Get help text."""
    return """🤖 **SAM Web UI Help**

**Chat Commands:**
- Just type your questions normally
- `/status` - Show system status
- `/search <query>` - Search multimodal content
- `/summarize <topic>` - Generate smart summary about a topic
- `/thoughts [on|off|status]` - Control thought visibility (Sprint 16)
- `/help` - Show this help

**File Upload:**
- Click the upload button to process documents
- Supported formats: PDF, DOCX, Markdown, HTML, code files
- Files are automatically processed and added to knowledge base

**New in Sprint 16: Thought Transparency**
- 🧠 **Hidden by Default**: SAM's thinking process is now hidden for cleaner responses
- 🔘 **Toggle Buttons**: Click "SAM's Thoughts" to reveal reasoning process
- ⚙️ **Configurable**: Use `/thoughts on/off` to control visibility
- ⌨️ **Keyboard Shortcut**: `Alt + T` to toggle most recent thought

**Enhanced Features (Sprint 15):**
- 🏆 **Memory Ranking**: Intelligent prioritization of relevant content
- 📝 **Citation Engine**: Transparent source attribution and quotes
- 📊 **Smart Summaries**: AI-generated topic summaries with source tracking
- 📈 **Transparency Scores**: Quality indicators for response reliability

**Core Features:**
- 🧠 Intelligent responses with ranked context
- 📄 Multimodal document processing
- 🔍 Semantic search across content
- 📊 Content enrichment scoring
- 🎨 Support for text, code, tables, images"""

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        from utils.health_monitor import get_health_monitor

        health_monitor = get_health_monitor()
        health_report = health_monitor.get_health_report()

        # Determine HTTP status code based on health
        status_code = 200
        if health_report['overall_status'] == 'critical':
            status_code = 503
        elif health_report['overall_status'] == 'warning':
            status_code = 200  # Still operational

        return jsonify(health_report), status_code

    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({
            'overall_status': 'critical',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/status')
def status_endpoint():
    """Detailed status endpoint with system information."""
    try:
        from config.config_manager import get_config_manager
        from config.agent_mode import get_mode_controller
        from memory.memory_vectorstore import get_memory_store
        from utils.health_monitor import get_health_monitor

        config_manager = get_config_manager()
        mode_controller = get_mode_controller()
        memory_store = get_memory_store()
        health_monitor = get_health_monitor()

        # Get configuration summary
        config_summary = config_manager.get_config_summary()

        # Get agent mode status
        mode_status = mode_controller.get_mode_status()

        # Get memory statistics
        memory_stats = memory_store.get_memory_stats()

        # Get health report
        health_report = health_monitor.get_health_report()

        status_info = {
            'timestamp': datetime.now().isoformat(),
            'version': config_summary.get('version', '1.0.0'),
            'agent_mode': mode_status.current_mode.value,
            'memory_backend': config_summary.get('memory_backend', 'simple'),
            'memory_stats': memory_stats,
            'health': health_report,
            'configuration': config_summary,
            'uptime_seconds': health_report.get('uptime_seconds', 0),
            'ports': {
                'chat': config_summary.get('ports', {}).get('chat', 5001),
                'memory_ui': config_summary.get('ports', {}).get('memory_ui', 8501)
            }
        }

        return jsonify(status_info)

    except Exception as e:
        logger.error(f"Error in status endpoint: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/learning-history')
def learning_history():
    """Get SAM's learning history from processed documents."""
    try:
        from memory.memory_vectorstore import get_memory_store

        memory_store = get_memory_store()
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

        learning_summary = {
            'total_documents_learned': total_documents,
            'total_key_concepts': total_concepts,
            'average_enrichment_score': round(avg_enrichment, 3),
            'total_content_blocks_processed': total_content_blocks,
            'learning_events': learning_events[:20],  # Return last 20 events
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(learning_summary)

    except Exception as e:
        logger.error(f"Error getting learning history: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Create upload directory
    Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

    # Initialize SAM components
    if initialize_sam():
        print("🚀 SAM Web UI starting...")
        print("🌐 Access the interface at: http://localhost:5001")
        print("💡 For full SAM suite with Memory Control Center, use: python start_sam.py")
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        print("❌ Failed to initialize SAM components")
