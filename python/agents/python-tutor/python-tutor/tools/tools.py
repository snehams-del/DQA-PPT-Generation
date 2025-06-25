# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# add docstring to this module

import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

from google.adk.tools import ToolContext


# Topic definitions
TOPICS = {
    1: "Basic Syntax and Variables",
    2: "Control Flow and Conditionals", 
    3: "Loops and Iteration",
    4: "Lists and Basic Functions"
}

# Quiz question pools for each topic
QUIZ_QUESTIONS = {
    1: [  # Basic Syntax and Variables
        {
            "question": "What is a variable in Python and how do you create one?",
            "key_concepts": ["variable", "assignment", "equals sign", "name", "value"],
            "sample_answer": "A variable is a name that stores a value. You create one by using the assignment operator (=), like: name = 'John'"
        },
        {
            "question": "What are the main data types in Python? Give an example of each.",
            "key_concepts": ["string", "integer", "float", "boolean", "str", "int", "bool"],
            "sample_answer": "String ('hello'), Integer (42), Float (3.14), Boolean (True/False)"
        },
        {
            "question": "How do you display output in Python?",
            "key_concepts": ["print", "output", "display", "console"],
            "sample_answer": "Use the print() function, like: print('Hello World')"
        },
        {
            "question": "What are Python's rules for variable naming?",
            "key_concepts": ["letters", "underscore", "numbers", "start", "keywords"],
            "sample_answer": "Start with letter or underscore, can contain letters/numbers/underscores, no spaces or special characters, can't be keywords"
        },
        {
            "question": "How do you add comments to Python code?",
            "key_concepts": ["hash", "#", "comment", "explain"],
            "sample_answer": "Use # for single line comments, like: # This is a comment"
        }
    ],
    2: [  # Control Flow and Conditionals
        {
            "question": "How do you write an if statement in Python?",
            "key_concepts": ["if", "condition", "colon", "indentation", "true"],
            "sample_answer": "Use 'if condition:' followed by indented code block that runs when condition is True"
        },
        {
            "question": "What's the difference between == and = in Python?",
            "key_concepts": ["comparison", "assignment", "equality", "operator"],
            "sample_answer": "== compares values for equality, = assigns a value to a variable"
        },
        {
            "question": "How do you check multiple conditions in Python?",
            "key_concepts": ["elif", "else", "and", "or", "multiple"],
            "sample_answer": "Use elif for additional conditions, else for default case, and/or for combining conditions"
        },
        {
            "question": "What are comparison operators in Python?",
            "key_concepts": ["==", "!=", "<", ">", "<=", ">=", "compare"],
            "sample_answer": "==, !=, <, >, <=, >= for comparing values"
        },
        {
            "question": "How do logical operators work in Python?",
            "key_concepts": ["and", "or", "not", "boolean", "logic"],
            "sample_answer": "'and' requires both conditions true, 'or' requires at least one true, 'not' reverses the boolean"
        }
    ],
    3: [  # Loops and Iteration
        {
            "question": "What's the difference between for loops and while loops?",
            "key_concepts": ["for", "while", "iteration", "condition", "sequence"],
            "sample_answer": "For loops iterate over sequences/ranges, while loops continue as long as a condition is True"
        },
        {
            "question": "How do you create a for loop that counts from 1 to 5?",
            "key_concepts": ["for", "range", "1", "5", "loop"],
            "sample_answer": "for i in range(1, 6): (range goes from 1 to 5 inclusive)"
        },
        {
            "question": "What do 'break' and 'continue' do in loops?",
            "key_concepts": ["break", "continue", "exit", "skip", "loop"],
            "sample_answer": "'break' exits the loop completely, 'continue' skips the rest of current iteration and goes to next"
        },
        {
            "question": "How do you loop through a list in Python?",
            "key_concepts": ["for", "list", "iterate", "items", "elements"],
            "sample_answer": "for item in my_list: or for i in range(len(my_list)):"
        },
        {
            "question": "When would you use a while loop instead of a for loop?",
            "key_concepts": ["while", "condition", "unknown", "iterations", "input"],
            "sample_answer": "When you don't know how many iterations you need, like waiting for user input or until a condition changes"
        }
    ],
    4: [  # Lists and Basic Functions
        {
            "question": "How do you create a list in Python and add items to it?",
            "key_concepts": ["list", "square brackets", "append", "add", "items"],
            "sample_answer": "Create with square brackets: my_list = [], add items with append(): my_list.append('item')"
        },
        {
            "question": "How do you access specific items in a list?",
            "key_concepts": ["index", "bracket", "position", "access", "zero"],
            "sample_answer": "Use square brackets with index: my_list[0] for first item (Python uses zero-based indexing)"
        },
        {
            "question": "How do you define a function in Python?",
            "key_concepts": ["def", "function", "parameters", "return", "colon"],
            "sample_answer": "Use 'def function_name(parameters):' followed by indented function body"
        },
        {
            "question": "What are some common list methods?",
            "key_concepts": ["append", "remove", "pop", "insert", "methods"],
            "sample_answer": "append() adds items, remove() deletes by value, pop() removes by index, insert() adds at position"
        },
        {
            "question": "How do you return a value from a function?",
            "key_concepts": ["return", "value", "function", "output"],
            "sample_answer": "Use the 'return' statement followed by the value: return result"
        }
    ]
}


# ----- Example of a Function tool -----
def get_current_date() -> dict:
    """
    Get the current date in the format YYYY-MM-DD
    """
    return {"current_date": datetime.now().strftime("%Y-%m-%d")}


def get_student_progress(tool_context: ToolContext) -> dict:
    """
    Check the student's current topic and past quiz performance.
    Returns progress information including current topic and areas needing review.
    """
    # Get current topic from memory (default to topic 1)
    current_topic = tool_context.state.get("current_topic", 1)
    
    # Get quiz history from memory
    quiz_history = tool_context.state.get("quiz_history", {})
    
    # Find questions that need review (scored incorrectly)
    review_needed = {}
    for topic_num, quizzes in quiz_history.items():
        topic_num = int(topic_num)
        incorrect_questions = []
        
        for quiz in quizzes:
            for i, result in enumerate(quiz.get("results", [])):
                if not result.get("correct", False):
                    incorrect_questions.append({
                        "question": result.get("question", ""),
                        "student_answer": result.get("student_answer", ""),
                        "date": quiz.get("date", "")
                    })
        
        if incorrect_questions:
            review_needed[topic_num] = incorrect_questions
    
    # Calculate overall progress
    total_topics = len(TOPICS)
    topics_completed = len([t for t in range(1, current_topic) if str(t) not in review_needed])
    progress_percentage = (topics_completed / total_topics) * 100
    
    return {
        "current_topic": current_topic,
        "current_topic_name": TOPICS.get(current_topic, "Unknown"),
        "total_topics": total_topics,
        "progress_percentage": progress_percentage,
        "review_needed": review_needed,
        "quiz_history_summary": {
            str(topic): len(quizzes) for topic, quizzes in quiz_history.items()
        }
    }


def generate_topic_quiz(tool_context: ToolContext, topic_number: int, num_questions: int = 3) -> dict:
    """
    Generate a quiz for a specific topic with the specified number of questions.
    Stores the current quiz in session state.
    """
    if topic_number not in TOPICS:
        return {"error": f"Invalid topic number: {topic_number}"}
    
    # Get available questions for this topic
    available_questions = QUIZ_QUESTIONS.get(topic_number, [])
    if len(available_questions) < num_questions:
        num_questions = len(available_questions)
    
    # Randomly select questions
    selected_questions = random.sample(available_questions, num_questions)
    
    # Create quiz structure
    quiz_data = {
        "topic_number": topic_number,
        "topic_name": TOPICS[topic_number],
        "questions": selected_questions,
        "current_question": 0,
        "total_questions": num_questions,
        "results": []
    }
    
    # Store in session state
    tool_context.state["current_quiz"] = quiz_data
    tool_context.state["quiz_active"] = True
    
    return {
        "topic_number": topic_number,
        "topic_name": TOPICS[topic_number], 
        "total_questions": num_questions,
        "first_question": selected_questions[0]["question"] if selected_questions else None,
        "quiz_started": True
    }


def evaluate_quiz_answer(tool_context: ToolContext, student_answer: str) -> dict:
    """
    Evaluate a student's natural language answer to the current quiz question.
    Updates session state and provides feedback.
    """
    # Get current quiz from session state
    current_quiz = tool_context.state.get("current_quiz")
    if not current_quiz:
        return {"error": "No active quiz found"}
    
    current_q_index = current_quiz["current_question"]
    if current_q_index >= len(current_quiz["questions"]):
        return {"error": "No more questions in quiz"}
    
    current_question = current_quiz["questions"][current_q_index]
    
    # Simple keyword-based evaluation (can be enhanced with LLM evaluation)
    key_concepts = current_question.get("key_concepts", [])
    student_lower = student_answer.lower()
    
    # Count how many key concepts are mentioned
    concepts_found = sum(1 for concept in key_concepts if concept.lower() in student_lower)
    concept_threshold = max(1, len(key_concepts) // 2)  # At least half the concepts
    
    is_correct = concepts_found >= concept_threshold
    
    # Store result
    result = {
        "question": current_question["question"],
        "student_answer": student_answer,
        "correct": is_correct,
        "concepts_found": concepts_found,
        "total_concepts": len(key_concepts),
        "sample_answer": current_question.get("sample_answer", "")
    }
    
    current_quiz["results"].append(result)
    current_quiz["current_question"] += 1
    
    # Update session state
    tool_context.state["current_quiz"] = current_quiz
    
    # Check if quiz is complete
    quiz_complete = current_quiz["current_question"] >= current_quiz["total_questions"]
    next_question = None
    
    if not quiz_complete:
        next_question = current_quiz["questions"][current_quiz["current_question"]]["question"]
    else:
        tool_context.state["quiz_active"] = False
    
    return {
        "correct": is_correct,
        "feedback": f"{'Correct!' if is_correct else 'Not quite right.'} You mentioned {concepts_found} out of {len(key_concepts)} key concepts.",
        "sample_answer": current_question.get("sample_answer", ""),
        "quiz_complete": quiz_complete,
        "next_question": next_question,
        "question_number": current_q_index + 1,
        "total_questions": current_quiz["total_questions"]
    }


def store_quiz_results(tool_context: ToolContext) -> dict:
    """
    Store completed quiz results in long-term memory and update progress.
    """
    # Get completed quiz from session state
    current_quiz = tool_context.state.get("current_quiz")
    if not current_quiz or tool_context.state.get("quiz_active", False):
        return {"error": "No completed quiz to store"}
    
    topic_number = current_quiz["topic_number"]
    
    # Calculate quiz score
    correct_answers = sum(1 for result in current_quiz["results"] if result["correct"])
    total_questions = len(current_quiz["results"])
    score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Create quiz record
    quiz_record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic_number": topic_number,
        "topic_name": TOPICS[topic_number],
        "score": score_percentage,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "results": current_quiz["results"]
    }
    
    # Get existing quiz history
    quiz_history = tool_context.state.get("quiz_history", {})
    topic_key = str(topic_number)
    
    if topic_key not in quiz_history:
        quiz_history[topic_key] = []
    
    quiz_history[topic_key].append(quiz_record)
    
    # Update state with quiz history
    tool_context.state["quiz_history"] = quiz_history
    
    # Update current topic if student passed (70% or better)
    passing_score = 70
    if score_percentage >= passing_score:
        current_topic = tool_context.state.get("current_topic", 1)
        if topic_number == current_topic and current_topic < len(TOPICS):
            tool_context.state["current_topic"] = current_topic + 1
    
    # Clear session state
    if "current_quiz" in tool_context.state:
        del tool_context.state["current_quiz"]
    if "quiz_active" in tool_context.state:
        del tool_context.state["quiz_active"]
    
    return {
        "stored": True,
        "topic_number": topic_number,
        "topic_name": TOPICS[topic_number],
        "score_percentage": score_percentage,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "passed": score_percentage >= passing_score,
        "next_topic": tool_context.state.get("current_topic", topic_number)
    }
