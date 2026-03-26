import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from presentation_agent.tools.visual_generator import generate_visual
from google.genai import types

class MockResponse:
    def __init__(self, data=None):
        if data:
            self.candidates = [MagicMock()]
            self.candidates[0].content.parts = [MagicMock()]
            self.candidates[0].content.parts[0].inline_data.data = data
        else:
            self.candidates = []

@pytest.mark.asyncio
@patch("presentation_agent.tools.visual_generator.initialize_genai_client")
@patch("presentation_agent.tools.visual_generator.GCS_BUCKET_NAME", "my-bucket")
@patch("presentation_agent.tools.visual_generator.get_gcs_client")
async def test_generate_visual_success_gcs(mock_get_gcs_client, mock_initialize_genai_client):
    mock_client = MagicMock()
    mock_initialize_genai_client.return_value = mock_client
    
    mock_client.models.generate_content = MagicMock(return_value=MockResponse(b"image_data"))

    mock_storage_client = MagicMock()
    mock_get_gcs_client.return_value = mock_storage_client

    result = await generate_visual("chart: A test chart")

    # With the new Hybrid logic, it should STILL return the local filepath even if GCS is configured
    assert not result.startswith("Error:")
    assert result.endswith(".png") 
    mock_client.models.generate_content.assert_called_once()
    mock_storage_client.bucket().blob().upload_from_string.assert_called_once()

@pytest.mark.asyncio
@patch("presentation_agent.tools.visual_generator.initialize_genai_client")
@patch("presentation_agent.tools.visual_generator.GCS_BUCKET_NAME", None)
async def test_generate_visual_success_local(mock_initialize_genai_client):
    mock_client = MagicMock()
    mock_initialize_genai_client.return_value = mock_client

    mock_client.models.generate_content = MagicMock(return_value=MockResponse(b"image_data"))

    result = await generate_visual("image: A test image")

    assert not result.startswith("Error:")
    assert not result.startswith("gs://")
    assert result.endswith(".png") # Temp file path
    mock_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
@patch("presentation_agent.tools.visual_generator.initialize_genai_client")
async def test_generate_visual_no_candidates(mock_initialize_genai_client):
    mock_client = MagicMock()
    mock_initialize_genai_client.return_value = mock_client

    mock_client.models.generate_content = MagicMock(return_value=MockResponse())

    result = await generate_visual("test prompt")

    assert result.startswith("Error: Visual generation failed.")


@pytest.mark.asyncio
@patch("presentation_agent.tools.visual_generator.initialize_genai_client")
@patch("presentation_agent.tools.visual_generator.GCS_BUCKET_NAME", "my-bucket")
@patch("presentation_agent.tools.visual_generator.get_gcs_client")
async def test_generate_visual_gcs_no_client(mock_get_gcs_client, mock_initialize_genai_client):
    mock_client = MagicMock()
    mock_initialize_genai_client.return_value = mock_client

    mock_client.models.generate_content = MagicMock(return_value=MockResponse(b"image_data"))

    mock_get_gcs_client.return_value = None

    result = await generate_visual("chart: A test chart")

    # If GCS fails, it logs a warning but STILL returns the local file path
    assert not result.startswith("Error:")
    assert result.endswith(".png")


@pytest.mark.asyncio
@patch("presentation_agent.tools.visual_generator.initialize_genai_client")
async def test_generate_visual_exception(mock_initialize_genai_client):
    mock_client = MagicMock()
    mock_initialize_genai_client.return_value = mock_client

    mock_client.models.generate_content = MagicMock(side_effect=Exception("API Error"))

    result = await generate_visual("test prompt")

    assert result.startswith("Error: Visual generation failed.")

@pytest.mark.asyncio
async def test_generate_visual_empty_prompt():
    result = await generate_visual("")
    assert result == "Error: Prompt cannot be empty."