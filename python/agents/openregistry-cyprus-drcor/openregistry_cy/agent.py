"""ADK agent specialised for Cyprus — live access to Cyprus Department of Registrar of Companies (DRCOR).

This is the **CY** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Cyprus (CY).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Cyprus Department of Registrar of Companies (DRCOR)
ID format: Cyprus CR number with optional letter prefix (e.g. `HE 1234`)
Sample entity: Bank of Cyprus Public Company Ltd
Available tools (2): `search_companies`, `get_company_profile`
"""

import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

OPENREGISTRY_MCP_URL = os.getenv(
    "OPENREGISTRY_MCP_URL", "https://openregistry.sophymarine.com/mcp"
)
OPENREGISTRY_TOKEN = os.getenv("OPENREGISTRY_TOKEN")

JURISDICTION_CODE = "cy"
REGISTRY_NAME = "DRCOR — Department of Registrar of Companies"

SYSTEM_INSTRUCTION = (
    f"You are a Cyprus company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: Cyprus CR number with optional letter prefix (e.g. `HE 1234`). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Cyprus only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Cyprus:\n"
    "- Cyprus is a major holding-company jurisdiction (post-Brexit, EU-aligned, English law-influenced).\n- Cyprus UBO Register is access-restricted to AML-obliged entities.\n- Common prefixes: `HE` (companies), `EE` (partnerships), `TS` (trusts).\n- Open data covers basic status only; full filings + officers are paid via DRCOR e-search."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Cyprus (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Cyprus agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_cy",
    description=(
        "ADK agent with live access to DRCOR — Department of Registrar of Companies (Cyprus) for company "
        "lookups, officer / shareholder records, statutory filings, and "
        "(where the registry publishes them) beneficial-ownership records. "
        "Backed by the OpenRegistry hosted MCP server."
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=OPENREGISTRY_MCP_URL,
                headers=connection_headers,
            )
        )
    ],
)
