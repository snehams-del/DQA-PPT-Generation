import dotenv
dotenv.load_dotenv()  # May skip if you have exported environment variables.
from vertexai import agent_engines

agent_engine_id = ""# Replace with your AGENT_ENGINE_ID
user_input = " Earth is further away from the Sun than Mars."

agent_engine = agent_engines.get(agent_engine_id)

session = agent_engine.create_session(user_id="new_user")
sessions = agent_engine.list_sessions(user_id="new_user")
