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

from google.adk.runners import InMemoryRunner
from google.adk import Agent
from google.genai import types
import asyncio

# Import the plugin.
from token_logger.plugin import TokenCounterLoggerPlugin

# Configure logging to see the output of the plugin.
import logging
logging.basicConfig(level=logging.INFO)


root_agent = Agent(
    model='gemini-2.0-flash',
    name='simple_agent',
    description='You are a simple agent that talks to the user.',
    instruction="""You are a simple agent that talks to the user.""",
)

async def main():
    prompts = ['Hello, how are you?', 'What is your name?', 'Tell me a joke.']
    runner = InMemoryRunner(
        agent=root_agent,
        app_name='test_plugin',
        plugins=[TokenCounterLoggerPlugin()],
    )

    session = await runner.session_service.create_session(
        user_id='user',
        app_name='test_plugin',
    )

    for prompt in prompts:
        async for event in runner.run_async(
            user_id='user',
            session_id=session.id,
            new_message=types.Content(
                role='user', parts=[types.Part.from_text(text=prompt)]
            )
        ):
            print(f'** Got event from {event.author}')

if __name__ == "__main__":
  asyncio.run(main())