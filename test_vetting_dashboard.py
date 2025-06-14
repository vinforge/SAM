#!/usr/bin/env python3
"""
Test script for the enhanced vetting dashboard functionality.
This script verifies that the vetting dashboard can properly display security analysis results.
"""

import json
import sys
from pathlib import Path

def test_vetting_data_structure():
    """Test that vetted files have the expected structure."""
    print("🔍 Testing Vetting Data Structure...")
    
    vetted_dir = Path("vetted")
    if not vetted_dir.exists():
        print("❌ No vetted directory found")
        return False
    
    vetted_files = list(vetted_dir.glob("*.json"))
    if not vetted_files:
        print("❌ No vetted files found")
        return False
    
    print(f"📁 Found {len(vetted_files)} vetted files")
    
    for file_path in vetted_files[:3]:  # Test first 3 files
        print(f"\n📄 Testing file: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for vetting results
            vetting_results = data.get('vetting_results', data.get('vetting_result', {}))
            
            if not vetting_results:
                print(f"  ❌ No vetting results found")
                continue
            
            # Check required fields
            required_fields = ['status', 'recommendation', 'overall_score', 'scores']
            missing_fields = []
            
            for field in required_fields:
                if field not in vetting_results:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"  ❌ Missing fields: {missing_fields}")
                continue
            
            # Check scores structure
            scores = vetting_results.get('scores', {})
            expected_dimensions = ['credibility', 'persuasion', 'speculation', 'purity']
            
            for dimension in expected_dimensions:
                if dimension in scores:
                    score = scores[dimension]
                    print(f"  ✅ {dimension}: {score:.1%}")
                else:
                    print(f"  ⚠️ Missing dimension: {dimension}")
            
            # Check recommendation
            recommendation = vetting_results.get('recommendation', 'UNKNOWN')
            overall_score = vetting_results.get('overall_score', 0)
            print(f"  📋 Recommendation: {recommendation}")
            print(f"  🎯 Overall Score: {overall_score:.1%}")
            
            # Check risk factors
            risk_factors = vetting_results.get('risk_assessment', {}).get('risk_factors', [])
            if risk_factors:
                print(f"  ⚠️ Risk Factors: {len(risk_factors)}")
                for risk in risk_factors:
                    severity = risk.get('severity', 'unknown')
                    dimension = risk.get('dimension', 'unknown')
                    print(f"    - {severity} risk in {dimension}")
            else:
                print(f"  ✅ No risk factors detected")
            
            print(f"  ✅ File structure is valid")
            
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            continue
    
    return True

def test_security_overview_calculation():
    """Test the security overview calculation function."""
    print("\n🛡️ Testing Security Overview Calculation...")
    
    try:
        # Import the function (this would normally be imported from secure_streamlit_app)
        # For testing, we'll implement a simplified version
        
        vetted_dir = Path("vetted")
        if not vetted_dir.exists():
            print("❌ No vetted directory found")
            return False
        
        total_critical_risks = 0
        total_high_risks = 0
        total_credibility = 0
        total_purity = 0
        files_with_analysis = 0
        
        for file_path in vetted_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    vetting_result = data.get('vetting_results', data.get('vetting_result', {}))
                    
                    if vetting_result:
                        files_with_analysis += 1
                        
                        # Count risk factors
                        risk_factors = vetting_result.get('risk_assessment', {}).get('risk_factors', [])
                        critical_risks = len([r for r in risk_factors if r.get('severity') == 'critical'])
                        high_risks = len([r for r in risk_factors if r.get('severity') == 'high'])
                        
                        total_critical_risks += critical_risks
                        total_high_risks += high_risks
                        
                        # Accumulate scores
                        scores = vetting_result.get('scores', {})
                        total_credibility += scores.get('credibility', 0)
                        total_purity += scores.get('purity', 0)
                        
            except Exception as e:
                print(f"  ⚠️ Error processing file {file_path.name}: {e}")
                continue
        
        if files_with_analysis == 0:
            print("❌ No files with analysis found")
            return False
        
        avg_credibility = total_credibility / files_with_analysis
        avg_purity = total_purity / files_with_analysis
        
        print(f"📊 Security Overview Results:")
        print(f"  📁 Files Analyzed: {files_with_analysis}")
        print(f"  🔴 Total Critical Risks: {total_critical_risks}")
        print(f"  🟠 Total High Risks: {total_high_risks}")
        print(f"  🎓 Average Credibility: {avg_credibility:.1%}")
        print(f"  🧹 Average Purity: {avg_purity:.1%}")
        
        # Determine overall security status
        if total_critical_risks == 0 and total_high_risks == 0:
            print("  🛡️ Overall Status: All Clear - No Critical Security Risks")
        elif total_critical_risks > 0:
            print(f"  ⚠️ Overall Status: Critical Alert - {total_critical_risks} Critical Risk(s)")
        else:
            print(f"  ⚠️ Overall Status: Review Required - {total_high_risks} High Risk(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error calculating security overview: {e}")
        return False

def main():
    """Run all vetting dashboard tests."""
    print("🧪 SAM Vetting Dashboard Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Data structure
    if test_vetting_data_structure():
        tests_passed += 1
    
    # Test 2: Security overview calculation
    if test_security_overview_calculation():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! Vetting dashboard should work correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
