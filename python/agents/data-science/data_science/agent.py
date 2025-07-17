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
import os
from datetime import date

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_artifacts
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from .prompts import return_instructions_root
#from .sub_agents import bqml_agent
from .sub_agents import alloydb_agent, bigquery_agent
from .sub_agents.alloydb.tools import \
    get_database_settings as get_alloydb_database_settings
#from .sub_agents import ds_agent
from .sub_agents.bigquery.tools import \
    get_database_settings as get_bq_database_settings

#from .tools import call_alloydb_agent, call_bigquery_agent, call_ds_agent

date_today = date.today()


def init_database_settings(callback_context: CallbackContext):
    """Initialize database settings on first use."""

    if "database_settings" in callback_context.state:
        return

    db_settings = {
        "bigquery": get_bq_database_settings(),
        "alloydb": get_alloydb_database_settings()
    }
    bq_schema = db_settings["bigquery"]["schema"]
    alloydb_schema = db_settings["alloydb"]["schema"]

    callback_context.state["database_settings"] = db_settings

    callback_context._invocation_context.agent.instruction = (
        return_instructions_root()
        + f"""

<SCHEMA DEFINITIONS>
<BIGQUERY>
--------- The BigQuery schema of the relevant database with a few sample rows. ---------
{bq_schema}

</BIGQUERY>

<ALLOYDB>
--------- The AlloyDB schema of the relevant database. ---------
{alloydb_schema}

</ALLOYDB>
</SCHEMA DEFINITIONS>

    """
        )


root_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL"),
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
        AgentTool(
            agent=bigquery_agent,
            skip_summarization=True,
        ),
        AgentTool(
            agent = alloydb_agent,
            skip_summarization=True,
        ),
#        AgentTool(
#            name = "ds_tool",
#            agent = ds_agent,
#            output_key = "ds_agent_output",
#            skip_summarization=True,
#        ),
        load_artifacts,
    ],
    before_agent_callback=init_database_settings,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
