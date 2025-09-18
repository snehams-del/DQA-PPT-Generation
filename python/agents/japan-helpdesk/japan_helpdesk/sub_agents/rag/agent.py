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

"""RAG agent for retrieving and synthesizing legal information."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search
from japan_helpdesk.shared_libraries.types import LegalResponse, json_response_config
from japan_helpdesk.sub_agents.rag import prompt


# Create search grounding agent for retrieving official information
_legal_search_agent = Agent(
    model="gemini-2.5-flash",
    name="legal_info_search",
    description="An agent providing Google-search grounding capability for Japanese legal and administrative information",
    instruction="""
    Answer the user's question directly using google_search grounding tool. Focus on official Japanese government sources, 
    legal procedures, and administrative requirements for foreigners in Japan.
    Provide accurate, factual information from reliable sources. Prioritize official government websites (.go.jp domains),
    immigration offices, city halls, and other authoritative sources.
    Be concise but comprehensive in your response.
    """,
    tools=[google_search],
)

# Create search grounding tool
legal_search_tool = AgentTool(agent=_legal_search_agent)

rag_agent = Agent(
    model="gemini-2.5-flash",
    name="rag_agent", 
    description="Retrieves and synthesizes legal and administrative information for foreigners in Japan",
    instruction=prompt.RAG_AGENT_INSTR,
    tools=[legal_search_tool],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=LegalResponse,
    output_key="legal_response",
    generate_content_config=json_response_config,
)
