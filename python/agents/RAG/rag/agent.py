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

import os
import uuid
import warnings
from typing import Any

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
    VertexAiRagRetrieval,
)
from openinference.instrumentation import using_session
from vertexai.preview import rag

from rag.tracing import instrument_adk_with_arize

from .prompts import return_instructions_root

load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
if not project_id:
    _, detected_project_id = google.auth.default()
    project_id = detected_project_id
os.environ.setdefault(
    "GOOGLE_CLOUD_PROJECT", project_id or "your-default-project"
)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

instrument_adk_with_arize()

# Initialize tools list
tools: list[Any] = []

# Only add RAG retrieval tool if RAG_CORPUS is configured
rag_corpus = os.environ.get("RAG_CORPUS")
gcp_project = os.environ.get("GOOGLE_CLOUD_PROJECT")

if rag_corpus and gcp_project and not rag_corpus.startswith(
    f"projects/{gcp_project}/"
):
    warnings.warn(
        "RAG_CORPUS project does not match GOOGLE_CLOUD_PROJECT. "
        "Skipping RAG retrieval tool to avoid permission errors.",
        stacklevel=2,
    )
    rag_corpus = None

if rag_corpus:
    ask_vertex_retrieval = VertexAiRagRetrieval(
        name="retrieve_rag_documentation",
        description=(
            "Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,"
        ),
        rag_resources=[
            rag.RagResource(
                # please fill in your own rag corpus
                # here is a sample rag corpus for testing purpose
                # e.g. projects/123/locations/us-central1/ragCorpora/456
                rag_corpus=rag_corpus
            )
        ],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )
    tools.append(ask_vertex_retrieval)

with using_session(session_id=str(uuid.uuid4())):
    root_agent = Agent(
        model="gemini-2.5-flash",
        name="ask_rag_agent",
        instruction=return_instructions_root(),
        tools=tools,
    )
