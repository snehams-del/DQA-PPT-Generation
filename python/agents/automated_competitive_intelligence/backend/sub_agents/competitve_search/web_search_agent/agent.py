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

"""websearch_agent for finding competitive products using search tools."""

from google.adk import Agent
from google.adk.tools import google_search
from ....config import config
from .prompt import WEBSEARCH_PROMPT
from google.genai import types

# Dynamically apply Domain-Aware search constraints if configured
actual_prompt = WEBSEARCH_PROMPT
if config.domain_search_targets:
    sites = " OR ".join([f"site:{site}" for site in config.domain_search_targets])
    domain_rules = f"\nCRITICAL SEARCH RULE: You MUST restrict your Google Search operations exclusively to the following highly trusted domains for the '{config.industry_domain}' industry: {', '.join(config.domain_search_targets)}. Achieve this by appending exactly `{sites}` to your generated Google Search queries. NEVER search on generic consumer sites like Amazon or Flipkart.\n"
    actual_prompt += domain_rules

websearch_agent = Agent(
    model=config.extractor_model,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
        max_output_tokens=config.max_output_tokens,
        seed=config.seed,
    ),
    name="websearch_agent",
    instruction=actual_prompt,
    output_key="query_competitor_specs_output",
    tools=[google_search],
)
