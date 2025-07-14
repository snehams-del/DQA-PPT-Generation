"""Defines the Capital Guess Game Root AI Agent."""

import logging

from google.genai import types
from google.adk.agents import Agent

from .config import AI_MODEL
from .prompt import GAME_ARCADE_AGENT_INSTR
from .shared_libraries.callbacks import *
from .sub_agents import capital_guess_workflow_agent

from .config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)

# capital_game_orchestrator_agent = Agent(
#     name="capital_game_orchestrator_agent",
#     model=AI_MODEL,
#     generate_content_config=types.GenerateContentConfig(temperature=0.1),
#     instruction="""
#     You are a game orchestrator agent.
#     """,
#     description="You are the Capital Game Agent responsible for orchestrating the gameplay.",
#     sub_agents=[
#         gameplay_workflow_agent,
#     ],
#     before_model_callback=before_model_cb,
#     before_agent_callback=before_agent_cb
# )


root_agent = Agent(
    model=AI_MODEL,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
    name="game_arcade_agent", 
    description="Let's the user choose a game to play",
    instruction=GAME_ARCADE_AGENT_INSTR,
    include_contents="none",
    # sub_agents=[
    #     capital_game_orchestrator_agent,
    # ],
    sub_agents=[
        capital_guess_workflow_agent,
    ],
    
    before_agent_callback=before_agent_cb,
)
