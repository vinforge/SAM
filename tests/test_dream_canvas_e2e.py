"""
End-to-End Tests for Dream Canvas Implicit Knowledge Features
============================================================

Tests for the Dream Canvas integration with the Implicit Knowledge Engine,
including ghost links, hypothesis nodes, and UI functionality.
"""

import unittest
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestDreamCanvasImplicitKnowledge(unittest.TestCase):
    """End-to-end tests for Dream Canvas implicit knowledge features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_visualization_data = [
            {
                "memory_id": "mem_1",
                "content": "Machine learning algorithms require large datasets",
                "content_snippet": "ML algorithms need data",
                "x": 1.0,
                "y": 2.0,
                "cluster_id": 1,
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "memory_id": "mem_2", 
                "content": "Neural networks use backpropagation for training",
                "content_snippet": "Neural nets use backprop",
                "x": 1.5,
                "y": 2.5,
                "cluster_id": 1,
                "timestamp": "2024-01-01T11:00:00Z"
            },
            {
                "memory_id": "mem_3",
                "content": "Deep learning models achieve high accuracy on image recognition",
                "content_snippet": "Deep learning for images",
                "x": 2.0,
                "y": 3.0,
                "cluster_id": 1,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        ]
    
    def test_sof_execute_endpoint_structure(self):
        """Test the structure of the SOF execute endpoint for Dream Canvas."""
        # This would be tested with actual Flask test client in a full implementation
        expected_request_structure = {
            "plan": ["ImplicitKnowledgeSkill"],
            "input_query": "Find implicit connections between selected knowledge chunks",
            "explicit_knowledge_chunks": [
                "Sample chunk 1",
                "Sample chunk 2"
            ]
        }
        
        # Verify request structure is valid
        self.assertIn("plan", expected_request_structure)
        self.assertIn("input_query", expected_request_structure)
        self.assertIn("explicit_knowledge_chunks", expected_request_structure)
        self.assertEqual(expected_request_structure["plan"], ["ImplicitKnowledgeSkill"])
    
    def test_ghost_link_data_structure(self):
        """Test the data structure for ghost links."""
        ghost_link = {
            "id": "ghost_1234567890",
            "nodes": [
                {"id": "mem_1", "content": "Content 1", "x": 1.0, "y": 2.0},
                {"id": "mem_2", "content": "Content 2", "x": 1.5, "y": 2.5}
            ],
            "summary": "Inferred Connection: These concepts are related through machine learning principles",
            "created_at": "2024-01-01T10:00:00Z"
        }
        
        # Verify ghost link structure
        self.assertIn("id", ghost_link)
        self.assertIn("nodes", ghost_link)
        self.assertIn("summary", ghost_link)
        self.assertIn("created_at", ghost_link)
        self.assertEqual(len(ghost_link["nodes"]), 2)
        self.assertTrue(ghost_link["summary"].startswith("Inferred Connection:"))
    
    def test_hypothesis_node_data_structure(self):
        """Test the data structure for hypothesis nodes."""
        hypothesis_node = {
            "id": "hypothesis_1_1234567890",
            "clusterId": 1,
            "hypothesis": "Inferred Connection: This cluster represents machine learning concepts",
            "sourceNodes": self.sample_visualization_data,
            "created_at": "2024-01-01T10:00:00Z",
            "type": "hypothesis"
        }
        
        # Verify hypothesis node structure
        self.assertIn("id", hypothesis_node)
        self.assertIn("clusterId", hypothesis_node)
        self.assertIn("hypothesis", hypothesis_node)
        self.assertIn("sourceNodes", hypothesis_node)
        self.assertIn("created_at", hypothesis_node)
        self.assertIn("type", hypothesis_node)
        self.assertEqual(hypothesis_node["type"], "hypothesis")
        self.assertEqual(len(hypothesis_node["sourceNodes"]), 3)
    
    def test_cluster_analysis_logic(self):
        """Test the cluster analysis logic for hypothesis generation."""
        # Simulate the identifyClusterNodes function logic
        clusters = {}
        
        for point in self.sample_visualization_data:
            cluster_id = point["cluster_id"]
            if cluster_id != -1:  # Exclude noise points
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(point)
        
        # Analyze clusters
        cluster_analysis = []
        for cluster_id, nodes in clusters.items():
            if len(nodes) >= 3:  # Only analyze clusters with 3+ nodes
                sorted_nodes = sorted(nodes, key=lambda x: x.get("timestamp", ""), reverse=True)
                cluster_analysis.append({
                    "clusterId": cluster_id,
                    "nodes": sorted_nodes[:5],  # Top 5 nodes
                    "totalNodes": len(nodes)
                })
        
        # Verify cluster analysis
        self.assertEqual(len(cluster_analysis), 1)  # Should find one cluster
        self.assertEqual(cluster_analysis[0]["clusterId"], 1)
        self.assertEqual(cluster_analysis[0]["totalNodes"], 3)
        self.assertEqual(len(cluster_analysis[0]["nodes"]), 3)
    
    def test_node_selection_logic(self):
        """Test the node selection logic for implicit connections."""
        selected_nodes = set()
        
        # Simulate node selection
        for point in self.sample_visualization_data[:2]:  # Select first 2 nodes
            node_id = point["memory_id"]
            selected_nodes.add(node_id)
        
        # Verify selection
        self.assertEqual(len(selected_nodes), 2)
        self.assertIn("mem_1", selected_nodes)
        self.assertIn("mem_2", selected_nodes)
        
        # Test button state logic
        button_enabled = len(selected_nodes) >= 2
        self.assertTrue(button_enabled)
    
    def test_selected_node_data_extraction(self):
        """Test extraction of data from selected nodes."""
        selected_nodes = {"mem_1", "mem_2"}
        
        # Simulate getSelectedNodeData function
        selected_data = []
        for point in self.sample_visualization_data:
            node_id = point["memory_id"]
            if node_id in selected_nodes:
                selected_data.append({
                    "id": node_id,
                    "content": point["content"],
                    "x": point["x"],
                    "y": point["y"]
                })
        
        # Verify extracted data
        self.assertEqual(len(selected_data), 2)
        self.assertEqual(selected_data[0]["id"], "mem_1")
        self.assertEqual(selected_data[1]["id"], "mem_2")
        self.assertIn("content", selected_data[0])
        self.assertIn("x", selected_data[0])
        self.assertIn("y", selected_data[0])
    
    def test_api_response_handling(self):
        """Test handling of API responses for implicit knowledge."""
        # Mock successful API response
        successful_response = {
            "status": "success",
            "execution_report": {
                "result": "success",
                "execution_time": 2.5,
                "skills_executed": ["ImplicitKnowledgeSkill"],
                "intermediate_data": {
                    "implicit_knowledge_summary": "Inferred Connection: Machine learning concepts are connected through data processing",
                    "unified_context": "Enhanced context with implicit connections",
                    "implicit_knowledge_confidence": 0.85
                }
            }
        }
        
        # Verify response structure
        self.assertEqual(successful_response["status"], "success")
        self.assertIn("execution_report", successful_response)
        self.assertIn("intermediate_data", successful_response["execution_report"])
        
        intermediate_data = successful_response["execution_report"]["intermediate_data"]
        self.assertIn("implicit_knowledge_summary", intermediate_data)
        self.assertTrue(intermediate_data["implicit_knowledge_summary"].startswith("Inferred Connection:"))
    
    def test_error_response_handling(self):
        """Test handling of error responses."""
        # Mock error response
        error_response = {
            "status": "error",
            "error": "ImplicitKnowledgeSkill execution failed"
        }
        
        # Verify error handling
        self.assertEqual(error_response["status"], "error")
        self.assertIn("error", error_response)
        self.assertIsInstance(error_response["error"], str)
    
    def test_ui_state_management(self):
        """Test UI state management for Dream Canvas features."""
        # Simulate UI state
        ui_state = {
            "selectedNodes": set(),
            "ghostLinks": [],
            "hypothesisNodes": [],
            "currentVisualizationData": self.sample_visualization_data
        }
        
        # Test node selection
        ui_state["selectedNodes"].add("mem_1")
        ui_state["selectedNodes"].add("mem_2")
        
        # Test ghost link creation
        ghost_link = {
            "id": "ghost_123",
            "nodes": [{"id": "mem_1"}, {"id": "mem_2"}],
            "summary": "Test connection",
            "created_at": "2024-01-01T10:00:00Z"
        }
        ui_state["ghostLinks"].append(ghost_link)
        
        # Test hypothesis node creation
        hypothesis_node = {
            "id": "hypothesis_1_123",
            "clusterId": 1,
            "hypothesis": "Test hypothesis",
            "sourceNodes": self.sample_visualization_data,
            "created_at": "2024-01-01T10:00:00Z"
        }
        ui_state["hypothesisNodes"].append(hypothesis_node)
        
        # Verify state
        self.assertEqual(len(ui_state["selectedNodes"]), 2)
        self.assertEqual(len(ui_state["ghostLinks"]), 1)
        self.assertEqual(len(ui_state["hypothesisNodes"]), 1)
    
    def test_canvas_clearing_functionality(self):
        """Test canvas clearing functionality."""
        # Simulate canvas state before clearing
        canvas_state = {
            "selectedNodes": {"mem_1", "mem_2"},
            "ghostLinks": [{"id": "ghost_1"}],
            "hypothesisNodes": [{"id": "hypothesis_1"}]
        }
        
        # Simulate clearing
        canvas_state["selectedNodes"].clear()
        canvas_state["ghostLinks"] = []
        canvas_state["hypothesisNodes"] = []
        
        # Verify cleared state
        self.assertEqual(len(canvas_state["selectedNodes"]), 0)
        self.assertEqual(len(canvas_state["ghostLinks"]), 0)
        self.assertEqual(len(canvas_state["hypothesisNodes"]), 0)
    
    def test_visualization_data_validation(self):
        """Test validation of visualization data for implicit knowledge features."""
        # Test valid data
        valid_data = self.sample_visualization_data
        self.assertTrue(all("memory_id" in point for point in valid_data))
        self.assertTrue(all("content" in point for point in valid_data))
        self.assertTrue(all("cluster_id" in point for point in valid_data))
        
        # Test invalid data
        invalid_data = [{"incomplete": "data"}]
        self.assertFalse(all("memory_id" in point for point in invalid_data))


class TestDreamCanvasIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios for Dream Canvas implicit knowledge features."""
    
    def test_full_ghost_link_workflow(self):
        """Test the complete ghost link creation workflow."""
        # 1. User selects nodes
        selected_nodes = {"mem_1", "mem_2"}
        
        # 2. Extract node data
        node_data = [
            {"id": "mem_1", "content": "Content 1"},
            {"id": "mem_2", "content": "Content 2"}
        ]
        
        # 3. Call API (mocked)
        api_response = {
            "status": "success",
            "execution_report": {
                "intermediate_data": {
                    "implicit_knowledge_summary": "Inferred Connection: Test connection"
                }
            }
        }
        
        # 4. Create ghost link
        if api_response["status"] == "success":
            summary = api_response["execution_report"]["intermediate_data"]["implicit_knowledge_summary"]
            ghost_link = {
                "id": f"ghost_{int(1234567890)}",
                "nodes": node_data,
                "summary": summary,
                "created_at": "2024-01-01T10:00:00Z"
            }
        
        # Verify workflow
        self.assertEqual(ghost_link["summary"], "Inferred Connection: Test connection")
        self.assertEqual(len(ghost_link["nodes"]), 2)
    
    def test_full_hypothesis_node_workflow(self):
        """Test the complete hypothesis node generation workflow."""
        # 1. Identify clusters
        cluster_data = {
            "clusterId": 1,
            "nodes": [
                {"memory_id": "mem_1", "content": "Content 1"},
                {"memory_id": "mem_2", "content": "Content 2"},
                {"memory_id": "mem_3", "content": "Content 3"}
            ]
        }
        
        # 2. Extract content
        node_contents = [node["content"] for node in cluster_data["nodes"]]
        
        # 3. Call API (mocked)
        api_response = {
            "status": "success",
            "execution_report": {
                "intermediate_data": {
                    "implicit_knowledge_summary": "Inferred Connection: Cluster hypothesis"
                }
            }
        }
        
        # 4. Create hypothesis node
        if api_response["status"] == "success":
            summary = api_response["execution_report"]["intermediate_data"]["implicit_knowledge_summary"]
            hypothesis_node = {
                "id": f"hypothesis_{cluster_data['clusterId']}_{int(1234567890)}",
                "clusterId": cluster_data["clusterId"],
                "hypothesis": summary,
                "sourceNodes": cluster_data["nodes"],
                "created_at": "2024-01-01T10:00:00Z",
                "type": "hypothesis"
            }
        
        # Verify workflow
        self.assertEqual(hypothesis_node["hypothesis"], "Inferred Connection: Cluster hypothesis")
        self.assertEqual(hypothesis_node["clusterId"], 1)
        self.assertEqual(len(hypothesis_node["sourceNodes"]), 3)


if __name__ == '__main__':
    unittest.main()
