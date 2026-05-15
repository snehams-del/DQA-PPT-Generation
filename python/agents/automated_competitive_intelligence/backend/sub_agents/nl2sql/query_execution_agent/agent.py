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

from google.adk.agents import LlmAgent
from .prompt import QUERY_EXECUTION_INSTRUCTION_STR
from ....tools.big_query_tools import bigquery_execution_tool
from ....config import config
from google.genai import types

# LLM Agent for execution of the bigquery sqls
query_execution_agent = LlmAgent(
    name="query_execution_agent",
    model=config.flash_model,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
        max_output_tokens=config.max_output_tokens,
        seed=config.seed,
    ),
    description=f"This agent is responsible for execution of queries in the bigquery and present the result as markdown table",
    instruction=QUERY_EXECUTION_INSTRUCTION_STR,
    tools=[bigquery_execution_tool],
    output_key="query_execution_output",
)
