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

"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""
import base64
import json
import logging
import os
from datetime import date

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
#from google.adk.tools import load_artifacts
from google.genai import types
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from .prompts import return_instructions_root
from .sub_agents.alloydb.tools import \
    get_database_settings as get_alloydb_database_settings
from .sub_agents.bigquery.tools import \
    get_database_settings as get_bq_database_settings
from .tools import (call_alloydb_agent, call_analytics_agent,
                    call_bigquery_agent)

# Configure Weave endpoint and authentication
WANDB_BASE_URL = "https://trace.wandb.ai"
PROJECT_ID = os.getenv("WANDB_PROJECT_ID")
OTEL_EXPORTER_OTLP_ENDPOINT = f"{WANDB_BASE_URL}/otel/v1/traces"

# Set up authentication
WANDB_API_KEY = os.getenv("WANDB_API_KEY")
AUTH = base64.b64encode(f"api:{WANDB_API_KEY}".encode()).decode()

OTEL_EXPORTER_OTLP_HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "project_id": PROJECT_ID,
}

# Create the OTLP span exporter with endpoint and headers
exporter = OTLPSpanExporter(
    endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
    headers=OTEL_EXPORTER_OTLP_HEADERS,
)

# Create a tracer provider and add the exporter
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

# Set the global tracer provider BEFORE importing/using ADK
trace.set_tracer_provider(tracer_provider)


date_today = date.today()

# Set up logging
# Note this level can be overridden by adk web on the command line;
# e.g. running `adk web --log_level DEBUG` or `adk web -v`
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database_settings(callback_context: CallbackContext):
    """Initialize database settings on first use."""

    if "database_settings" in callback_context.state:
        return

    db_settings = {
        "bigquery": get_bq_database_settings(),
        "alloydb": get_alloydb_database_settings(),
        "cross_dataset_relations": ""
    }

    CROSS_DATASET_RELATIONS_DEFS = os.getenv("CROSS_DATASET_RELATIONS_DEFS",
        "")
    if CROSS_DATASET_RELATIONS_DEFS:
        with open(CROSS_DATASET_RELATIONS_DEFS, "r", encoding="utf-8") as f:
            db_settings["cross_dataset_relations"] = json.load(f)

    bq_schema = db_settings["bigquery"]["schema"]
    alloydb_schema = db_settings["alloydb"]["schema"]
    callback_context.state["database_settings"] = db_settings

    callback_context._invocation_context.agent.instruction = (
        return_instructions_root()
        + f"""

<DATASET DEFINITIONS>
<BIGQUERY>
<DESCRIPTION>
This data warehouse is used to analyze everything to run the business better.
It contains historical data from the AlloyDB database, enriched with other
large-scale datasets. The data is somewhat denormalized (flattened) into wide
tables to make querying faster and simpler.
For multi-year data, it includes data for the year 2024-2025.
</DESCRIPTION>
<SCHEMA>
--------- The BigQuery schema of the relevant database with a few sample rows. ---------
{bq_schema}
</SCHEMA>
</BIGQUERY>

<ALLOYDB>
<DESCRIPTION>
This database runs the airline's booking engine and flight management system. It
needs to be fast, reliable, and consistent for tasks like selling a ticket,
assigning a seat, or updating a flight's status.
The schema is normalized to ensure data integrity and avoid redundancy.
It only includes data from the year 2025.
</DESCRIPTION>
<SCHEMA>
--------- The AlloyDB schema of the relevant database. ---------
{alloydb_schema}
</SCHEMA>
</ALLOYDB>

<CROSS_DATASET_RELATIONS>
--------- The cross dataset relations between BigQuery and AlloyDB. ---------
{db_settings["cross_dataset_relations"]}

</CROSS_DATASET_RELATIONS>
</SCHEMA DEFINITIONS>

    """
        )


root_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", ""),
    name="data_science_root_agent",
    instruction=return_instructions_root(),
    global_instruction=(
        f"""
        You are a Data Science and Data Analytics Multi Agent System.
        Todays date: {date_today}
        """
    ),
    #sub_agents=[bqml_agent],
    tools=[ # type: ignore
        call_bigquery_agent,
        call_alloydb_agent,
        call_analytics_agent,
        #load_artifacts,
    ],
    before_agent_callback=init_database_settings,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
