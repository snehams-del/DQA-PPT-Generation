"""Utility functions for interacting with the Gemini API."""
import logging
from typing import Any, Dict, List, Optional

from google import auth
from google import genai
from google.api_core import exceptions as api_exceptions
from google.genai import types
from google.genai.types import HarmBlockThreshold, HarmCategory

from content_gen_agent.utils.evaluate_media import (
    evaluate_media,
)

IMAGE_MIME_TYPE = "image/png"

SAFETY_SETTINGS = [
    types.SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=HarmBlockThreshold.OFF,
    ),
    types.SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.OFF,
    ),
    types.SafetySetting(
        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=HarmBlockThreshold.OFF,
    ),
    types.SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.OFF,
    ),
]

GENERATE_CONTENT_CONFIG = types.GenerateContentConfig(
    temperature=1.0,
    top_p=0.95,
    safety_settings=SAFETY_SETTINGS,
    image_config=types.ImageConfig(
        aspect_ratio="9:16",
    )
)

async def call_gemini_image_api(
    client: genai.Client,
    model: str,
    contents: List[Any],
    image_prompt: str,
) -> Dict[str, Any]:
    """Calls the Gemini image generation API and evaluates the result.

    Args:
        client: The Gemini API client.
        model: The name of the model to use for image generation.
        contents: The content to send to the model.
        image_prompt: The prompt used for image generation.

    Returns:
        A dictionary with the image bytes, evaluation, and MIME type.
    """
    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=GENERATE_CONTENT_CONFIG,
        )
        if (
            response.candidates
            and response.candidates[0].content
            and response.candidates[0].content.parts
        ):
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    evaluation = await evaluate_media(
                        image_bytes, IMAGE_MIME_TYPE, image_prompt
                    )
                    return {
                        "image_bytes": image_bytes,
                        "evaluation": evaluation,
                        "mime_type": IMAGE_MIME_TYPE,
                    }
    except (api_exceptions.GoogleAPICallError, ValueError) as e:
        logging.error(
            "Error calling image generation API: %s", e, exc_info=True
        )
    return {}


def initialize_gemini_client() -> Optional[genai.Client]:
    """Initializes and returns a Gemini client.

    Returns:
        A genai.Client instance or None if initialization fails.
    """
    try:
        client = genai.Client()
        return client
    except (auth.exceptions.DefaultCredentialsError, ValueError) as e:
        logging.error("Failed to initialize Gemini client: %s", e, exc_info=True)
        return None
