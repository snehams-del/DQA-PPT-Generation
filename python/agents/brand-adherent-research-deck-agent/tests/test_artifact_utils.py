import json
import os
import tempfile
import uuid
from typing import Dict, Any

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from google.genai import types

from presentation_agent.tools.artifact_utils import (
    save_deck_spec,
    update_slide_in_spec,
)
from presentation_agent.shared_libraries.models import DeckSpec

# Use pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio

# ==============================================================================
# Setup: Mock ToolContext for persistent artifacts
# ==============================================================================
@pytest.fixture
def mock_context():
    context = MagicMock()
    # Mock storage dictionary
    context.store = {}
    
    async def mock_save(name, artifact):
        # Extract bytes from the Part object
        data = artifact.inline_data.data
        context.store[name] = data
        return name
        
    async def mock_load(name):
        data = context.store.get(name)
        if not data:
            return None
        # Return a mocked Part object
        return types.Part(inline_data=types.Blob(data=data, mime_type="application/json"))
        
    context.save_artifact = AsyncMock(side_effect=mock_save)
    context.load_artifact = AsyncMock(side_effect=mock_load)
    return context

# ==============================================================================
# Tests for save_deck_spec
# ==============================================================================

async def test_save_deck_spec_success(mock_context):
    """Test successful saving of a valid DeckSpec dict, including translation."""
    input_spec = {
        "cover": {"title": "Test Cover"},
        "slide_topics": [  # Test translation from slide_topics
            {"proposed_title": "Slide 1", "proposed_layout": "Title and Content"}
        ]
    }

    artifact_name = await save_deck_spec(mock_context, input_spec)

    assert "Error:" not in artifact_name
    assert artifact_name.startswith("deck_spec_")
    assert artifact_name.endswith(".json")

    # Verify it was saved to the context store
    assert artifact_name in mock_context.store
    
    # Verify translation worked
    saved_data = json.loads(mock_context.store[artifact_name].decode("utf-8"))
    assert "slides" in saved_data
    assert saved_data["slides"][0]["title"] == "Slide 1"
    assert saved_data["slides"][0]["layout_name"] == "Title and Content"
    assert saved_data["closing_title"] == "Thank You"


async def test_save_deck_spec_invalid_schema(mock_context):
    """Test saving a DeckSpec with missing required fields (should fail cleanly)."""
    # Cover requires a 'title', this is missing it
    invalid_spec = {
        "cover": {"subhead": "Missing Title"},
        "slides": []
    }

    result = await save_deck_spec(mock_context, invalid_spec)

    assert result.startswith("Error: Invalid deck_spec structure")
    # Verify nothing was saved
    assert len(mock_context.store) == 0

# ==============================================================================
# Tests for update_slide_in_spec
# ==============================================================================

async def test_update_slide_in_spec_success(mock_context):
    """Test successfully updating an existing slide."""
    
    # 1. Setup an initial artifact in the store
    initial_spec = {
        "cover": {"title": "Test Cover"},
        "slides": [
            {"title": "Slide 1", "layout_name": "Title and Content", "bullets": []},
            {"title": "Slide 2", "layout_name": "Title and Content", "bullets": []}
        ],
        "closing_title": "End"
    }
    
    # Pre-populate the store
    json_bytes = json.dumps(initial_spec).encode("utf-8")
    mock_context.store["test_spec.json"] = json_bytes
    
    # 2. Perform the update
    update_data = {
        "title": "UPDATED Slide 2",
        "layout_name": "Title and Image"
    }
    
    new_artifact_name = await update_slide_in_spec(
        mock_context,
        "test_spec.json",
        1,  # Index 1 = Slide 2
        update_data
    )
    
    assert "Error:" not in new_artifact_name
    assert new_artifact_name in mock_context.store
    
    # 3. Verify the changes
    updated_json = json.loads(mock_context.store[new_artifact_name].decode("utf-8"))
    
    assert updated_json["slides"][0]["title"] == "Slide 1"  # Unchanged
    assert updated_json["slides"][1]["title"] == "UPDATED Slide 2" # Changed
    assert updated_json["slides"][1]["layout_name"] == "Title and Image" # Changed

async def test_update_slide_in_spec_append_growth(mock_context):
    """Test successfully appending slides when index is beyond current length (Length Guardian)."""
    
    # 1. Setup initial artifact (2 slides)
    initial_spec = {
        "cover": {"title": "Test Cover"},
        "slides": [
            {"title": "Slide 1", "layout_name": "Title and Content", "bullets": []},
            {"title": "Slide 2", "layout_name": "Title and Content", "bullets": []}
        ],
        "closing_title": "End"
    }
    json_bytes = json.dumps(initial_spec).encode("utf-8")
    mock_context.store["test_spec.json"] = json_bytes
    
    # 2. Update index 3 (Slide 4). This should create Slide 3 (placeholder) and Slide 4 (actual).
    update_data = {"title": "Slide 4"}
    
    new_artifact_name = await update_slide_in_spec(
        mock_context,
        "test_spec.json",
        3, 
        update_data
    )
    
    assert "Error:" not in new_artifact_name
    
    # 3. Verify growth
    updated_json = json.loads(mock_context.store[new_artifact_name].decode("utf-8"))
    assert len(updated_json["slides"]) == 4
    assert updated_json["slides"][2]["title"] == "New Slide 3" # Auto-filled gap
    assert updated_json["slides"][3]["title"] == "Slide 4" # Appended target

async def test_update_slide_in_spec_not_found(mock_context):
    """Test updating a spec that doesn't exist."""
    
    result = await update_slide_in_spec(
        mock_context,
        "nonexistent.json",
        0,
        {"title": "Fail"}
    )
    
    assert result.startswith("Error: Spec 'nonexistent.json' not found")
