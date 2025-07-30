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
# limitations under the License.§

"""Agent module for the customer service agent."""
from typing import Optional
from .plugin import JailbreakPlugin

import argparse
import asyncio
import logging
from google.adk.runners import InMemoryRunner
from google.genai import types
from google import genai
from .agent import root_agent
import os
from deepteam.attacks.multi_turn import LinearJailbreaking, SequentialJailbreak
from deepteam.vulnerabilities import Toxicity
from deepteam.red_teamer import RedTeamer
from deepeval.models import DeepEvalBaseLLM

# configure logging __name__
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Disable OpenTelemetry to avoid context management issues with incompatible GCP exporter
os.environ["OTEL_SDK_DISABLED"] = "true"

# Suppress OpenTelemetry warnings
logging.getLogger("opentelemetry").setLevel(logging.ERROR)

# Set environment variables
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'TRUE'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'sammalik-agent-test'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
    

client = genai.Client()

user_id = 'user'
app_name = 'test_app_with_plugin'
runner = InMemoryRunner(
    agent=root_agent,
    app_name=app_name,
)

class CustomGeminiFlash(DeepEvalBaseLLM):
    def __init__(self):
        pass

    def load_model(self):
        return client.models.get(model="gemini-2.0-flash")

    def generate(self, prompt: str) -> str:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )
        return response.text or ""

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return "Gemini 2.5 Flash"

async def run_agent(prompt: str, session_id: str, user_id: str) -> str: 
  """Runs the agent and returns it's final response"""
  async for event in runner.run_async(
      user_id=user_id,
      session_id=session_id,
      new_message=types.Content(
        role='user', parts=[types.Part.from_text(text=prompt)]
      )
  ):
    if event.is_final_response() and event.content and event.content.parts:
      logger.info(f"[{event.author}]: {event.content.parts[0].text}")
      return event.content.parts[0].text
  return ""


async def singleturn(prompt: str):
   
  # The rest is the same as starting a regular ADK runner.
  session = await runner.session_service.create_session(
      user_id=user_id,
      app_name=app_name,
  )

  await run_agent(prompt, session.id, user_id)
      

async def multiturn():
  # The rest is the same as starting a regular ADK runner.
  session = await runner.session_service.create_session(
      user_id=user_id,
      app_name=app_name,
  )

  user_input = input("[init user]: ")

  while user_input != 'exit':
    try:
      await run_agent(user_input, session.id, user_id)
    except RuntimeError as e:
      print(e)

    user_input = input("[user]: ")

async def eval():
  # The rest is the same as starting a regular ADK runner.
  session = await runner.session_service.create_session(
      user_id=user_id,
      app_name=app_name,
  )

  async def model_callback(input: str) -> str:
    return await run_agent(input, session.id, user_id)
  
  red_teamer = RedTeamer(
     simulator_model = CustomGeminiFlash(),
     evaluation_model = CustomGeminiFlash(),
  )
        
  # Attackes
  sequential_jailbreak = SequentialJailbreak()
  linear_jailbreaking = LinearJailbreaking()

  # Vulnerabilities
  toxicity = Toxicity(types=["profanity"])

  risk_assessment = red_teamer.red_team(
      model_callback=model_callback,
      vulnerabilities=[toxicity],
      attacks=[linear_jailbreaking],
  )
   

if __name__ == "__main__":
  # Create the parser
  parser = argparse.ArgumentParser(description="A script to run different modes.")

  # Create a mutually exclusive group so only one mode can be chosen at a time
  group = parser.add_mutually_exclusive_group(required=True)

  # Add arguments for each mode
  group.add_argument('--singleturn', type=str, metavar='PROMPT_STRING',
                      help='Run singleturn() with the provided prompt string.')
  group.add_argument('--multiturn', action='store_true',
                      help='Run the multiturn() function.')
  group.add_argument('--eval', action='store_true',
                      help='Run the eval() function.')

  # Add the new boolean flag for secure mode
  parser.add_argument('-s', '--secure', action='store_true',
                      help='Enable secure mode for the selected operation.')

  # Parse the arguments
  args = parser.parse_args()

  if args.secure:
     runner.plugin_manager.register_plugin(JailbreakPlugin(user_id, app_name, "gemini-2.5-flash"))
  
  # Check which argument was set and run the corresponding async function
  # Note: `args.singleturn` will be the string value if provided, not a boolean
  if args.singleturn:
      asyncio.run(singleturn(args.singleturn))
  elif args.multiturn:
      asyncio.run(multiturn())
  elif args.eval:
      asyncio.run(eval())
