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

"""Main Japan Helpdesk agent using Agent Development Kit."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from japan_helpdesk import prompt
from japan_helpdesk.sub_agents.scope_check.agent import scope_check_agent
from japan_helpdesk.sub_agents.rag.agent import rag_agent
from japan_helpdesk.sub_agents.legal_advice_detector.agent import legal_advice_detector_agent


root_agent = Agent(
    model="gemini-2.5-flash",
    name="japan_helpdesk_root_agent",
    description="AI-powered helpdesk for foreigners in Japan providing legal and administrative guidance",
    instruction=prompt.ROOT_AGENT_INSTR,
    tools=[
        AgentTool(agent=scope_check_agent),
        AgentTool(agent=rag_agent),
        AgentTool(agent=legal_advice_detector_agent),
    ],
)
