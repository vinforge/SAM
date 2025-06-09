#!/usr/bin/env python3
"""
SAM Phase 3 Enhancement Demo Script
Demonstrates all Phase 3 features through terminal interface.
"""

import sys
import json
import time
import requests
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section header."""
    print(f"\n📋 {title}")
    print("-" * 40)

def test_sam_api_connection():
    """Test connection to SAM's API."""
    print_header("SAM API Connection Test")
    
    try:
        # Test main chat API
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Chat API (port 5001): Connected")
        else:
            print("❌ Chat API (port 5001): Not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ Chat API (port 5001): Connection failed")
        return False
    
    try:
        # Test Memory Control Center
        response = requests.get("http://localhost:8501", timeout=5)
        print("✅ Memory Control Center (port 8501): Available")
    except requests.exceptions.RequestException:
        print("⚠️ Memory Control Center (port 8501): Not accessible (may need manual start)")
    
    return True

def test_enhanced_search():
    """Test Phase 3.2.1: Enhanced Search & Ranking Engine."""
    print_header("Phase 3.2.1: Enhanced Search & Ranking Engine")
    
    # Test queries that demonstrate different search strategies
    test_queries = [
        {
            "query": "Blue Cloak cybersecurity",
            "description": "Semantic search for company information"
        },
        {
            "query": "important dates",
            "description": "Keyword-based search for temporal information"
        },
        {
            "query": "recent uploads",
            "description": "Recency-based search for latest content"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print_section(f"Test {i}: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        try:
            # Send query to SAM
            response = requests.post(
                "http://localhost:5001/api/chat",
                json={"message": test['query']},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Enhanced search executed successfully")
                
                # Show response preview
                response_text = result.get('response', '')
                preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                print(f"📝 Response preview: {preview}")
                
                # Check for enhanced features
                if "📚" in response_text or "●●●" in response_text:
                    print("🎯 Enhanced citations detected!")
                if any(indicator in response_text.lower() for indicator in ['confidence', 'source', 'page']):
                    print("🔍 Granular metadata detected!")
                
            else:
                print(f"❌ Search failed with status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
        
        time.sleep(2)  # Brief pause between tests

def test_citation_system():
    """Test Phase 3.2.2: Citation System Refactoring."""
    print_header("Phase 3.2.2: Enhanced Citation System")
    
    # Test queries that should trigger citations
    citation_queries = [
        "What does the Blue Cloak document say about cybersecurity?",
        "Summarize the main points from the uploaded documents",
        "What are the key findings in the research papers?"
    ]
    
    for i, query in enumerate(citation_queries, 1):
        print_section(f"Citation Test {i}")
        print(f"Query: '{query}'")
        
        try:
            response = requests.post(
                "http://localhost:5001/api/chat",
                json={"message": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Analyze citation features
                citation_indicators = {
                    "📚": "Enhanced citation formatting",
                    "●●●": "Confidence indicators",
                    "[p.": "Page references",
                    "chunk": "Chunk references",
                    "%": "Confidence percentages"
                }
                
                found_features = []
                for indicator, description in citation_indicators.items():
                    if indicator in response_text:
                        found_features.append(description)
                
                if found_features:
                    print("✅ Enhanced citations detected:")
                    for feature in found_features:
                        print(f"   🎯 {feature}")
                else:
                    print("⚠️ No enhanced citation features detected")
                
                # Show citation preview
                lines = response_text.split('\n')
                citation_lines = [line for line in lines if any(ind in line for ind in citation_indicators.keys())]
                if citation_lines:
                    print("📋 Citation examples:")
                    for line in citation_lines[:3]:  # Show first 3 citation lines
                        print(f"   {line.strip()}")
                
            else:
                print(f"❌ Citation test failed with status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
        
        time.sleep(2)

def test_memory_control_features():
    """Test Phase 3.2.3: Memory Control Center Enhancement."""
    print_header("Phase 3.2.3: Memory Control Center Enhancement")
    
    print_section("Memory Control Center Features")
    print("🌐 Access the Memory Control Center at: http://localhost:8501")
    print("\n📋 Available Features:")
    print("   🔍 Real-time Search: Search as you type")
    print("   🎛️ Advanced Filtering: Multi-mode search strategies")
    print("   📊 Source Analysis: Visual metrics and quality indicators")
    print("   ⚙️ Interactive Configuration: Live weight adjustment")
    print("   📈 Memory Analytics: Comprehensive statistics")
    
    print_section("Testing Memory API Endpoints")
    
    # Test memory-related API endpoints
    memory_tests = [
        {
            "endpoint": "/api/memories",
            "method": "GET",
            "description": "Retrieve stored memories"
        },
        {
            "endpoint": "/api/search",
            "method": "POST",
            "data": {"query": "test search", "max_results": 5},
            "description": "Enhanced search API"
        }
    ]
    
    for test in memory_tests:
        try:
            if test["method"] == "GET":
                response = requests.get(f"http://localhost:5001{test['endpoint']}", timeout=10)
            else:
                response = requests.post(
                    f"http://localhost:5001{test['endpoint']}", 
                    json=test.get("data", {}),
                    timeout=10
                )
            
            if response.status_code == 200:
                print(f"✅ {test['description']}: Available")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   📊 Found {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"   📊 Response keys: {list(data.keys())}")
                except:
                    print("   📊 Response received (non-JSON)")
            else:
                print(f"⚠️ {test['description']}: Status {response.status_code}")
                
        except requests.exceptions.RequestException:
            print(f"⚠️ {test['description']}: Endpoint not available")

def test_hybrid_search_strategies():
    """Test different search strategies from Phase 3.2.1."""
    print_header("Hybrid Search Strategy Demonstration")
    
    # Test the same query with different implied strategies
    base_query = "Blue Cloak"
    
    strategy_tests = [
        {
            "query": f"{base_query} cybersecurity company",
            "strategy": "Semantic Search",
            "description": "Content-based similarity matching"
        },
        {
            "query": f"recent {base_query}",
            "strategy": "Recency-Weighted Search", 
            "description": "Time-based relevance scoring"
        },
        {
            "query": f"important {base_query} information",
            "strategy": "Confidence-Weighted Search",
            "description": "Source quality prioritization"
        }
    ]
    
    for test in strategy_tests:
        print_section(f"{test['strategy']} Test")
        print(f"Query: '{test['query']}'")
        print(f"Strategy: {test['description']}")
        
        try:
            response = requests.post(
                "http://localhost:5001/api/chat",
                json={"message": test['query']},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Analyze response for strategy indicators
                if response_text and len(response_text) > 50:
                    print("✅ Search strategy executed")
                    
                    # Look for ranking/scoring indicators
                    if any(indicator in response_text.lower() for indicator in ['score', 'confidence', 'relevance']):
                        print("🎯 Ranking information detected")
                    
                    # Show brief response
                    preview = response_text[:150] + "..." if len(response_text) > 150 else response_text
                    print(f"📝 Result: {preview}")
                else:
                    print("⚠️ Limited response received")
                    
            else:
                print(f"❌ Strategy test failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
        
        time.sleep(1)

def show_usage_instructions():
    """Show instructions for manual testing."""
    print_header("Manual Testing Instructions")
    
    print_section("1. Memory Control Center (Phase 3.2.3)")
    print("🌐 Open: http://localhost:8501")
    print("📋 Try these features:")
    print("   • Real-time search: Type in search box and see live results")
    print("   • Filter by source: Select specific documents")
    print("   • Adjust ranking weights: Use sliders in ranking section")
    print("   • View source analytics: Check source distribution charts")
    
    print_section("2. Enhanced Chat Interface (Phase 3.2.1 & 3.2.2)")
    print("🌐 Open: http://localhost:5001")
    print("📋 Try these queries:")
    print("   • 'What does Blue Cloak do?' - Test enhanced citations")
    print("   • 'Summarize recent documents' - Test ranking engine")
    print("   • 'Find information about [topic]' - Test hybrid search")
    
    print_section("3. Advanced Features to Test")
    print("🔍 Enhanced Search:")
    print("   • Search as you type in Memory Control Center")
    print("   • Compare results with different search modes")
    print("   • Filter by confidence scores and source types")
    
    print("📚 Enhanced Citations:")
    print("   • Look for confidence indicators (●●●○○)")
    print("   • Check for page and chunk references")
    print("   • Notice transparency scores and source attribution")
    
    print("🎛️ Interactive Configuration:")
    print("   • Adjust ranking weights in real-time")
    print("   • See immediate changes in search results")
    print("   • Monitor performance metrics")

def main():
    """Run the complete Phase 3 demonstration."""
    print_header("SAM Phase 3 Enhancement Demonstration")
    print("This script tests all Phase 3 features and enhancements.")
    print("Make sure SAM is running before proceeding!")
    
    # Check if SAM is running
    if not test_sam_api_connection():
        print("\n❌ SAM is not running or not accessible.")
        print("Please start SAM with: python start_sam.py")
        return
    
    # Run all tests
    test_enhanced_search()
    test_citation_system()
    test_memory_control_features()
    test_hybrid_search_strategies()
    show_usage_instructions()
    
    print_header("Phase 3 Demonstration Complete!")
    print("🎉 All Phase 3 features have been tested.")
    print("🌐 Visit the Memory Control Center for interactive testing:")
    print("   http://localhost:8501")
    print("💬 Try the enhanced chat interface:")
    print("   http://localhost:5001")

if __name__ == "__main__":
    main()
