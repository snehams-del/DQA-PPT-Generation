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
from .prompt import EXTRACT_DATASHEET_URLS_PROMPT
from ....config import config
from google.genai import types

# LLM Agent for execution of the bigquery sqls
extract_datasheet_url_agent = LlmAgent(
    name="extract_datasheet_url_agent",
    model=config.nl2sql_model,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
        max_output_tokens=config.max_output_tokens,
        seed=config.seed,
    ),
    description=f"This agent is responsible for extracting the url from the given query execution output",
    instruction=EXTRACT_DATASHEET_URLS_PROMPT,
    output_key="query_extract_datasheet_output",
)
