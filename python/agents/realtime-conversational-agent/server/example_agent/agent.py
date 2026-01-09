import os

from google.adk.agents import Agent
from google.genai.types import (
    GenerateContentConfig,
    HarmBlockThreshold,
    HarmCategory,
    SafetySetting,
)

from .prompts import AGENT_INSTRUCTION

# Constants
_ENV_VERTEX_AI_FLAG = "GOOGLE_GENAI_USE_VERTEXAI"
_MODEL_VERTEX_AI = "gemini-live-2.5-flash-preview-native-audio"
_MODEL_GEMINI_API = "gemini-2.5-flash-native-audio-preview-12-2025"


def _get_model_name() -> str:
    """Get the appropriate model name based on the API provider.
    
    Model naming differs between providers:
    - Vertex AI: Uses "gemini-live-*" format (with "live" prefix, no date suffix)
    - Google AI Studio (Gemini API): Uses "gemini-*-preview-*-*" format 
      (with date suffix, no "live" prefix)
    
    Returns:
        The model name string appropriate for the configured API provider.
    """
    use_vertex_ai = os.getenv(_ENV_VERTEX_AI_FLAG, "FALSE").upper() == "TRUE"
    return _MODEL_VERTEX_AI if use_vertex_ai else _MODEL_GEMINI_API


genai_config = GenerateContentConfig(
    temperature=0.5
)

root_agent = Agent(
    name="example_agent",
    model=_get_model_name(),
    description="A helpful AI assistant.",
    instruction=AGENT_INSTRUCTION
)