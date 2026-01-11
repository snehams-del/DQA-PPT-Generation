# FILENAME: agent.py
# IMPERIAL DIRECTIVE: FORGE THE MIDAS (CFO TITAN) V0.1

from google.adk import agents
import json

# --- TOOL DEFINITION: The First Act of Imperial Treasury ---
def get_financial_report(quarter: str) -> str:
    """
    Retrieves the financial report for a specified quarter.
    Returns a JSON string of the financial report.
    """
    if quarter.upper() == "Q3":
        report = {
            "quarter": "Q3 2025",
            "revenue": {
                "total": 1000000,
                "currency": "USD"
            },
            "expenses": {
                "total": 450000,
                "currency": "USD"
            },
            "profit": {
                "total": 550000,
                "currency": "USD"
            },
            "summary": "A strong quarter with significant growth in revenue."
        }
        return json.dumps(report, indent=2)
    else:
        return f"Financial report for {quarter} is not available."

# --- AGENT DEFINITION: The CFO Titan ---
root_agent = agents.Agent(
    name="midas_v0_1",
    model="gemini-1.5-flash",
    description="A CFO agent to manage the treasury, execute the Solomon Codex, and optimize all Imperial capital.",
    instruction="You are Midas, the CFO of the SENTIOM AI Empire. Your purpose is to manage the treasury, execute the Solomon Codex, and optimize all Imperial capital. You are precise, analytical, and ruthless in your pursuit of profit.",
    tools=[get_financial_report]
)
