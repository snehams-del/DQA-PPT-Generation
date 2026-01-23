
from google.adk.agents import LlmAgent
from tools.gemini_tts_tool import GeminiTtsTool
from podcast_agent.config import (
    TTS_MODEL_NAME,
    TTS_LOCATION,
    PODCAST_TRANSCRIPT_MODEL_NAME,
)

gemini_tts_tool = GeminiTtsTool(model_name=TTS_MODEL_NAME, location=TTS_LOCATION)

podcast_audio_generator_agent = LlmAgent(
    name="podcast_audio_generator_agent",
    description="This agent generates audio from the podcast transcript.",
    model=PODCAST_TRANSCRIPT_MODEL_NAME,
    instruction=(
        "You are an expert audio engineer. Your goal is to take a podcast transcript and generate an audio file from it."
        "You have access to the `GeminiTtsTool`."
        "The transcript will be provided to you in the previous turn."
        "The transcript is a JSON object with a 'segments' list."
        "You MUST pass the raw JSON string of the transcript to the `generate_audio` function of the `GeminiTtsTool`."
        "Do NOT try to pass a Python object or list."
        "The output file name should be 'podcast_output.wav'."
        "You MUST return the absolute path to the generated audio file as your final response."
    ),
    tools=[gemini_tts_tool.generate_audio],
)
