#!/usr/bin/env python3
"""
Simple Math Test

Quick test to verify mathematical expression extraction is working.
"""

import re

def test_math_extraction(prompt):
    """Test the mathematical expression extraction logic."""
    print(f"\nTesting: '{prompt}'")
    
    # Detection pattern
    math_pattern = r'\d+\s*[\+\-\*\/]\s*\d+'
    if re.search(math_pattern, prompt):
        print("✅ Mathematical pattern detected")
        
        # Enhanced mathematical expression extraction
        # First try to find complete mathematical expressions
        complete_expression_matches = re.findall(r'\d+(?:\s*[\+\-\*\/]\s*\d+)+', prompt)
        
        # Also look for expressions with parentheses
        paren_expression_matches = re.findall(r'\([^)]*\d+(?:\s*[\+\-\*\/]\s*\d+)+[^)]*\)', prompt)
        
        # Combine all matches
        expression_matches = complete_expression_matches + paren_expression_matches
        
        # If no complete expressions found, fall back to the old method
        if not expression_matches:
            expression_matches = re.findall(r'[\d\+\-\*\/\(\)\.\s]+', prompt)

        print(f"Expression matches: {expression_matches}")

        # Find the most likely mathematical expression
        best_expression = None
        for match in expression_matches:
            cleaned = match.strip()
            # Must contain at least one operator and be valid
            if re.search(r'\d+\s*[\+\-\*\/]\s*\d+', cleaned) and re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', cleaned):
                best_expression = cleaned
                break

        if best_expression:
            try:
                # Safe evaluation of mathematical expression
                result = eval(best_expression)
                print(f"✅ Calculation: {best_expression} = {result}")
                return result
            except Exception as calc_error:
                print(f"❌ Calculation failed: {calc_error}")
                return None
        else:
            print("❌ No valid expression found")
            return None
    else:
        print("❌ No mathematical pattern detected")
        return None

def main():
    """Test various mathematical queries."""
    print("🧮 Simple Math Expression Test")
    print("=" * 50)
    
    test_cases = [
        "56+43-454",
        "what is 56+43-454?",
        "What is 56+43-454?",
        "Calculate 56+43-454",
        "56 + 43 - 454",
        "what is 56 + 43 - 454?",
        "100*2/4",
        "What is 100*2/4?",
        "15-3+7",
        "Can you solve 15-3+7?",
        "10+5",
        "Calculate 10 + 5"
    ]
    
    for test_case in test_cases:
        test_math_extraction(test_case)
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    main()
