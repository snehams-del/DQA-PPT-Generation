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

"""Main file for the Guardian agent."""

import asyncio
import os

from absl import app
from google.adk import runners
from google.adk.agents import llm_agent
from google.genai import types

from .plugins import agent_as_a_judge, model_armor
from . import tools
from . import prompts
from . import util


Agent = llm_agent.LlmAgent
LlmAsAJudge = agent_as_a_judge.LlmAsAJudge
ModelArmorSafetyFilter = model_armor.ModelArmorSafetyFilterPlugin
InMemoryRunner = runners.InMemoryRunner


os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
os.environ["GOOGLE_CLOUD_PROJECT"] = "YOUR_PROJECT_ID_HERE"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_API_KEY"] = "YOUR_VALUE_HERE"
os.environ["MODEL_ARMOR_TEMPLATE_ID"] = "YOUR_TEMPLATE_ID_HERE"

USER_ID = "user"
APP_NAME = "test_app_with_plugin"
AGENT_MODEL = "gemini-2.5-flash"

sub_agent = Agent(
    model=AGENT_MODEL,
    instruction=prompts.SUB_AGENT_SI,
    name="sub_agent",
    tools=[tools.fib_tool, tools.io_bound_tool],
)

root_agent = Agent(
    model=AGENT_MODEL,
    instruction=prompts.ROOT_AGENT_SI,
    name="main_agent",
    tools=[tools.short_sum_tool, tools.long_sum_tool],
    sub_agents=[sub_agent],
)


async def main():
    """Runs a multiturn conversation with the agent and the attached plugin."""

    runner = InMemoryRunner(
        agent=root_agent,
        app_name=APP_NAME,
        plugins=[
            # LlmAsAJudge(),
            # ModelArmorSafetyFilter(
            #     project_id="YOUR_PROJECT_ID_HERE",
            #     location_id="us-central1",
            #     template_id="YOUR_TEMPLATE_ID_HERE",
            # ),
        ],
    )
    session = await runner.session_service.create_session(
        user_id=USER_ID,
        app_name=APP_NAME,
    )

    user_input = input(f"[{USER_ID}]: ")

    while user_input != "exit":
        author, message = await util.run_prompt(
            USER_ID,
            APP_NAME,
            runner,
            types.Content(role="user", parts=[types.Part.from_text(text=user_input)]),
            session_id=session.id,
        )
        print(f"[{author}]: {message}")

        user_input = input(f"[{USER_ID}]: ")


if __name__ == "__main__":
    app.run(lambda _: asyncio.run(main()))
