# SAM Query Routing Fix - Restored Basic Question Answering

## Problem Identified

SAM was unable to answer basic questions like "tell me a joke", "what is 3+56-83?", or "what is an LLM?" because the query routing system was being too aggressive in suggesting web retrieval for ANY query that didn't have local memory context.

### Symptoms
- All basic questions resulted in: "I couldn't find closely relevant information"
- Web search escalation was suggested for simple queries that the LLM should handle directly
- Math problems, jokes, greetings, and explanations were not being processed

### Root Cause Analysis

The issue was in the `WebRetrievalSuggester.should_suggest_web_retrieval()` method in `utils/web_retrieval_suggester.py`. The logic was:

```python
# PROBLEMATIC LOGIC (BEFORE FIX)
def should_suggest_web_retrieval(self, query: str, context_results: List[Any]) -> bool:
    # Suggest if no local results found
    if not context_results or len(context_results) == 0:
        return True  # ❌ TOO AGGRESSIVE - suggests web retrieval for ALL queries without context
    
    # Suggest if results are very limited
    if len(context_results) < 2:
        return True  # ❌ TOO AGGRESSIVE
```

This meant that ANY query without sufficient local context would trigger web retrieval suggestions instead of allowing the LLM to generate responses directly.

## Solution Implemented

### 1. **Enhanced Web Retrieval Logic**

Modified `utils/web_retrieval_suggester.py` to be more intelligent about when to suggest web retrieval:

```python
# FIXED LOGIC (AFTER FIX)
def should_suggest_web_retrieval(self, query: str, context_results: List[Any]) -> bool:
    query_lower = query.lower()
    
    # CRITICAL FIX: Don't suggest web retrieval for basic queries that LLM can handle
    basic_query_indicators = [
        'tell me a joke', 'joke', 'funny', 'humor',
        'what is', 'calculate', 'compute', 'math', '+', '-', '*', '/',
        'hello', 'hi', 'how are you', 'good morning', 'good afternoon',
        'explain', 'define', 'meaning of', 'what does', 'how to',
        'write', 'create', 'generate', 'make', 'help me',
        'story', 'poem', 'essay', 'letter', 'email',
        'translate', 'language', 'grammar', 'spelling'
    ]
    
    # If it's a basic query the LLM can handle, don't suggest web retrieval
    if any(indicator in query_lower for indicator in basic_query_indicators):
        return False
    
    # Don't suggest for very short queries (likely basic questions)
    if len(query.split()) <= 3:
        return False
    
    # Only suggest web retrieval for specific types of queries that need current information
    web_retrieval_indicators = [
        'latest', 'recent', 'current', 'today', 'now', '2024', '2025',
        'news', 'breaking', 'update', 'announcement',
        'price', 'stock', 'weather', 'forecast',
        'who is', 'biography', 'profile of', 'information about',
        'research', 'study', 'paper', 'article',
        'company', 'organization', 'website', 'official'
    ]
    
    # Check if query explicitly needs web information
    needs_web_info = any(indicator in query_lower for indicator in web_retrieval_indicators)
    
    # Only suggest web retrieval if:
    # 1. Query explicitly needs web information AND
    # 2. No local results found OR very limited results
    if needs_web_info:
        if not context_results or len(context_results) == 0:
            return True
        if len(context_results) < 2:
            return True
    
    return False
```

### 2. **Enhanced System Prompts**

Modified `web_ui/app.py` to ensure general queries are handled properly even without context:

```python
# ENHANCED SYSTEM PROMPT FOR GENERAL QUERIES
base_prompt = "You are SAM, an intelligent multimodal assistant. Answer the user's question helpfully and accurately. You can handle a wide variety of questions including jokes, math problems, explanations, creative writing, and general knowledge questions."

if context.strip():
    system_prompt = f"{base_prompt}\n\nWhen thinking through complex questions, you can use <think>...</think> tags to show your reasoning process. This helps users understand how you arrived at your answer.\n\nAdditional context from your knowledge base:{context}"
else:
    system_prompt = f"{base_prompt}\n\nWhen thinking through complex questions, you can use <think>...</think> tags to show your reasoning process. This helps users understand how you arrived at your answer."
```

### 3. **Added Global Instance Function**

Added missing global instance function to `utils/web_retrieval_suggester.py`:

```python
# Global instance
_web_retrieval_suggester = None

def get_web_retrieval_suggester() -> WebRetrievalSuggester:
    """Get or create a global web retrieval suggester instance."""
    global _web_retrieval_suggester
    
    if _web_retrieval_suggester is None:
        _web_retrieval_suggester = WebRetrievalSuggester()
    
    return _web_retrieval_suggester
```

## Testing Results

### ✅ Basic Queries (Should NOT trigger web retrieval)
- `"tell me a joke"` → `False` ✅
- `"what is 3+56-83?"` → `False` ✅  
- `"hello"` → `False` ✅
- `"explain what an LLM is"` → `False` ✅
- `"write a short poem"` → `False` ✅

### ✅ Web-Specific Queries (Should trigger web retrieval)
- `"latest news about AI"` → `True` ✅
- `"current stock price of Apple"` → `True` ✅
- `"who is the current president"` → `True` ✅
- `"recent research on quantum computing"` → `True` ✅

## Impact

### Before Fix
- ❌ SAM couldn't answer basic questions
- ❌ All queries without local context triggered web retrieval suggestions
- ❌ Math problems, jokes, greetings failed
- ❌ Poor user experience for simple interactions

### After Fix
- ✅ SAM can handle basic questions directly using LLM
- ✅ Web retrieval only suggested for queries that actually need current information
- ✅ Math problems, jokes, explanations work properly
- ✅ Improved user experience for general interactions
- ✅ Maintains intelligent web retrieval for appropriate queries

## Files Modified

1. **`utils/web_retrieval_suggester.py`**
   - Enhanced `should_suggest_web_retrieval()` logic
   - Added basic query detection
   - Added global instance function

2. **`web_ui/app.py`**
   - Enhanced system prompts for general queries
   - Improved context handling when no local results found

## Conclusion

The fix restores SAM's ability to answer basic questions while maintaining intelligent web retrieval suggestions for queries that actually need current information. This provides a much better user experience and allows SAM to function as expected for general conversational AI tasks.

**Key Principle**: The LLM should handle basic queries directly, and web retrieval should only be suggested for queries that explicitly need current, external information.
