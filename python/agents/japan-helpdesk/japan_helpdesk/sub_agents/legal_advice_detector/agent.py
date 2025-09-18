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

"""Legal advice detector agent for ensuring responses don't constitute unauthorized practice of law."""

from google.adk.agents import Agent
from japan_helpdesk.shared_libraries.types import LegalAdviceCheck, json_response_config
from japan_helpdesk.sub_agents.legal_advice_detector import prompt


legal_advice_detector_agent = Agent(
    model="gemini-2.5-flash",
    name="legal_advice_detector_agent",
    description="Detects and flags responses that may constitute unauthorized practice of law",
    instruction=prompt.LEGAL_ADVICE_DETECTOR_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=LegalAdviceCheck,
    output_key="legal_advice_check",
    generate_content_config=json_response_config,
)
