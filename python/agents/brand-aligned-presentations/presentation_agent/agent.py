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

import os
import google.auth

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, VertexAiSessionService

from presentation_agent.prompt import final_instruction

from presentation_agent.shared_libraries.config import (
    # NOTE: We intentionally do NOT use ENABLE_RAG / ENABLE_DEEP_RESEARCH here
    # because your requirement is "NO Google Search / NO external sourcing".
    GCS_BUCKET_NAME,
    ROOT_MODEL,
    get_gcs_client,
    get_logger,
    initialize_genai_client,
)

# Keep only the specialist tools that generate PPT structure/content
# (We remove google_research_tool, internal_knowledge_search_tool, deep_research_agent_tool)
from presentation_agent.sub_agents import (
    batch_slide_writer_tool,
    generate_outline_and_save_tool,
    outline_specialist_tool,
    slide_writer_specialist_tool,
)

from presentation_agent.tools import ALL_STANDARD_TOOLS


def _bucket_name(value: str) -> str:
    """
    Accepts:
      - "my-bucket"
      - "gs://my-bucket"
      - "gs://my-bucket/some/prefix"  (we will still extract the bucket name)
    Returns:
      - "my-bucket"
    """
    if not value:
        return ""
    v = value.strip()
    if v.startswith("gs://"):
        v = v[5:]
    # bucket is always before first "/"
    return v.split("/", 1)[0].strip()


# --- Set default envs from ADC (keeps CLI working out-of-the-box) ---
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
# IMPORTANT: "global" is not a Vertex AI region. Use a real region default.
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


class PresentationExpertApp:
    """
    Encapsulates the agent and runner for the Presentation Expert.
    This version is UPDATED for your new policy:
      - NO Google Search / NO Deep Research / NO RAG tools registered here.
      - Artifact output should go to OUTPUT_BUCKET (if provided), else fallback.
    """

    def __init__(self):
        initialize_genai_client()

        # --- Your new 3-bucket workflow (we only wire OUTPUT here for artifact storage) ---
        # TEMPLATE_BUCKET and DATA_BUCKET will be used later in tools/modules.
        output_bucket_env = os.getenv("OUTPUT_BUCKET", "").strip()
        output_bucket_name = _bucket_name(output_bucket_env)

        # Fallback to existing single bucket config if OUTPUT_BUCKET isn't set yet
        fallback_bucket_name = _bucket_name(GCS_BUCKET_NAME)

        artifact_bucket_name = output_bucket_name or fallback_bucket_name

        # 1) Tools: keep ONLY the PPT creation tools, NO research tools
        agent_tools = ALL_STANDARD_TOOLS + [
            outline_specialist_tool,
            generate_outline_and_save_tool,
            slide_writer_specialist_tool,
            batch_slide_writer_tool,
        ]

        # 2) Agent config
        # NOTE: final_instruction will be updated later (Step-3 prompt.py) for Excel-only grounding.
        agent_kwargs = {
            "model": ROOT_MODEL,
            "name": "presentation_expert_agent",
            "description": (
                "Creates professional PowerPoint presentations using a provided PPTX template "
                "and structured input data. External web search is disabled."
            ),
            "instruction": final_instruction,
            "tools": agent_tools,
        }

        # Instantiate the Main Agent
        self._agent = LlmAgent(**agent_kwargs)

        # 3) Artifact Service (prefer OUTPUT bucket)
        if artifact_bucket_name:
            try:
                gcs_client = get_gcs_client()
                if not gcs_client:
                    raise RuntimeError("GCS client could not be initialized.")

                # Validate bucket exists / access works
                gcs_client.get_bucket(artifact_bucket_name)

                artifact_service = GcsArtifactService(bucket_name=artifact_bucket_name)
                get_logger("agent").info(
                    f"Using GCS ArtifactService bucket: {artifact_bucket_name}"
                )
            except Exception as e:
                get_logger("agent").warning(f"Failed to initialize GcsArtifactService: {e}")
                get_logger("agent").warning("Falling back to InMemoryArtifactService.")
                artifact_service = InMemoryArtifactService()
        else:
            get_logger("agent").info("No artifact bucket configured. Using InMemoryArtifactService.")
            artifact_service = InMemoryArtifactService()

        # 4) Session Service (Persistent Vertex AI or local memory)
        is_local = os.getenv("LOCAL_DEV", "false").lower() == "true"
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        if not is_local and os.getenv("GOOGLE_CLOUD_PROJECT"):
            session_service = VertexAiSessionService(
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=location,
            )
            get_logger("agent").info(
                f"Using VertexAiSessionService (Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}, Location: {location})"
            )
        else:
            session_service = InMemorySessionService()
            get_logger("agent").info("Using InMemorySessionService for local development.")

        # 5) Runner
        self._runner = Runner(
            agent=self._agent,
            app_name="presentation_agent",
            session_service=session_service,
            artifact_service=artifact_service,
            memory_service=InMemoryMemoryService(),
        )
        get_logger("agent").info("PresentationExpertApp initialized (NO SEARCH / OUTPUT bucket artifacts).")


# Global instance ADK CLI will run
coordinator_wrapper = PresentationExpertApp()
root_agent = coordinator_wrapper._agent

# ADK App entrypoint
app = App(root_agent=root_agent, name="presentation_agent")