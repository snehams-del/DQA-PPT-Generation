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

"""BigQuery ML Agent."""
import os

from data_science.sub_agents.bigquery.agent import bigquery_agent
from data_science.sub_agents.bigquery.tools import \
    get_database_settings as get_bq_database_settings
from data_science.sub_agents.bqml.tools import (check_bq_models,
                                                execute_bqml_code,
                                                rag_response)
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .prompts import return_instructions_bqml


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    if "database_settings" in callback_context.state:
        return

    # setting up database settings in session.state
    db_settings = {
        "bigquery": get_bq_database_settings(),
    }
    callback_context.state["database_settings"] = db_settings

    schema = callback_context.state["database_settings"]["bigquery"]["schema"]

    callback_context._invocation_context.agent.instruction = (
        return_instructions_bqml()
        + f"""

   </BQML Reference for this query>

    <The BigQuery schema of the relevant data with a few sample rows>
    {schema}
    </The BigQuery schema of the relevant data with a few sample rows>
    """
    )


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""

    agent_tool = AgentTool(agent=bigquery_agent)
    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output


root_agent = Agent(
    model=os.getenv("BQML_AGENT_MODEL"),
    name="bq_ml_agent",
    instruction=return_instructions_bqml(),
    before_agent_callback=setup_before_agent_call,
    tools=[execute_bqml_code, check_bq_models, call_db_agent, rag_response],
)
