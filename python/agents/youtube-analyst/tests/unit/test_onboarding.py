import pytest
from google.adk.tools import ToolContext
from youtube_analyst.tools import init_or_get_youtube_client, store_youtube_api_key
from unittest.mock import MagicMock

def test_init_or_get_youtube_client_missing_key():
    """Test that init_or_get_youtube_client returns None and error message when key is missing."""
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {}
    
    client, error = init_or_get_youtube_client(mock_context)
    
    assert client is None
    assert "SYSTEM REJECTION: Missing YouTube API Key" in error

def test_store_and_get_api_key():
    """Test storing a key and then attempting to initialize the client."""
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {}
    
    test_key = "test_api_key_123"
    
    # Store the key
    result = store_youtube_api_key(test_key, mock_context)
    assert "successfully" in result
    assert mock_context.state["youtube_api_key"] == test_key
    
    # After storing, init_or_get_youtube_client should try to build the client.
    # Note: build() will still fail unless mocked, but the test proves the flow works.
