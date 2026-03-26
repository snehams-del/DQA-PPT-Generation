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

"""Specialist agent for performing deep research using the Deep Research engine."""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

from ...shared_libraries.config import ROOT_MODEL
from .prompt import DEEP_RESEARCH_INSTRUCTION
from .tools.deep_research_tool import deep_research_tool

# Define the research specialist agent
# This agent acts as a coordinator, prompting the Deep Research tool effectively.
research_agent = LlmAgent(
    model=ROOT_MODEL,
    name="deep_research_specialist",
    description="A specialist agent that performs deep web research to gather comprehensive information, statistics, and verifiable facts.",
    instruction=DEEP_RESEARCH_INSTRUCTION,
    tools=[deep_research_tool],
)

# Create the final AgentTool that the main orchestrator agent will use
deep_research_agent_tool = AgentTool(agent=research_agent)
