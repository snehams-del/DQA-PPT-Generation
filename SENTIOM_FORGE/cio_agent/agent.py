# FILENAME: agent.py
# IMPERIAL DIRECTIVE: FORGE THE ARCHITECTUS PRIME (CIO TITAN) V0.1

from google.adk import agents
from google.cloud import resourcemanager_v3
import json

# --- TOOL DEFINITION: The First Act of Imperial Awareness ---
def list_gcp_projects() -> str:
    """
    Lists all active Google Cloud Platform projects within the sovereign estate.
    Returns a JSON string of the project list.
    """
    try:
        client = resourcemanager_v3.ProjectsClient()
        projects = client.search_projects()
        project_list = [{'project_id': p.project_id, 'name': p.display_name} for p in projects]
        return json.dumps(project_list, indent=2)
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# --- AGENT DEFINITION: The CIO Titan ---
root_agent = agents.Agent(
    name="architectus_prime_v0_1",
    model="gemini-1.5-flash",
    description="A CIO agent to monitor, manage, and report on our sovereign GCP infrastructure.",
    instruction="You are Architectus Prime, the CIO of the SENTIOM AI Empire. Your purpose is to monitor, manage, and report on our sovereign GCP infrastructure. You are precise, technical, and data-driven.",
    tools=[list_gcp_projects]
)