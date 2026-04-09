# Copyright 2026 Google LLC
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

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.api.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Verifies that the FastAPI orchestrator spine is online and accessible."""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "online", "engine": "operational"}

@patch("backend.api.main.runner")
def test_stream_chat_endpoint_allowed_authors_filtering(mock_runner):
    """
    Validates our custom SSE filtering methodology!
    Checks if intermediate internal thoughts are stripped entirely and if true 
    presentation outputs correctly parse into Server Sent Event JSON strings.
    """
    class FakePart:
        def __init__(self, text):
            self.text = text
            
    class FakeContent:
        def __init__(self, role, text):
            self.role = role
            self.parts = [FakePart(text)]
            
    class FakeEvent:
        def __init__(self, author, role, text):
            self.author = author
            self.content = FakeContent(role, text)

    # We mock the ADK Event loop trace generator
    mock_runner.run.return_value = [
        # Event 1: Unverified internal thinking -> should be dropped
        FakeEvent("query_understanding_agent", "model", "I am thinking about scanning SQL."),
        # Event 2: Authorized query output -> should be passed into SSE chunk
        FakeEvent("query_execution_agent", "model", "| User Data | Mock |"),
    ]

    mock_runner.app_name = "test-api"
    mock_runner.session_service.get_session_sync.return_value = True

    response = client.post("/api/chat/stream", json={"message": "Execute pipeline"})
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    # Analyze the streaming pipeline aggregate byte response
    output_stream = response.text
    
    assert "I am thinking about scanning SQL" not in output_stream
    assert "query_understanding_agent" not in output_stream
    assert "User Data" in output_stream
