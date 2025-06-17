#!/usr/bin/env python3
"""
Test Mathematical Query Processing

Simple test to verify mathematical query detection and processing.

Usage:
    python test_math_query.py

Author: SAM Development Team
Version: 1.0.0
"""

import re
import sys

def test_math_detection():
    """Test mathematical pattern detection."""
    print("🧮 Testing Mathematical Query Detection")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What is 67+53-532?",
        "Calculate 10 + 5",
        "67+53-532",
        "What is 100 * 2 / 4?",
        "Can you solve 15 - 3 + 7?",
        "Hello world",  # Non-math query
        "What is the weather?"  # Non-math query
    ]
    
    # Mathematical pattern (same as in secure_streamlit_app.py)
    math_pattern = r'\d+\s*[\+\-\*\/]\s*\d+'
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        # Check if pattern matches
        match = re.search(math_pattern, query)
        if match:
            print(f"✅ Mathematical pattern detected: {match.group()}")
            
            # Extract the full mathematical expression
            expression_match = re.search(r'[\d\+\-\*\/\(\)\.\s]+', query)
            if expression_match:
                expression = expression_match.group().strip()
                print(f"📊 Extracted expression: '{expression}'")
                
                # Validate the expression
                if re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', expression):
                    print(f"✅ Expression is valid for evaluation")
                    
                    try:
                        result = eval(expression)
                        print(f"🧮 Calculation result: {expression} = {result}")
                    except Exception as e:
                        print(f"❌ Calculation failed: {e}")
                else:
                    print(f"❌ Expression contains invalid characters")
            else:
                print(f"❌ Could not extract mathematical expression")
        else:
            print(f"❌ No mathematical pattern detected")

def test_sof_availability():
    """Test if SOF v2 is available."""
    print("\n🤖 Testing SOF v2 Availability")
    print("=" * 50)
    
    try:
        # Test SOF imports
        from sam.orchestration import is_sof_enabled, get_sof_integration
        print("✅ SOF modules can be imported")
        
        # Check if enabled
        enabled = is_sof_enabled()
        print(f"📊 SOF Enabled: {enabled}")
        
        if enabled:
            try:
                sof_integration = get_sof_integration()
                print(f"✅ SOF Integration created: {sof_integration is not None}")
                
                if sof_integration:
                    print(f"📊 SOF Initialized: {sof_integration._initialized}")
                    return True
                else:
                    print("❌ SOF Integration is None")
                    return False
            except Exception as e:
                print(f"❌ Failed to get SOF integration: {e}")
                return False
        else:
            print("❌ SOF is not enabled")
            return False
            
    except Exception as e:
        print(f"❌ Failed to import SOF modules: {e}")
        return False

def test_calculator_direct():
    """Test calculator tool directly."""
    print("\n🧮 Testing Calculator Tool Direct")
    print("=" * 50)
    
    try:
        from sam.orchestration.skills.calculator_tool import CalculatorTool
        from sam.orchestration.uif import SAM_UIF
        
        calculator = CalculatorTool()
        print("✅ CalculatorTool imported and created")
        
        # Test the specific query
        test_expression = "67+53-532"
        test_uif = SAM_UIF(input_query=f"What is {test_expression}?")
        test_uif.intermediate_data["calculation_expression"] = test_expression
        
        print(f"🧮 Testing calculation: {test_expression}")
        
        result_uif = calculator.execute(test_uif)
        
        if "calculation_result" in result_uif.intermediate_data:
            result = result_uif.intermediate_data["calculation_result"]
            print(f"✅ Calculator result: {test_expression} = {result}")
            return True
        else:
            print("❌ Calculator did not produce result")
            print(f"📊 Available data: {list(result_uif.intermediate_data.keys())}")
            return False
            
    except Exception as e:
        print(f"❌ Calculator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_math():
    """Test the fallback math calculation."""
    print("\n⚡ Testing Fallback Math Calculation")
    print("=" * 50)
    
    # This is the same logic as in the secure_streamlit_app.py fallback
    query = "What is 67+53-532?"
    
    import re
    math_pattern = r'\d+\s*[\+\-\*\/]\s*\d+'
    
    if re.search(math_pattern, query):
        print(f"✅ Mathematical query detected: '{query}'")
        
        try:
            # Extract the mathematical expression
            expression = re.search(r'[\d\+\-\*\/\(\)\.\s]+', query).group().strip()
            print(f"📊 Extracted expression: '{expression}'")
            
            # Validate and evaluate safely
            if re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', expression):
                try:
                    # Safe evaluation of mathematical expression
                    result = eval(expression)
                    print(f"✅ Fallback calculation: {expression} = {result}")
                    
                    response = f"""🧮 **Mathematical Calculation**

**Expression:** {expression}
**Result:** {result}

I calculated this using SAM's built-in calculator. For more complex mathematical operations, you can ask me to perform calculations with functions like sin, cos, log, sqrt, etc."""
                    
                    print(f"📄 Generated response:")
                    print(response)
                    return True
                    
                except Exception as calc_error:
                    print(f"❌ Mathematical calculation failed: {calc_error}")
                    return False
            else:
                print(f"❌ Expression contains invalid characters")
                return False
                
        except Exception as e:
            print(f"❌ Mathematical expression extraction failed: {e}")
            return False
    else:
        print(f"❌ No mathematical pattern detected in: '{query}'")
        return False

def main():
    """Main test function."""
    print("🧮 Mathematical Query Processing Test")
    print("=" * 60)
    print("Testing SAM's ability to detect and process mathematical queries")
    
    # Run all tests
    test_math_detection()
    sof_available = test_sof_availability()
    calculator_works = test_calculator_direct()
    fallback_works = test_fallback_math()
    
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"🤖 SOF v2 Available: {'✅' if sof_available else '❌'}")
    print(f"🧮 Calculator Tool Works: {'✅' if calculator_works else '❌'}")
    print(f"⚡ Fallback Math Works: {'✅' if fallback_works else '❌'}")
    
    if sof_available and calculator_works:
        print("\n🎉 Mathematical queries should work via SOF v2!")
        return 0
    elif fallback_works:
        print("\n✅ Mathematical queries should work via fallback!")
        return 0
    else:
        print("\n❌ Mathematical queries will not work properly")
        print("🔧 Check SOF v2 configuration and calculator tool setup")
        return 1

if __name__ == "__main__":
    sys.exit(main())
