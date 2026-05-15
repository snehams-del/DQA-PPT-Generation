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
from .prompt import SUMMARIZE_COMPARATIVE_ANALYSIS
from ....config import config
from google.genai import types

# LLM Agent for execution of the bigquery sqls
summarizer_agent = LlmAgent(
    name="summarizer_agent",
    model=config.summarizer_model,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
        max_output_tokens=config.max_output_tokens,
        seed=config.seed,
    ),
    description=f"This agent is responsible for summarising the comparative analysis of the original product with competitor product.",
    instruction=SUMMARIZE_COMPARATIVE_ANALYSIS,
    output_key="query_summary_output",
)
