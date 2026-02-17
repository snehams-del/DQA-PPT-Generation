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

from google.adk.agents import LlmAgent
from podcast_agent.tools.gemini_tts_tool import GeminiTtsTool
from podcast_agent.models.podcast_transcript import PodcastTranscript
from podcast_agent.config import (
    TTS_LOCATION,
    PODCAST_TRANSCRIPT_MODEL_NAME,
)

gemini_tts_tool = GeminiTtsTool(location=TTS_LOCATION)

podcast_audio_generator_agent = LlmAgent(
    name="podcast_audio_generator_agent",
    description="This agent generates audio from the podcast transcript.",
    model=PODCAST_TRANSCRIPT_MODEL_NAME,
    instruction=(
        "You are an expert audio engineer. Your goal is to take a podcast transcript and generate an audio file from it."
        "You have access to the `GeminiTtsTool`."
        "The transcript is provided in: "
        "{podcast_episode_transcript}"
        "You need to call `gemini_tts_tool.generate_audio(script: PodcastTranscript, output_file: str)`."
        "Pass the `podcast_episode_transcript` to the tool."
        "The output file name should be 'podcast_output.wav'."
        "You MUST return the absolute path to the generated audio file as your final response."
    ),
    tools=[gemini_tts_tool.generate_audio],
)
