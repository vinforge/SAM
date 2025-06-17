#!/usr/bin/env python3
"""
Test different query types to show how intelligent routing works
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from web_retrieval.query_router import QueryRouter

def test_query_routing():
    """Test how different queries are routed."""
    router = QueryRouter()
    
    test_queries = [
        # News queries (will use news_api_tool)
        "latest AI developments",
        "current technology trends 2024",
        "breaking news about artificial intelligence",
        
        # General search queries (will use cocoindex_tool)
        "information about machine learning algorithms",
        "research on quantum computing",
        "details about blockchain technology",
        "how does neural network work",
        
        # URL queries (will use url_content_extractor)
        "https://example.com/article",
        
        # Source-specific queries (will use rss_reader_tool)
        "CNN news about technology",
        "BBC latest reports"
    ]
    
    print("🧪 Query Routing Test Results")
    print("=" * 60)
    
    for query in test_queries:
        routing = router.route_query(query)
        print(f"\n📝 Query: '{query}'")
        print(f"🎯 Primary Tool: {routing['primary_tool']}")
        print(f"🔄 Fallback Chain: {' → '.join(routing['fallback_chain'])}")
        print(f"💭 Reasoning: {routing['reasoning']}")
        print(f"🎲 Confidence: {routing['confidence']:.2f}")
    
    print("\n" + "=" * 60)
    print("💡 To get CocoIndex (intelligent search) instead of news:")
    print("   - Use 'information about...' instead of 'latest...'")
    print("   - Use 'research on...' instead of 'current...'")
    print("   - Use 'details about...' instead of 'news about...'")

if __name__ == "__main__":
    test_query_routing()
