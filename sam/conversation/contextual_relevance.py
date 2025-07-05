#!/usr/bin/env python3
"""
SAM Contextual Relevance Engine - Task 31 Phase 1
=================================================

Implements intelligent conversation threading through vector-based relevance
calculation. Automatically detects topic changes and manages conversation
context to prevent pollution while maintaining coherence.

Part of Task 31: Conversational Intelligence Engine
Author: SAM Development Team
Version: 1.0.0
"""

import logging
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class RelevanceResult:
    """Result of contextual relevance calculation."""
    similarity_score: float
    is_relevant: bool
    threshold_used: float
    calculation_method: str
    confidence: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ConversationThread:
    """Represents an archived conversation thread."""
    thread_id: str
    title: str
    messages: List[Dict[str, Any]]
    created_at: str
    last_updated: str
    message_count: int
    topic_keywords: List[str]
    embedding_summary: Optional[List[float]]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationThread':
        return cls(**data)

class ContextualRelevanceEngine:
    """
    Intelligent conversation threading engine using vector-based relevance.
    
    Features:
    - Vector similarity calculation for topic continuity
    - Automatic conversation archiving and titling
    - Configurable relevance thresholds
    - Graceful degradation for robustness
    - Integration with MEMOIR episodic memory
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Contextual Relevance Engine.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(f"{__name__}.ContextualRelevanceEngine")
        
        # Default configuration
        self.config = {
            'relevance_threshold': 0.6,
            'temporal_decay_factor': 0.1,
            'max_conversation_length': 50,
            'auto_archive_enabled': True,
            'embedding_model': 'sentence-transformers',
            'title_generation_temperature': 0.3,
            'fallback_to_related': True,  # Graceful degradation
            'min_conversation_length': 3,  # Minimum turns before archiving
            'storage_directory': 'conversation_threads'
        }
        
        if config:
            self.config.update(config)
        
        # Initialize embedding system
        self.embedding_system = None
        self._initialize_embedding_system()
        
        # Storage setup
        self.storage_dir = Path(self.config['storage_directory'])
        self.storage_dir.mkdir(exist_ok=True)
        
        self.logger.info("ContextualRelevanceEngine initialized")
    
    def calculate_relevance(self, new_query: str, conversation_buffer: List[Dict[str, Any]]) -> RelevanceResult:
        """
        Calculate contextual relevance between new query and conversation buffer.
        
        Args:
            new_query: The new user query
            conversation_buffer: List of conversation turns
            
        Returns:
            RelevanceResult with similarity score and decision
        """
        try:
            if not conversation_buffer:
                # No existing conversation - always relevant (start new)
                return RelevanceResult(
                    similarity_score=1.0,
                    is_relevant=True,
                    threshold_used=self.config['relevance_threshold'],
                    calculation_method='empty_buffer',
                    confidence=1.0,
                    metadata={'reason': 'No existing conversation buffer'}
                )
            
            # Check minimum conversation length
            if len(conversation_buffer) < self.config['min_conversation_length']:
                return RelevanceResult(
                    similarity_score=1.0,
                    is_relevant=True,
                    threshold_used=self.config['relevance_threshold'],
                    calculation_method='insufficient_history',
                    confidence=0.8,
                    metadata={'reason': f'Conversation too short ({len(conversation_buffer)} turns)'}
                )
            
            # Extract text content from conversation buffer
            buffer_text = self._extract_buffer_text(conversation_buffer)
            
            if not buffer_text.strip():
                # Empty buffer content - treat as new conversation
                return RelevanceResult(
                    similarity_score=0.0,
                    is_relevant=False,
                    threshold_used=self.config['relevance_threshold'],
                    calculation_method='empty_content',
                    confidence=0.9,
                    metadata={'reason': 'No meaningful content in buffer'}
                )
            
            # Calculate vector similarity
            similarity_score = self._calculate_vector_similarity(new_query, buffer_text)
            
            # Apply temporal weighting (recent messages matter more)
            weighted_score = self._apply_temporal_weighting(similarity_score, conversation_buffer)
            
            # Determine relevance
            threshold = self.config['relevance_threshold']
            is_relevant = weighted_score >= threshold
            
            # Calculate confidence based on score distance from threshold
            confidence = self._calculate_confidence(weighted_score, threshold)
            
            return RelevanceResult(
                similarity_score=weighted_score,
                is_relevant=is_relevant,
                threshold_used=threshold,
                calculation_method='vector_similarity',
                confidence=confidence,
                metadata={
                    'raw_similarity': similarity_score,
                    'temporal_adjustment': weighted_score - similarity_score,
                    'buffer_length': len(conversation_buffer),
                    'buffer_text_length': len(buffer_text)
                }
            )
            
        except Exception as e:
            self.logger.warning(f"Relevance calculation failed: {e}")
            
            # Graceful degradation - assume relevant to maintain conversation flow
            if self.config['fallback_to_related']:
                return RelevanceResult(
                    similarity_score=0.7,  # Safe fallback score
                    is_relevant=True,
                    threshold_used=self.config['relevance_threshold'],
                    calculation_method='fallback_related',
                    confidence=0.3,
                    metadata={'error': str(e), 'fallback_reason': 'Calculation failed, assuming related'}
                )
            else:
                return RelevanceResult(
                    similarity_score=0.0,
                    is_relevant=False,
                    threshold_used=self.config['relevance_threshold'],
                    calculation_method='fallback_unrelated',
                    confidence=0.3,
                    metadata={'error': str(e), 'fallback_reason': 'Calculation failed, assuming unrelated'}
                )
    
    def archive_conversation_thread(self, conversation_buffer: List[Dict[str, Any]], 
                                  force_title: Optional[str] = None) -> ConversationThread:
        """
        Archive a conversation thread with automatic title generation.
        
        Args:
            conversation_buffer: List of conversation turns to archive
            force_title: Optional manual title override
            
        Returns:
            ConversationThread object with generated metadata
        """
        try:
            if not conversation_buffer:
                # Handle empty buffer gracefully with fallback
                logger.warning("Archiving empty conversation buffer - creating fallback thread")
                fallback_title = f"Empty Chat from {datetime.now().strftime('%Y-%m-%d %H:%M')}"

                thread = ConversationThread(
                    thread_id=f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    title=fallback_title,
                    messages=[],
                    created_at=datetime.now().isoformat(),
                    last_updated=datetime.now().isoformat(),
                    message_count=0,
                    topic_keywords=[],
                    embedding_summary=None,
                    metadata={
                        'title_generation_method': 'fallback_timestamp',
                        'archival_timestamp': datetime.now().isoformat(),
                        'archival_reason': 'empty_buffer_fallback'
                    }
                )

                # Store the fallback thread
                self._store_conversation_thread(thread)
                return thread
            
            # Generate unique thread ID
            thread_id = self._generate_thread_id(conversation_buffer)
            
            # Generate title (or use forced title)
            if force_title:
                title = force_title
                title_method = 'manual'
            else:
                title = self._generate_conversation_title(conversation_buffer)
                title_method = 'auto_generated'
            
            # Extract topic keywords
            topic_keywords = self._extract_topic_keywords(conversation_buffer)
            
            # Generate embedding summary for future relevance calculations
            embedding_summary = self._generate_embedding_summary(conversation_buffer)
            
            # Create conversation thread
            thread = ConversationThread(
                thread_id=thread_id,
                title=title,
                messages=conversation_buffer.copy(),
                created_at=conversation_buffer[0].get('timestamp', datetime.now().isoformat()),
                last_updated=datetime.now().isoformat(),
                message_count=len(conversation_buffer),
                topic_keywords=topic_keywords,
                embedding_summary=embedding_summary,
                metadata={
                    'title_generation_method': title_method,
                    'archival_timestamp': datetime.now().isoformat(),
                    'archival_reason': 'contextual_relevance_break'
                }
            )
            
            # Store thread persistently
            self._store_conversation_thread(thread)
            
            # Store in MEMOIR episodic memory (Phase 1 integration)
            self._store_in_memoir(thread)
            
            self.logger.info(f"Archived conversation thread: '{title}' ({len(conversation_buffer)} messages)")
            
            return thread
            
        except Exception as e:
            self.logger.error(f"Failed to archive conversation thread: {e}")
            
            # Graceful degradation - create minimal thread with timestamp title
            fallback_title = f"Chat from {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            thread = ConversationThread(
                thread_id=self._generate_thread_id(conversation_buffer),
                title=fallback_title,
                messages=conversation_buffer.copy(),
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                message_count=len(conversation_buffer),
                topic_keywords=[],
                embedding_summary=None,
                metadata={
                    'title_generation_method': 'fallback_timestamp',
                    'archival_timestamp': datetime.now().isoformat(),
                    'archival_reason': 'error_fallback',
                    'error': str(e)
                }
            )
            
            # Still try to store the thread
            try:
                self._store_conversation_thread(thread)
            except:
                self.logger.error("Failed to store fallback conversation thread")
            
            return thread
    
    def get_archived_threads(self, limit: Optional[int] = None) -> List[ConversationThread]:
        """
        Retrieve archived conversation threads.
        
        Args:
            limit: Optional limit on number of threads to return
            
        Returns:
            List of ConversationThread objects, sorted by last_updated desc
        """
        try:
            threads = []
            
            # Load threads from storage
            for thread_file in self.storage_dir.glob("thread_*.json"):
                try:
                    with open(thread_file, 'r') as f:
                        thread_data = json.load(f)
                    
                    thread = ConversationThread.from_dict(thread_data)
                    threads.append(thread)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load thread {thread_file}: {e}")
            
            # Sort by last_updated (most recent first)
            threads.sort(key=lambda t: t.last_updated, reverse=True)
            
            # Apply limit if specified
            if limit:
                threads = threads[:limit]
            
            return threads
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve archived threads: {e}")
            return []
    
    def search_archived_threads(self, query: str, limit: int = 10) -> List[Tuple[ConversationThread, float]]:
        """
        Search archived threads by relevance to query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of (ConversationThread, relevance_score) tuples
        """
        try:
            threads = self.get_archived_threads()
            scored_threads = []
            
            for thread in threads:
                # Calculate relevance to search query
                thread_text = f"{thread.title} {' '.join(thread.topic_keywords)}"
                
                try:
                    score = self._calculate_vector_similarity(query, thread_text)
                    scored_threads.append((thread, score))
                except:
                    # Fallback to keyword matching
                    score = self._keyword_similarity(query, thread_text)
                    scored_threads.append((thread, score))
            
            # Sort by relevance score
            scored_threads.sort(key=lambda x: x[1], reverse=True)
            
            # Return top results
            return scored_threads[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to search archived threads: {e}")
            return []

    def _initialize_embedding_system(self) -> None:
        """Initialize the embedding system for vector similarity."""
        try:
            # Try to use existing SAM embedding capabilities
            from memory.memory_vectorstore import MemoryVectorStore
            self.embedding_system = 'sam_vectorstore'
            self.logger.info("Using SAM MemoryVectorStore for embeddings")

        except ImportError:
            try:
                # Fallback to sentence-transformers if available
                import sentence_transformers
                self.embedding_system = 'sentence_transformers'
                self.logger.info("Using sentence-transformers for embeddings")

            except ImportError:
                # Final fallback to keyword-based similarity
                self.embedding_system = 'keyword_fallback'
                self.logger.warning("No embedding system available, using keyword fallback")

    def _extract_buffer_text(self, conversation_buffer: List[Dict[str, Any]]) -> str:
        """Extract meaningful text content from conversation buffer."""
        text_parts = []

        for turn in conversation_buffer:
            content = turn.get('content', '')
            role = turn.get('role', '')

            # Skip empty content
            if not content.strip():
                continue

            # Add role context for better understanding
            text_parts.append(f"{role}: {content}")

        return "\n".join(text_parts)

    def _calculate_vector_similarity(self, text1: str, text2: str) -> float:
        """Calculate vector similarity between two texts."""
        try:
            if self.embedding_system == 'sam_vectorstore':
                return self._sam_vector_similarity(text1, text2)
            elif self.embedding_system == 'sentence_transformers':
                return self._sentence_transformer_similarity(text1, text2)
            else:
                return self._keyword_similarity(text1, text2)

        except Exception as e:
            self.logger.warning(f"Vector similarity calculation failed: {e}")
            return self._keyword_similarity(text1, text2)

    def _sam_vector_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using SAM's vector store."""
        try:
            # Use SAM's existing embedding capabilities
            from memory.memory_vectorstore import MemoryVectorStore

            # This is a simplified approach - in practice, we'd use SAM's embedding model
            # For now, return a reasonable similarity based on text overlap
            return self._keyword_similarity(text1, text2)

        except Exception as e:
            self.logger.warning(f"SAM vector similarity failed: {e}")
            return self._keyword_similarity(text1, text2)

    def _sentence_transformer_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using sentence transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            import torch

            # Load model (cache for efficiency)
            if not hasattr(self, '_st_model'):
                self._st_model = SentenceTransformer('all-MiniLM-L6-v2')

            # Generate embeddings
            embeddings = self._st_model.encode([text1, text2])

            # Calculate cosine similarity
            similarity = torch.nn.functional.cosine_similarity(
                torch.tensor(embeddings[0]).unsqueeze(0),
                torch.tensor(embeddings[1]).unsqueeze(0)
            ).item()

            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]

        except Exception as e:
            self.logger.warning(f"Sentence transformer similarity failed: {e}")
            return self._keyword_similarity(text1, text2)

    def _keyword_similarity(self, text1: str, text2: str) -> float:
        """Fallback keyword-based similarity calculation."""
        try:
            # Simple keyword overlap similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}

            words1 = words1 - stop_words
            words2 = words2 - stop_words

            if not words1 or not words2:
                return 0.0

            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))

            return intersection / union if union > 0 else 0.0

        except Exception as e:
            self.logger.warning(f"Keyword similarity calculation failed: {e}")
            return 0.0

    def _apply_temporal_weighting(self, similarity_score: float, conversation_buffer: List[Dict[str, Any]]) -> float:
        """Apply temporal weighting to give more importance to recent messages."""
        try:
            if not conversation_buffer:
                return similarity_score

            # Calculate recency boost for recent messages
            decay_factor = self.config['temporal_decay_factor']
            total_messages = len(conversation_buffer)

            # Recent messages get higher weight
            recent_weight = 1.0 + (decay_factor * (total_messages / 10.0))

            # Apply weighting (but don't exceed 1.0)
            weighted_score = min(1.0, similarity_score * recent_weight)

            return weighted_score

        except Exception as e:
            self.logger.warning(f"Temporal weighting failed: {e}")
            return similarity_score

    def _calculate_confidence(self, score: float, threshold: float) -> float:
        """Calculate confidence based on distance from threshold."""
        try:
            # Distance from threshold
            distance = abs(score - threshold)

            # Higher distance = higher confidence
            # Scale to [0.3, 1.0] range
            confidence = 0.3 + (distance * 0.7)

            return min(1.0, confidence)

        except:
            return 0.5  # Default confidence

    def _generate_thread_id(self, conversation_buffer: List[Dict[str, Any]]) -> str:
        """Generate unique thread ID based on conversation content."""
        try:
            # Create hash from conversation content and timestamp
            content_text = self._extract_buffer_text(conversation_buffer)
            timestamp = datetime.now().isoformat()

            hash_input = f"{content_text}_{timestamp}".encode()
            thread_hash = hashlib.sha256(hash_input).hexdigest()[:16]

            return f"thread_{thread_hash}"

        except Exception as e:
            self.logger.warning(f"Thread ID generation failed: {e}")
            return f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _generate_conversation_title(self, conversation_buffer: List[Dict[str, Any]]) -> str:
        """Generate a descriptive title for the conversation using LLM."""
        try:
            # Extract key content for title generation
            content_text = self._extract_buffer_text(conversation_buffer)

            # Limit content length for LLM call
            if len(content_text) > 1000:
                content_text = content_text[:1000] + "..."

            # Create title generation prompt
            title_prompt = f"""Generate a concise, descriptive title (max 60 characters) for this conversation:

{content_text}

Title should capture the main topic or theme. Examples:
- "Discussion about Blue Lamps Secret"
- "TPV Security Configuration"
- "Memory System Troubleshooting"

Title:"""

            # Call LLM for title generation
            title = self._call_llm_for_title(title_prompt)

            # Clean and validate title
            title = title.strip().strip('"').strip("'")
            if len(title) > 60:
                title = title[:57] + "..."

            if not title or len(title) < 3:
                raise ValueError("Generated title too short or empty")

            return title

        except Exception as e:
            self.logger.warning(f"Title generation failed: {e}")

            # Fallback to timestamp-based title
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            return f"Chat from {timestamp}"

    def _call_llm_for_title(self, prompt: str) -> str:
        """Call LLM to generate conversation title."""
        try:
            import requests

            # Use Ollama API for title generation
            ollama_payload = {
                "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config['title_generation_temperature'],
                    "max_tokens": 20,
                    "top_p": 0.9
                }
            }

            response = requests.post(
                "http://localhost:11434/api/generate",
                json=ollama_payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                title = result.get('response', '').strip()

                if title:
                    return title

            raise Exception(f"LLM call failed with status {response.status_code}")

        except Exception as e:
            self.logger.warning(f"LLM title generation failed: {e}")
            raise

    def _extract_topic_keywords(self, conversation_buffer: List[Dict[str, Any]]) -> List[str]:
        """Extract key topic words from conversation."""
        try:
            content_text = self._extract_buffer_text(conversation_buffer)

            # Simple keyword extraction (could be enhanced with NLP)
            words = content_text.lower().split()

            # Remove stop words and short words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

            keywords = []
            word_counts = {}

            for word in words:
                # Clean word
                word = ''.join(c for c in word if c.isalnum()).lower()

                if len(word) > 3 and word not in stop_words:
                    word_counts[word] = word_counts.get(word, 0) + 1

            # Get most frequent words
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, count in sorted_words[:10] if count > 1]

            return keywords

        except Exception as e:
            self.logger.warning(f"Keyword extraction failed: {e}")
            return []

    def _generate_embedding_summary(self, conversation_buffer: List[Dict[str, Any]]) -> Optional[List[float]]:
        """Generate embedding summary for future relevance calculations."""
        try:
            content_text = self._extract_buffer_text(conversation_buffer)

            if self.embedding_system == 'sentence_transformers':
                if not hasattr(self, '_st_model'):
                    from sentence_transformers import SentenceTransformer
                    self._st_model = SentenceTransformer('all-MiniLM-L6-v2')

                embedding = self._st_model.encode(content_text)
                return embedding.tolist()

            # For other systems, return None (will use text-based similarity)
            return None

        except Exception as e:
            self.logger.warning(f"Embedding summary generation failed: {e}")
            return None

    def _store_conversation_thread(self, thread: ConversationThread) -> None:
        """Store conversation thread to persistent storage."""
        try:
            thread_file = self.storage_dir / f"{thread.thread_id}.json"

            with open(thread_file, 'w') as f:
                json.dump(thread.to_dict(), f, indent=2)

            self.logger.debug(f"Stored conversation thread: {thread_file}")

        except Exception as e:
            self.logger.error(f"Failed to store conversation thread: {e}")
            raise

    def _store_in_memoir(self, thread: ConversationThread) -> None:
        """Store conversation thread in MEMOIR episodic memory."""
        try:
            # Integration with MEMOIR system (Phase 6)
            # This creates a memory entry for the archived conversation

            memory_content = f"Conversation: {thread.title}\n"
            memory_content += f"Messages: {thread.message_count}\n"
            memory_content += f"Topics: {', '.join(thread.topic_keywords)}\n"
            memory_content += f"Summary: Archived conversation thread from {thread.created_at}"

            # Try to store in MEMOIR if available
            try:
                import streamlit as st
                if hasattr(st.session_state, 'secure_memory_store'):
                    memory_store = st.session_state.secure_memory_store

                    # Store as episodic memory
                    memory_store.store_memory(
                        content=memory_content,
                        memory_type="episodic",
                        metadata={
                            "thread_id": thread.thread_id,
                            "conversation_title": thread.title,
                            "message_count": thread.message_count,
                            "topic_keywords": thread.topic_keywords,
                            "archival_timestamp": thread.last_updated
                        }
                    )

                    self.logger.info(f"Stored conversation thread in MEMOIR: {thread.title}")

            except Exception as memoir_error:
                self.logger.warning(f"Failed to store in MEMOIR: {memoir_error}")
                # Continue without MEMOIR storage - not critical

        except Exception as e:
            self.logger.warning(f"MEMOIR integration failed: {e}")
            # Non-critical failure - continue without MEMOIR storage


# Global instance
_contextual_relevance_engine: Optional[ContextualRelevanceEngine] = None

def get_contextual_relevance_engine(config: Optional[Dict[str, Any]] = None) -> ContextualRelevanceEngine:
    """Get the global contextual relevance engine instance."""
    global _contextual_relevance_engine

    if _contextual_relevance_engine is None:
        _contextual_relevance_engine = ContextualRelevanceEngine(config)
    return _contextual_relevance_engine
