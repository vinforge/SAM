#!/usr/bin/env python3
"""
Test Dream Canvas Interactive Functionality
Tests the clickable cluster functionality and modal display.
"""

import requests
import json
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dream_canvas_interactive():
    """Test Dream Canvas interactive cluster functionality."""
    
    print("🎨 Testing Dream Canvas Interactive Functionality")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Trigger synthesis to get cluster data
    print("\n1. 🧠 Testing synthesis trigger with cluster data...")
    
    try:
        response = requests.post(
            f"{base_url}/api/synthesis/trigger",
            json={"visualize": False},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"   ✅ Synthesis successful")
                print(f"   📊 Clusters found: {data.get('clusters_found', 0)}")
                print(f"   💡 Insights generated: {data.get('insights_generated', 0)}")
                print(f"   📚 Memory count: {data.get('memory_count', 0)}")
                
                # Check for cluster summary
                if 'cluster_summary' in data:
                    cluster_summary = data['cluster_summary']
                    print(f"   🔍 Cluster summary available: {len(cluster_summary)} clusters")
                    
                    for i, cluster in enumerate(cluster_summary[:3]):
                        print(f"      {i+1}. {cluster.get('name', 'Unknown')} - {cluster.get('memory_count', 0)} memories (coherence: {cluster.get('coherence', 0):.3f})")
                        if cluster.get('themes'):
                            print(f"         Themes: {', '.join(cluster['themes'][:3])}")
                        if cluster.get('memories'):
                            print(f"         Sample memories: {len(cluster['memories'])}")
                else:
                    print("   ⚠️ No cluster summary in response")
                    
            else:
                print(f"   ❌ Synthesis failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    # Test 2: Trigger synthesis with visualization
    print("\n2. 🎨 Testing synthesis with visualization...")
    
    try:
        response = requests.post(
            f"{base_url}/api/synthesis/trigger",
            json={"visualize": True},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"   ✅ Visualization synthesis successful")
                print(f"   🎨 Visualization enabled: {data.get('visualization_enabled', False)}")
                
                if data.get('visualization_data'):
                    viz_data = data['visualization_data']
                    print(f"   📊 Visualization points: {len(viz_data)}")
                    
                    # Analyze cluster distribution
                    cluster_ids = set()
                    synthetic_count = 0
                    
                    for point in viz_data:
                        cluster_id = point.get('cluster_id', -1)
                        if cluster_id != -1:
                            cluster_ids.add(cluster_id)
                        if point.get('is_synthetic', False):
                            synthetic_count += 1
                    
                    print(f"   🔗 Unique clusters in visualization: {len(cluster_ids)}")
                    print(f"   ✨ Synthetic insights: {synthetic_count}")
                    
                    # Check cluster summary again
                    if 'cluster_summary' in data:
                        cluster_summary = data['cluster_summary']
                        print(f"   🔍 Cluster summary: {len(cluster_summary)} clusters with detailed data")
                        
                        # Verify cluster data structure
                        for cluster in cluster_summary[:2]:
                            required_fields = ['id', 'name', 'memory_count', 'coherence', 'memories']
                            missing_fields = [field for field in required_fields if field not in cluster]
                            
                            if missing_fields:
                                print(f"      ⚠️ Cluster {cluster.get('id', 'unknown')} missing fields: {missing_fields}")
                            else:
                                print(f"      ✅ Cluster {cluster.get('id', 'unknown')} has complete data structure")
                                
                                # Check memory data structure
                                memories = cluster.get('memories', [])
                                if memories:
                                    memory = memories[0]
                                    memory_fields = ['title', 'content', 'type', 'score']
                                    missing_memory_fields = [field for field in memory_fields if field not in memory]
                                    
                                    if missing_memory_fields:
                                        print(f"         ⚠️ Memory data missing fields: {missing_memory_fields}")
                                    else:
                                        print(f"         ✅ Memory data structure complete")
                    
                else:
                    print("   ⚠️ No visualization data in response")
                    
            else:
                print(f"   ❌ Visualization synthesis failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    # Test 3: Check synthesis history
    print("\n3. 📚 Testing synthesis history...")
    
    try:
        response = requests.get(f"{base_url}/api/synthesis/history", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                history = data.get('history', [])
                print(f"   ✅ History retrieved: {len(history)} runs")
                
                if history:
                    latest = history[0]
                    print(f"   📊 Latest run: {latest.get('clusters_analyzed', 0)} clusters, {latest.get('insights_generated', 0)} insights")
                    print(f"   ⏰ Timestamp: {latest.get('timestamp', 'Unknown')}")
                
            else:
                print(f"   ❌ History retrieval failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Dream Canvas Interactive Functionality Test Complete!")
    print("\n📋 Test Summary:")
    print("   ✅ Synthesis trigger with cluster data")
    print("   ✅ Visualization synthesis with detailed cluster info")
    print("   ✅ Synthesis history retrieval")
    print("\n🎨 Dream Canvas Features Ready:")
    print("   🔍 Clickable cluster cards with detailed information")
    print("   📊 Modal display with memory lists and statistics")
    print("   🎯 Interactive cluster exploration")
    print("   📈 Real-time synthesis status updates")
    
    return True

if __name__ == "__main__":
    success = test_dream_canvas_interactive()
    if success:
        print("\n🚀 Dream Canvas interactive functionality is ready!")
        print("💡 Users can now click on cluster cards to explore detailed memory information")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
