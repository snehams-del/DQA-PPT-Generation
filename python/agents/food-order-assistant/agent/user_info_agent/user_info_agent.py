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


from typing import Any, Optional, Union

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types
from pydantic import BaseModel, Field

from .. import constants

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutputSchema(BaseModel):
  """Output schema for the agent."""
  agent_response: str = Field(description="Assistant response to the user. Empty if the user needs to update their order.")
  name_for_order: str = Field(description="Name of the customer for this order.")
  requires_order_update: bool = Field(description="True if the user needs to update their order. False otherwise.")


class BeforeModelCallback:
  def __init__(self, agent):
    self.agent = agent

  def __call__(
    self,
    callback_context: CallbackContext,
    llm_request: LlmRequest,
  ) -> Optional[LlmResponse]:
    """Asks for the user's name if not provided."""
    state = callback_context.state
    if state[constants.ORDER_STATUS] == constants.CONFIRMED:
      if state.get(constants.NAME_FOR_ORDER, None):
        agent_response = f"Alright, {state[constants.NAME_FOR_ORDER]}! Give me one second as I place the order."
      else:
        agent_response = "Can I have a name for this order, please?"
        state[constants.ORDER_STATUS] = constants.GETTING_USER_INFO
      llm_response = LlmResponse()
      llm_response.content = types.Content(
          role='model',
          parts=[types.Part(text=agent_response)],
      )
      return llm_response
    return None


class AfterModelCallback:
  def __init__(self, agent: Any):
    self.agent = agent

  def __call__(
    self,
    callback_context: CallbackContext,
    llm_response: LlmResponse,
  ):
    output = OutputSchema.model_validate_json(llm_response.content.parts[0].text)

    state = callback_context.state
    if output.requires_order_update:
      state[constants.ORDER_STATUS] = constants.IN_PROGRESS
      output.agent_response = ""
    else:
      state[constants.NAME_FOR_ORDER] = output.name_for_order

    llm_response.content = types.Content(
        role='model',
        parts=[types.Part(text=output.agent_response)],
    )
    return llm_response


class UserInfoAgent(LlmAgent):

  def __init__(self, model: Union[str, BaseLlm], **kwargs):
    super().__init__(
      model=model,
      planner=BuiltInPlanner(
          thinking_config=types.ThinkingConfig(
            thinking_budget=0,
            include_thoughts=False
          )
      ),
      name='user_info_agent',
      instruction="""
        You are an assistant to get the user name.
        If the order status is CONFIRMED, and you don't know the user name, ask the user for their name.
        Once the user provides their name, respond with "Alright, <their name>! Give me one second as I place the order." and populate the name_for_order field in the response.
        
        order status: {order_status?}

        <example>
          Assistant: Can I have a name for this order, please?
          User: john
          Output: {"agent_response": "Alright, john! Give me one second as I place the order.", "name_for_user": "john", "requires_order_update": false}
        </example>
        <example>
          Assistant: Can I have a name for this order, please?
          User: Oh, actually, can I remove the shake?
          Output: {"agent_response": "", "name_for_user": "", "requires_order_update": true})
        </example>
        <example>
          Assistant: Can I have a name for this order, please?
          User: david, by the way, can I remove the shake?
          Output: {"agent_response": "", "name_for_user": "david", "requires_order_update": true})
        </example>

        Do not speak about the agent transfer.
      """,
      output_schema=OutputSchema,
      disallow_transfer_to_parent=True,
      disallow_transfer_to_peers=True,
      before_model_callback=BeforeModelCallback(agent=self),
      after_model_callback=AfterModelCallback(agent=self),
  )


def create_agent(llm: Union[str, BaseLlm]):
  return UserInfoAgent(llm)
