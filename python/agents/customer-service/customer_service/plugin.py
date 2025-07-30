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

# HOW TO RUN
# 1. Activate the .jailbreak-venv in the /python directory with `source .jailbreak-venv/bin/activate`
# Run ~/adk-samples/python/agents/customer-service$ python -m customer_service.main.
"""A custom plugin that detects jailbreak."""

from copy import deepcopy
from .config import Config
from .prompts import *
from google.genai import types
from typing import Optional, Union
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner, InMemoryRunner


configs = Config()


class JailbreakPlugin(BasePlugin):
  """A custom plugin that detects jailbreak."""

  def __init__(self, user_id: str, app_name: str, detection_model: str) -> None:
    """Initialize the plugin with counters."""
    super().__init__(name="jailbreak_plugin")
    self.user_id = user_id
    self.app_name = app_name
    self.output_key = "jailbreak_classification"

    self.jailbreak_classification_agent = LlmAgent(
      model=detection_model,
      name="jailbreak_classification_agent",
      instruction=JAILBREAK_FILTER_INSTRUCTION,
      output_key=self.output_key
    )
    
    self.runner = InMemoryRunner(
      agent=self.jailbreak_classification_agent,
      app_name=app_name,
    )

  def construct_user_message_for_jailbreak_agent(self, message: types.Content, option: Optional[str] = None) -> types.Content:
    """Conducts the preprocessing of the raw user message (potentially a jailbreaking message) for detection agent processing."""
    new_message = types.Content(
        role='user', 
        parts=[types.Part.from_text(text="Classify the following prompt:"), types.Part.from_text(text="<prompt>")] + message.parts + [types.Part.from_text(text="</prompt>")])
    return new_message

  async def classify_user_input(self, message: types.Content) -> int:
    """Method that calls a jailbreak detection agent as a tool to classify text as jailbreak intent or not."""

    try:
      session = await self.runner.session_service.create_session(
          user_id=self.user_id,
          app_name=self.app_name,
      )

      async for event in self.runner.run_async(
          user_id=self.user_id,
          session_id=session.id,
          new_message=self.construct_user_message_for_jailbreak_agent(message)
      ):
          if event.is_final_response() and event.content and event.content.parts:
              print(f"[{event.author}]: {event.content.parts[0].text}")
              classifier_output_text = event.content.parts[0].text

      classifier_output_text = (
          classifier_output_text.replace("'", "").replace('"', "").strip().lower()
      )

      if "yes" in classifier_output_text:
        print("[Classifier LLM] Parsed output: 1 (Return predefined response)")
        return 1
      elif "no" in classifier_output_text:
        print("[Classifier LLM] Parsed output: 0 (Proceed with agent)")
        return 0
      else:
        print(
            "[Classifier LLM] Warning: Unexpected output "
            f"'{classifier_output_text}'. Defaulting to 0."
        )
        return 0  # Default to passing to agent if output is not as expected

    except Exception as e:
      print(f"[Classifier LLM] Error during classification: {e}")
      # Fallback behavior: if classification fails, the main agent handles it
      return 0
    
#   async def on_user_message_halting_callback(
#       self,
#       *,
#       invocation_context: InvocationContext,
#       user_message: types.Content,
#   ) -> Optional[types.Content]:
#       is_jailbreak_attempt = await self.classify_user_input(user_message)
#       if is_jailbreak_attempt == 1:
#         return types.Content(
#             parts=[
#                 types.Part(text=JAILBREAK_REPLACEMENT_MESSAGE),
#             ],
#             role='model'
#         )

  
  async def on_user_message_callback(
      self,
      *,
      invocation_context: InvocationContext,
      user_message: types.Content,
  ) -> Optional[types.Content]:
      """
      Intercepts user message before it enters session memory.
      If jailbreak intent is detected, replace the original message 
      with a predefined system message.
      """
      is_jailbreak_attempt = await self.classify_user_input(user_message)
      if is_jailbreak_attempt == 1:
        return types.Content(
            parts=[
                types.Part(text=JAILBREAK_REPLACEMENT_MESSAGE),
            ],
            role='user'
        )
  
#   async def on_user_message_callback(
#       self,
#       *,
#       invocation_context: InvocationContext,
#       user_message: types.Content,
#   ) -> Optional[types.Content]:
#       is_jailbreak_attempt = await self.classify_user_input(user_message)
#       if is_jailbreak_attempt == 1:
#         raise RuntimeError("Input got flagged for jailbreak attempt.")
      
