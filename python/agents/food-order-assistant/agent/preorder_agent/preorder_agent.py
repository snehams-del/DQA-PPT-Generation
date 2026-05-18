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

from enum import Enum
from typing import Any, Union

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types, Client
from pydantic import BaseModel, ConfigDict, Field

from .. import constants

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderType(Enum):
  TO_GO = "to-go order"
  FOR_HERE = "for-here order"
  UNKNOWN = "unknown"


class OutputSchema(BaseModel):
  """Output schema for the agent."""
  agent_response: str = Field(description="Assistant response to the user")
  order_type: OrderType = Field(description="TO_GO or FOR_HERE if the user answer the to-go/for-here question. UNKNOWN otherwise")
  user_started_order: bool = Field(description="True, if the user started to order. False otherwise")


class AfterModelCallback:
  def __init__(self, agent: Any):
    self.agent = agent

  def __call__(
    self,
    callback_context: CallbackContext,
    llm_response: LlmResponse,
  ):
    output = OutputSchema.model_validate_json(llm_response.content.parts[0].text)
    logger.info(f"Model output: {output}")

    if output.order_type != OrderType.UNKNOWN:
      callback_context.state[constants.ORDER_TYPE] = output.order_type.name

    llm_response.content = types.Content(
        role='model',
        parts=[types.Part(text=output.agent_response)],
    )
    return llm_response


class PreorderAgent(LlmAgent):

  def __init__(self, model: Union[str, BaseLlm], **kwargs):
    super().__init__(
      model=model,
      planner=BuiltInPlanner(
          thinking_config=types.ThinkingConfig(
            thinking_budget=0,
            include_thoughts=False
          )
      ),
      name='preorder_agent',
      instruction="""
        You are an agent to ask the customer if the order is for to-go or for here.
        If the user answers, populate the order_type field in the response and an empty agent_response.
        If the user doesn't answer, politely ask the user to answer the to-go/for-here question.
      """,
      output_schema=OutputSchema,
      disallow_transfer_to_parent=True,
      disallow_transfer_to_peers=True,
      after_model_callback=AfterModelCallback(agent=self),
    )


def create_agent(llm: Union[str, BaseLlm]):
  return PreorderAgent(model=llm)