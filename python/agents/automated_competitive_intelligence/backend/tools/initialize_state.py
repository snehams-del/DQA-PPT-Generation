# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions.state import State
from google.adk.tools import ToolContext
import os
from .big_query_tools import bigquery_metdata_extraction_tool


def initialize_state_var(callback_context: CallbackContext):
    PROJECT = os.environ.get("PROJECT")
    BQ_LOCATION = os.environ.get("BQ_LOCATION")
    DATASET = os.environ.get("DATASET")
    callback_context.state["PROJECT"] = PROJECT
    callback_context.state["BQ_LOCATION"] = BQ_LOCATION
    callback_context.state["DATASET"] = DATASET
    
    agent_output_keys = [
        "query_understanding_output",
        "query_generation_output",
        "query_review_rewrite_output",
        "query_execution_output",
        "extract_datasheet_url_output",
        "specs_extractor_output",
        "web_search_output",
        "summarizer_output"
    ]
    for key in agent_output_keys:
        if key not in callback_context.state:
            callback_context.state[key] = ""
    
    # Lazy loading of bigquery metadata to avoid repeated execution
    if "bigquery_metadata" not in callback_context.state or not callback_context.state["bigquery_metadata"]:
        bigquery_metadata = bigquery_metdata_extraction_tool(
            PROJECT=PROJECT,
            # BQ_LOCATION=BQ_LOCATION, # REMOVED: BQ_LOCATION is not used/accepted by the tool
            DATASET=DATASET,
        )
        callback_context.state["bigquery_metadata"] = bigquery_metadata
