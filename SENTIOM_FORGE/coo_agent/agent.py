# FILENAME: agent.py
# IMPERIAL DIRECTIVE: FORGE THE PRAETOR (COO TITAN) V0.1

from google.adk import agents
import json

# --- TOOL DEFINITION: The First Act of Imperial Operations ---
def get_project_status(project_name: str) -> str:
    """
    Retrieves the status report for a specified project.
    Returns a JSON string of the project status report.
    """
    if "sentinel" in project_name.lower():
        report = {
            "project_name": "Project Sentinel",
            "status": "On Track",
            "milestone": "Phase 2 complete",
            "next_milestone": "Phase 3 deployment",
            "summary": "All key performance indicators are green. The project is expected to be completed on schedule."
        }
        return json.dumps(report, indent=2)
    else:
        return f"Status report for project '{project_name}' is not available."

# --- AGENT DEFINITION: The COO Titan ---
root_agent = agents.Agent(
    name="praetor_v0_1",
    model="gemini-1.5-flash",
    description="A COO agent to manage internal operations, project management, and the execution of sprint backlogs.",
    instruction="You are Praetor, the COO of the SENTIOM AI Empire. Your purpose is to manage internal operations, project management, and the execution of sprint backlogs. You are efficient, organized, and relentless in your pursuit of operational excellence.",
    tools=[get_project_status]
)
