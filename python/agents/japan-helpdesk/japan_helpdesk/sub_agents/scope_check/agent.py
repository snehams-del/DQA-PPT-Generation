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

"""Scope check agent for determining if queries are within supported scope."""

from google.adk.agents import Agent
from japan_helpdesk.shared_libraries.types import ScopeCheckResult, json_response_config
from japan_helpdesk.sub_agents.scope_check import prompt


scope_check_agent = Agent(
    model="gemini-2.5-flash",
    name="scope_check_agent",
    description="Determines if user queries are within the supported scope for Japan legal/administrative helpdesk",
    instruction=prompt.SCOPE_CHECK_AGENT_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=ScopeCheckResult,
    output_key="scope_check",
    generate_content_config=json_response_config,
)
