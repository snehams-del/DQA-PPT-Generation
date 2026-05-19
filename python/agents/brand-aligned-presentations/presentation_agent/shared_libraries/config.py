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

import logging
import os
import sys
from typing import Optional, Tuple

from google import genai
from google.cloud import storage

# ==============================================================================
# Logging
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

def get_logger(name: str) -> logging.Logger:
    """Returns a standard Python logger."""
    return logging.getLogger(name)

log = get_logger("config")


# ==============================================================================
# Helpers
# ==============================================================================
def _to_bool(val: Optional[str], default: bool = False) -> bool:
    """Parse common boolean env strings."""
    if val is None:
        return default
    v = str(val).strip().lower()
    return v in ("1", "true", "yes", "y", "on")

def _normalize_bucket_name(value: str) -> str:
    """
    Accepts:
      - bucket
      - gs://bucket
      - gs://bucket/some/prefix
      - bucket/some/prefix
    Returns:
      - bucket
    """
    if not value:
        return ""
    v = value.strip()
    if v.startswith("gs://"):
        v = v[5:]
    v = v.strip("/")

    # if a path/prefix is included, keep only the bucket root
    if "/" in v:
        v = v.split("/", 1)[0]
    return v

def _normalize_prefix(value: str) -> str:
    """Normalize optional 'folder' prefix inside a bucket."""
    if not value:
        return ""
    v = value.strip().strip("/")
    return f"{v}/" if v else ""

def _split_gs_uri(gs_uri: str) -> Tuple[str, str]:
    """Split gs://bucket/path into (bucket, path)."""
    if not gs_uri.startswith("gs://"):
        raise ValueError(f"Expected gs:// URI, got: {gs_uri}")
    no_scheme = gs_uri[5:]
    parts = no_scheme.split("/", 1)
    bucket = parts[0]
    path = parts[1] if len(parts) > 1 else ""
    return bucket, path


# ==============================================================================
# Exported Config Variables (read from environment)
# ==============================================================================

# Core project config
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Models
ROOT_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
IMAGE_GENERATION_MODEL = os.getenv("IMAGE_GENERATION_MODEL", "imagen-3.0-generate-002")

# Optional configs (kept for compatibility with original repo)
PROJECT_NUMBER = os.getenv("GOOGLE_CLOUD_PROJECT_NUMBER", "")
DATASTORE_ID = os.getenv("DATASTORE_ID", "")
DEFAULT_TEMPLATE_URI = os.getenv("DEFAULT_TEMPLATE_URI", "")
MODEL_ARMOR_TEMPLATE_ID = os.getenv("MODEL_ARMOR_TEMPLATE_ID")

# Research flags (we keep them for compatibility, but your agent.py no longer registers research tools)
ENABLE_RAG = _to_bool(os.getenv("ENABLE_RAG", "false"), default=False)
ENABLE_DEEP_RESEARCH = _to_bool(os.getenv("ENABLE_DEEP_RESEARCH", "false"), default=False)

# ==============================================================================
# NEW: Three-bucket workflow for DQA
# ==============================================================================
# These are the buckets you decided:
# - Template bucket: dqa_template_bucket
# - Data bucket: dqa_data_bucket
# - Output bucket: dqa_output_bucket
#
# You will set these in .env at runtime.
TEMPLATE_BUCKET = _normalize_bucket_name(os.getenv("TEMPLATE_BUCKET", ""))
DATA_BUCKET = _normalize_bucket_name(os.getenv("DATA_BUCKET", ""))
OUTPUT_BUCKET = _normalize_bucket_name(os.getenv("OUTPUT_BUCKET", ""))

# Optional prefixes inside each bucket (folder-like organization)
TEMPLATE_PREFIX = _normalize_prefix(os.getenv("TEMPLATE_PREFIX", ""))
DATA_PREFIX = _normalize_prefix(os.getenv("DATA_PREFIX", ""))
OUTPUT_PREFIX = _normalize_prefix(os.getenv("OUTPUT_PREFIX", ""))

# ==============================================================================
# Artifact storage bucket used by ADK ArtifactService
# ==============================================================================
# Backward compatible fallback:
# Original repo uses GCP_STAGING_BUCKET and GCS_BUCKET_NAME.
#
# For DQA:
# - We prefer OUTPUT_BUCKET for storing rendered PPT output artifacts,
#   but we still keep this variable because other modules may reference it.
_gcp_staging_bucket_env = os.getenv("GCP_STAGING_BUCKET", "")
GCS_BUCKET_NAME = _normalize_bucket_name(
    _gcp_staging_bucket_env
    or os.getenv("GCS_BUCKET_NAME", "")
    or (f"{GOOGLE_CLOUD_PROJECT}-staging-bucket" if GOOGLE_CLOUD_PROJECT else "")
)

# If OUTPUT_BUCKET is provided, it is typically the best default for artifacts
# because final decks should land in output storage.
ARTIFACT_BUCKET_NAME = OUTPUT_BUCKET or GCS_BUCKET_NAME


# ==============================================================================
# Common artifact filenames (kept for compatibility)
# ==============================================================================
PRESENTATION_SPEC_ARTIFACT = "presentation_spec.json"

# This was used for research; we keep the filename but in your new flow it should contain:
# "NO_EXTERNAL_SOURCES. Use ONLY Excel-provided data."
RESEARCH_SUMMARY_ARTIFACT = "research_summary.txt"


# ==============================================================================
# Global genai client (initialized via function)
# ==============================================================================
_genai_client = None


# ==============================================================================
# Client Initialization
# ==============================================================================
def initialize_genai_client():
    """Initializes and returns the global Vertex AI GenAI client."""
    global _genai_client
    if _genai_client is None:
        try:
            if not GOOGLE_CLOUD_PROJECT:
                log.warning(
                    "GOOGLE_CLOUD_PROJECT is not set. Vertex AI client init may fail."
                )
            _genai_client = genai.Client(
                vertexai=True,
                project=GOOGLE_CLOUD_PROJECT,
                location=GOOGLE_CLOUD_LOCATION,
            )
            log.info(
                f"Vertex AI client initialized for project '{GOOGLE_CLOUD_PROJECT}' in location '{GOOGLE_CLOUD_LOCATION}'."
            )
        except Exception as e:
            log.error(f"CRITICAL: Failed to initialize Vertex AI client: {e}")
            _genai_client = None
    return _genai_client


def get_gcs_client():
    """Initializes and returns a GCS client with robust project detection."""
    try:
        if GOOGLE_CLOUD_PROJECT:
            return storage.Client(project=GOOGLE_CLOUD_PROJECT)
        return storage.Client()
    except Exception as e:
        get_logger("get_gcs_client").error(f"Failed to initialize GCS client: {e}")
        get_logger("get_gcs_client").warning(
            "Ensure you are authenticated (e.g., `gcloud auth application-default login`)."
        )
        return None
