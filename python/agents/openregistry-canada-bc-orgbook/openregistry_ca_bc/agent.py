"""ADK agent specialised for Canada (British Columbia) — live access to BC Registries (OrgBook BC verifiable-credential ledger, Province of British Columbia).

This is the **CA-BC** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Canada (British Columbia) (CA-BC).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: BC Registries (OrgBook BC verifiable-credential ledger, Province of British Columbia)
ID format: BC company number (e.g. `BC1234567` BC-incorporated, `A0099999` extra-provincial)
Sample entity: A BC-incorporated company
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

JURISDICTION_CODE = "ca-bc"
REGISTRY_NAME = "BC Registries (OrgBook BC)"

SYSTEM_INSTRUCTION = (
    f"You are a Canada (British Columbia) company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: BC company number (e.g. `BC1234567` BC-incorporated, `A0099999` extra-provincial). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Canada (British Columbia) only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Canada (British Columbia):\n"
    "- OrgBook BC is built on **verifiable-credential ledger** technology (Hyperledger Indy) — credentials are cryptographically signed.\n- BC has many extra-provincial entities (companies registered elsewhere doing business in BC).\n- BC corporate types: `BC Limited Company`, `Cooperative`, `Society`, `Sole Proprietor`.\n- Officers + UBO data is paid via BC Online — open dataset is basic status only."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Canada (British Columbia) (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Canada (British Columbia) agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_ca_bc",
    description=(
        "ADK agent with live access to BC Registries (OrgBook BC) (Canada (British Columbia)) for company "
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
