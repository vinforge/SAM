"""
MemoryRetrievalSkill - SAM Memory System Interface
=================================================

Wraps SAM's existing memory systems (vector store, episodic memory, knowledge capsules)
into the SOF skill framework. Provides unified access to all memory components.
"""

import logging
from typing import List, Dict, Any, Optional
from ..uif import SAM_UIF
from .base import BaseSkillModule, SkillExecutionError

logger = logging.getLogger(__name__)


class MemoryRetrievalSkill(BaseSkillModule):
    """
    Skill that interfaces with SAM's comprehensive memory systems.
    
    Retrieves relevant information from:
    - Vector store (semantic search)
    - Episodic memory (user interactions)
    - Knowledge capsules (structured knowledge)
    - Long-term memory (persistent storage)
    """
    
    skill_name = "MemoryRetrievalSkill"
    skill_version = "1.0.0"
    skill_description = "Retrieves relevant information from SAM's memory systems"
    skill_category = "memory"
    
    # Dependency declarations
    required_inputs = ["input_query"]
    optional_inputs = ["user_id", "session_id", "active_profile", "search_context"]
    output_keys = ["memory_results", "retrieved_documents", "memory_confidence"]
    
    # Skill characteristics
    requires_external_access = False
    requires_vetting = False
    can_run_parallel = True
    estimated_execution_time = 0.5  # seconds
    
    def __init__(self):
        super().__init__()
        self._memory_store = None
        self._integrated_memory = None
        self._initialize_memory_systems()
    
    def _initialize_memory_systems(self) -> None:
        """Initialize connections to SAM's memory systems."""
        try:
            # Import SAM memory components
            from memory.memory_vectorstore import get_memory_store
            from memory.integrated_memory import get_integrated_memory
            
            self._memory_store = get_memory_store()
            self._integrated_memory = get_integrated_memory()
            
            self.logger.info("Memory systems initialized successfully")
            
        except ImportError as e:
            self.logger.error(f"Failed to import memory systems: {e}")
            raise SkillExecutionError(f"Memory system initialization failed: {e}")
        except Exception as e:
            self.logger.error(f"Error initializing memory systems: {e}")
            raise SkillExecutionError(f"Memory system setup error: {e}")
    
    def execute(self, uif: SAM_UIF) -> SAM_UIF:
        """
        Execute memory retrieval with comprehensive search across all memory systems.
        
        Args:
            uif: Universal Interface Format with query and context
            
        Returns:
            Updated UIF with memory retrieval results
        """
        try:
            query = uif.input_query
            user_id = uif.user_id
            session_id = uif.session_id
            active_profile = uif.active_profile
            
            # Get search parameters from intermediate data
            search_context = uif.intermediate_data.get("search_context", {})
            max_results = search_context.get("max_results", 10)
            similarity_threshold = search_context.get("similarity_threshold", 0.7)
            
            self.logger.info(f"Retrieving memories for query: {query[:100]}...")
            
            # Perform comprehensive memory search
            memory_results = self._search_all_memory_systems(
                query=query,
                user_id=user_id,
                session_id=session_id,
                active_profile=active_profile,
                max_results=max_results,
                similarity_threshold=similarity_threshold
            )
            
            # Process and structure results
            processed_results = self._process_memory_results(memory_results)
            
            # Calculate overall confidence
            confidence = self._calculate_memory_confidence(processed_results)
            
            # Store results in UIF
            uif.intermediate_data["memory_results"] = processed_results
            uif.intermediate_data["retrieved_documents"] = self._extract_documents(processed_results)
            uif.intermediate_data["memory_confidence"] = confidence
            
            # Set skill outputs
            uif.set_skill_output(self.skill_name, {
                "results_count": len(processed_results.get("all_results", [])),
                "confidence": confidence,
                "search_query": query,
                "memory_sources": list(processed_results.keys())
            })
            
            self.logger.info(f"Memory retrieval completed: {len(processed_results.get('all_results', []))} results")
            
            return uif
            
        except Exception as e:
            self.logger.exception("Error during memory retrieval")
            raise SkillExecutionError(f"Memory retrieval failed: {str(e)}")
    
    def _search_all_memory_systems(self, 
                                 query: str,
                                 user_id: Optional[str] = None,
                                 session_id: Optional[str] = None,
                                 active_profile: str = "general",
                                 max_results: int = 10,
                                 similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Search across all available memory systems.
        
        Returns:
            Dictionary with results from each memory system
        """
        results = {}
        
        try:
            # Vector store search
            if self._memory_store:
                vector_results = self._memory_store.search(
                    query=query,
                    top_k=max_results,
                    threshold=similarity_threshold
                )
                results["vector_store"] = vector_results
                
        except Exception as e:
            self.logger.warning(f"Vector store search failed: {e}")
            results["vector_store"] = []
        
        try:
            # Integrated memory search
            if self._integrated_memory:
                integrated_results = self._integrated_memory.search_memories(
                    query=query,
                    user_id=user_id,
                    max_results=max_results
                )
                results["integrated_memory"] = integrated_results
                
        except Exception as e:
            self.logger.warning(f"Integrated memory search failed: {e}")
            results["integrated_memory"] = []
        
        try:
            # Knowledge capsule search
            capsule_results = self._search_knowledge_capsules(query, max_results)
            results["knowledge_capsules"] = capsule_results
            
        except Exception as e:
            self.logger.warning(f"Knowledge capsule search failed: {e}")
            results["knowledge_capsules"] = []
        
        return results
    
    def _search_knowledge_capsules(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search knowledge capsules for relevant information."""
        try:
            from memory.knowledge_capsules import get_capsule_manager
            
            capsule_manager = get_capsule_manager()
            capsules = capsule_manager.search_capsules(query, max_results=max_results)
            
            return [
                {
                    "id": capsule.capsule_id,
                    "name": capsule.name,
                    "content": capsule.content,
                    "tags": capsule.tags,
                    "relevance_score": getattr(capsule, 'relevance_score', 0.8)
                }
                for capsule in capsules
            ]
            
        except Exception as e:
            self.logger.warning(f"Knowledge capsule search error: {e}")
            return []
    
    def _process_memory_results(self, memory_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and consolidate results from all memory systems.
        
        Returns:
            Processed and structured memory results
        """
        processed = {
            "all_results": [],
            "by_source": memory_results,
            "summary": {
                "total_results": 0,
                "sources_used": [],
                "highest_confidence": 0.0
            }
        }
        
        # Consolidate all results
        all_results = []
        highest_confidence = 0.0
        
        for source, results in memory_results.items():
            if results:
                processed["summary"]["sources_used"].append(source)
                
                for result in results:
                    # Normalize result format
                    normalized_result = self._normalize_memory_result(result, source)
                    all_results.append(normalized_result)
                    
                    # Track highest confidence
                    confidence = normalized_result.get("confidence", 0.0)
                    highest_confidence = max(highest_confidence, confidence)
        
        # Sort by confidence/relevance
        all_results.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
        
        processed["all_results"] = all_results
        processed["summary"]["total_results"] = len(all_results)
        processed["summary"]["highest_confidence"] = highest_confidence
        
        return processed
    
    def _normalize_memory_result(self, result: Any, source: str) -> Dict[str, Any]:
        """
        Normalize memory results from different sources into a common format.
        
        Returns:
            Normalized result dictionary
        """
        normalized = {
            "source": source,
            "confidence": 0.0,
            "content": "",
            "metadata": {}
        }
        
        if isinstance(result, dict):
            normalized.update(result)
            normalized["confidence"] = result.get("similarity_score", result.get("confidence", 0.0))
            normalized["content"] = result.get("content", result.get("text", str(result)))
        else:
            # Handle object-based results
            normalized["content"] = str(result)
            if hasattr(result, 'similarity_score'):
                normalized["confidence"] = result.similarity_score
            elif hasattr(result, 'confidence'):
                normalized["confidence"] = result.confidence
        
        return normalized
    
    def _extract_documents(self, processed_results: Dict[str, Any]) -> List[str]:
        """
        Extract document references from memory results.
        
        Returns:
            List of document identifiers/references
        """
        documents = []
        
        for result in processed_results.get("all_results", []):
            # Extract document references from metadata
            metadata = result.get("metadata", {})
            doc_ref = metadata.get("document_id") or metadata.get("source_document")
            
            if doc_ref and doc_ref not in documents:
                documents.append(doc_ref)
        
        return documents
    
    def _calculate_memory_confidence(self, processed_results: Dict[str, Any]) -> float:
        """
        Calculate overall confidence in memory retrieval results.
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        all_results = processed_results.get("all_results", [])
        
        if not all_results:
            return 0.0
        
        # Calculate weighted average confidence
        total_confidence = sum(result.get("confidence", 0.0) for result in all_results)
        avg_confidence = total_confidence / len(all_results)
        
        # Boost confidence based on number of sources
        source_count = len(processed_results.get("summary", {}).get("sources_used", []))
        source_boost = min(0.1 * source_count, 0.3)  # Max 30% boost
        
        final_confidence = min(1.0, avg_confidence + source_boost)
        
        return round(final_confidence, 3)
