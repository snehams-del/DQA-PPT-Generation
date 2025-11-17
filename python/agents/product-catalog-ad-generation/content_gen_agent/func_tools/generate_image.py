# Copyright 2025 Google LLC
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
"""Handles the generation of images based on storyline prompts."""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

from content_gen_agent.utils.evaluate_media import (
    calculate_evaluation_score,
)
from content_gen_agent.utils.gemini_utils import call_gemini_image_api, initialize_gemini_client
from content_gen_agent.utils.images import (
    IMAGE_MIME_TYPE,
    _load_gcs_image
)

# --- Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

GCP_PROJECT = os.getenv("GCP_PROJECT")

IMAGE_GEN_MODEL_GEMINI = "gemini-2.5-flash-image"

STORYLINE_MODEL = "gemini-2.5-pro"
MAX_RETRIES = 3
ASSET_SHEET_FILENAME = "asset_sheet.png"
LOGO_GCS_URI_BASE = "branding_logos/logo.png"

def get_bucket() -> str:
    """Retrieves the GCS bucket name from environment variables.

    Returns:
        The GCS bucket name.

    Raises:
        RuntimeError: If neither GCS_BUCKET nor GCP_PROJECT are set.
    """
    try:
        return os.environ["GCS_BUCKET"]
    except KeyError as e:
        if GCP_PROJECT:
            bucket = f"{GCP_PROJECT}-contentgen-static"
            logging.warning(
                "GCS_BUCKET environment variable not set; defaulting to %s", bucket
            )
            return bucket
        raise RuntimeError(
            "Neither GCS_BUCKET nor GCP_PROJECT environment variables are set"
        ) from e


GCS_BUCKET = get_bucket()
LOGO_GCS_URI = f"{GCS_BUCKET}/{LOGO_GCS_URI_BASE}"

client = initialize_gemini_client()


async def generate_one_image(
    prompt: str,
    input_images: List[types.Part],
    filename_prefix: str,
) -> Dict[str, Any]:
    """Generates a single image using Gemini, handling retries.

    Args:
        prompt (str): The prompt for image generation.
        input_images (List[types.Part]): A list of input images as Part objects.
        filename_prefix (str): The prefix for the output filename.

    Returns:
        A dictionary containing the result of the image generation.
    """
    if not input_images:
        return {
            "status": "failed",
            "detail": "Input image(s) are required for image generation.",
        }

    contents = [prompt, *input_images]
    tasks = [
        call_gemini_image_api(
            client=client,
            model=IMAGE_GEN_MODEL_GEMINI,
            contents=contents,
            image_prompt=prompt,
        )
        for _ in range(MAX_RETRIES)
    ]
    results = await asyncio.gather(*tasks)
    successful_attempts = [res for res in results if res]

    if not successful_attempts:
        return {
            "status": "failed",
            "detail": f"All image generation attempts failed for prompt: '{prompt}'.",
        }

    best_attempt = max(
        successful_attempts,
        key=lambda x: calculate_evaluation_score(x.get("evaluation")),
    )

    if best_attempt.get("evaluation").decision != "Pass":
        score = calculate_evaluation_score(best_attempt["evaluation"])
        logging.warning(
            "No image passed evaluation for '%s'. Best score: %s", prompt, score
        )

    filename = f"{filename_prefix}.png"
    return {
        "status": "success",
        "detail": f"Image generated successfully for {filename}.",
        "filename": filename,
        "image_bytes": best_attempt["image_bytes"],
    }


# pylint: disable=too-many-locals
async def generate_images_from_storyline(
    prompts: List[str],
    tool_context: ToolContext,
    scene_numbers: Optional[List[int]] = None,
    logo_prompt_present: bool = True,
) -> List[str]:
    """Generates images for a commercial storyboard based on a visual style guide.

    Args:
        prompts (List[str]): a list of prompts in the order of the scene numbers, one
          prompt for each scene's image.
            - If logo_prompt_present is true, the last prompt is for the logo background.
            - Make sure to split up each scene's prompt and make them independent of each other.
            - Each prompt should only describe the first frame of that particular scene in detail.
                        - Make sure to mention that each image should fill the space and not have
              empty whitespace around it.
            - Never include children.
        tool_context (ToolContext): Context for saving artifacts.
        scene_numbers (Optional[List[int]]): A list of scene numbers to generate
          images for.
          - If None or empty, images will be
          - generated for all scenes.
          - Note that scene numbers are 0-based.
          - Defaults to None.
        logo_prompt_present (bool): Whether the prompts list contains a prompt for the
          logo scene. You must set this to false if the prompts list does not
          contain a prompt for the logo scene. If true, the logo prompt must be
          last. Defaults to True.

    Returns:
        A list of JSON strings with the status of each image generation.
    """
    if not client:
        return [
            json.dumps(
                {"status": "failed", "detail": "Gemini client not initialized."}
            )
        ]

    storage_client = storage.Client()
    logo_image = await _load_gcs_image(LOGO_GCS_URI, storage_client)
    if not logo_image:
        return [
            json.dumps(
                {
                    "status": "failed",
                    "detail": f"Failed to load logo from '{LOGO_GCS_URI}'.",
                }
            )
        ]

    try:
        asset_sheet_image = await tool_context.load_artifact(
            ASSET_SHEET_FILENAME
        )
        if not asset_sheet_image:
            raise ValueError("Asset sheet artifact is empty.")
    except (FileNotFoundError, ValueError) as e:
        return [
            json.dumps(
                {
                    "status": "failed",
                    "detail": f"Failed to load asset sheet: {e}",
                }
            )
        ]

    tasks = []
    scenes_to_generate = (
        scene_numbers if scene_numbers is not None else range(len(prompts))
    )

    for i, scene_num in enumerate(scenes_to_generate):
        if not 0 <= i < len(prompts):
            continue

        prompt = prompts[i]
        is_logo_scene = logo_prompt_present and scene_num == len(prompts) - 1
        filename_prefix = f"{scene_num}_"

        if is_logo_scene:
            logo_prompt = f"Place the company logo centered on the following background: {prompt}"
            tasks.append(
                generate_one_image(logo_prompt, [logo_image], filename_prefix)
            )
        else:
            tasks.append(
                generate_one_image(
                    prompt, [asset_sheet_image], filename_prefix
                )
            )

    results = await asyncio.gather(*tasks)
    results.sort(key=lambda r: r.get("filename", ""))

    save_tasks = []
    for result in results:
        if result.get("status") == "success" and result.get("image_bytes"):
            filename = result["filename"]
            image_bytes = result["image_bytes"]
            save_tasks.append(
                tool_context.save_artifact(
                    filename,
                    types.Part.from_bytes(
                        data=image_bytes, mime_type=IMAGE_MIME_TYPE
                    ),
                )
            )
            result["detail"] = f"Image stored as {filename}."
            del result["image_bytes"]

    await asyncio.gather(*save_tasks)
    return [json.dumps(res) for res in results]
