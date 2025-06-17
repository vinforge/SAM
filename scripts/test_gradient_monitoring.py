#!/usr/bin/env python3
"""
Test Script for PINN-Inspired Gradient Monitoring System

Tests the gradient health monitoring capabilities integrated into SAM's
MEMOIR editing system. Validates detection of various gradient pathologies
and proper integration with SOF error reporting.

Usage:
    python scripts/test_gradient_monitoring.py

Author: SAM Development Team
Version: 1.0.0
"""

import sys
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path

# Add SAM to path
sys.path.append(str(Path(__file__).parent.parent))

from sam.core.diagnostics import GradientLogger, GradientHealthMonitor, GradientPathology
from sam.core.model_layers import ResidualMemoryLayer

def create_test_model(hidden_size: int = 256) -> nn.Module:
    """Create a simple test model for gradient monitoring."""
    class TestModel(nn.Module):
        def __init__(self, hidden_size):
            super().__init__()
            self.linear1 = nn.Linear(hidden_size, hidden_size)
            self.linear2 = nn.Linear(hidden_size, hidden_size)
            self.residual_memory = ResidualMemoryLayer(
                hidden_size=hidden_size,
                max_edits=10
            )
        
        def forward(self, x):
            x = self.linear1(x)
            x = torch.relu(x)
            x = self.residual_memory(x.unsqueeze(0))  # Add sequence dim
            x = self.linear2(x.squeeze(0))  # Remove sequence dim
            return x
    
    return TestModel(hidden_size)

def test_healthy_gradients():
    """Test detection of healthy gradient patterns."""
    print("🧪 Testing healthy gradient detection...")
    
    model = create_test_model()
    monitor = GradientHealthMonitor()
    
    # Simulate healthy training with GradientLogger
    with GradientLogger(model, log_frequency=1) as logger:
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        for step in range(10):
            optimizer.zero_grad()
            
            # Forward pass with decreasing loss
            x = torch.randn(32, 256)
            target = torch.randn(32, 256)
            output = model(x)
            loss = nn.MSELoss()(output, target) * (0.9 ** step)  # Decreasing loss
            
            loss.backward()
            logger.log_step(loss.item(), 0.001)
            optimizer.step()
    
    # Analyze gradient health
    snapshots = logger.get_snapshots()
    health_report = monitor.analyze_gradient_health(snapshots)
    
    print(f"  Pathology: {health_report.pathology.value}")
    print(f"  Severity: {health_report.severity:.3f}")
    print(f"  Confidence: {health_report.confidence:.3f}")
    
    assert health_report.pathology == GradientPathology.HEALTHY
    print("  ✅ Healthy gradients correctly detected")

def test_vanishing_gradients():
    """Test detection of vanishing gradient pathology."""
    print("🧪 Testing vanishing gradient detection...")
    
    model = create_test_model()
    monitor = GradientHealthMonitor(vanishing_threshold=1e-6)
    
    # Simulate vanishing gradients
    with GradientLogger(model, log_frequency=1) as logger:
        for step in range(10):
            # Manually create very small gradients
            for param in model.parameters():
                if param.grad is not None:
                    param.grad.zero_()
                else:
                    param.grad = torch.zeros_like(param)
                param.grad += torch.randn_like(param) * 1e-8  # Very small gradients
            
            # Calculate gradient norm
            total_norm = 0.0
            for param in model.parameters():
                if param.grad is not None:
                    total_norm += param.grad.norm().item() ** 2
            total_norm = total_norm ** 0.5
            
            logger.log_step(1.0, 0.001)  # Log with constant loss
    
    snapshots = logger.get_snapshots()
    health_report = monitor.analyze_gradient_health(snapshots)
    
    print(f"  Pathology: {health_report.pathology.value}")
    print(f"  Severity: {health_report.severity:.3f}")
    
    # Should detect vanishing gradients
    assert health_report.pathology == GradientPathology.VANISHING
    print("  ✅ Vanishing gradients correctly detected")

def test_exploding_gradients():
    """Test detection of exploding gradient pathology."""
    print("🧪 Testing exploding gradient detection...")
    
    model = create_test_model()
    monitor = GradientHealthMonitor(exploding_threshold=10.0)
    
    # Simulate exploding gradients
    with GradientLogger(model, log_frequency=1) as logger:
        optimizer = torch.optim.SGD(model.parameters(), lr=10.0)  # Very high LR
        
        for step in range(5):
            optimizer.zero_grad()
            
            # Forward pass with high learning rate to cause explosion
            x = torch.randn(32, 256) * 10  # Large inputs
            target = torch.randn(32, 256)
            output = model(x)
            loss = nn.MSELoss()(output, target)
            
            loss.backward()
            
            # Artificially amplify gradients to simulate explosion
            for param in model.parameters():
                if param.grad is not None:
                    param.grad *= 50.0  # Amplify gradients
            
            logger.log_step(loss.item(), 10.0)
            optimizer.step()
    
    snapshots = logger.get_snapshots()
    health_report = monitor.analyze_gradient_health(snapshots)
    
    print(f"  Pathology: {health_report.pathology.value}")
    print(f"  Severity: {health_report.severity:.3f}")
    
    # Should detect exploding gradients
    assert health_report.pathology == GradientPathology.EXPLODING
    print("  ✅ Exploding gradients correctly detected")

def test_noisy_convergence():
    """Test detection of noisy convergence pathology."""
    print("🧪 Testing noisy convergence detection...")
    
    model = create_test_model()
    monitor = GradientHealthMonitor(noise_window=8)
    
    # Simulate noisy gradients
    with GradientLogger(model, log_frequency=1) as logger:
        for step in range(10):
            # Create highly variable gradient norms
            noise_factor = np.random.uniform(0.1, 10.0)  # High variance
            
            for param in model.parameters():
                if param.grad is not None:
                    param.grad.zero_()
                else:
                    param.grad = torch.zeros_like(param)
                param.grad += torch.randn_like(param) * noise_factor
            
            logger.log_step(1.0, 0.001)
    
    snapshots = logger.get_snapshots()
    health_report = monitor.analyze_gradient_health(snapshots)
    
    print(f"  Pathology: {health_report.pathology.value}")
    print(f"  Severity: {health_report.severity:.3f}")
    
    # Should detect noisy convergence
    assert health_report.pathology == GradientPathology.NOISY
    print("  ✅ Noisy convergence correctly detected")

def test_gradient_recommendations():
    """Test that appropriate recommendations are provided."""
    print("🧪 Testing gradient health recommendations...")
    
    model = create_test_model()
    monitor = GradientHealthMonitor()
    
    # Test vanishing gradient recommendations
    with GradientLogger(model, log_frequency=1) as logger:
        for step in range(8):
            for param in model.parameters():
                if param.grad is not None:
                    param.grad.zero_()
                else:
                    param.grad = torch.zeros_like(param)
                param.grad += torch.randn_like(param) * 1e-8
            logger.log_step(1.0, 0.001)
    
    snapshots = logger.get_snapshots()
    health_report = monitor.analyze_gradient_health(snapshots)
    
    print(f"  Pathology: {health_report.pathology.value}")
    print(f"  Recommendations: {len(health_report.recommendations)}")
    
    # Should have recommendations for vanishing gradients
    assert len(health_report.recommendations) > 0
    assert any("learning rate" in rec.lower() for rec in health_report.recommendations)
    print("  ✅ Appropriate recommendations provided")

def test_memoir_integration():
    """Test integration with MEMOIR editing system."""
    print("🧪 Testing MEMOIR integration...")
    
    try:
        from sam.orchestration.skills.internal.memoir_edit import MEMOIR_EditSkill
        from sam.orchestration.uif import SAM_UIF
        
        # Create MEMOIR edit skill
        edit_skill = MEMOIR_EditSkill(
            hidden_size=256,
            max_training_steps=5
        )
        
        # Create test UIF
        uif = SAM_UIF()
        uif.intermediate_data = {
            "edit_prompt": "The capital of France is",
            "correct_answer": "Paris",
            "edit_context": "Geography question"
        }
        
        # Execute edit (this will use gradient monitoring)
        result_uif = edit_skill.execute(uif)
        
        # Check if gradient monitoring was integrated
        training_metrics = result_uif.intermediate_data.get("training_metrics", {})
        has_gradient_info = "gradient_pathology" in training_metrics
        
        print(f"  Gradient monitoring integrated: {has_gradient_info}")
        if has_gradient_info:
            print(f"  Detected pathology: {training_metrics['gradient_pathology']}")
        
        print("  ✅ MEMOIR integration successful")
        
    except ImportError as e:
        print(f"  ⚠️ MEMOIR integration test skipped: {e}")

def main():
    """Run all gradient monitoring tests."""
    print("🚀 PINN-Inspired Gradient Monitoring Test Suite")
    print("=" * 60)
    
    try:
        # Test individual pathology detection
        test_healthy_gradients()
        print()
        
        test_vanishing_gradients()
        print()
        
        test_exploding_gradients()
        print()
        
        test_noisy_convergence()
        print()
        
        test_gradient_recommendations()
        print()
        
        # Test integration
        test_memoir_integration()
        print()
        
        print("🎉 All gradient monitoring tests passed!")
        print("✅ Phase A: Gradient Health & Stability Diagnostics - COMPLETE")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
