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
import os

from google.genai import Client

from typing import Any

from . import constants, custom_workflow_agent
from .confirmation_agent import confirmation_agent
from .menu_agent import menu_agent
from .preorder_agent import preorder_agent as preorder_agent
from .user_info_agent import user_info_agent


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_next_agent(session_state: dict[str, Any]) -> str:
    """
    Determines the next agent to run based on the session state.
    """
    logger.info(f"State: {session_state}")

    if session_state.get(constants.ORDER_TYPE, "UNKNOWN") == "UNKNOWN":
        return constants.PREORDER_AGENT
    order_status = session_state.get(constants.ORDER_STATUS, "UNKNOWN")
    if order_status in set(['UNKNOWN', constants.IN_PROGRESS]):
        return constants.MENU_AGENT
    if order_status == constants.FINISHED:
        return constants.CONFIRMATION_AGENT
    if order_status == constants.CONFIRMED and not session_state.get(constants.NAME_FOR_ORDER, None):
        return constants.USER_INFO_AGENT
    if order_status == constants.GETTING_USER_INFO:
        return constants.USER_INFO_AGENT
    return constants.DONE


def create_agent(genai_client: Client):
    # Update models as needed.
    preorder_agent_model = "gemini-2.5-flash"
    menu_agent_model = "gemini-2.5-flash"
    confirmation_agent_model = "gemini-2.5-flash"
    user_info_agent_model = "gemini-2.5-flash"

    logger.info(f"## preorder_agent: {preorder_agent_model}")
    logger.info(f"## menu_agent: {menu_agent_model}")
    logger.info(f"## confirmation_agent: {confirmation_agent_model}")
    logger.info(f"## user_info_agent: {user_info_agent_model}")

    return custom_workflow_agent.CustomWorkflowAgent(
        name="OrderFlowAgent",
        agent_map = {
            "preorder_agent": preorder_agent.create_agent(preorder_agent_model),
            "menu_agent": menu_agent.create_agent(menu_agent_model),
            "confirmation_agent": confirmation_agent.create_agent(confirmation_agent_model),
            "user_info_agent": user_info_agent.create_agent(user_info_agent_model),
        },
        get_next_agent=get_next_agent,
    )