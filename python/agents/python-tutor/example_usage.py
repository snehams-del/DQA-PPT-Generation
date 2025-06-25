#!/usr/bin/env python3
"""
Example usage of the enhanced Python Tutor Agent with state and memory management.

This script demonstrates how the Python tutor works with:
- Four structured topics
- Quiz generation and evaluation
- Session state for current quiz progress
- Long-term memory for cross-session learning
"""

import os
from google.adk.sessions import Session
from python_tutor.agent import root_agent

def main():
    """Demonstrate the Python tutor functionality"""
    
    # Create a session for the student
    session = Session(
        user_id="student_123",
        session_id="learning_session_1"
    )
    
    print("=== Python Tutor Demo ===")
    print("This demo shows how the Python tutor works with:")
    print("1. Four structured topics (Basic Syntax → Control Flow → Loops → Lists & Functions)")
    print("2. Conversational teaching followed by quizzes")
    print("3. Cross-session memory and progress tracking")
    print("4. Adaptive learning based on quiz performance")
    print()
    
    # Simulate a first-time student interaction
    print("--- First Session: New Student ---")
    
    # Student starts their learning journey
    messages = [
        "Hi! I'm new to Python and want to learn programming.",
        "Yes, I'd like to start with the basics.",
        "A variable is like a container that holds a value. You create one with the equals sign.",
        "The main types are strings for text, integers for whole numbers, floats for decimals, and booleans for true/false.",
        "You use the print function to show output on the screen.",
    ]
    
    for i, message in enumerate(messages):
        print(f"Student: {message}")
        response = root_agent.run(message, session)
        print(f"Tutor: {response.content}")
        print()
        
        if i == 0:  # After first message, show what the agent discovers
            print("(The agent checks progress and finds this is a new student)")
        elif i == 1:  # After agreeing to start
            print("(The agent begins Topic 1: Basic Syntax and Variables)")
        elif i >= 2:  # During quiz
            print("(The agent evaluates the quiz answer and provides feedback)")
        
        print("-" * 50)
    
    print("\n--- Second Session: Returning Student ---")
    
    # Simulate student returning in a new session
    new_session = Session(
        user_id="student_123", 
        session_id="learning_session_2"
    )
    
    print("Student: Hi, I'm back to continue learning Python!")
    response = root_agent.run("Hi, I'm back to continue learning Python!", new_session)
    print(f"Tutor: {response.content}")
    print()
    print("(The agent checks long-term memory and finds previous quiz results)")
    print("(If any questions were answered incorrectly, it offers review)")
    print("(Then progresses to the next topic based on mastery)")
    
    print("\n--- Key Features Demonstrated ---")
    print("✓ Structured 4-topic curriculum")
    print("✓ Conversational teaching approach")
    print("✓ Natural language quiz evaluation") 
    print("✓ Session state for current quiz tracking")
    print("✓ Long-term memory for progress persistence")
    print("✓ Adaptive learning based on performance")
    print("✓ Cross-session continuity")
    
    print("\n--- Session State Example ---")
    print("During quiz: {")
    print("  'current_quiz': {")
    print("    'topic_number': 1,")
    print("    'current_question': 2,")
    print("    'results': [{'correct': True}, {'correct': False}]")
    print("  },")
    print("  'quiz_active': True")
    print("}")
    
    print("\n--- Long-term Memory Example ---")
    print("Across sessions: {")
    print("  'current_topic': 2,")
    print("  'quiz_history': {")
    print("    '1': [{'score': 66.7, 'date': '2025-01-XX', 'results': [...]}]")
    print("  }")
    print("}")

if __name__ == "__main__":
    # Set up environment for demo
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
    
    main() 