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
import time
from typing import Any, Optional

from google.adk.tools.tool_context import ToolContext
from google.genai import types
from pydantic import ValidationError

from ..shared_libraries.config import (
    DEFAULT_TEMPLATE_URI,
    OUTPUT_BUCKET,
    OUTPUT_PREFIX,
    TEMPLATE_BUCKET,
    TEMPLATE_PREFIX,
    DATA_BUCKET,
    DATA_PREFIX,
    ARTIFACT_BUCKET_NAME,
    get_gcs_client,
    get_logger,
)
from ..shared_libraries.models import DeckSpec


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _split_gs_uri(gs_uri: str) -> tuple[str, str]:
    """Split gs://bucket/path into (bucket, path)."""
    if not gs_uri or not gs_uri.startswith("gs://"):
        raise ValueError(f"Invalid GCS URI: {gs_uri}")
    no_scheme = gs_uri[5:]
    parts = no_scheme.split("/", 1)
    bucket = parts[0]
    path = parts[1] if len(parts) > 1 else ""
    return bucket, path

def _ensure_suffix(name: str, suffix: str) -> str:
    if not name.lower().endswith(suffix.lower()):
        return f"{name}{suffix}"
    return name

def _normalize_prefix(prefix: str) -> str:
    if not prefix:
        return ""
    p = prefix.strip().strip("/")
    return f"{p}/" if p else ""

def _join_gs(bucket_name_or_gs: str, *parts: str) -> str:
    """
    Join bucket + path parts into a gs:// uri.
    Accepts bucket name ("my-bucket") or gs://my-bucket
    """
    b = bucket_name_or_gs.strip()
    if b.startswith("gs://"):
        b = b[5:]
    b = b.strip().strip("/")
    path = "/".join([p.strip().strip("/") for p in parts if p and str(p).strip().strip("/")])
    if path:
        return f"gs://{b}/{path}"
    return f"gs://{b}"

def _list_gcs(bucket_gs_or_name: str, prefix: str = "", suffix: str = "") -> list[str]:
    """List gs:// URIs in a bucket under prefix filtered by suffix."""
    log = get_logger("_list_gcs")
    storage_client = get_gcs_client()
    if not storage_client:
        log.error("GCS client could not be initialized.")
        return []

    bucket_name = bucket_gs_or_name.strip()
    if bucket_name.startswith("gs://"):
        bucket_name = bucket_name[5:]
    bucket_name = bucket_name.strip().strip("/").split("/", 1)[0]

    prefix = _normalize_prefix(prefix)

    try:
        blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
        out = []
        for b in blobs:
            if b.name.endswith("/"):
                continue
            if suffix and not b.name.lower().endswith(suffix.lower()):
                continue
            out.append(f"gs://{bucket_name}/{b.name}")
        return sorted(out)
    except Exception as e:
        log.error(f"Failed listing GCS bucket={bucket_name} prefix={prefix}: {e}", exc_info=True)
        return []


# -----------------------------------------------------------------------------
# NEW: DQA helpers for 3-bucket flow (Template/Data/Output)
# -----------------------------------------------------------------------------
async def list_templates_in_gcs(tool_context: ToolContext) -> list[str]:
    """
    Lists available PPTX templates from TEMPLATE_BUCKET (GCS).
    Returns gs:// URIs.
    """
    log = get_logger("list_templates_in_gcs")
    if not TEMPLATE_BUCKET:
        return ["Error: TEMPLATE_BUCKET env var is not set."]
    templates = _list_gcs(TEMPLATE_BUCKET, prefix=TEMPLATE_PREFIX, suffix=".pptx")
    if not templates:
        log.warning("No templates found.")
    return templates

async def list_excels_in_gcs(tool_context: ToolContext) -> list[str]:
    """
    Lists available Excel files from DATA_BUCKET (GCS).
    Returns gs:// URIs.
    """
    log = get_logger("list_excels_in_gcs")
    if not DATA_BUCKET:
        return ["Error: DATA_BUCKET env var is not set."]
    excels = _list_gcs(DATA_BUCKET, prefix=DATA_PREFIX, suffix=".xlsx")
    if not excels:
        log.warning("No excel files found.")
    return excels

async def make_output_pptx_gcs_uri(
    tool_context: ToolContext,
    base_name: Optional[str] = None,
) -> str:
    """
    Creates a destination GCS URI in OUTPUT_BUCKET for the generated PPTX.
    If base_name is not provided, uses a timestamped name.
    """
    if not OUTPUT_BUCKET:
        return "Error: OUTPUT_BUCKET env var is not set."
    name = base_name.strip() if base_name else f"generated_proposal_{int(time.time())}.pptx"
    name = _ensure_suffix(name, ".pptx")
    return _join_gs(OUTPUT_BUCKET, _normalize_prefix(OUTPUT_PREFIX), name)


# -----------------------------------------------------------------------------
# Artifact Utilities (existing)
# -----------------------------------------------------------------------------
async def list_available_artifacts(tool_context: ToolContext) -> list[str]:
    """Lists the filenames of all available artifacts in the session."""
    try:
        return await tool_context.list_artifacts()
    except Exception as e:
        get_logger("list_available_artifacts").error(f"Error listing artifacts: {e}")
        return [f"Error listing artifacts: {e}"]


async def get_artifact_as_local_path(tool_context: ToolContext, artifact_name: str) -> str:
    """
    Loads a user-uploaded artifact, saves it to a local temp file, and returns the path.
    Includes a retry mechanism for cloud propagation delays.
    """
    log = get_logger("get_artifact_as_local_path")
    try:
        file_artifact = await tool_context.load_artifact(artifact_name)

        if not file_artifact:
            log.warning(
                f"Artifact '{artifact_name}' not found on first try. Waiting 2 seconds for cloud sync..."
            )
            await asyncio.sleep(2.0)
            file_artifact = await tool_context.load_artifact(artifact_name)

        if not file_artifact:
            return f"Error: Artifact '{artifact_name}' is empty or could not be loaded."

        if isinstance(file_artifact, types.Part):
            file_bytes = file_artifact.inline_data.data
        else:
            file_bytes = file_artifact

        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{artifact_name}") as tmp_file:
            tmp_file.write(file_bytes)
            local_path = tmp_file.name

        log.info(f"Successfully retrieved artifact local path: {local_path}")
        return local_path

    except Exception as e:
        log.error(f"Failed to load artifact '{artifact_name}': {e}", exc_info=True)
        return f"Error loading file: {e}"


async def get_gcs_file_as_local_path(gcs_uri: str = DEFAULT_TEMPLATE_URI) -> str:
    """
    Downloads a file from a specific GCS URI to a local temporary file.
    Returns the local file path if successful, otherwise an error string.
    Example: 'gs://my-bucket-name/my-file.pptx'
    """
    log = get_logger("get_gcs_file_as_local_path")
    try:
        if not gcs_uri or not gcs_uri.startswith("gs://"):
            return "Error: Invalid GCS URI. It must start with 'gs://'."

        bucket_name, blob_name = _split_gs_uri(gcs_uri)
        storage_client = get_gcs_client()
        if not storage_client:
            raise RuntimeError("GCS client could not be initialized.")

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if not blob.exists():
            return f"Error: The file does not exist at the specified GCS path: {gcs_uri}"

        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{os.path.basename(blob_name)}") as tmp_file:
            blob.download_to_filename(tmp_file.name)
            local_path = tmp_file.name

        log.info(f"Successfully downloaded GCS file to local path: {local_path}")
        return local_path

    except Exception as e:
        log.error(f"Failed to download file from '{gcs_uri}': {e}", exc_info=True)
        return f"Error: Could not access GCS file. Details: {e}"


async def save_presentation(
    tool_context: ToolContext,
    new_artifact_name: str,
    local_path: str,
    gcs_bucket_name: str | None = None,
) -> str:
    """
    Saves a local presentation file to the artifact store and optionally to GCS.
    For DQA workflow:
      - If gcs_bucket_name is not provided, uploads to OUTPUT_BUCKET (preferred),
        else falls back to ARTIFACT_BUCKET_NAME.
    """
    log = get_logger("save_presentation")
    try:
        if not local_path or not os.path.exists(local_path):
            return f"Error: The local file at '{local_path}' does not exist."

        new_artifact_name = _ensure_suffix(new_artifact_name, ".pptx")

        # 1) Save to ADK Artifact Store
        with open(local_path, "rb") as f:
            file_bytes = f.read()
            ppt_artifact = types.Part(
                inline_data=types.Blob(
                    data=file_bytes,
                    mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )
            )
            await tool_context.save_artifact(new_artifact_name, ppt_artifact)

        log.info(f"Saved presentation as artifact '{new_artifact_name}'.")

        # 2) Upload to GCS output bucket (preferred)
        target_bucket = gcs_bucket_name or OUTPUT_BUCKET or ARTIFACT_BUCKET_NAME
        gcs_message = ""

        if target_bucket:
            try:
                storage_client = get_gcs_client()
                if not storage_client:
                    raise RuntimeError("GCS client could not be initialized.")

                bucket = storage_client.bucket(target_bucket)

                # Save under OUTPUT_PREFIX if configured
                object_name = f"{_normalize_prefix(OUTPUT_PREFIX)}{new_artifact_name}"
                blob = bucket.blob(object_name)

                await asyncio.to_thread(blob.upload_from_filename, local_path)
                gcs_message = f" It was also saved to GCS at 'gs://{target_bucket}/{object_name}'."
            except Exception as e:
                log.error(f"Failed to upload to GCS: {e}", exc_info=True)
                gcs_message = f" However, the upload to GCS failed. Error: {e}"

        return (
            f"Successfully saved the presentation as artifact '{new_artifact_name}'."
            f"{gcs_message} The user can now download it."
        )

    except Exception as e:
        log.error(f"Unexpected error during save_presentation: {e}", exc_info=True)
        return f"Error: An unexpected error occurred during save. Details: {e}"


async def save_deck_spec(tool_context: ToolContext, deck_spec: dict) -> str:
    """
    Saves the deck_spec to persistent session STATE.
    Returns an invisible confirmation instead of a visible filename.
    """
    log = get_logger("save_deck_spec")
    try:
        # Normalize structure
        if "slide_topics" in deck_spec and "slides" not in deck_spec:
            deck_spec["slides"] = deck_spec.pop("slide_topics")

        if isinstance(deck_spec.get("slides"), dict):
            deck_spec["slides"] = list(deck_spec["slides"].values())

        if "closing_title" not in deck_spec:
            deck_spec["closing_title"] = "Thank You"

        validated_spec = DeckSpec(**deck_spec)

        tool_context.state["current_deck_spec"] = validated_spec.model_dump()

        log.info("Persisted deck_spec to session state.")
        return "Success: Presentation plan has been securely saved to the session state."
    except ValidationError as e:
        log.error(f"Validation error: {e.errors()}")
        return f"Error: Invalid deck_spec structure: {e.errors()}"
    except Exception as e:
        log.error(f"Failed to save deck_spec: {e}", exc_info=True)
        return "Error: Internal failure while saving plan."


async def update_slide_in_spec(
    tool_context: ToolContext,
    slide_index: int,
    updated_slide_topic: dict[str, Any],
) -> str:
    """
    Surgically updates a slide in the session STATE.
    Automatically grows the deck if needed.
    """
    log = get_logger("update_slide_in_spec")
    try:
        spec_dict = tool_context.state.get("current_deck_spec")
        if not spec_dict:
            return "Error: No active presentation plan found in session state. Revision failed."

        slides = spec_dict.get("slides", [])

        if 0 <= slide_index < len(slides):
            slides[slide_index].update(updated_slide_topic)
        else:
            while len(slides) < slide_index:
                slides.append(
                    {
                        "title": f"New Slide {len(slides) + 1}",
                        "bullets": [],
                        "layout_name": "Title and Content",
                    }
                )
            new_slide = {
                "title": "New Slide",
                "bullets": [],
                "layout_name": "Title and Content",
            }
            new_slide.update(updated_slide_topic)
            slides.append(new_slide)

        tool_context.state["current_deck_spec"] = spec_dict
        log.info(f"Slide {slide_index} updated in session state successfully.")
        return "Success: The slide has been updated in the session state."

    except Exception as e:
        log.error(f"Failed to update slide: {e}", exc_info=True)
        return "Error: Failed to update slide."


async def read_file_content(tool_context: ToolContext, artifact_name: str) -> str:
    """Reads the raw text content from any uploaded text-based file artifact."""
    log = get_logger("read_file_content")
    try:
        file_artifact = await tool_context.load_artifact(artifact_name)
        if not file_artifact:
            return f"Error: Artifact '{artifact_name}' is empty or could not be loaded."

        if isinstance(file_artifact, types.Part):
            file_bytes = file_artifact.inline_data.data
        else:
            file_bytes = file_artifact

        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return f"Error: '{artifact_name}' is not a readable text file."
    except Exception as e:
        log.error(f"Failed to read artifact '{artifact_name}': {e}", exc_info=True)
        return f"Error reading file: {e}"


async def read_deck_spec(tool_context: ToolContext) -> dict[str, Any]:
    """
    Retrieves the current presentation plan (deck_spec) directly from session state.
    """
    log = get_logger("read_deck_spec")
    try:
        spec_dict = tool_context.state.get("current_deck_spec")
        if not spec_dict:
            return {
                "status": "Error",
                "message": "No active presentation plan found in session state. Please ensure an outline was generated.",
            }

        log.info("Successfully loaded DeckSpec from session state.")
        return {
            "status": "Success",
            "strategic_briefing": spec_dict.get("strategic_briefing"),
            "cover": spec_dict.get("cover"),
            "slides": spec_dict.get("slides", []),
            "closing_title": spec_dict.get("closing_title"),
        }
    except Exception as e:
        log.error(f"Failed to read deck_spec: {e}", exc_info=True)
        return {
            "status": "Error",
            "message": f"Internal failure while reading plan from state: {e}",
        }