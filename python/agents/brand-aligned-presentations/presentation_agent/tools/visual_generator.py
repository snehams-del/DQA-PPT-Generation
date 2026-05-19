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

import asyncio
import os
import tempfile
import uuid

from google.genai import types

from ..shared_libraries.config import (
    GOOGLE_CLOUD_LOCATION,
    GOOGLE_CLOUD_PROJECT,
    OUTPUT_BUCKET,
    OUTPUT_PREFIX,
    get_gcs_client,
    get_logger,
    initialize_genai_client,
)


async def generate_visual(prompt: str) -> str:
    """
    Generates a visual from a single string prompt using a multi-modal model.
    Returns the GCS URI of the generated image (in OUTPUT_BUCKET),
    or a temp local path if OUTPUT_BUCKET is not configured.
    """
    log = get_logger("generate_visual_tool")

    if not prompt:
        return "Error: Prompt cannot be empty."

    # Strip any prefixes like "chart:" or "image:" as the model understands context
    prompt = prompt.strip()
    if prompt.lower().startswith("chart:"):
        chart_description = prompt[len("chart:") :]
        prompt = f"A professional data visualization representing: {chart_description}"
    elif prompt.lower().startswith("image:"):
        prompt = prompt[len("image:") :]

    prompt = prompt.strip()

    log.info(f"Generating visual for prompt: '{prompt}'")

    try:
        # Initialize / get Vertex AI GenAI client
        client = initialize_genai_client()
        if client is None:
            return "Error: Vertex AI client is not initialized. Check GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION."

        # You can override the image model by env var if needed
        model_name = os.getenv("IMAGE_CONTENT_MODEL_NAME", "gemini-2.5-flash-image")

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model_name,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="4:3"),
            ),
        )

        # Extract image bytes safely
        image_bytes = None
        try:
            if (
                response.candidates
                and response.candidates[0].content
                and response.candidates[0].content.parts
                and response.candidates[0].content.parts[0].inline_data
                and response.candidates[0].content.parts[0].inline_data.data
            ):
                image_bytes = response.candidates[0].content.parts[0].inline_data.data
        except Exception:
            image_bytes = None

        if not image_bytes:
            raise RuntimeError("Model did not return valid image bytes.")

        # If OUTPUT_BUCKET is set, upload there (DQA requirement)
        if OUTPUT_BUCKET:
            storage_client = get_gcs_client()
            if storage_client is None:
                raise RuntimeError("GCS client could not be initialized.")

            bucket = storage_client.bucket(OUTPUT_BUCKET)

            # Store images under output prefix + generated_images/
            prefix = (OUTPUT_PREFIX or "").strip().strip("/")
            if prefix:
                prefix = prefix + "/"
            image_filename = f"{prefix}generated_images/{uuid.uuid4().hex}.png"

            blob = bucket.blob(image_filename)

            await asyncio.to_thread(
                blob.upload_from_string,
                image_bytes,
                content_type="image/png",
                timeout=60,
            )

            gcs_uri = f"gs://{OUTPUT_BUCKET}/{image_filename}"
            log.info(f"Visual saved to OUTPUT_BUCKET. URI: {gcs_uri}")
            return gcs_uri

        # Otherwise fallback to local temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_bytes)
            local_filepath = tmp.name

        log.info(f"OUTPUT_BUCKET not set. Saved visual locally: {local_filepath}")
        return local_filepath

    except Exception as e:
        log.error(
            f"Visual generation FAILED for prompt '{prompt}': {e}",
            exc_info=True,
        )
        return f"Error: Visual generation failed. Details: {e}"
``