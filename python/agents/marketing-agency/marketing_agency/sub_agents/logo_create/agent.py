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

"""logo_create_agent: for creating logos"""

import os
import uuid

from google.adk import Agent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import Client, types
from google.cloud import storage

from . import prompt

MODEL = "gemini-2.5-pro"
MODEL_IMAGE = "imagen-3.0-generate-002"


async def generate_image(img_prompt: str, tool_context: "ToolContext"):
    """Generates an image based on the prompt."""
    client = Client()
    response = client.models.generate_images(
        model=MODEL_IMAGE,
        prompt=img_prompt,
        config={"number_of_images": 1},
    )
    if not response.generated_images:
        return {"status": "failed"}
    image_bytes = response.generated_images[0].image.image_bytes

    # Save in ADK artifacts (visible in Dev UI / artifact_delta)
    await tool_context.save_artifact(
        "image.png",
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    )

    # Additionally persist to GCS when running on Agent Engines so it can be fetched later
    gcs_uri = ""
    bucket_name = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET") or os.getenv("GCS_BUCKET")
    if bucket_name:
        try:
            client = storage.Client()
            # Use a unique object path to avoid collisions across runs
            object_name = f"adk-artifacts/logos/{uuid.uuid4().hex}.png"
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            blob.upload_from_string(image_bytes, content_type="image/png")
            gcs_uri = f"gs://{bucket_name}/{object_name}"
        except Exception:
            # Ignore upload issues so the tool still succeeds; artifact remains in ADK
            gcs_uri = ""

    return {
        "status": "success",
        "detail": "Image generated successfully and stored in artifacts.",
        "filename": "image.png",
        "gcs_uri": gcs_uri,
    }


logo_create_agent = Agent(
    model=MODEL,
    name="logo_create_agent",
    description=(
        "An agent that generates images and answers "
        "questions about the images."
    ),
    instruction=prompt.LOGO_CREATE_PROMPT,
    output_key="logo_create_output",
    tools=[generate_image, load_artifacts],
)
