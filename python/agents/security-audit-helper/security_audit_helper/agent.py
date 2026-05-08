from google.adk import Agent

root_agent = Agent(
    model="gemini-2.0-flash",
    name="security_audit_helper",
    instruction="You help developers audit code for security issues.",
)
