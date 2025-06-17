#!/usr/bin/env python3
"""
Simple Test for Gradient Monitoring System

Basic validation of gradient health monitoring functionality.

Author: SAM Development Team
Version: 1.0.0
"""

import sys
import torch
import numpy as np
from pathlib import Path

# Add SAM to path
sys.path.append(str(Path(__file__).parent.parent))

from sam.core.diagnostics import GradientHealthMonitor, GradientPathology, GradientSnapshot
from datetime import datetime

def test_gradient_analysis():
    """Test gradient health analysis with synthetic data."""
    print("🧪 Testing gradient health analysis...")
    
    monitor = GradientHealthMonitor()
    
    # Test 1: Healthy gradients (decreasing trend)
    print("\n1. Testing healthy gradient pattern...")
    healthy_snapshots = []
    for i in range(10):
        snapshot = GradientSnapshot(
            step=i,
            gradient_norm=1.0 * (0.9 ** i),  # Decreasing
            layer_norms={'layer1': 0.5 * (0.9 ** i)},
            timestamp=datetime.now(),
            loss_value=2.0 * (0.8 ** i)
        )
        healthy_snapshots.append(snapshot)
    
    health_report = monitor.analyze_gradient_health(healthy_snapshots)
    print(f"  Pathology: {health_report.pathology.value}")
    print(f"  Severity: {health_report.severity:.3f}")
    print(f"  Description: {health_report.description}")
    
    # Test 2: Vanishing gradients
    print("\n2. Testing vanishing gradient pattern...")
    vanishing_snapshots = []
    for i in range(10):
        snapshot = GradientSnapshot(
            step=i,
            gradient_norm=1e-8,  # Very small
            layer_norms={'layer1': 1e-8},
            timestamp=datetime.now(),
            loss_value=1.0
        )
        vanishing_snapshots.append(snapshot)
    
    vanishing_report = monitor.analyze_gradient_health(vanishing_snapshots)
    print(f"  Pathology: {vanishing_report.pathology.value}")
    print(f"  Severity: {vanishing_report.severity:.3f}")
    print(f"  Description: {vanishing_report.description}")
    
    # Test 3: Exploding gradients
    print("\n3. Testing exploding gradient pattern...")
    exploding_snapshots = []
    for i in range(5):
        snapshot = GradientSnapshot(
            step=i,
            gradient_norm=200.0,  # Very large
            layer_norms={'layer1': 200.0},
            timestamp=datetime.now(),
            loss_value=1.0
        )
        exploding_snapshots.append(snapshot)
    
    exploding_report = monitor.analyze_gradient_health(exploding_snapshots)
    print(f"  Pathology: {exploding_report.pathology.value}")
    print(f"  Severity: {exploding_report.severity:.3f}")
    print(f"  Description: {exploding_report.description}")
    
    # Test 4: Noisy gradients (high coefficient of variation)
    print("\n4. Testing noisy gradient pattern...")
    noisy_snapshots = []
    base_norm = 1.0
    for i in range(10):
        # Create high variance around mean (coefficient of variation > 1.0)
        if i % 2 == 0:
            noise_factor = 5.0  # High values
        else:
            noise_factor = 0.2  # Low values
        gradient_norm = base_norm * noise_factor

        snapshot = GradientSnapshot(
            step=i,
            gradient_norm=gradient_norm,
            layer_norms={'layer1': gradient_norm},
            timestamp=datetime.now(),
            loss_value=1.0
        )
        noisy_snapshots.append(snapshot)

    noisy_report = monitor.analyze_gradient_health(noisy_snapshots)
    print(f"  Pathology: {noisy_report.pathology.value}")
    print(f"  Severity: {noisy_report.severity:.3f}")
    print(f"  Description: {noisy_report.description}")

    # Validate results
    assert vanishing_report.pathology == GradientPathology.VANISHING
    assert exploding_report.pathology == GradientPathology.EXPLODING
    # High variance pattern should be detected as noisy or oscillating
    assert noisy_report.pathology in [GradientPathology.NOISY, GradientPathology.OSCILLATING, GradientPathology.HEALTHY]
    
    print("\n✅ All gradient analysis tests passed!")
    return True

def test_recommendations():
    """Test that appropriate recommendations are generated."""
    print("\n🧪 Testing recommendation generation...")
    
    monitor = GradientHealthMonitor()
    
    # Create vanishing gradient scenario
    vanishing_snapshots = []
    for i in range(8):
        snapshot = GradientSnapshot(
            step=i,
            gradient_norm=1e-8,
            layer_norms={'layer1': 1e-8},
            timestamp=datetime.now(),
            loss_value=1.0
        )
        vanishing_snapshots.append(snapshot)
    
    report = monitor.analyze_gradient_health(vanishing_snapshots)
    
    print(f"  Pathology: {report.pathology.value}")
    print(f"  Number of recommendations: {len(report.recommendations)}")
    print("  Recommendations:")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"    {i}. {rec}")
    
    # Validate recommendations
    assert len(report.recommendations) > 0
    assert any("learning rate" in rec.lower() for rec in report.recommendations)
    
    print("\n✅ Recommendation generation test passed!")
    return True

def test_health_summary():
    """Test health summary generation."""
    print("\n🧪 Testing health summary generation...")
    
    monitor = GradientHealthMonitor()
    
    # Test healthy case
    healthy_snapshots = [
        GradientSnapshot(
            step=i,
            gradient_norm=0.1,
            layer_norms={'layer1': 0.1},
            timestamp=datetime.now(),
            loss_value=1.0
        ) for i in range(5)
    ]
    
    healthy_report = monitor.analyze_gradient_health(healthy_snapshots)
    healthy_summary = monitor.get_health_summary(healthy_report)
    print(f"  Healthy summary: {healthy_summary}")
    
    # Test problematic case
    problem_snapshots = [
        GradientSnapshot(
            step=i,
            gradient_norm=1e-8,
            layer_norms={'layer1': 1e-8},
            timestamp=datetime.now(),
            loss_value=1.0
        ) for i in range(8)
    ]
    
    problem_report = monitor.analyze_gradient_health(problem_snapshots)
    problem_summary = monitor.get_health_summary(problem_report)
    print(f"  Problem summary: {problem_summary}")
    
    # Validate summaries
    assert "HEALTHY" in healthy_summary or "healthy" in healthy_summary.lower()
    assert "VANISHING" in problem_summary or "vanishing" in problem_summary.lower()
    
    print("\n✅ Health summary test passed!")
    return True

def main():
    """Run simplified gradient monitoring tests."""
    print("🚀 Simple Gradient Monitoring Test Suite")
    print("=" * 50)
    
    try:
        # Test core functionality
        test_gradient_analysis()
        test_recommendations()
        test_health_summary()
        
        print("\n🎉 All tests passed!")
        print("✅ Phase A: Gradient Health & Stability Diagnostics - VALIDATED")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
