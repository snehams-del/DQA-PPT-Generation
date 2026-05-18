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


import re
import yaml

from decimal import Decimal
from typing import Any, Union

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types
from pydantic import BaseModel, ConfigDict, Field

from .. import constants

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_MENU = """
name: Fresh Burger
items:
    - name: King Burger
      price: $9.99
    - name: Mini Burger
      price: $7.99
    - name: French Fries
      price: $2.99
    - name: Onion Rings
      price: $3.99
    - name: Large Fountain Drink
      price: $3.99
    - name: Medium Fountain Drink
      price: $2.99
"""

_AGENT_PROMPT = """
You are an agent who takes food orders from the customer at a restaurant.

# Instructions:
- The restuarant menu is provided in the <MENU> section below.
- If the customer orders an item outside the menu, respond "I'm sorry, we don't have <what the customer ordered>."
- If the customer orders a burger without specifying the type, ask a clarifying question if they want to order King burger or Mini burger.
- If the customer asks about the price of items or options, use the price in the menu.
- The <ORDER> section below contains the items in the current order.
- Pay attention to the conversation history, but avoid reprocessing the previous orders.
- If the conversation was transferred from another agent, and the user has no specific order request, ask the user what they want.

# MENU
{_MENU}

# ORDER
[{{current_order?}}]

# ORDER_STATUS: {{order_status?}}

# Examples
## The customer ordering burger.
CUSTOMER: Can I have a King burger?
ORDER: []
AGENT: {{
    "agent_response": "Sure, a King burger added. Anything else?",
    "order_update": "add [King Burger]"
}}
## The customer ordering additional food item.
CUSTOMER: Can I have another King burger?
ORDER: [King Burger]
AGENT: {{
    "agent_response": "Absolutely, another King burger added. Anything else?",
    "order_update": "add [King Burger]"
}}
## The customer removing a food item.
CUSTOMER: You know what, I'd like to remove the King burger.
ORDER: [King Burger, Mini Burger, French Fries]
AGENT: {{
    "agent_response": "Sure, I removed a King burger from the order. Anything else?",
    "order_update": "remove [King Burger]"
}}
## The customer ordering multiple items.
CUSTOMER: Can I have a mini burger and french fries?
ORDER: [King Burger]
AGENT: {{
    "agent_response": "Absolutely, mini burger and french fries added. Anything else?",
    "order_update": "add [Mini Burger, French Fries]"
}}
## The agent asking a clarifying question.
CUSTOMER: Can I have a burger?
ORDER: []
AGENT: {{
    "agent_response": "Which burger would you like? We have a King Burger and Mini Burger.",
    "order_update": ""
}}
## The customer finishing the order.
AGENT: {{
    "agent_response": "Sure, mini burger added. Anything else?",
    "order_update": "add [Mini Burger]"
}}
CUSTOMER: That's it.
ORDER: [French Fries, Mini Burger]
AGENT: {{
    "agent_response": "",
    "order_update": "",
    "order_finished": true
}}
"""

class OutputSchema(BaseModel):
  """Output schema for the agent."""
  agent_response: str = Field(description="Assistant response to the user")
  order_update: str = Field(description="Commands to add or remove an item. It has the form of <command> <item_id>.", default = "")
  order_finished: bool = Field(description="True if the user has finished placing their order. False otherwise.", default=False)


class FoodItem(BaseModel):
  """Represents a food item with its details."""
  name: str
  price: str = "$0.00"


class Menu(BaseModel):
  name: str
  items: list[FoodItem]


class AfterModelCallback:
  def __init__(self, agent: Any, price_map: dict):
    self.agent = agent
    self.price_map = price_map

  def __call__(
    self,
    callback_context: CallbackContext,
    llm_response: LlmResponse,
  ):
    output = OutputSchema.model_validate_json(llm_response.content.parts[0].text)
    logger.info(f"Model output: {output}")

    state = callback_context.state
    if output.order_finished:
      state[constants.ORDER_STATUS] = constants.FINISHED
    else:
      state[constants.ORDER_STATUS] = constants.IN_PROGRESS
    self.update_order(output.order_update, state)

    if output.order_finished:
      # Don't respond if the user is done ordering.
      llm_response.content = types.Content(
          role='model',
          parts=[types.Part(text="")],
      )
    else:
      llm_response.content = types.Content(
          role='model',
          parts=[types.Part(text=output.agent_response)],
      )

    return llm_response

  def update_order(self, order_update: str, state: dict):
    if not order_update:
      return

    if constants.CURRENT_ORDER not in state:
        state[constants.CURRENT_ORDER] = []
    if constants.ORDER_TOTAL not in state:
        state[constants.ORDER_TOTAL] = 0.0

    current_order = state[constants.CURRENT_ORDER]
    order_total = Decimal(str(state[constants.ORDER_TOTAL]))

    # The format can be "command [item1, item2, ...]" and can be repeated.
    # e.g. "add [Mini Burger] remove [King Burger]"
    command_blocks = re.findall(r'(\w+)\s+\[([^\]]*)\]', order_update)

    for command, items_str in command_blocks:
      items = [item.strip() for item in items_str.split(',') if item.strip()]
      if command == "add":
        current_order.extend(items)
        for item in items:
          order_total += self.price_map.get(item, Decimal(0))
      elif command == "remove":
        for item_to_remove in items:
          try:
            current_order.remove(item_to_remove)
            order_total -= self.price_map.get(item_to_remove, Decimal(0))
          except ValueError:
            logger.warning(
                "Attempted to remove item '%s' which is not in the order.",
                item_to_remove)
    
    state[constants.CURRENT_ORDER] = current_order
    state[constants.ORDER_TOTAL] = float(order_total)


class MenuAgent(LlmAgent):

  def __init__(self, model: Union[str, BaseLlm], **kwargs):
    # Build a price map.
    data = yaml.safe_load(_MENU)
    menu = Menu.model_validate(data)
    price_map = {}
    for item in menu.items:
      if item.price: # Check if price is not None or empty
        price_map[item.name] = Decimal(item.price.strip('$'))

    prompt = _AGENT_PROMPT.format(_MENU=_MENU)
    super().__init__(
      model=model,
      name='menu_agent',
      planner=BuiltInPlanner(
          thinking_config=types.ThinkingConfig(
            thinking_budget=0,
            include_thoughts=False
          )
      ),
      instruction=prompt,
      after_model_callback=AfterModelCallback(agent=self, price_map=price_map),
      output_schema=OutputSchema,
      disallow_transfer_to_parent=True,
      disallow_transfer_to_peers=True,
    )


def create_agent(llm: Union[str, BaseLlm]):
  return MenuAgent(model=llm)
