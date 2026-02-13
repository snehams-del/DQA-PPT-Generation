
import os
import hashlib
import logging
import json
import requests
import wave
import io
from typing import List, Dict, Optional
import google.auth
from google.auth.transport.requests import Request
import random
from podcast_agent.models.media_script import MediaScript, SpeakerProfile, ScriptSegment

# Gemini TTS REST API Implementation favoring "gemini-2.5-pro-tts" model features

class GeminiTtsTool:
    def __init__(self, model_name: str = "gemini-2.5-pro-tts", location: str = "us-central1"):
        """
        Initializes the Gemini TTS Tool using direct REST API calls.
        """
        self.model_name = model_name
        self.location = location
        self.logger = logging.getLogger(__name__)
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        
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
            host_voice = random.choice(self.female_voices)
            expert_voice = random.choice(self.male_voices)
        else:
            host_voice = random.choice(self.male_voices)
            expert_voice = random.choice(self.female_voices)
            
        self.logger.info(f"Voice Assignment - Host: {host_voice} ({'Female' if host_is_female else 'Male'}), Expert: {expert_voice} ({'Male' if host_is_female else 'Female'})")

        # Mapping for MultiSpeakerVoiceConfig
        self.speaker_voice_map = {
            "Host": host_voice,
            "Expert": expert_voice,
        }
        
        # Pool for unknown speakers (exclude chosen ones)
        all_voices = self.male_voices + self.female_voices
        self.voice_pool = [v for v in all_voices if v not in [host_voice, expert_voice]]
        random.shuffle(self.voice_pool)

        # Setup Auth
        self.credentials, self.detected_project = google.auth.default()
        if not self.project_id:
            self.project_id = self.detected_project

    def _get_auth_token(self) -> str:
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        return self.credentials.token

    def _get_voice_id_for_speaker(self, speaker_alias: str) -> str:
        """Determines the Gemini voice ID (e.g., 'Puck') for a given speaker alias."""
        if speaker_alias in self.speaker_voice_map:
            return self.speaker_voice_map[speaker_alias]
        
        # Deterministic assignment
        idx = int(hashlib.md5(speaker_alias.encode()).hexdigest(), 16) % len(self.voice_pool)
        return self.voice_pool[idx]

    def generate_audio(self, script: MediaScript, output_file: str = "podcast.wav") -> str:
        print(f"DEBUG: generate_audio called with script: {script}")
        """
        Generates audio using the Gemini TTS MultiSpeakerMarkup API via REST.
        Args:
            script: MediaScript object containing the podcast script.
            output_file: Path to the output WAV file.
        """
        # We expect a MediaScript object, but for safety in dynamic environments, we can check.
        # If it's a dict (from JSON), we might need to cast it, but the agent should pass the object.
        
        # The script object has:
        # script.speakers: List[SpeakerProfile]
        # script.segments: List[ScriptSegment]
        
        return self._generate_audio_impl(script, output_file)

    def _generate_audio_impl(self, script, output_file: str = "podcast.wav") -> str:
        """
        Generates audio using the Gemini TTS MultiSpeakerMarkup API via REST.
        """
        token = self._get_auth_token()
        
        # Endpoint: texttospeech.googleapis.com
        hostname = "texttospeech.googleapis.com"
        if self.location and self.location != "global":
             hostname = f"{self.location}-texttospeech.googleapis.com"
             
        url = f"https://{hostname}/v1beta1/text:synthesize"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
            "x-goog-user-project": self.project_id
        }

        # 1. Flatten transcript into a single list of turns for MultiSpeakerMarkup
        all_turns = []
        
        # In MediaScript, segments are already a flat list of ScriptSegment(speaker_id, text)
        for segment in script.segments:
            all_turns.append({"speaker": segment.speaker_id, "text": segment.text})

        # Chunking strategy: Group turns until text length approaches safety limit
        inputs = []
        current_turns = []
        current_len = 0
        MAX_CHAR_LIMIT = 500 
        
        for turn in all_turns:
            turn_len = len(turn['text'])
            if current_len + turn_len > MAX_CHAR_LIMIT and current_turns:
                inputs.append(current_turns)
                current_turns = []
                current_len = 0
            
            current_turns.append(turn)
            current_len += turn_len
            
        if current_turns:
            inputs.append(current_turns)

        # 2. Generate Audio for each chunk
        combined_chunks = []
        params = None

        for chunk_idx, turn_batch in enumerate(inputs):
            api_turns = []
            distinct_speakers = set()
            speaker_voice_configs = []
            seen_aliases = set()
            
            def get_safe_alias(raw_id):
                import re
                safe = re.sub(r'[^a-zA-Z0-9]', '', raw_id)
                if not safe:
                     safe = "SpeakerUnknown"
                return safe

            # Add speakers present in this chunk
            for t in turn_batch:
                raw_speaker = t['speaker']
                safe_alias = get_safe_alias(raw_speaker)
                
                t['speaker'] = safe_alias 
                
                api_turns.append({
                    "text": t['text'],
                    "speaker": safe_alias
                })

                if safe_alias not in seen_aliases:
                    # Look up voice ID
                    # 1. Try to find speaker name in script.speakers matching raw_speaker
                    # 2. If found, check if mapped in self.speaker_voice_map
                    # 3. Else fallback to deterministic assignment
                    
                    voice_id = None
                    # Check pre-defined map first (Host/Expert)
                    if raw_speaker in self.speaker_voice_map:
                        voice_id = self.speaker_voice_map[raw_speaker]
                    else:
                        # Try to find common name in speakers list? 
                        # For now, just use the deterministic fallback or existing map logic
                        voice_id = self._get_voice_id_for_speaker(raw_speaker)
                        
                    speaker_voice_configs.append({
                        "speakerAlias": safe_alias,
                        "speakerId": voice_id
                    })
                    seen_aliases.add(safe_alias)

            # Ensure at least 2 speakers to satisfy API requirement
            if len(seen_aliases) < 2 and api_turns:
                 current_speaker = list(seen_aliases)[0]
                 dummy_speaker = "Expert" if current_speaker == "Host" else "Host"
                 if dummy_speaker == current_speaker:
                     dummy_speaker = "SpeakerTwo"
                 
                 api_turns.append({
                     "text": ".",
                     "speaker": dummy_speaker
                 })
                 
                 if dummy_speaker not in seen_aliases:
                      if dummy_speaker in self.speaker_voice_map:
                          voice_id = self.speaker_voice_map[dummy_speaker]
                      else:
                          voice_id = self._get_voice_id_for_speaker(dummy_speaker)
                          
                      speaker_voice_configs.append({
                          "speakerAlias": dummy_speaker,
                          "speakerId": voice_id
                      })
                      seen_aliases.add(dummy_speaker)

            payload = {
                "input": {
                    "multiSpeakerMarkup": {
                        "turns": api_turns
                    },
                    "prompt": "You are a professional podcast production engine. Ensure all speakers sound natural, take appropriate breaths, and react to each other's points with realistic human intonation."
                },
                "voice": {
                    "languageCode": "en-US",
                    "modelName": self.model_name,
                    "multiSpeakerVoiceConfig": {
                         "speakerVoiceConfigs": speaker_voice_configs
                    }
                },
                "audioConfig": {
                    "audioEncoding": "LINEAR16",
                    "sampleRateHertz": 24000 
                }
            }
            
            import time
            time.sleep(1)



            try:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = requests.post(url, headers=headers, json=payload, timeout=60)
                        response.raise_for_status()
                        break 
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code >= 500 and attempt < max_retries - 1:
                            import time
                            wait = 2 ** attempt
                            self.logger.warning(f"Got {e.response.status_code}, retrying in {wait}s...")
                            time.sleep(wait)
                            continue
                        raise 
                
                data = response.json()
                
                if "audioContent" in data:
                    import base64
                    audio_bytes = base64.b64decode(data["audioContent"])
                    
                    with wave.open(io.BytesIO(audio_bytes), 'rb') as wav_reader:
                        if params is None:
                            params = wav_reader.getparams()
                        combined_chunks.append(wav_reader.readframes(wav_reader.getnframes()))
                else:
                    self.logger.warning(f"No audio content in response for chunk {chunk_idx}")

            except Exception as e:
                self.logger.error(f"Failed to generate audio chunk {chunk_idx}: {e}")

                if hasattr(e, 'response') and e.response is not None:
                     self.logger.error(f"API Error Response: {e.response.text}")

        # 3. Save
        if not output_file.endswith(".wav"):
             output_file += ".wav"
        output_path = os.path.abspath(output_file)
        
        if params and combined_chunks:
            with wave.open(output_path, 'wb') as wav_writer:
                wav_writer.setparams(params)
                for chunk in combined_chunks:
                    wav_writer.writeframes(chunk)
            return output_path
        else:
            print("Warning: No audio generated.")
            return ""

