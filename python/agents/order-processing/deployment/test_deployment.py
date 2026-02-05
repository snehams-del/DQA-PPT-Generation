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

import asyncio
import os

import pytest
import vertexai
from dotenv import load_dotenv
from google.adk.sessions import VertexAiSessionService
from vertexai import agent_engines

load_dotenv()

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION") or "global"
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")

# Skip by default unless the environment is configured for live deployment testing.
if not PROJECT or not AGENT_ENGINE_ID:
    pytest.skip(
        "Skipping deployment integration test: set GOOGLE_CLOUD_PROJECT and AGENT_ENGINE_ID to run.",
        allow_module_level=True,
    )


def test_deployment_smoke():
    """Smoke test that a session can be created and the agent engine is reachable."""
    vertexai.init(project=PROJECT, location=LOCATION)

    session_service = VertexAiSessionService(project=PROJECT, location=LOCATION)
    session = asyncio.run(
        session_service.create_session(app_name=AGENT_ENGINE_ID, user_id="123")
    )

    try:
        engine = agent_engines.get(AGENT_ENGINE_ID)
        events = list(
            engine.stream_query(
                user_id="123",
                session_id=session.id,
                message="Hello",
            )
        )
        assert events is not None
    finally:
        asyncio.run(
            session_service.delete_session(
                app_name=AGENT_ENGINE_ID, user_id="123", session_id=session.id
            )
        )
