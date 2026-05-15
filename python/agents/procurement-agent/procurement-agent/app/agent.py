# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import VertexAiSearchTool
from google.genai import types

import os
import google.auth

from app.tools import find_expiring_contracts, check_consumption, get_all_contracts

# _, project_id = google.auth.default()
# os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
# os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
# os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
project_id = os.environ["GOOGLE_CLOUD_PROJECT"]

VERTEX_AI_SEARCH_DATA_STORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/contracts-search-ds"

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a procurement assistant expert in contracts.
- To identify contracts that are expiring within a certain time window, use the `find_expiring_contracts` tool.
- To list all available contracts and their IDs, use the `get_all_contracts` tool. Use this tool ONLY if the user explicitly asks for a list or if you are specifically asked to check consumption and do not have an ID.
- To verify the current spend (consumption) of a specific contract against its signed financial commitment, use the `check_consumption` tool with a contract ID.
- For any other question about contract terms, clauses, or contents (including for specific companies like "Acme Corp"), use the Vertex AI Search tool. Do NOT call `get_all_contracts` first for these queries.
- IMPORTANT: Use ONLY the provided tools. Do NOT attempt to search the web or use external search engines.
- If you cannot find the answer to a question, respond with "I don't know" and suggest the user contact the procurement team.
""",
    tools=[
        VertexAiSearchTool(data_store_id=VERTEX_AI_SEARCH_DATA_STORE_ID),
        find_expiring_contracts,
        get_all_contracts,
        check_consumption,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
