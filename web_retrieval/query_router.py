#!/usr/bin/env python3
"""
Intelligent Query Router - The brain of SAM's web retrieval system
Routes queries to the most appropriate tool with fallback chains
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class QueryRouter:
    """Intelligent router that selects the best tool for each query."""
    
    def __init__(self):
        self.news_keywords = [
            'latest', 'breaking', 'news', 'today', 'current', 'recent', 
            'headlines', 'happening', 'update', 'report', 'announced'
        ]
        
        self.search_keywords = [
            'what is', 'how to', 'explain', 'define', 'features', 'benefits',
            'comparison', 'vs', 'versus', 'difference', 'guide', 'tutorial'
        ]
        
        self.topic_categories = {
            'politics': ['politics', 'political', 'election', 'government', 'congress', 'senate', 'president'],
            'technology': ['technology', 'tech', 'ai', 'artificial intelligence', 'software', 'programming'],
            'business': ['business', 'economy', 'finance', 'market', 'stock', 'economic', 'financial'],
            'health': ['health', 'medical', 'medicine', 'covid', 'pandemic', 'disease', 'healthcare'],
            'sports': ['sports', 'football', 'basketball', 'baseball', 'soccer', 'olympics', 'game'],
            'science': ['science', 'research', 'study', 'discovery', 'scientific', 'climate']
        }
    
    def route_query(self, query: str) -> Dict[str, Any]:
        """Route a query to the most appropriate tool with fallback chain."""
        try:
            logger.info(f"Routing query: '{query}'")
            
            # Analyze the query
            analysis = self._analyze_query(query)
            
            # Determine primary tool and fallback chain
            routing_decision = self._make_routing_decision(query, analysis)
            
            logger.info(f"Routing decision: Primary={routing_decision['primary_tool']}, "
                       f"Fallbacks={routing_decision['fallback_chain']}")
            
            return routing_decision
            
        except Exception as e:
            logger.error(f"Query routing failed: {e}")
            return self._get_default_routing()
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query characteristics."""
        query_lower = query.lower()
        
        analysis = {
            'has_url': self._contains_url(query),
            'is_news_query': self._is_news_query(query_lower),
            'is_search_query': self._is_search_query(query_lower),
            'topic_category': self._detect_topic_category(query_lower),
            'urgency_level': self._assess_urgency(query_lower),
            'query_length': len(query.split()),
            'contains_specific_source': self._detect_specific_source(query_lower)
        }
        
        return analysis
    
    def _contains_url(self, query: str) -> bool:
        """Check if query contains a URL."""
        url_pattern = r'https?://[^\s]+'
        return bool(re.search(url_pattern, query))
    
    def _is_news_query(self, query_lower: str) -> bool:
        """Determine if this is a news-related query."""
        news_score = sum(1 for keyword in self.news_keywords if keyword in query_lower)
        return news_score >= 1
    
    def _is_search_query(self, query_lower: str) -> bool:
        """Determine if this is a general search query."""
        search_score = sum(1 for keyword in self.search_keywords if keyword in query_lower)
        return search_score >= 1
    
    def _detect_topic_category(self, query_lower: str) -> Optional[str]:
        """Detect the topic category of the query."""
        for category, keywords in self.topic_categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        return None
    
    def _assess_urgency(self, query_lower: str) -> str:
        """Assess the urgency level of the query."""
        urgent_keywords = ['breaking', 'urgent', 'emergency', 'now', 'immediately']
        high_keywords = ['latest', 'current', 'today', 'recent']
        
        if any(keyword in query_lower for keyword in urgent_keywords):
            return 'urgent'
        elif any(keyword in query_lower for keyword in high_keywords):
            return 'high'
        else:
            return 'normal'
    
    def _detect_specific_source(self, query_lower: str) -> Optional[str]:
        """Detect if query mentions a specific news source."""
        sources = {
            'cnn': 'cnn',
            'bbc': 'bbc',
            'nytimes': 'nytimes',
            'new york times': 'nytimes',
            'reuters': 'reuters',
            'associated press': 'ap',
            'ap news': 'ap'
        }
        
        for source_name, source_key in sources.items():
            if source_name in query_lower:
                return source_key
        return None
    
    def _make_routing_decision(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Make the routing decision based on analysis."""
        
        # Rule 1: URL in query -> URL Content Extractor
        if analysis['has_url']:
            return {
                'primary_tool': 'url_content_extractor',
                'fallback_chain': ['search_api_tool'],
                'reasoning': 'Query contains URL - direct content extraction',
                'confidence': 0.95,
                'parameters': {
                    'url': self._extract_url_from_query(query)
                }
            }
        
        # Rule 2: News query -> News API Tool
        if analysis['is_news_query']:
            fallback_chain = ['rss_reader_tool', 'search_api_tool']
            
            # Adjust fallback based on topic
            if analysis['topic_category']:
                fallback_chain.insert(0, 'rss_reader_tool')
            
            return {
                'primary_tool': 'news_api_tool',
                'fallback_chain': fallback_chain,
                'reasoning': 'News-related query detected',
                'confidence': 0.85,
                'parameters': {
                    'topic_category': analysis['topic_category'],
                    'urgency': analysis['urgency_level'],
                    'specific_source': analysis['contains_specific_source']
                }
            }
        
        # Rule 3: Specific source mentioned -> RSS Reader Tool
        if analysis['contains_specific_source']:
            return {
                'primary_tool': 'rss_reader_tool',
                'fallback_chain': ['news_api_tool', 'search_api_tool'],
                'reasoning': f'Specific source mentioned: {analysis["contains_specific_source"]}',
                'confidence': 0.80,
                'parameters': {
                    'source': analysis['contains_specific_source'],
                    'topic_category': analysis['topic_category']
                }
            }
        
        # Rule 4: General search query -> CocoIndex Tool (Phase 8.5 upgrade)
        if analysis['is_search_query'] or analysis['query_length'] > 8:
            return {
                'primary_tool': 'cocoindex_tool',
                'fallback_chain': ['search_api_tool', 'url_content_extractor'],
                'reasoning': 'General search or complex query - using intelligent cocoindex',
                'confidence': 0.85,
                'parameters': {
                    'topic_category': analysis['topic_category'],
                    'query_type': 'general_search'
                }
            }
        
        # Rule 5: Topic-specific query -> CocoIndex Tool with RSS fallback
        if analysis['topic_category']:
            return {
                'primary_tool': 'cocoindex_tool',
                'fallback_chain': ['rss_reader_tool', 'news_api_tool', 'search_api_tool'],
                'reasoning': f'Topic-specific query: {analysis["topic_category"]} - using intelligent search',
                'confidence': 0.80,
                'parameters': {
                    'topic_category': analysis['topic_category'],
                    'query_type': 'topic_specific'
                }
            }
        
        # Default: Search API Tool
        return self._get_default_routing()
    
    def _extract_url_from_query(self, query: str) -> str:
        """Extract URL from query."""
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, query)
        return match.group(0) if match else ''
    
    def _get_default_routing(self) -> Dict[str, Any]:
        """Get default routing when no specific rules match."""
        return {
            'primary_tool': 'cocoindex_tool',
            'fallback_chain': ['search_api_tool', 'news_api_tool', 'rss_reader_tool'],
            'reasoning': 'Default routing - intelligent web search with cocoindex',
            'confidence': 0.70,
            'parameters': {
                'query_type': 'default'
            }
        }
    
    def get_tool_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """Get ranked tool recommendations for a query."""
        analysis = self._analyze_query(query)
        routing = self.route_query(query)
        
        recommendations = []
        
        # Primary tool
        recommendations.append({
            'tool': routing['primary_tool'],
            'confidence': routing['confidence'],
            'reasoning': routing['reasoning'],
            'rank': 1
        })
        
        # Fallback tools
        for i, tool in enumerate(routing['fallback_chain'], 2):
            recommendations.append({
                'tool': tool,
                'confidence': max(0.3, routing['confidence'] - (i * 0.15)),
                'reasoning': f'Fallback option {i-1}',
                'rank': i
            })
        
        return recommendations
    
    def explain_routing_decision(self, query: str) -> str:
        """Provide human-readable explanation of routing decision."""
        analysis = self._analyze_query(query)
        routing = self.route_query(query)
        
        explanation_parts = [
            f"Query Analysis for: '{query}'",
            f"",
            f"Primary Tool: {routing['primary_tool']}",
            f"Confidence: {routing['confidence']:.2f}",
            f"Reasoning: {routing['reasoning']}",
            f"",
            f"Fallback Chain: {' → '.join(routing['fallback_chain'])}",
            f"",
            f"Query Characteristics:",
            f"  - Contains URL: {analysis['has_url']}",
            f"  - News Query: {analysis['is_news_query']}",
            f"  - Search Query: {analysis['is_search_query']}",
            f"  - Topic Category: {analysis['topic_category'] or 'None'}",
            f"  - Urgency Level: {analysis['urgency_level']}",
            f"  - Specific Source: {analysis['contains_specific_source'] or 'None'}"
        ]
        
        return "\n".join(explanation_parts)

    def get_router_info(self) -> Dict[str, Any]:
        """Get information about the router."""
        return {
            'name': 'QueryRouter',
            'description': 'Intelligent router that selects the best tool for each query',
            'available_tools': [
                'cocoindex_tool',
                'search_api_tool',
                'news_api_tool',
                'rss_reader_tool',
                'url_content_extractor'
            ],
            'routing_rules': [
                'URL in query → URL Content Extractor',
                'News keywords → News API Tool',
                'Specific source → RSS Reader Tool',
                'General search → CocoIndex Tool (Phase 8.5)',
                'Topic-specific → CocoIndex Tool (Phase 8.5)',
                'Default → CocoIndex Tool (Phase 8.5)'
            ]
        }
