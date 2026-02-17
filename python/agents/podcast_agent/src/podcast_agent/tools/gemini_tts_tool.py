import os
import hashlib
import logging
import io
import wave
import random
from typing import List, Dict, Optional
import concurrent.futures

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.cloud import texttospeech
from google.api_core.exceptions import RetryError, TooManyRequests, ServiceUnavailable, InternalServerError

from podcast_agent.models.podcast_transcript import PodcastTranscript, PodcastSegment, SpeakerDialogue, PodcastMetadata

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

        # Database of Gemini Voices by Gender
        self.male_voices = [
            "Achird", "Algenib", "Algieba", "Alnilam", "Charon", "Enceladus", 
            "Fenrir", "Iapetus", "Orus", "Puck", "Rasalgethi", "Sadachbia", 
            "Sadaltager", "Schedar", "Umbriel", "Zubenelgenubi"
        ]
        self.female_voices = [
            "Achernar", "Aoede", "Autonoe", "Callirrhoe", "Despina", "Erinome", 
            "Gacrux", "Kore", "Laomedeia", "Leda", "Pulcherrima", "Sulafat", 
            "Vindemiatrix", "Zephyr"
        ]

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
        
        # Determine unique speakers in this script to build the MultiSpeaker configuration
        # For this podcast agent, we expect Host and Expert.
        unique_speakers = []
        for segment in script.segments:
            for dialogue in segment.speaker_dialogues:
                if dialogue.speaker_id not in unique_speakers:
                    unique_speakers.append(dialogue.speaker_id)
        
        # Limit to 2 speakers as per API constraints
        if len(unique_speakers) > 2:
            self.logger.warning(f"Found {len(unique_speakers)} speakers, but API only supports 2. Truncating.")
            unique_speakers = unique_speakers[:2]
            
        # Build speaker configuration mapping transcript speaker names to our assigned voices
        import re
        speaker_voice_configs = []
        for idx, speaker_name in enumerate(unique_speakers):
            voice_id = self.host_voice if idx == 0 else self.expert_voice
            # Sanitize speaker alias: only alphanumeric, no whitespace
            sanitized_alias = re.sub(r'[^a-zA-Z0-9]', '', speaker_name)
            speaker_voice_configs.append(
                texttospeech.MultispeakerPrebuiltVoice(
                    speaker_alias=sanitized_alias,
                    speaker_id=voice_id
                )
            )
            # Update the speaker name in segments to match the sanitized alias
            for segment in script.segments:
                for dialogue in segment.speaker_dialogues:
                    if dialogue.speaker_id == speaker_name:
                        dialogue.speaker_id = sanitized_alias

        # Execute synthesis across segments in parallel
        # Max workers set to 3 to prevent immediate aggressive ratelimiting while still gaining speed
        audio_segments_ordered = [None] * len(script.segments)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Reconstruct ordered audio list
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
                    
        # Filter out any failed segments (None)
        valid_segments_bytes = [seg for seg in audio_segments_ordered if seg is not None]
        
        if not valid_segments_bytes:
            self.logger.warning("No audio was successfully generated.")
            return ""
            
        # Assemble using raw wave library
        combined_chunks = []
        params = None

        for idx, segment_bytes in enumerate(valid_segments_bytes):
            try:
                with wave.open(io.BytesIO(segment_bytes), 'rb') as wav_reader:
                    if params is None:
                        params = wav_reader.getparams()
                    combined_chunks.append(wav_reader.readframes(wav_reader.getnframes()))
            except Exception as e:
                self.logger.error(f"Failed to read segment {idx} bytes: {e}")

        # Export compiled chunks to WAV file
        if params and combined_chunks:
            with wave.open(output_path, 'wb') as wav_writer:
                wav_writer.setparams(params)
                for chunk in combined_chunks:
                    wav_writer.writeframes(chunk)
            self.logger.info(f"Audio extraction complete. Saved to: {output_path}")
            return output_path
        else:
            self.logger.warning("No audio generated.")
            return ""
