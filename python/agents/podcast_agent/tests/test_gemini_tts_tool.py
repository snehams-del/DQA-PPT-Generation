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

import pytest
from unittest.mock import Mock, patch, MagicMock
from google.cloud import texttospeech
import io
import wave
import struct

from podcast_agent.models.podcast_transcript import PodcastTranscript, PodcastSegment, SpeakerDialogue, PodcastMetadata
from podcast_agent.tools.gemini_tts_tool import GeminiTtsTool

@pytest.fixture
def mock_sdk_client():
    """
    Provides a mocked TextToSpeechClient for testing.
    
    This fixture mocks the Gemini TTS client and its synthesize_speech method,
    returning a minimal valid WAV file to simulate successful audio generation
    without making actual API calls.
    """
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
    """
    Generates a sample PodcastTranscript for testing.
    
    This script contains a few segments with multiple speakers (Host and Expert)
    to verify that the TTS tool correctly handles multi-speaker synthesis.
    """
    dialogues = [
        SpeakerDialogue(speaker_id="Host", text="Welcome to the podcast."),
        SpeakerDialogue(speaker_id="Expert", text="Thanks for having me."),
        SpeakerDialogue(speaker_id="Host", text="Let's get started.")
    ]
    segment = PodcastSegment(
        segment_title="Intro",
        title="Intro title",
        start_time=0.0,
        end_time=10.0,
        speaker_dialogues=dialogues
    )
    metadata = PodcastMetadata(
        episode_title="Test Episode",
        duration_seconds=10,
        summary="Test summary"
    )
    return PodcastTranscript(metadata=metadata, speakers=[], segments=[segment])

def test_gemini_tts_tool_initialization(mock_sdk_client):
    """
    Tests the initialization of the GeminiTtsTool.
    
    Verifies that defaults like voice_name and model_id are correctly set,
    and that host/expert voices are assigned according to gender rules.
    """
    tool = GeminiTtsTool()
    assert tool.voice_name == "en-US-Studio-MultiSpeaker"
    assert tool.model_id == "gemini-2.5-pro-tts"
    # One should be male, one female based on initialization rules
    assert (tool.host_voice in tool.male_voices and tool.expert_voice in tool.female_voices) or \
           (tool.host_voice in tool.female_voices and tool.expert_voice in tool.male_voices)

def test_generate_audio(mock_sdk_client, sample_script, tmp_path):
    """
    Tests the high-level generate_audio method of GeminiTtsTool.
    
    Verifies that the tool correctly orchestrates the synthesis process,
    calls the internal parallel synthesis wrapper, and produces an output file.
    """
    tool = GeminiTtsTool()
    output_file = str(tmp_path / "test_output.wav")
    
    with patch.object(tool, '_synthesize_segments_parallel') as mock_synth:
        # Create a valid minimal WAV file bytes manually (44 byte header)
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_writer:
            wav_writer.setnchannels(1)
            wav_writer.setsampwidth(2)
            wav_writer.setframerate(24000)
            wav_writer.writeframes(b'')
            
        wav_bytes = wav_io.getvalue()
        mock_synth.return_value = [wav_bytes]
        
        result_path = tool.generate_audio(script=sample_script, output_file=output_file)
        
        # Verify the parallel pool wrapper was called
        assert mock_synth.call_count == 1
    
    # Verify the output file was created
    assert result_path == output_file
    
    # Evaluate the calls to ensure proper Request formatting
    calls = mock_synth.call_args_list
    for call in calls:
        script = call.args[0]
        speaker_configs = call.args[1]
        
        assert isinstance(script, PodcastTranscript)
        
        # Verify both Host and Expert are in the voice config
        assert len(speaker_configs) == 2
        aliases = [c.speaker_alias for c in speaker_configs]
        assert "Host" in aliases
        assert "Expert" in aliases
