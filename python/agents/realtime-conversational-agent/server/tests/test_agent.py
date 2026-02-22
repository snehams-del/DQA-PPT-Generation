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

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from example_agent.agent import root_agent
from example_agent.prompts import AGENT_INSTRUCTION


# --- Agent configuration tests ---


def test_agent_name():
    assert root_agent.name == "example_agent"


def test_agent_model():
    assert "gemini-live" in root_agent.model


def test_agent_description():
    assert root_agent.description is not None
    assert len(root_agent.description) > 0


def test_agent_has_instruction():
    assert root_agent.instruction is not None
    assert len(root_agent.instruction.strip()) > 0


# --- Prompt tests ---


def test_instruction_not_empty():
    assert len(AGENT_INSTRUCTION.strip()) > 0


def test_instruction_contains_tutor_content():
    lower = AGENT_INSTRUCTION.lower()
    assert "tutor" in lower or "math" in lower


def test_instruction_socratic_method():
    assert "Socratic" in AGENT_INSTRUCTION or "socratic" in AGENT_INSTRUCTION.lower()


# --- FastAPI app tests ---


def test_app_created():
    from main import app

    assert app is not None


def test_app_has_websocket_route():
    from main import app

    paths = [route.path for route in app.routes]
    assert "/ws/{user_id}" in paths


# --- agent_to_client_messaging tests ---


async def test_agent_to_client_messaging_text_event():
    """Tests that a model text event is sent to the client correctly."""
    from main import agent_to_client_messaging

    mock_websocket = AsyncMock()

    mock_part = MagicMock()
    mock_part.text = "Great question! Let's break it down."
    mock_part.inline_data = None
    mock_part.function_call = None
    mock_part.function_response = None

    mock_event = MagicMock()
    mock_event.author = "agent"
    mock_event.partial = False
    mock_event.turn_complete = False
    mock_event.interrupted = False
    mock_event.content = MagicMock()
    mock_event.content.role = "model"
    mock_event.content.parts = [mock_part]

    async def mock_live_events():
        yield mock_event

    await agent_to_client_messaging(mock_websocket, mock_live_events())

    mock_websocket.send_text.assert_called_once()
    sent = json.loads(mock_websocket.send_text.call_args[0][0])
    assert sent["author"] == "agent"
    assert any(p["type"] == "text" for p in sent["parts"])
    assert sent["output_transcription"]["text"] == "Great question! Let's break it down."


async def test_agent_to_client_messaging_turn_complete():
    """Tests that a turn_complete event with no content is forwarded."""
    from main import agent_to_client_messaging

    mock_websocket = AsyncMock()

    mock_event = MagicMock()
    mock_event.author = "agent"
    mock_event.partial = False
    mock_event.turn_complete = True
    mock_event.interrupted = False
    mock_event.content = None

    async def mock_live_events():
        yield mock_event

    await agent_to_client_messaging(mock_websocket, mock_live_events())

    mock_websocket.send_text.assert_called_once()
    sent = json.loads(mock_websocket.send_text.call_args[0][0])
    assert sent["turn_complete"] is True


async def test_agent_to_client_messaging_user_transcription():
    """Tests that a user-role event is sent as input_transcription."""
    from main import agent_to_client_messaging

    mock_websocket = AsyncMock()

    mock_part = MagicMock()
    mock_part.text = "What is the Pythagorean theorem?"
    mock_part.inline_data = None
    mock_part.function_call = None
    mock_part.function_response = None

    mock_event = MagicMock()
    mock_event.author = "user"
    mock_event.partial = False
    mock_event.turn_complete = False
    mock_event.interrupted = False
    mock_event.content = MagicMock()
    mock_event.content.role = "user"
    mock_event.content.parts = [mock_part]

    async def mock_live_events():
        yield mock_event

    await agent_to_client_messaging(mock_websocket, mock_live_events())

    mock_websocket.send_text.assert_called_once()
    sent = json.loads(mock_websocket.send_text.call_args[0][0])
    assert sent["input_transcription"]["text"] == "What is the Pythagorean theorem?"


async def test_agent_to_client_messaging_empty_event_skipped():
    """Tests that empty, non-terminal events are not forwarded."""
    from main import agent_to_client_messaging

    mock_websocket = AsyncMock()

    mock_event = MagicMock()
    mock_event.author = "agent"
    mock_event.partial = False
    mock_event.turn_complete = False
    mock_event.interrupted = False
    mock_event.content = None

    async def mock_live_events():
        yield mock_event

    await agent_to_client_messaging(mock_websocket, mock_live_events())

    mock_websocket.send_text.assert_not_called()
