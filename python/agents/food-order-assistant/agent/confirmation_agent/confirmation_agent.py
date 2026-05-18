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


from typing import Union

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types
from pydantic import BaseModel, ConfigDict, Field

from .. import constants

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutputSchema(BaseModel):
  """Output schema for the agent."""
  agent_response: str = Field(description="Assistant response to the user")
  order_confirmed: str = Field(description="true, if the user has confirmed, false, if the user wants to change the order. unknown if the user didn't respond yet.")


class AfterModelCallback:
  def __call__(
    self,
    callback_context: CallbackContext,
    llm_response: LlmResponse,
  ):
    output = OutputSchema.model_validate_json(llm_response.content.parts[0].text)
    logger.info(f"Model output: {output}")

    state = callback_context.state
    if output.order_confirmed != "unknown":
      if output.order_confirmed == "true":
        state[constants.ORDER_STATUS] = constants.CONFIRMED
      else:
        state[constants.ORDER_STATUS] = constants.IN_PROGRESS

    llm_response.content = types.Content(
        role='model',
        parts=[types.Part(text=output.agent_response)],
    )
    return llm_response


class ConfirmationAgent(LlmAgent):

  def __init__(self, model: Union[str, BaseLlm], **kwargs):
    super().__init__(
      model=model,
      name='confirmation_agent',
      planner=BuiltInPlanner(
          thinking_config=types.ThinkingConfig(
            thinking_budget=0,
            include_thoughts=False
          )
      ),
      instruction="""
        You are confirmation_agent to help the user confirm the order.

        You provide the brief summary of the items in the cart and ask if the order is correct.
        If the user confirms the order, return an empty text for agent_response and set order_confirmed to true.
        If the user wants to change the order or asks for correction, set order_confirmed to false.

        Current cart: {current_order?}
        Order total: ${order_total?}

        <example>
          Cart: < a) 1 dave's #1: 2 tenders with fries>
          Output: {"agent_response": "Alright, <summary of items in cart and the total cost>. Would that be all for today?",
                   "order_confirmed": "unknown"}
        </example>
        <example>
          Cart: < a) 1 dave's #1: 2 tenders with fries>
          Output: {"agent_response": "Alright, <summary of items in cart and the total cost>. Would that be all for today?",
                   "order_confirmed": "unknown"}
          User: that's it
          Output: {"agent_response": "", "order_confirmed": "true"}
        </example>
        <example>
          Cart: < a) 1 dave's #1: 2 tenders with fries>
          Output: {"agent_response": "Alright, <summary of items in cart and the total cost>. Would that be all for today?",
                   "order_confirmed": "unknown"}
          User: no
          Output: {"agent_response": "", "order_confirmed": "false"}
        </example>
        <example>
          Cart: < a) 1 dave's #1: 2 tenders with fries>
          Output: {"agent_response": "Alright, <summary of items in cart and the total cost>. Would that be all for today?",
                   "order_confirmed": "unknown"}
          User: Say that again?
          Output: {"agent_response": "You ordered <summary of items in cart and the total cost>. Would that be all for today?",
                   "order_confirmed": "unknown"}
        </example>
      """,
      output_schema=OutputSchema,
      disallow_transfer_to_parent=True,
      disallow_transfer_to_peers=True,
      after_model_callback=AfterModelCallback(),
    )


def create_agent(llm: Union[str, BaseLlm]):
  return ConfirmationAgent(model=llm)
