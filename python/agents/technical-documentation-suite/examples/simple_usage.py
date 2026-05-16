#!/usr/bin/env python3
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

"""
Simple usage example for Technical Documentation Suite.
Demonstrates basic multi-agent orchestration patterns using ADK.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from technical_documentation_suite.agent import root_agent


def run_simple_example():
    """Run a simple documentation generation example."""
    
    print("🎼 Technical Documentation Suite - Simple Example")
    print("=" * 60)
    
    # Set up session and runner
    session_service = InMemorySessionService()
    session = session_service.create_session(
        app_name="tech_docs_simple",
        user_id="user_123",
        session_id="session_456"
    )
    
    runner = Runner(
        agent=root_agent,
        session_service=session_service
    )
    
    # Example documentation request
    content = types.Content(
        role="user",
        parts=[types.Part(text="""
Generate comprehensive technical documentation for a Python FastAPI project with the following structure:

Repository: https://github.com/example/fastapi-microservice
- main.py (FastAPI application)
- models/ (Pydantic models)
- routes/ (API endpoints)
- services/ (business logic)
- database/ (SQLAlchemy setup)
- tests/ (pytest tests)

Please create:
1. API documentation with examples
2. Architecture overview
3. Installation and setup guide
4. Developer documentation

Output format: Markdown
Quality threshold: High
""")]
    )
    
    print("Starting documentation generation workflow...")
    print("-" * 40)
    
    try:
        # Run the workflow
        for event in runner.run(
            user_id="user_123",
            session_id="session_456", 
            new_message=content
        ):
            if event.content and event.content.parts:
                print(f"[{event.author}] {event.content.parts[0].text[:200]}...")
                print()
            
    except Exception as e:
        print(f"❌ Error during workflow execution: {e}")
        return False
    
    print("✅ Documentation generation completed!")
    return True


def run_quick_analysis_example():
    """Run a quick code analysis example."""
    
    print("\n🔍 Quick Code Analysis Example")
    print("=" * 40)
    
    session_service = InMemorySessionService()
    session = session_service.create_session(
        app_name="quick_analysis",
        user_id="user_456",
        session_id="session_789"
    )
    
    runner = Runner(
        agent=root_agent,
        session_service=session_service
    )
    
    # Quick analysis request
    content = types.Content(
        role="user",
        parts=[types.Part(text="""
Analyze this Python code structure and provide a brief documentation outline:

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="User Management API")

class User(BaseModel):
    id: int
    name: str
    email: str

users_db = []

@app.get("/")
def read_root():
    return {"message": "User Management API"}

@app.get("/users")
def get_users():
    return users_db

@app.post("/users")
def create_user(user: User):
    users_db.append(user)
    return user

@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Just provide a quick analysis and documentation outline.
""")]
    )
    
    try:
        for event in runner.run(
            user_id="user_456",
            session_id="session_789",
            new_message=content
        ):
            if event.content and event.content.parts:
                print(f"[{event.author}] {event.content.parts[0].text[:300]}...")
                print()
                
    except Exception as e:
        print(f"❌ Error during quick analysis: {e}")
        return False
    
    print("✅ Quick analysis completed!")
    return True


if __name__ == "__main__":
    print("Technical Documentation Suite - ADK Examples")
    print("=" * 50)
    
    # Check environment setup
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("⚠️  Warning: No API credentials detected.")
        print("Please set GOOGLE_API_KEY or configure Vertex AI credentials.")
        print("See .env.example for configuration options.")
        print()
    
    # Run examples
    try:
        # Run simple example
        success1 = run_simple_example()
        
        # Run quick analysis example  
        success2 = run_quick_analysis_example()
        
        if success1 and success2:
            print("\n🎉 All examples completed successfully!")
            print("\nNext steps:")
            print("- Try with your own repository URL")
            print("- Experiment with different documentation types")
            print("- Explore advanced orchestration patterns")
        else:
            print("\n⚠️  Some examples encountered issues.")
            print("Check your API credentials and try again.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Examples interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 