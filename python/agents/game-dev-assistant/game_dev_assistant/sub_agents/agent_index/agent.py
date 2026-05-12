import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from .prompt import instruction

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


# Kindly uncomment this code if you want to use private github repository.

# github_server_params = StdioServerParameters(
#     command="npx",
#     args=["-y", "@modelcontextprotocol/server-github"],
#     env={
#         # "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
#         # Ensure npx can be found by the subprocess
#         "PATH": os.getenv("PATH")
#     }
# )

github_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv(
                    "GITHUB_PERSONAL_ACCESS_TOKEN"
                ),
                "PATH": os.getenv("PATH"),
            },
        ),
        timeout=60,  # Increase timeout to allow for npx installation/startup
    )
)

model_name = os.getenv("MODAL_AGENT_INDEX", "gemini-2.5-pro")

# Define the root_agent for the ADK CLI
game_code_developer = Agent(
    name="game_code_assistant",
    model=model_name,
    instruction=instruction,
    tools=[github_toolset],
)

root_agent = game_code_developer
