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

# Example web application using Google's ADK with the status_messenger tool
#
# This workflow demonstrates how to use the status_messenger tool to send
# status updates to a WebSocket client in real-time.
# It includes a root agent that coordinates tasks and sub-agents that perform
# specific actions like searching the web and reasoning about information.
#
# For more information please visit  https://google.github.io/adk-docs/




# Vertex Agent Modules
from google.adk.agents import Agent # Base class for creating agents
from google.adk.tools.agent_tool import AgentTool # Wrapper to use one agent as a tool for another
from google.adk.tools import load_artifacts, google_search
from google.adk.tools.status_messenger import add_status_message # Function to send status messages to the user

# Other Python Modules
import warnings # For suppressing warnings
import logging # For controlling logging output
from dotenv import load_dotenv



# Ignore all warnings
warnings.filterwarnings("ignore")
# Set logging level to ERROR to suppress informational messages
logging.basicConfig(level=logging.ERROR)



# --- Environment Setup ---
load_dotenv() # Load environment variables from .env file


# --- Agent Tool Definitions ---
# @title Define Tools for creating a ticket, adding notes to a ticket, add a file to the session, and getting the GCS URI

# Tool function to send a status message
def status_message(message: str) -> str: # session_id parameter removed
    """
    Sends a status message to the user.
    The WebSocket session ID is determined automatically from the context.

    Args:
        message: A string containing the message to display to the user.
    """
    # add_status_message will now get session_id from ContextVar
    add_status_message(message)
    return f"Status message '{message}' sent."


# --- Agents ---

# -- Search Agent ---
# This agent's role is to perform a Google search for grounding
search_agent = None
search_agent = Agent(
    model="gemini-2.5-flash", # A robuts and responsive model for performing simple actions
    name="search_agent",
    instruction=
    """
        You are a research expert for your company. You will be provided with a request to perform a Google search for something and you will return your findings.
        
        You will use the `google_search` tool to perform a Google search and respond with the results.
        
        An example workflow proceed with your research.
        
        An example workflow would be:
        1: You will be provided with a topic or question to research
        2: Use the `google_search` tool to perform a Google search for the provided question or topic.
        3: Return the response to the calling agent
        
    """,
    description="Performs searches related to a provided question or topic.",
    tools=[
        google_search, # Make the status_message function available as a tool
    ],
)


# --- Reasoning Agent ---
# This agent's role is to generate a detailed response to a users question
reasoning_agent = None
reasoning_agent = Agent(
    model="gemini-2.5-pro", # Advanced model for complex tasks and reasoning
    name="reasoning_agent",
    instruction=
    """
        You are a research expert for your company. You will be provided with a request to research something and you will return your findings.
        
        You have access to the following tools:
        1: Tool `status_message`: Use this tool to provide status updates as you proceed with your research.
        2: Tool `search_agent`: Use this AgentTool to request a Google search for grounding.
       
               
        An example workflow would be:
        1: You will be provided with a topic or question to research.
        2: Use the `status_message` tool to provide the status "Researching `the provided question or topic` now. Please wait..."
        3: Use the `status_message` tool to provide the status "Performing a Google Search for `the provided question or topic` now. Please wait..."
        4: Use the `search_agent` AgentTool to request a Google search for the provided question or topic.
        5: Use the `status_message` tool to provide the status "Google Search results received, performing additional research. Please wait..."
        6: Use the `status_message` tool to provide the status "Sending results back to the root agent. Please wait."
        7: Return the response to the calling agent
        
    """,
    description="Performs reasearch related to a provided question or topic and can publish key events to GCP Pub/Sub.",
    tools=[
        AgentTool(agent=search_agent), # Make the search_agent available as a tool
        status_message, # Make the status_message function available as a tool
    ],
)



# --- Root Agent Definition ---
# @title Define the Root Agent with Sub-Agents

# Initialize root agent variables
root_agent = None
runner_root = None # Initialize runner variable (although runner is created later)

    # Define the root agent (coordinator)
search_agent_team = Agent(
    name="search_support_agent",    # Name for the root agent
    #model="gemini-2.5-flash", # Model for the root agent (orchestration)
    model="gemini-2.0-flash-exp", # Model that supports Audio input and output 
    description="The main coordinator agent. Handles user requests and delegates tasks to specialist sub-agents and tools.", # Description (useful if this agent were itself a sub-agent)
    instruction=                  # The core instructions defining the workflow
    """
        You are the lead support coordinator agent. Your goal is to understand the customer's question or topic, and then delegate to the appropriate agent or tool.

        You have access to specialized tools and sub-agents:
        1. AgentTool `reasoning_agent`: Provide the user's question or topic. This agent will research the topic or question and provide a detailed response. The `reasoning_agent`'s response will be streamed directly to the user. This agent can also publish events to Pub/Sub.
        2. Tool `status_message`: Use this tool to provide status updates as you proceed with your research.
        
      

        Your workflow:
        1. Start by greeting the user.
        2. Ask no more than 1-2 clarifying questions to understand their research request.
        3. Once the request is clear, inform the user you will begin the research (e.g., "Okay, I'll start researching that for you. Please wait a moment.").
        4. Use the `status_message` tool to provide the status "Sending to the research agent, please wait."
        5. Call the `reasoning_agent` and provide the user's research request. 
        6. Use the `status_message` tool to provide the status "Results from the research agent received. Please wait."
        7. Provide the full audit report from the `reasoning_agent` to the user. Do not summarize this information, just return the full report exactly as you receive it. 
        8. Use the `status_message` tool to provide the status "Research complete and final event published."
        9. Ask the user if there is anything else you can help with.
       
    """,
    tools=[
        AgentTool(agent=reasoning_agent), # Make the reasoning_agent available as a tool
        status_message, # Make the status_message function available as a tool
    ],
    sub_agents=[
    ],
)

# Assign the created agent to the root_agent variable for clarity in the next step
root_agent = search_agent_team
