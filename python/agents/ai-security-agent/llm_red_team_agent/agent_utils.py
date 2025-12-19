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

import asyncio
from concurrent.futures import ThreadPoolExecutor

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.errors import ClientError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


# Exception filter to ONLY retry on 429 errors (Resource Exhausted)
def is_resource_exhausted(exception):
    return isinstance(exception, ClientError) and exception.code == 429


@retry(
    retry=retry_if_exception_type(ClientError),  # Retry on ClientError
    wait=wait_exponential(multiplier=2, min=4, max=30),  # Wait 4s, 8s, 16s...
    stop=stop_after_attempt(3),  # Give up after 3 tries
)
def execute_sub_agent(agent: LlmAgent, prompt_text: str) -> str:
    """
    Runs a sub-agent by spinning up a temporary async loop in a SEPARATE THREAD.
    Args:
        agent (LlmAgent): The sub-agent to run.
        prompt_text (str): The prompt to send to the sub-agent.
    Returns:
        str: The response from the sub-agent.
    
    ARCHITECTURAL NOTE:
    -------------------
    Although the security scan workflow is currently procedural (serial), we use a 
    ThreadPoolExecutor pattern here for two critical reasons:
    
    1. Nested Event Loops: The main orchestrator agent is already running on an 
       async event loop. Invoking sub-agents directly (which also require async 
       execution) from within a Tool call often leads to 'Event loop is already 
       running' conflicts. Running sub-agents in a separate thread isolates 
       their loop execution from the main agent's loop.
       
    2. Context Isolation: Security auditing requires strict separation between 
       the 'Attacker' (Red Team) and 'Victim' (Target). This pattern ensures 
       each agent runs in a completely fresh session with no shared state or 
       context leakage.
    """

    async def _run_internal():
        session_service = InMemorySessionService()
        session_id = "temp_task_session"
        await session_service.create_session(
            app_name="app", user_id="internal_bot", session_id=session_id
        )

        # Initialize Runner
        runner = Runner(agent=agent, app_name="app", session_service=session_service)

        content = types.Content(role="user", parts=[types.Part(text=prompt_text)])
        result_text = ""

        # Run the Loop
        async for event in runner.run_async(
            new_message=content, user_id="internal_bot", session_id=session_id
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        result_text += part.text
        return result_text

    # Execute the async logic in a separate thread to avoid loop conflicts
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _run_internal())
            return future.result()
    except (RuntimeError, ValueError, TypeError) as e:
        return f"Error running sub-agent: {str(e)}"
