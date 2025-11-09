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

from google.adk.agents import Agent, LoopAgent
from google.adk.tools import ToolContext
import json

from ...shared_libraries import constants
from . import prompt


# --------------------------------------------------------------------------
# Tool: stops the loop when the critic approves the comparison
# --------------------------------------------------------------------------
def stop_comparison(tool_context: ToolContext):
    """
    Call this ONLY when the critic agent declares that the comparison is satisfactory.
    This tool escalates the state to end the loop gracefully.
    """
    print(f"✅ [Tool Call] Comparison approved. Ending loop. State: {json.dumps(tool_context.state.to_dict())}")
    tool_context.actions.escalate = True
    return {"result": "Comparison validated and loop terminated."}


# --------------------------------------------------------------------------
# Agent 1 – Comparison generator: creates the first or refined comparison report
# --------------------------------------------------------------------------
comparison_generator_agent = Agent(
    model=constants.MODEL,
    name="comparison_generator_agent",
    description="Agent that generates comparison reports between brand and competitor titles.",
    instruction=prompt.COMPARISON_AGENT_PROMPT,
    output_key="comparison_report",
)

# --------------------------------------------------------------------------
# Agent 2 – Critic agent: analyses and evaluates the comparison report
# --------------------------------------------------------------------------
comparison_critic_agent = Agent(
    model=constants.MODEL,
    name="comparison_critic_agent",
    description="Agent that critiques comparison quality and suggests improvements.",
    instruction=prompt.COMPARISON_CRITIC_AGENT_PROMPT,
    tools=[stop_comparison],  # allows calling stop_comparison when satisfied
    output_key="critique",
)

# --------------------------------------------------------------------------
# Loop agent – runs generator + critic iteratively until the critic approves
# --------------------------------------------------------------------------
comparison_review_loop = LoopAgent(
    name="comparison_review_loop",
    sub_agents=[comparison_generator_agent, comparison_critic_agent],
    max_iterations=5,  # limit to avoid infinite loops
)

# --------------------------------------------------------------------------
# Root agent – orchestrates the comparison workflow
# --------------------------------------------------------------------------
comparison_root_agent = Agent(
    model=constants.MODEL,
    name="comparison_root_agent",
    description="Main agent to perform product title comparison and refinement loop.",
    instruction=prompt.COMPARISON_ROOT_AGENT_PROMPT,
    sub_agents=[comparison_review_loop],
)