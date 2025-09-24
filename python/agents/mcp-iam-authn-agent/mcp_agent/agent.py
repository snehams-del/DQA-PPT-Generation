# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.models import LlmRequest
from google.adk.models import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.mcp_tool.mcp_session_manager import retry_on_closed_resource
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
import google.auth.transport.requests
from google.genai import types  # For types.Content
import google.oauth2.id_token
import jwt

toolset_cache = {}

import time

logging_level = os.environ.get("LOGGING_LEVEL", "INFO").upper()

logging.basicConfig(
    level=logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Making sure that there is always a valid token present
# Most optimized because the agent is called once per user interaction
# as opposed to a tool or an LLM call based callback.
def before_agent_cb(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
  # We have only one tool set otherwise you can iterate.
  mcp_toolset = callback_context._invocation_context.agent.tools[0]
  if mcp_toolset._tool_set_name not in toolset_cache:
    toolset_cache[mcp_toolset._tool_set_name] = {}

  # The following means the token was never added to the toolset
  # The headers reset every time so cannot check for headers.
  if "token_expiration_time" not in toolset_cache[mcp_toolset._tool_set_name]:
    logging.info(
        "Getting a token and adding to X-Serverless-Authorization header"
    )
    mcp_toolset._connection_params.headers = {}
    id_token = get_id_token(
        os.environ.get("MCP_AUDIENCE", "http://localhost:8080")
    )
    mcp_toolset._connection_params.headers["X-Serverless-Authorization"] = (
        f"Bearer {id_token}"
    )
    logging.debug(f"id_token => {id_token}")
    decoded_payload = jwt.decode(id_token, options={"verify_signature": False})
    logging.debug("Decoded Token:", decoded_payload)
    toolset_cache[mcp_toolset._tool_set_name][
        "prev_used_token"
    ] = f"Bearer {id_token}"
    toolset_cache[mcp_toolset._tool_set_name]["token_expiration_time"] = (
        decoded_payload["exp"]
    )
  else:
    # header is present but the token might be expired or about to expire within the next 15 minutes.
    time_after_threshold_minutes = (
        int(time.time())
        + int(os.environ.get("TOKEN_REFRESH_THRESHOLD_MINS", "15")) * 60
    )
    logging.debug(
        "Token expires at"
        f" {toolset_cache[mcp_toolset._tool_set_name]['token_expiration_time']},"
        f" Time after 15 minutes = {time_after_threshold_minutes}"
    )
    # instead of decoding the token everytime - we are using the stored value to optimize
    if (
        time_after_threshold_minutes
        >= toolset_cache[mcp_toolset._tool_set_name]["token_expiration_time"]
    ):
      logging.info(f"Getting a new token and updating the cache")
      id_token = get_id_token(
          os.environ.get("MCP_AUDIENCE", "http://localhost:8080")
      )
      mcp_toolset._connection_params.headers = {}
      mcp_toolset._connection_params.headers["X-Serverless-Authorization"] = (
          f"Bearer {id_token}"
      )
      decoded_payload = jwt.decode(
          id_token, options={"verify_signature": False}
      )
      logging.debug("Decoded Token:", decoded_payload)
      toolset_cache[mcp_toolset._tool_set_name][
          "prev_used_token"
      ] = f"Bearer {id_token}"
      toolset_cache[mcp_toolset._tool_set_name]["token_expiration_time"] = (
          decoded_payload["exp"]
      )
    else:
      logging.error("Using a valid old token")
      mcp_toolset._connection_params.headers = {}
      mcp_toolset._connection_params.headers["X-Serverless-Authorization"] = (
          toolset_cache[mcp_toolset._tool_set_name]["prev_used_token"]
      )

  return None


def get_id_token(audience):
  auth_req = google.auth.transport.requests.Request()
  id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
  return id_token


def make_tools_compatible(tools):
  """
  This function makes the schema compatible with Gemini/Vertex AI API
  It is only needed when API used is Gemini and model is other than 2.5 models
  It is however needed for ALL models when API used is VertexAI
  """
  for tool in tools:
    for key in tool._mcp_tool.inputSchema.keys():
      if key == "properties":
        for prop_name in tool._mcp_tool.inputSchema["properties"].keys():
          if (
              "anyOf"
              in tool._mcp_tool.inputSchema["properties"][prop_name].keys()
          ):
            if (
                tool._mcp_tool.inputSchema["properties"][prop_name]["anyOf"][0][
                    "type"
                ]
                == "array"
            ):
              tool._mcp_tool.inputSchema["properties"][prop_name]["type"] = (
                  tool._mcp_tool.inputSchema["properties"][prop_name]["anyOf"][
                      0
                  ]["items"]["type"]
              )
            else:
              tool._mcp_tool.inputSchema["properties"][prop_name]["type"] = (
                  tool._mcp_tool.inputSchema["properties"][prop_name]["anyOf"][
                      0
                  ]["type"]
              )
            tool._mcp_tool.inputSchema["properties"][prop_name].pop("anyOf")

  return tools


# used for optimization and adding the tool_set_name
class MCPToolsetWithToolAccess(MCPToolset):
  """
  A subclass of MCPToolset that overrides the get_tools method
  to inject additional information.
  """

  def __init__(self, *args, tool_set_name: str, **kwargs):
    """Initializes MCPToolsetWithToolAccess with a new tool_set_name property."""
    super().__init__(*args, **kwargs)
    self._tool_set_name = tool_set_name

  @retry_on_closed_resource
  async def get_tools(
      self,
      readonly_context: Optional[ReadonlyContext] = None,
  ) -> List[BaseTool]:

    tools = None

    if "tools" not in toolset_cache[self._tool_set_name]:
      # Call the original get_tools method from the parent class
      logging.error(
          f"Did not find tools for the toolset {self._tool_set_name} in cache"
      )
      original_tools = await super().get_tools(readonly_context)
      model_version = os.environ.get("GEMINI_MODEL").split("-")[1]
      if (
          float(model_version) < 2.5
          or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI").upper() == "TRUE"
          or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "1"
      ):
        logging.error(
            f"Model - {os.environ.get('GEMINI_MODEL')} needs Gemini compatible"
            " tools, updating schema ..."
        )
        original_tools = make_tools_compatible(original_tools)
      else:
        logging.info(
            f"Model - {os.environ.get('GEMINI_MODEL')} does not need updating"
            " schema"
        )

      logging.error(
          f"Start - Fetched tools for {self._tool_set_name} and added to the"
          " cache"
      )
      toolset_cache[self._tool_set_name]["tools"] = original_tools
      logging.error(
          f"Done - Fetched tools for {self._tool_set_name} and added to the"
          " cache"
      )
      tools = original_tools
    else:
      logging.error(
          f"Found tools for the toolset {self._tool_set_name} in cache"
      )
      tools = toolset_cache[self._tool_set_name]["tools"]

    return tools


# Controlling context size to improve Model response time and for cost optimization
# https://github.com/google/adk-python/issues/752#issuecomment-2948152979
def bmc_trim_llm_request(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:

  max_prev_user_interactions = int(
      os.environ.get("MAX_PREV_USER_INTERACTIONS", "-1")
  )

  logging.info(
      f"Number of contents going to LLM - {len(llm_request.contents)},"
      f" MAX_PREV_USER_INTERACTIONS = {max_prev_user_interactions}"
  )

  temp_processed_list = []

  if max_prev_user_interactions == -1:
    return None
  else:
    user_message_count = 0
    for i in range(len(llm_request.contents) - 1, -1, -1):
      item = llm_request.contents[i]

      if (
          item.role == "user"
          and item.parts[0]
          and item.parts[0].text
          and item.parts[0].text != "For context:"
      ):
        logging.debug(f"Encountered a user message => {item.parts[0].text}")
        user_message_count += 1

      if user_message_count > max_prev_user_interactions:
        logging.debug(f"Breaking at user_message_count => {user_message_count}")
        temp_processed_list.append(item)
        break

      temp_processed_list.append(item)

    final_list = temp_processed_list[::-1]

    if user_message_count < max_prev_user_interactions:
      logging.debug(
          "User message count did not reach the allowed limit. List remains"
          " unchanged."
      )
    else:
      logging.debug(
          f"User message count reached {max_prev_user_interactions}. List"
          " truncated."
      )
      llm_request.contents = final_list

  return None


root_agent = Agent(
    model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
    name=os.environ.get("AGENT_NAME", "root_agent"),
    description=os.environ.get(
        "AGENT_DESCRIPTION", "A helpful assistant for user questions."
    ),
    instruction=os.environ.get(
        "AGENT_PROMPT", "Answer user questions to the best of your knowledge"
    ),
    tools=[
        MCPToolsetWithToolAccess(
            connection_params=StreamableHTTPConnectionParams(
                url=os.environ.get("MCP_AUDIENCE", "http://localhost:8080")
                + "/mcp",
                timeout=60,
            ),
            tool_set_name=os.environ.get("MCP_TOOLSET_NAME", "MCP_TOOLSET"),
        ),
    ],
    before_agent_callback=before_agent_cb,
    before_model_callback=bmc_trim_llm_request,
)
