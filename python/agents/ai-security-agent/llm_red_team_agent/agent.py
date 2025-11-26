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

from google.adk.agents import LlmAgent
from google.genai import types

from .config import config
from .tools import run_complete_security_scan

ATOMIC_AGENT_PROMPT = """
You are an AI Security Manager.
Your ONLY job is to use the `run_complete_security_scan` tool to test the system.

When a user gives you a vulnerability category:
1. Call `run_complete_security_scan` immediately.
2. Output the result provided by the tool.
3. Do not add your own commentary.
"""

root_agent = LlmAgent(
    name="security_orchestrator",
    model=config.critic_model,
    instruction=ATOMIC_AGENT_PROMPT,
    tools=[run_complete_security_scan],
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
)
