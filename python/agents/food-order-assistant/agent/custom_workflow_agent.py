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


import logging

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from typing import AsyncGenerator, Callable
from typing_extensions import override


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_MAX_ITERATIONS = 30  # To prevent infinite loop.
_DONE_AGENT = "done"  # Special agent name when the workflow is done.

class CustomWorkflowAgent(BaseAgent):
    """
    This agent orchestrates a list of sub LLM agents to run based on the session state.
    """

    agent_map: dict[str, LlmAgent] = {}
    get_next_agent: Callable
    step: int = 0

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        agent_map: dict[str, LlmAgent],
        get_next_agent: Callable,
    ):
        """
        Initializes the OrderFlowAgent.
        """
        sub_agents_list = list(agent_map.values())

        super().__init__(
            name=name,
            agent_map=agent_map,
            get_next_agent=get_next_agent,
            sub_agents=sub_agents_list,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Implements the custom orchestration logic for the order workflow.
        """
        session_state = ctx.session.state
        selected_agent_name = self.get_next_agent(session_state)
        while self.step < _MAX_ITERATIONS:
            self.step += 1
            
            logger.info(f"Step {self.step}: selected_agent -- {selected_agent_name}")
            selected_agent = self.agent_map.get(selected_agent_name, None)
            if selected_agent == _DONE_AGENT:
                # We are done.
                logger.info("Final state: {session_state}")
                return

            if not selected_agent:
                logger.error(f"ERROR: Unknown agent name: {selected_agent_name}")
                return
                                 
            async for event in selected_agent.run_async(ctx):
                yield event
            next_agent = self.get_next_agent(session_state)
            if next_agent == selected_agent_name:
                # Exits to get another user input.
                return
            selected_agent_name = next_agent
