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


def _env():
    load_dotenv()
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    engine_id = os.getenv("AGENT_ENGINE_ID")
    return project, location, engine_id


@pytest.mark.integration
def test_agent_engine_responds():
    project, location, engine_id = _env()

    if not engine_id:
        pytest.skip("AGENT_ENGINE_ID not set (deploy first).")

    assert project, "GOOGLE_CLOUD_PROJECT not set"
    assert location, "GOOGLE_CLOUD_LOCATION not set"

    vertexai.init(project=project, location=location)

    sessions = VertexAiSessionService(project=project, location=location)
    session = asyncio.run(
        sessions.create_session(app_name=engine_id, user_id="pytest")
    )

    engine = agent_engines.get(engine_id)
    events = list(
        engine.stream_query(
            user_id="pytest",
            session_id=session.id,
            message="Hello",
        )
    )

    asyncio.run(
        sessions.delete_session(
            app_name=engine_id,
            user_id="pytest",
            session_id=session.id,
        )
    )

    assert events, "No events returned from agent engine"


def main():
    project, location, engine_id = _env()

    if not engine_id:
        raise SystemExit("AGENT_ENGINE_ID not set. Deploy first so it's written into .env.")

    vertexai.init(project=project, location=location)

    sessions = VertexAiSessionService(project=project, location=location)
    session = asyncio.run(
        sessions.create_session(app_name=engine_id, user_id="123")
    )
    engine = agent_engines.get(engine_id)

    print("Type 'quit' to exit.")
    try:
        while True:
            msg = input("Input: ").strip()
            if msg == "quit":
                break
            for event in engine.stream_query(
                user_id="123",
                session_id=session.id,
                message=msg,
            ):
                print(event)
    finally:
        asyncio.run(
            sessions.delete_session(
                app_name=engine_id,
                user_id="123",
                session_id=session.id,
            )
        )


if __name__ == "__main__":
    main()