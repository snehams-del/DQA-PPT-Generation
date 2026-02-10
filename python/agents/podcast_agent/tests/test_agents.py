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

import json
from pathlib import Path

import dotenv
import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

from podcast_agent.agent import podcast_agent


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_run_with_txt():
    """Tests that the agent can generate a transcript from a text file."""
    runner = InMemoryRunner(agent=podcast_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )

    file_path = Path("./tests/test_artifacts/test_pyramid.txt")
    file_content = file_path.read_bytes()

    content = types.Content(
        parts=[
            types.Part(
                text=(
                    "Generate podcast from this document. Podcast host name is"
                    " Charlotte, expert's name is Dr Joe Sponge"
                )
            ),
            types.Part(
                inline_data=types.Blob(
                    mime_type="text/plain", data=file_content
                )
            ),
        ]
    )

    found_valid_transcript = False

    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        print(f"DEBUG: Event from {event.author} (final={event.is_final_response()})")
        if event.content and event.content.parts:
             text = event.content.parts[0].text or "No Text"
             print(f"DEBUG: Content: {text[:100]}...")
        if (
            event.is_final_response()
            and event.author == "podcast_audio_generator_agent"
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text and "podcast_output.wav" in part.text:
                        found_valid_transcript = True

    assert found_valid_transcript, (
        "No final event found with valid transcript metadata"
    )
