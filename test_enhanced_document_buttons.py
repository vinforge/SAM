#!/usr/bin/env python3
"""
Test script to verify the enhanced document analysis button logic.

This script tests that the enhanced prompts are generated correctly based on
document types and that they leverage SAM's full analytical capabilities.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_prompt_generation():
    """Test that enhanced prompts are generated correctly for different document types."""
    
    print("🧪 Testing Enhanced Document Button Logic")
    print("=" * 50)
    
    # Import the enhanced prompt functions
    try:
        from secure_streamlit_app import (
            generate_enhanced_summary_prompt,
            generate_enhanced_questions_prompt,
            generate_enhanced_analysis_prompt
        )
        print("✅ Successfully imported enhanced prompt functions")
    except ImportError as e:
        print(f"❌ Failed to import functions: {e}")
        return False
    
    # Test cases for different document types
    test_cases = [
        {
            "filename": "research_paper_on_ai.pdf",
            "expected_type": "research paper",
            "should_contain": ["Research Paper Focus", "Methodology", "Academic Standards"]
        },
        {
            "filename": "business_proposal_2024.docx", 
            "expected_type": "proposal",
            "should_contain": ["Proposal Focus", "Strategic Analysis", "Implementation"]
        },
        {
            "filename": "quarterly_report_analysis.pdf",
            "expected_type": "report",
            "should_contain": ["Report Focus", "Business Context", "Actionable Insights"]
        },
        {
            "filename": "technical_specification.md",
            "expected_type": "general",
            "should_contain": ["Text Analysis", "Content Structure", "Knowledge Extraction"]
        },
        {
            "filename": "meeting_notes.txt",
            "expected_type": "general", 
            "should_contain": ["Text Analysis", "Main themes", "Actionable insights"]
        }
    ]
    
    all_tests_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['filename']} ({test_case['expected_type']})")
        
        # Test Summary Prompt
        try:
            summary_prompt = generate_enhanced_summary_prompt(test_case['filename'])
            
            # Check that prompt is enhanced (not generic)
            if len(summary_prompt) < 500:  # Enhanced prompts should be substantial
                print(f"❌ Summary prompt too short: {len(summary_prompt)} chars")
                all_tests_passed = False
            else:
                print(f"✅ Summary prompt generated: {len(summary_prompt)} chars")
            
            # Check for document-specific content
            contains_specific = any(keyword in summary_prompt for keyword in test_case['should_contain'])
            if contains_specific:
                print("✅ Summary prompt contains document-type-specific content")
            else:
                print(f"❌ Summary prompt missing specific content: {test_case['should_contain']}")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Summary prompt generation failed: {e}")
            all_tests_passed = False
        
        # Test Questions Prompt
        try:
            questions_prompt = generate_enhanced_questions_prompt(test_case['filename'])
            
            if len(questions_prompt) < 500:
                print(f"❌ Questions prompt too short: {len(questions_prompt)} chars")
                all_tests_passed = False
            else:
                print(f"✅ Questions prompt generated: {len(questions_prompt)} chars")
                
            # Check for question categories
            required_categories = ["Clarification Questions", "Insight Questions", "Application Questions"]
            has_categories = all(cat in questions_prompt for cat in required_categories)
            if has_categories:
                print("✅ Questions prompt contains all required categories")
            else:
                print("❌ Questions prompt missing required categories")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Questions prompt generation failed: {e}")
            all_tests_passed = False
        
        # Test Analysis Prompt
        try:
            analysis_prompt = generate_enhanced_analysis_prompt(test_case['filename'])
            
            if len(analysis_prompt) < 800:  # Analysis should be most comprehensive
                print(f"❌ Analysis prompt too short: {len(analysis_prompt)} chars")
                all_tests_passed = False
            else:
                print(f"✅ Analysis prompt generated: {len(analysis_prompt)} chars")
                
            # Check for analytical framework
            required_sections = ["Structural Analysis", "Content Deep Dive", "Insight Synthesis", "Strategic Implications"]
            has_framework = all(section in analysis_prompt for section in required_sections)
            if has_framework:
                print("✅ Analysis prompt contains comprehensive framework")
            else:
                print("❌ Analysis prompt missing framework sections")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Analysis prompt generation failed: {e}")
            all_tests_passed = False
    
    return all_tests_passed

def test_prompt_quality():
    """Test the quality and structure of generated prompts."""
    
    print("\n🔍 Testing Prompt Quality")
    print("=" * 30)
    
    try:
        from secure_streamlit_app import generate_enhanced_summary_prompt
        
        # Test with a research paper
        prompt = generate_enhanced_summary_prompt("machine_learning_research_paper.pdf")
        
        # Quality checks
        quality_indicators = [
            ("Synthesis approach", "SYNTHESIS APPROACH" in prompt),
            ("Structured output", "STRUCTURED OUTPUT" in prompt),
            ("Document-specific analysis", "DOCUMENT-SPECIFIC ANALYSIS" in prompt),
            ("Capability leverage", "LEVERAGE YOUR CAPABILITIES" in prompt),
            ("Research focus", "Research Paper Focus" in prompt),
            ("Academic standards", "Academic Standards" in prompt)
        ]
        
        all_quality_passed = True
        for indicator, check in quality_indicators:
            if check:
                print(f"✅ {indicator}")
            else:
                print(f"❌ Missing: {indicator}")
                all_quality_passed = False
        
        return all_quality_passed
        
    except Exception as e:
        print(f"❌ Quality test failed: {e}")
        return False

def test_document_type_detection():
    """Test that document type detection works correctly."""
    
    print("\n🎯 Testing Document Type Detection")
    print("=" * 35)
    
    try:
        from secure_streamlit_app import generate_enhanced_summary_prompt
        
        # Test different document types
        test_files = {
            "ai_research_study.pdf": "Research Paper Focus",
            "business_proposal.docx": "Proposal Focus", 
            "quarterly_report.pdf": "Report Focus",
            "technical_spec.md": "Text Analysis",
            "random_document.txt": "Text Analysis"
        }
        
        all_detection_passed = True
        for filename, expected_focus in test_files.items():
            prompt = generate_enhanced_summary_prompt(filename)
            
            if expected_focus in prompt:
                print(f"✅ {filename} → {expected_focus}")
            else:
                print(f"❌ {filename} → Expected '{expected_focus}' not found")
                all_detection_passed = False
        
        return all_detection_passed
        
    except Exception as e:
        print(f"❌ Document type detection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Enhanced Document Button Tests")
    print("=" * 60)
    
    # Run all tests
    test1_passed = test_enhanced_prompt_generation()
    test2_passed = test_prompt_quality()
    test3_passed = test_document_type_detection()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Enhanced Prompt Generation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Prompt Quality: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"   Document Type Detection: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL TESTS PASSED! Enhanced document buttons are working correctly.")
        print("\n💡 The enhanced buttons now provide:")
        print("   • Document-type-aware intelligent analysis")
        print("   • Strategic, high-value questions and insights")
        print("   • Comprehensive analytical frameworks")
        print("   • Full utilization of SAM's capabilities")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED! Enhanced button logic needs attention.")
        sys.exit(1)
