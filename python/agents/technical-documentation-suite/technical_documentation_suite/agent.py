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

"""Technical Documentation Suite - Main Orchestrator Agent"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from technical_documentation_suite import prompt
from technical_documentation_suite.sub_agents.code_analyzer import code_analyzer
from technical_documentation_suite.sub_agents.documentation_writer import documentation_writer
from technical_documentation_suite.sub_agents.diagram_generator import diagram_generator
from technical_documentation_suite.sub_agents.translation_agent import translation_agent
from technical_documentation_suite.sub_agents.quality_assurance import quality_assurance
from technical_documentation_suite.sub_agents.feedback_collector import feedback_collector


# Create agent tools for each specialized agent
code_analyzer_tool = AgentTool(agent=code_analyzer)
documentation_writer_tool = AgentTool(agent=documentation_writer)
diagram_generator_tool = AgentTool(agent=diagram_generator)
translation_agent_tool = AgentTool(agent=translation_agent)
quality_assurance_tool = AgentTool(agent=quality_assurance)
feedback_collector_tool = AgentTool(agent=feedback_collector)


# Main orchestrator agent
root_agent = Agent(
    model="gemini-2.5-flash",
    name="technical_documentation_orchestrator",
    description="Advanced multi-agent orchestrator for comprehensive technical documentation generation",
    instruction=prompt.ROOT_AGENT_INSTR,
    tools=[
        code_analyzer_tool,
        documentation_writer_tool,
        diagram_generator_tool,
        translation_agent_tool,
        quality_assurance_tool,
        feedback_collector_tool,
    ],
) 