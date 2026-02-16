import pytest
from unittest.mock import Mock, patch, MagicMock
from google.cloud import texttospeech
import io
import wave
import struct

from podcast_agent.models.media_script import MediaScript, ScriptSegment
from podcast_agent.tools.gemini_tts_tool import GeminiTtsTool

@pytest.fixture
def mock_sdk_client():
    with patch("podcast_agent.tools.gemini_tts_tool.texttospeech.TextToSpeechClient") as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create a valid minimal WAV file bytes manually (44 byte header)
        # This allows wave.open() to successfully parse it in the tool
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_writer:
            wav_writer.setnchannels(1)
            wav_writer.setsampwidth(2)
            wav_writer.setframerate(24000)
            wav_writer.writeframes(b'')
            
        wav_bytes = wav_io.getvalue()
        
        # Mock the response
        mock_response = Mock()
        mock_response.audio_content = wav_bytes
        mock_client.synthesize_speech.return_value = mock_response
        
        yield mock_client

@pytest.fixture
def sample_script():
    segments = [
        ScriptSegment(speaker_id="Host", text="Welcome to the podcast."),
        ScriptSegment(speaker_id="Expert", text="Thanks for having me."),
        ScriptSegment(speaker_id="Host", text="Let's get started.")
    ]
    return MediaScript(speakers=[], segments=segments)

def test_gemini_tts_tool_initialization(mock_sdk_client):
    tool = GeminiTtsTool()
    assert tool.voice_name == "en-US-Studio-MultiSpeaker"
    assert tool.model_id == "gemini-2.5-pro-tts"
    # One should be male, one female based on initialization rules
    assert (tool.host_voice in tool.male_voices and tool.expert_voice in tool.female_voices) or \
           (tool.host_voice in tool.female_voices and tool.expert_voice in tool.male_voices)

def test_generate_audio(mock_sdk_client, sample_script, tmp_path):
    tool = GeminiTtsTool()
    output_file = str(tmp_path / "test_output.wav")
    
    result_path = tool.generate_audio(script=sample_script, output_file=output_file)
    
    # Verify the SDK was called for each segment (3 total)
    assert mock_sdk_client.synthesize_speech.call_count == 3
    
    # Verify the output file was created
    assert result_path == output_file
    
    # Evaluate the calls to ensure proper Request formatting
    calls = mock_sdk_client.synthesize_speech.call_args_list
    for call in calls:
        request = call.kwargs['request']
        assert isinstance(request, texttospeech.SynthesizeSpeechRequest)
        assert request.audio_config.sample_rate_hertz == 24000
        assert request.voice.name == "en-US-Studio-MultiSpeaker"
        assert request.voice.model_name == "gemini-2.5-pro-tts"
        # Verify both Host and Expert are in the voice config
        configs = request.voice.multi_speaker_voice_config.speaker_voice_configs
        assert len(configs) == 2
        aliases = [c.speaker_alias for c in configs]
        assert "Host" in aliases
        assert "Expert" in aliases
