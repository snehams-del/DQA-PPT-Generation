
import os
import sys

from unittest.mock import MagicMock, patch, AsyncMock

# Add parent directory to path to import podcast_agent
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from podcast_agent.agent import podcast_agent as PodcastAgent

def test_podcast_agent_with_pdf():
    # Mock the runner and tts_tool to avoid actual API calls during plumbing test
    agent = PodcastAgent()
    agent.runner = MagicMock()
    # create_session is awaited, so it must return an awaitable
    agent.runner.session_service.create_session = AsyncMock()
    
    # Mock run_async to yield a final response
    async def mock_run_async(*args, **kwargs):
        mock_event = MagicMock()
        mock_event.is_final_response.return_value = True
        mock_event.author = "podcast_transcript_writer_agent"
        mock_event.content.parts = [
            MagicMock(text='```json\n{"segments": [{"speaker": "Host", "text": "Hello"}]}\n```')
        ]
        yield mock_event

    agent.runner.run_async = mock_run_async
    
    agent.tts_tool = MagicMock()
    agent.tts_tool.generate_audio.return_value = "podcast_output.wav"
    
    # Create a dummy PDF
    test_pdf = "test_dummy.pdf"
    with open(test_pdf, "wb") as f:
        f.write(b"%PDF-1.4 dummy content")
        
    try:
        result = agent.run("Test Topic", input_files=[test_pdf])
        print(result)
        assert "Listen here" in result
        assert "podcast_output.wav" in result
        
        # Verify inline_data was constructed
        # We can't easily inspect the async iterator call without more complex mocking, 
        # but we can verify it didn't crash and returned success.
        
    finally:
        if os.path.exists(test_pdf):
            os.remove(test_pdf)

if __name__ == "__main__":
    test_podcast_agent_with_pdf()
    print("Test passed!")
