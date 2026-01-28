
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

    def generate_audio(self, transcript_json: str, output_file: str = "podcast.wav") -> str:
        """
        Generates audio using the Gemini TTS MultiSpeakerMarkup API via REST.
        Args:
            transcript_json: JSON string containing the podcast transcript with 'segments'.
            output_file: Path to the output WAV file.
        """
        try:
             # Handle cases where the LLM passes a python dict as string or wrapped in markdown
             cleaned_json = transcript_json.strip()
             if cleaned_json.startswith("```json"):
                 cleaned_json = cleaned_json[7:]
             if cleaned_json.endswith("```"):
                 cleaned_json = cleaned_json[:-3]
             cleaned_json = cleaned_json.strip()
             
             data = json.loads(cleaned_json)
             if isinstance(data, list):
                 transcript_segments = data
             elif "segments" in data:
                 transcript_segments = data["segments"]
             else:
                 # Fallback if structure is unknown, assume list of turns? 
                 # Or just log warning and try usage
                 transcript_segments = [data]
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse transcript JSON: {e}")
            return f"Error: Invalid JSON provided. {e}"

        return self._generate_audio_impl(transcript_segments, output_file)

    def _generate_audio_impl(self, transcript_segments: List[Dict], output_file: str = "podcast.wav") -> str:
        """
        Generates audio using the Gemini TTS MultiSpeakerMarkup API via REST.
        """
        token = self._get_auth_token()
        
        # Endpoint: texttospeech.googleapis.com (Global usually works, or regional)
        # Docs use standard client, which defaults to global unless client_options set.
        # User linked docs suggest "gemini-2.5-pro-tts" model availability.
        # Let's use the standard endpoint with the model param.
        
        hostname = "texttospeech.googleapis.com"
        # If user explicitly wants regional, we can use it, but global is safest for 404 avoidance unless strictly required.
        if self.location and self.location != "global":
             hostname = f"{self.location}-texttospeech.googleapis.com"
             
        url = f"https://{hostname}/v1beta1/text:synthesize"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
            "x-goog-user-project": self.project_id
        }

        # 1. Flatten transcript into a single list of turns for MultiSpeakerMarkup
        # Assuming we can send one large request if it fits (~5000 chars?). 
        # If not, we chunk. Gemini TTS supports larger contexts but let's be safe (~4096 chars common limit).
        
        all_turns = []
        for seg in transcript_segments:
            dialogues = getattr(seg, 'speaker_dialogues', [])
            if not dialogues and isinstance(seg, dict):
                dialogues = seg.get('speaker_dialogues', [])
                
            for turn in dialogues:
                speaker_id = getattr(turn, 'speaker_id', None) or turn.get('speaker_id')
                text = getattr(turn, 'text', None) or turn.get('text')
                if text and speaker_id:
                    all_turns.append({"speaker": speaker_id, "text": text})

        # Chunking strategy: Group turns until text length approaches safety limit (e.g. 4000 chars)
        inputs = []
        current_turns = []
        current_len = 0
        MAX_CHAR_LIMIT = 500 # Reduced to 500 to avoid 502 timeouts aggressively
        
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
            # Construct MultiSpeakerMarkup
            # API expects: input={"multiSpeakerMarkup": {"turns": [...]}}
            # Each turn: {"text": "...", "speaker": "alias"}
            # AND unique mappings in voice config
            
            api_turns = []
            distinct_speakers = set()
            
            # Construct Voice Config map
            speaker_voice_configs = []
            seen_aliases = set()
            
            # Map raw speaker IDs to safe aliases
            # We need to maintain this mapping across chunks if we want consistency?
            # Actually, we process all chunks in one go here, so we can just consistent map.
            # But the speaker_voice_map is based on raw aliases? No, let's fix.
            
            # Improved mapping:
            # 1. Sanitize the speaker ID to be strictly alphanumeric for the API.
            # 2. Use the ORIGINAL ID to lookup the voice from self.speaker_voice_map.
            
            def get_safe_alias(raw_id):
                # Replace non-alnum with nothing (collapse)
                import re
                safe = re.sub(r'[^a-zA-Z0-9]', '', raw_id)
                if not safe:
                     safe = "SpeakerUnknown"
                return safe

            # Add speakers present in this chunk
            for t in turn_batch:
                raw_speaker = t['speaker']
                safe_alias = get_safe_alias(raw_speaker)
                
                # Update the turn to use the safe alias
                t['speaker'] = safe_alias 
                # Note: modifying 'turn_batch' dicts in place is fine as they are local to this loop context or copied
                
                api_turns.append({
                    "text": t['text'],
                    "speaker": safe_alias
                })

                if safe_alias not in seen_aliases:
                    # Use RAW speaker for voice lookup (e.g. "Host")
                    voice_id = self._get_voice_id_for_speaker(raw_speaker)
                    speaker_voice_configs.append({
                        "speakerAlias": safe_alias,
                        "speakerId": voice_id
                    })
                    seen_aliases.add(safe_alias)

            # Ensure at least 2 speakers to satisfy API requirement
            # If the chunk only has 1 speaker, the API fails with "Multi-speaker synthesis requires two distinct speakers."
            if len(seen_aliases) < 2 and api_turns:
                 # Find a speaker alias that isn't the current one
                 current_speaker = list(seen_aliases)[0]
                 dummy_speaker = "Expert" if current_speaker == "Host" else "Host"
                 # Just in case current_speaker is something else
                 if dummy_speaker == current_speaker:
                     dummy_speaker = "SpeakerTwo"
                 
                 # Append a dummy silent turn
                 api_turns.append({
                     "text": ".",
                     "speaker": dummy_speaker
                 })
                 
                 # Register the dummy speaker's voice
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
                    "prompt": "Generate a podcast conversation."
                },
                "voice": {
                    "languageCode": "en-US",
                    "modelName": self.model_name, # "gemini-2.5-flash-tts"
                    "multiSpeakerVoiceConfig": {
                         "speakerVoiceConfigs": speaker_voice_configs
                    }
                },
                "audioConfig": {
                    "audioEncoding": "LINEAR16",
                    "sampleRateHertz": 24000 
                }
            }
            
            # Rate limiting / Backoff for stability
            import time
            time.sleep(1)

            # Debug Payload
            if chunk_idx == 0:
                print(f"DEBUG: Payload for chunk {chunk_idx}: {json.dumps(payload, indent=2)}")

            try:
                # Retry logic for 500-level errors
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # print(f"DEBUG: Sending payload to {url}")
                        response = requests.post(url, headers=headers, json=payload)
                        response.raise_for_status()
                        break # Success
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code >= 500 and attempt < max_retries - 1:
                            import time
                            wait = 2 ** attempt
                            self.logger.warning(f"Got {e.response.status_code}, retrying in {wait}s...")
                            time.sleep(wait)
                            continue
                        raise # Re-raise if not 5xx or retries exhausted
                
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

