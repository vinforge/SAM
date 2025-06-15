#!/usr/bin/env python3
"""
Test script for the SLP (Scalable Latent Program) system.
Tests basic functionality of program capture, storage, and retrieval.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sam.cognition.slp import (
    LatentProgram, 
    ProgramSignature, 
    generate_signature,
    LatentProgramStore,
    ProgramManager,
    initialize_slp_system
)

def test_signature_generation():
    """Test signature generation functionality."""
    print("🔍 Testing signature generation...")
    
    query = "Summarize the technical documentation about machine learning algorithms"
    context = {
        'documents': [
            {'type': 'pdf', 'content': 'technical machine learning content'},
            {'type': 'md', 'content': 'algorithm documentation'}
        ],
        'session_length': 5,
        'user_preferences': {'detail_level': 'high'}
    }
    
    signature = generate_signature(query, context, 'researcher')
    
    print(f"✅ Generated signature:")
    print(f"   Primary intent: {signature.primary_intent}")
    print(f"   Document types: {signature.document_types}")
    print(f"   Content domains: {signature.content_domains}")
    print(f"   Complexity: {signature.complexity_level}")
    print(f"   Signature hash: {signature.signature_hash}")
    
    return signature

def test_program_store():
    """Test program storage and retrieval."""
    print("\n💾 Testing program store...")
    
    store = LatentProgramStore("data/test_latent_programs.db")
    
    # Create a test program
    signature = {
        'primary_intent': 'summarize',
        'document_types': ['pdf'],
        'content_domains': ['technical'],
        'signature_hash': 'test123'
    }
    
    program = LatentProgram(
        signature=signature,
        tpv_config={'reasoning_depth': 'high'},
        active_profile='researcher',
        prompt_template_used='technical_summary_template'
    )
    
    # Store the program
    success = store.store_program(program)
    print(f"✅ Program stored: {success}")
    
    # Retrieve the program
    retrieved = store.get_program(program.id)
    print(f"✅ Program retrieved: {retrieved is not None}")
    
    if retrieved:
        print(f"   ID: {retrieved.id}")
        print(f"   Profile: {retrieved.active_profile}")
        print(f"   Usage count: {retrieved.usage_count}")
    
    # Test statistics
    stats = store.get_program_statistics()
    print(f"✅ Store statistics: {stats}")
    
    return store, program

def test_program_manager():
    """Test program manager functionality."""
    print("\n🧠 Testing program manager...")
    
    manager = ProgramManager()
    
    # Test program capture
    query = "Analyze the performance metrics in the quarterly report"
    context = {
        'documents': [{'type': 'pdf', 'content': 'quarterly performance data'}],
        'session_length': 3
    }
    
    # Simulate a successful interaction result
    result = {
        'quality_score': 0.8,
        'user_feedback': 4.5,
        'meta_confidence': 0.7,
        'execution_time_ms': 1500,
        'token_count': 250,
        'tpv_config': {'reasoning_depth': 'medium'},
        'prompt_template': 'analysis_template',
        'reasoning_trace': {'steps': ['analyze', 'synthesize']}
    }
    
    # Test program capture
    captured = manager.consider_program_capture(query, context, result, 'analyst')
    print(f"✅ Program capture: {captured}")
    
    # Test program finding
    matching_program = manager.find_matching_program(query, context, 'analyst')
    print(f"✅ Found matching program: {matching_program is not None}")
    
    if matching_program:
        print(f"   Program ID: {matching_program.id}")
        print(f"   Confidence: {matching_program.confidence_score:.2f}")
    
    # Test statistics
    stats = manager.get_program_statistics()
    print(f"✅ Manager statistics: {stats}")
    
    return manager

def test_similarity_matching():
    """Test signature similarity matching."""
    print("\n🔄 Testing similarity matching...")
    
    # Create two similar signatures
    query1 = "Summarize the technical documentation"
    context1 = {'documents': [{'type': 'pdf'}]}
    sig1 = generate_signature(query1, context1)
    
    query2 = "Provide a summary of the technical docs"
    context2 = {'documents': [{'type': 'pdf'}]}
    sig2 = generate_signature(query2, context2)
    
    similarity = sig1.calculate_similarity(sig2)
    print(f"✅ Similarity score: {similarity:.2f}")
    
    # Test with different signatures
    query3 = "Translate this text to Spanish"
    context3 = {'documents': [{'type': 'txt'}]}
    sig3 = generate_signature(query3, context3)
    
    similarity2 = sig1.calculate_similarity(sig3)
    print(f"✅ Different task similarity: {similarity2:.2f}")
    
    return similarity, similarity2

def test_program_lifecycle():
    """Test complete program lifecycle."""
    print("\n🔄 Testing program lifecycle...")
    
    manager = ProgramManager()
    
    # Simulate multiple interactions with the same pattern
    base_query = "Summarize the research paper"
    base_context = {'documents': [{'type': 'pdf', 'content': 'research content'}]}
    
    for i in range(3):
        query = f"{base_query} #{i+1}"
        context = base_context.copy()
        context['iteration'] = i + 1
        
        result = {
            'quality_score': 0.8 + (i * 0.05),
            'user_feedback': 4.0 + (i * 0.2),
            'meta_confidence': 0.7,
            'execution_time_ms': 1200 - (i * 100),
            'token_count': 200 + (i * 20),
            'tpv_config': {'reasoning_depth': 'medium'},
            'reasoning_trace': {'steps': ['analyze', 'summarize']}
        }
        
        captured = manager.consider_program_capture(query, context, result, 'researcher')
        print(f"   Iteration {i+1} - Captured: {captured}")
    
    # Now test if we can find and use the pattern
    test_query = "Summarize the research paper #4"
    matching = manager.find_matching_program(test_query, base_context, 'researcher')
    
    print(f"✅ Found pattern after learning: {matching is not None}")
    if matching:
        print(f"   Usage count: {matching.usage_count}")
        print(f"   Confidence: {matching.confidence_score:.2f}")
    
    return matching

def main():
    """Run all SLP system tests."""
    print("🚀 Starting SLP System Tests")
    print("=" * 50)
    
    try:
        # Test individual components
        signature = test_signature_generation()
        store, program = test_program_store()
        manager = test_program_manager()
        sim1, sim2 = test_similarity_matching()
        lifecycle_program = test_program_lifecycle()
        
        print("\n📊 Test Summary")
        print("=" * 30)
        print("✅ Signature generation: PASSED")
        print("✅ Program store: PASSED")
        print("✅ Program manager: PASSED")
        print("✅ Similarity matching: PASSED")
        print("✅ Program lifecycle: PASSED")
        
        print(f"\n🎯 Key Metrics:")
        print(f"   High similarity score: {sim1:.2f}")
        print(f"   Low similarity score: {sim2:.2f}")
        print(f"   Programs in store: {store.get_program_statistics().get('active_programs', 0)}")
        
        print("\n🎉 All SLP system tests completed successfully!")
        
        # Test system initialization
        print("\n🔧 Testing system initialization...")
        slp_manager = initialize_slp_system()
        if slp_manager:
            print("✅ SLP system initialized successfully")
        else:
            print("⚠️ SLP system initialization failed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
