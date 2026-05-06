from google.adk import Agent

root_agent = Agent(
    model="gemini-2.0-flash",
    name="security_test",
    instruction="You are a test agent.",
)
