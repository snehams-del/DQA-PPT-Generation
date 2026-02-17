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

import os
import io
import logging
from pydub import AudioSegment
import random
import re
from typing import List
import concurrent.futures

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.cloud import texttospeech
from google.api_core.exceptions import RetryError, TooManyRequests, ServiceUnavailable, InternalServerError

from podcast_agent.models.podcast_transcript import PodcastTranscript, PodcastMetadata, PodcastSegment, SpeakerDialogue
from podcast_agent.tools.voice_constants import MALE_VOICES, FEMALE_VOICES

class GeminiTtsTool:
    def __init__(self, location: str = "us-central1"):
        """
        Initializes the Gemini TTS Tool using the google-cloud-texttospeech SDK.
        """
        self.voice_name = "en-US-Studio-MultiSpeaker"
        self.model_id = "gemini-2.5-pro-tts"
        self.location = location
        self.logger = logging.getLogger(__name__)
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        
        # Initialize SDK Client
        # The SDK natively resolves Application Default Credentials (ADC).
        self.client = texttospeech.TextToSpeechClient()

        self.male_voices = MALE_VOICES
        self.female_voices = FEMALE_VOICES

        # Randomly assign genders to Host and Expert (one Male, one Female)
        # 50% chance Host is Female
        host_is_female = random.choice([True, False])
        if host_is_female:
            self.host_voice = random.choice(self.female_voices)
            self.expert_voice = random.choice(self.male_voices)
        else:
            self.host_voice = random.choice(self.male_voices)
            self.expert_voice = random.choice(self.female_voices)
            
        self.logger.info(f"Voice Assignment - Host: {self.host_voice} ({'Female' if host_is_female else 'Male'}), Expert: {self.expert_voice} ({'Male' if host_is_female else 'Female'})")

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=4, min=4, max=60),
        retry=retry_if_exception_type((TooManyRequests, ServiceUnavailable, InternalServerError)),
        reraise=True
    )
    def _synthesize_segment(self, segment: PodcastSegment, speaker_voice_configs: List[texttospeech.MultispeakerPrebuiltVoice]) -> bytes:
        """
        Synthesizes a single segment leveraging the texttospeech SDK.
        Decorated with tenacity to retry on transient or quota errors.
        Returns raw audio bytes in WAV LINEAR16 format.
        """
        # Assemble MultiSpeakerMarkup.Turn
        turns = []
        for dialogue in segment.speaker_dialogues:
            turns.append(
                texttospeech.MultiSpeakerMarkup.Turn(
                    speaker=dialogue.speaker_id,
                    text=dialogue.text
                )
            )
        
        voice_selection = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=self.voice_name,
            model_name=self.model_id,
            multi_speaker_voice_config=texttospeech.MultiSpeakerVoiceConfig(
                speaker_voice_configs=speaker_voice_configs
            )
        )
        
        # Audio Configuration targeting 24kHz Studio output
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=24000
        )
        
        request = texttospeech.SynthesizeSpeechRequest(
            input=texttospeech.SynthesisInput(
                multi_speaker_markup=texttospeech.MultiSpeakerMarkup(turns=turns),
                prompt="You are a professional podcast production engine. Ensure all speakers sound natural, take appropriate breaths, and react to each other's points with realistic human intonation."
            ),
            voice=voice_selection,
            audio_config=audio_config
        )
        
        try:
            response = self.client.synthesize_speech(request=request)
            return response.audio_content
        except Exception as e:
            self.logger.error(f"Error synthesizing segment: {e}")
            raise

    def generate_audio(self, script: PodcastTranscript, output_file: str = "podcast.wav") -> str:
        """
        Generates audio using the Google Cloud Text-to-Speech SDK supporting MultiSpeakerMarkup.
        Args:
            script: PodcastTranscript object or equivalent dictionary containing the podcast transcript.
            output_file: Path to the output WAV file.
        Returns:
            Absolute path to the generated audio file.
        """
        # Handle case where input might be a dictionary (e.g. when called via ADK/LLM)
        if isinstance(script, dict):
            try:
                script = PodcastTranscript.model_validate(script)
            except Exception as e:
                self.logger.warning(f"Failed to validate PodcastTranscript Pydantic model: {e}. Attempting manual extraction.")
                # Manual fallback if Pydantic validation fails
                segments = script.get("segments", [])
                podcast_segments = []
                for s in segments:
                    dialogues_data = s.get("speaker_dialogues", [])
                    speaker_dialogues = []
                    for d in dialogues_data:
                        if d.get("text") and d.get("speaker_id"):
                            speaker_dialogues.append(SpeakerDialogue(speaker_id=d["speaker_id"], text=d["text"]))
                    if speaker_dialogues:
                        podcast_segments.append(PodcastSegment(
                            segment_title=s.get("segment_title", ""),
                            title=s.get("title", ""),
                            start_time=s.get("start_time", 0.0),
                            end_time=s.get("end_time", 0.0),
                            speaker_dialogues=speaker_dialogues
                        ))
                script = PodcastTranscript(
                    metadata=PodcastMetadata(episode_title="Audio Generation", duration_seconds=0, summary="Audio gen fallback"),
                    speakers=[],
                    segments=podcast_segments
                )
                
        self.logger.info(f"Starting audio generation for podcast transcript with {len(script.segments)} parts.")
        
        if not output_file.endswith(".wav"):
             output_file += ".wav"
        output_path = os.path.abspath(output_file)
        
        speaker_voice_configs = self._prepare_speaker_configs(script)
        
        valid_segments_bytes = self._synthesize_segments_parallel(script, speaker_voice_configs)
        if not valid_segments_bytes:
            self.logger.warning("No audio was successfully generated.")
            return ""
            
        return self._assemble_wav_file(valid_segments_bytes, output_path)

    def _prepare_speaker_configs(self, script: PodcastTranscript) -> List[texttospeech.MultispeakerPrebuiltVoice]:
        """Extracts unique speakers and assigns them to the prebuilt voice configs."""
        unique_speakers = []
        for segment in script.segments:
            for dialogue in segment.speaker_dialogues:
                if dialogue.speaker_id not in unique_speakers:
                    unique_speakers.append(dialogue.speaker_id)
        
        if len(unique_speakers) > 2:
            self.logger.warning(f"Found {len(unique_speakers)} speakers, but API only supports 2. Truncating.")
            unique_speakers = unique_speakers[:2]
            
        speaker_voice_configs = []
        for idx, speaker_name in enumerate(unique_speakers):
            voice_id = self.host_voice if idx == 0 else self.expert_voice
            sanitized_alias = re.sub(r'[^a-zA-Z0-9]', '', speaker_name)
            speaker_voice_configs.append(
                texttospeech.MultispeakerPrebuiltVoice(
                    speaker_alias=sanitized_alias,
                    speaker_id=voice_id
                )
            )
            for segment in script.segments:
                for dialogue in segment.speaker_dialogues:
                    if dialogue.speaker_id == speaker_name:
                        dialogue.speaker_id = sanitized_alias
        
        return speaker_voice_configs

    def _synthesize_segments_parallel(self, script: PodcastTranscript, speaker_voice_configs: List[texttospeech.MultispeakerPrebuiltVoice]) -> List[bytes]:
        """Executes the synthesis of each segment in parallel and returns the ordered audio bytes."""
        audio_segments_ordered = [None] * len(script.segments)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_idx = {
                executor.submit(self._synthesize_segment, segment, speaker_voice_configs): idx
                for idx, segment in enumerate(script.segments)
            }
            
            for future in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    audio_bytes = future.result()
                    audio_segments_ordered[idx] = audio_bytes
                except Exception as exc:
                    self.logger.error(f"Segment {idx} generated an exception: {exc}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                    
        return [seg for seg in audio_segments_ordered if seg is not None]

    def _assemble_wav_file(self, audio_segments: List[bytes], output_path: str) -> str:
        """Assembles the raw audio bytes into a continuous, high-quality audio file."""
        if not audio_segments:
            self.logger.warning("No audio segments provided for assembly.")
            return ""
            
        combined_audio = AudioSegment.empty()

        for idx, segment_bytes in enumerate(audio_segments):
            try:
                segment_audio = AudioSegment.from_file(io.BytesIO(segment_bytes), format="wav")
                combined_audio += segment_audio
                # Add a brief pause between segments for better pacing
                combined_audio += AudioSegment.silent(duration=200)
            except Exception as e:
                self.logger.error(f"Failed to read segment {idx} bytes: {e}")

        if len(combined_audio) > 0:
            file_format = output_path.split('.')[-1]
            combined_audio.export(output_path, format=file_format)
            self.logger.info(f"Audio extraction complete. Saved to: {output_path}")
            return output_path
        else:
            self.logger.warning("No audio generated.")
            return ""
