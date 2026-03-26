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

"""Specialist agent for performing web research using Google Search."""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool, google_search

from ...shared_libraries.config import ROOT_MODEL
from .prompt import GOOGLE_RESEARCH_INSTRUCTION

# Define the research specialist agent
research_agent = LlmAgent(
    model=ROOT_MODEL,
    name="research_specialist",
    description="A specialist agent that performs web searches using Google Search to gather up-to-date information, facts, and statistics for presentation content.",
    instruction=GOOGLE_RESEARCH_INSTRUCTION,
    tools=[google_search],
)

# Create the final tool that the main agent will use
google_research_tool = AgentTool(agent=research_agent)
