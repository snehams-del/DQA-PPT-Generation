import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from presentation_agent.sub_agents.synthesizer.agent import batch_generate_slides

class MockResponse:
    def __init__(self, text):
        self.text = text

@pytest.mark.asyncio
async def test_batch_generate_slides_success():
    slide_topics = [{"focus_area": "A", "proposed_title": "Title A"}]
    research_summary = "Sum A"
    tool_context = MagicMock()
    
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=MockResponse('{"title": "Title A", "layout_name": "Title and Content", "bullets": ["B1"]}'))
    
    with patch("presentation_agent.sub_agents.synthesizer.agent.initialize_genai_client", return_value=mock_client):
        result = await batch_generate_slides(research_summary=research_summary, tool_context=tool_context, slide_topics=slide_topics)
        
    assert len(result) == 1
    assert result[0]["title"] == "Title A"
    assert result[0]["bullets"] == ["B1"]

@pytest.mark.asyncio
async def test_batch_generate_slides_json_error():
    slide_topics = [{"focus_area": "A", "proposed_title": "Title A"}]
    research_summary = "Sum A"
    tool_context = MagicMock()
    
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=MockResponse('Invalid JSON'))
    
    with patch("presentation_agent.sub_agents.synthesizer.agent.initialize_genai_client", return_value=mock_client):
        result = await batch_generate_slides(research_summary=research_summary, tool_context=tool_context, slide_topics=slide_topics)
        
    assert len(result) == 1
    assert result[0]["title"] == "Title A"
    assert "Generation failed" in result[0]["bullets"][0]

@pytest.mark.asyncio
async def test_batch_generate_slides_exception():
    slide_topics = [{"focus_area": "A", "proposed_title": "Title A"}]
    research_summary = "Sum A"
    tool_context = MagicMock()
    
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("API Call Failed"))
    
    with patch("presentation_agent.sub_agents.synthesizer.agent.initialize_genai_client", return_value=mock_client):
        result = await batch_generate_slides(research_summary=research_summary, tool_context=tool_context, slide_topics=slide_topics)
        
    assert len(result) == 1
    assert result[0]["title"] == "Title A"
    assert "API Call Failed" in result[0]["bullets"][0]

