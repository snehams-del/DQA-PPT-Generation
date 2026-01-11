import os

from google.adk.agents import Agent
from google.genai.types import (
    GenerateContentConfig,
    HarmBlockThreshold,
    HarmCategory,
    SafetySetting,
)

from .prompts import AGENT_INSTRUCTION

# Determine model name based on API choice
# Check if Vertex AI is being used
use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE").upper() == "TRUE"

if use_vertex:
    # Vertex AI Live API model name format
    model_name = "gemini-live-2.5-flash-preview-native-audio-09-2025"
else:
    # Gemini Live API model name format
    model_name = "gemini-2.5-flash-native-audio-preview-09-2025"

genai_config = GenerateContentConfig(
    temperature=0.5
)

root_agent = Agent(
   name="example_agent",
   model=model_name,
   description="A helpful AI assistant.",
   instruction=AGENT_INSTRUCTION,
   generate_content_config=genai_config,
)