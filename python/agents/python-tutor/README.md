# Python Tutor - ADK Python Sample Agent

## Overview

The **Python Tutor** agent is an intelligent tutoring system that guides students through a structured Python programming curriculum. Built with Google's Agent Development Kit (ADK), this agent demonstrates advanced state management and memory capabilities for personalized, adaptive learning experiences.

This sample agent showcases ADK's State and Memory concepts through a real-world educational use case, featuring cross-session learning continuity and adaptive quiz generation.

## Agent Details

The key features of the Python Tutor agent are:

| Feature              | Description                     |
| -------------------- | ------------------------------- |
| **Interaction Type** | Conversational                  |
| **Complexity**       | Intermediate                    |
| **Agent Type**       | Single Agent with State/Memory  |
| **Components**       | State, Memory, Tools            |
| **Vertical**         | Education, Programming Learning |

## Key Features

### 🎓 Structured Learning Curriculum

- **Topic 1**: Basic Syntax and Variables
- **Topic 2**: Control Flow and Conditionals
- **Topic 3**: Loops and Iteration
- **Topic 4**: Lists and Basic Functions

### 🧠 Intelligent State & Memory Management

- **Session State**: Tracks current quiz progress, question flow, and immediate context
- **Long-term Memory**: Stores quiz results, learning progress, and performance history across sessions
- **Adaptive Learning**: Adjusts teaching based on individual student performance

### 📝 Dynamic Quiz System

- Generates contextual quizzes for each topic
- Accepts natural language answers (no strict syntax required)
- Provides immediate feedback and explanations
- Stores results for future review and adaptation

### 🔄 Cross-Session Continuity

- Remembers student progress between sessions
- Re-presents incorrectly answered questions for review
- Only advances topics after demonstrating mastery
- Provides personalized learning paths

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Python Tutor Agent                      │
├─────────────────────────────────────────────────────────────┤
│  Session State (Short-term)    │  Memory (Long-term)       │
│  • Current quiz progress       │  • Topic progression      │
│  • Active question index       │  • Quiz history           │
│  • Session quiz results        │  • Performance analytics  │
│  • Temporary context           │  • Learning preferences   │
├─────────────────────────────────────────────────────────────┤
│                         Tools                              │
│  • get_student_progress()   • generate_topic_quiz()        │
│  • evaluate_quiz_answer()   • store_quiz_results()         │
│  • get_current_date()                                      │
└─────────────────────────────────────────────────────────────┘
```

## Teaching Flow

1. **Progress Check**: Agent reviews student's current topic and past performance
2. **Conversational Teaching**: Interactive discussion of topic concepts with examples
3. **Quiz Generation**: Creates 3 personalized questions for the current topic
4. **Natural Assessment**: Evaluates answers using concept recognition (not syntax matching)
5. **Adaptive Feedback**: Provides explanations and determines next steps
6. **Memory Storage**: Records quiz results and updates learning progress
7. **Cross-Session Review**: Re-engages with missed concepts in future sessions

## 💻 Run Locally

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/getting-started/installation) (to manage dependencies)
- Git (for cloning the repository, see [Installation Instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))
- Google Cloud CLI ([Installation Instructions](https://cloud.google.com/sdk/docs/install))

### Steps

1. Clone the repository:

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/python-tutor
```

2. Configure Gemini API Key:

Get an API Key from Google AI Studio: https://aistudio.google.com/apikey

3. Set environment variables:

```sh
export "GOOGLE_API_KEY=<your_api_key_here>"
export "GOOGLE_GENAI_USE_VERTEXAI=FALSE"
```

4. Run via ADK web:

```sh
uv run adk web
```

5. Try the example script:

```sh
uv run python example_usage.py
```

## State and Memory Examples

### Session State (Current Conversation)

```python
context.state = {
    "current_quiz": {
        "topic_number": 1,
        "topic_name": "Basic Syntax and Variables",
        "current_question": 1,
        "total_questions": 3,
        "results": [
            {"correct": True, "question": "What is a variable?", ...}
        ]
    },
    "quiz_active": True
}
```

### Long-term Memory (Across Sessions)

```python
context.memory = {
    "current_topic": 2,
    "quiz_history": {
        "1": [
            {
                "date": "2025-01-15 14:30:00",
                "score": 66.7,
                "correct_answers": 2,
                "total_questions": 3,
                "results": [...]
            }
        ]
    }
}
```

## Tool Functions

- **`get_student_progress()`**: Retrieves current topic, progress percentage, and areas needing review
- **`generate_topic_quiz(topic_number, num_questions=3)`**: Creates randomized quiz questions for specified topic
- **`evaluate_quiz_answer(student_answer)`**: Assesses natural language responses using concept matching
- **`store_quiz_results()`**: Saves completed quiz data to long-term memory and updates progress
- **`get_current_date()`**: Provides current date for record-keeping

## ☁️ Deploy to Google Cloud

For complete deployment instructions to Google Cloud Run, see [DEPLOYMENT.md](DEPLOYMENT.md).

Quick deployment with ADK CLI:

```bash
adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --service_name=python-tutor-agent \
    --with_ui \
    python-tutor/
```

## Example Interaction Flow

```
Student: "Hi, I want to learn Python programming"
Tutor: "Welcome! Let me check your progress... I see you're new. Let's start with Topic 1: Basic Syntax and Variables..."

[After conversational teaching]
Tutor: "Now let's test your understanding with a quiz. Question 1: What is a variable in Python?"
Student: "A variable stores data and you create it with an equals sign"
Tutor: "Excellent! You mentioned the key concepts of storage and assignment..."

[After completing quiz]
Tutor: "Great job! You scored 100% on Basic Syntax and Variables. Let's move to Topic 2: Control Flow..."

[In next session]
Student: "Hi, I'm back!"
Tutor: "Welcome back! I see you mastered Topic 1 and we're ready for Topic 2: Control Flow and Conditionals..."
```

## Educational Impact

This agent demonstrates how AI can provide:

- **Personalized Learning**: Adapts to individual pace and understanding
- **Continuous Assessment**: Regular quizzes with immediate feedback
- **Mastery-Based Progression**: Ensures understanding before advancing
- **Long-term Retention**: Reviews difficult concepts across sessions
- **Natural Interaction**: Conversational teaching that feels human-like

Perfect for showcasing ADK's capabilities in educational technology and adaptive learning systems.
