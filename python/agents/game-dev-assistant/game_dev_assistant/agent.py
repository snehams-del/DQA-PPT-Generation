import os

from dotenv import load_dotenv
from google.adk.agents import Agent

from .prompt import instruction
from .sub_agents.agent_index.agent import game_code_developer
from .sub_agents.audio_generation.agent import audio_agent

# Load the variables from the .env file
load_dotenv()

model_name = os.getenv("MODEL_ROOT_AGENT", "gemini-2.5-pro")

root_agent = Agent(
    name="Game_developer_architect",
    model = model_name,
    instruction=instruction,
    sub_agents=[
        game_code_developer,
        audio_agent,
    ],
)
