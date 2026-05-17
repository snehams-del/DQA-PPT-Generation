"""
Receipt-signing research agent.

Every tool call produces an Ed25519-signed receipt following the
IETF Internet-Draft format (draft-farley-acta-signed-receipts).
Receipts are independently verifiable offline.
"""

from google.adk import Agent
from google.adk.tools import FunctionTool
from protect_mcp_adk import ReceiptPlugin, ReceiptSigner

from . import tools

# Initialize receipt signing
# In production, load from file: ReceiptSigner.from_key_file("keys/agent.json")
signer = ReceiptSigner.generate()

receipt_plugin = ReceiptPlugin(
    signer,
    auto_export_path="receipts.jsonl",
    log_receipts=True,
)

# Create the agent with receipt signing enabled
agent = Agent(
    model="gemini-2.0-flash",
    name="research_agent",
    instruction=(
        "You are a research assistant that helps users investigate topics. "
        "Use web_search to find information, read_document to extract content, "
        "and analyze_data to produce insights. "
        "Every tool call you make is cryptographically signed for audit purposes."
    ),
    tools=[
        FunctionTool(tools.web_search),
        FunctionTool(tools.read_document),
        FunctionTool(tools.analyze_data),
    ],
    plugins=[receipt_plugin],
)
