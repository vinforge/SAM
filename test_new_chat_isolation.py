#!/usr/bin/env python3
"""
Test script to verify that New Chat functionality properly isolates conversation history.

This script simulates the conversation flow to ensure that when a user clicks "New Chat",
the historic chat data doesn't interfere with the new conversation.
"""

import sys
import os
import logging
from unittest.mock import Mock, patch
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_conversation_isolation():
    """Test that new chats start with empty conversation history."""
    
    print("🧪 Testing New Chat Conversation Isolation")
    print("=" * 50)
    
    try:
        # Mock Streamlit session state
        mock_session_state = {
            'session_id': 'test_session_001',
            'user_id': 'test_user',
            'chat_history': [],
            'conversation_history': ""
        }
        
        # Test 1: Simulate existing conversation
        print("\n📝 Test 1: Simulating existing conversation...")
        
        with patch('streamlit.session_state', mock_session_state):
            # Import after patching to ensure mocks are in place
            from sam.session.state_manager import get_session_manager
            
            session_manager = get_session_manager()
            session_id = 'test_session_001'
            
            # Create session and add some conversation history
            session_manager.create_session(session_id, 'test_user')
            session_manager.add_turn(session_id, 'user', 'What is machine learning?')
            session_manager.add_turn(session_id, 'assistant', 'Machine learning is a subset of AI...')
            session_manager.add_turn(session_id, 'user', 'Can you give me examples?')
            session_manager.add_turn(session_id, 'assistant', 'Sure! Examples include...')
            
            # Get conversation history
            history_before = session_manager.format_conversation_history(session_id, max_turns=8)
            print(f"✅ Conversation history before clear: {len(history_before)} characters")
            print(f"   Preview: {history_before[:100]}...")
            
            # Test 2: Simulate "New Chat" button click
            print("\n🔄 Test 2: Simulating 'New Chat' button click...")
            
            # Archive current conversation (this is what the New Chat button does)
            from sam.conversation.contextual_relevance import get_contextual_relevance_engine
            relevance_engine = get_contextual_relevance_engine()
            
            conversation_buffer = session_manager.get_conversation_history(session_id)
            if conversation_buffer:
                archived_thread = relevance_engine.archive_conversation_thread(conversation_buffer)
                print(f"✅ Archived conversation: '{archived_thread.title}'")
            
            # Clear the session (this is what the New Chat button does)
            session_manager.clear_session(session_id)
            
            # Clear session state variables
            mock_session_state['chat_history'] = []
            mock_session_state['conversation_history'] = ""
            
            print("✅ Session cleared successfully")
            
            # Test 3: Verify empty history for new conversation
            print("\n🔍 Test 3: Verifying empty history for new conversation...")
            
            # Get conversation history BEFORE adding new prompt (this is the fix)
            history_after_clear = session_manager.format_conversation_history(session_id, max_turns=8)
            print(f"✅ Conversation history after clear: '{history_after_clear}'")
            
            # Verify it's empty or shows "No recent conversation history"
            is_empty = (history_after_clear == "" or 
                       history_after_clear == "No recent conversation history.")
            
            if is_empty:
                print("✅ SUCCESS: New chat starts with empty conversation history!")
            else:
                print(f"❌ FAILURE: New chat still has history: '{history_after_clear}'")
                return False
            
            # Test 4: Simulate adding new prompt and verify isolation
            print("\n📝 Test 4: Testing new conversation isolation...")
            
            # Add a new user prompt (this simulates a user asking a question in the new chat)
            new_prompt = "What is quantum computing?"
            session_manager.add_turn(session_id, 'user', new_prompt)
            
            # Get history again - this should now show only the new prompt
            history_with_new_prompt = session_manager.format_conversation_history(session_id, max_turns=8)
            print(f"✅ History after adding new prompt: '{history_with_new_prompt}'")
            
            # Verify the new prompt is there but no old conversation
            contains_new_prompt = new_prompt in history_with_new_prompt
            contains_old_content = "machine learning" in history_with_new_prompt.lower()
            
            if contains_new_prompt and not contains_old_content:
                print("✅ SUCCESS: New conversation is properly isolated!")
                return True
            else:
                print(f"❌ FAILURE: Conversation isolation failed")
                print(f"   Contains new prompt: {contains_new_prompt}")
                print(f"   Contains old content: {contains_old_content}")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_history_order():
    """Test that conversation history is retrieved BEFORE adding current prompt."""
    
    print("\n🧪 Testing Conversation History Order")
    print("=" * 50)
    
    try:
        # Mock the session state and session manager behavior
        mock_session_state = {
            'session_id': 'test_session_002',
            'user_id': 'test_user',
            'conversation_history': ""
        }
        
        with patch('streamlit.session_state', mock_session_state):
            from sam.session.state_manager import get_session_manager
            
            session_manager = get_session_manager()
            session_id = 'test_session_002'
            
            # Create empty session
            session_manager.create_session(session_id, 'test_user')
            
            # Simulate the fixed order of operations:
            # 1. Get conversation history BEFORE adding current prompt
            history_before_adding = session_manager.format_conversation_history(session_id, max_turns=8)
            
            # 2. Add current prompt to buffer
            current_prompt = "Hello, this is a new conversation"
            session_manager.add_turn(session_id, 'user', current_prompt)
            
            # 3. Verify that the history retrieved before adding is empty
            is_empty_before = (history_before_adding == "" or 
                             history_before_adding == "No recent conversation history.")
            
            if is_empty_before:
                print("✅ SUCCESS: History retrieved before adding prompt is empty")
                return True
            else:
                print(f"❌ FAILURE: History before adding prompt: '{history_before_adding}'")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: Order test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting New Chat Isolation Tests")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_conversation_isolation()
    test2_passed = test_conversation_history_order()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Conversation Isolation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   History Order: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! New Chat isolation is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED! New Chat isolation needs more work.")
        sys.exit(1)
