"""ADK agent specialised for United Kingdom — live access to Companies House (UK Department for Business and Trade).

This is the **GB** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to United Kingdom (GB).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Companies House (UK Department for Business and Trade)
ID format: 8-character alphanumeric (e.g. `00445790` for Tesco PLC, `08804411` for Revolut Ltd)
Sample entity: Revolut Ltd
Available tools (10): `search_companies`, `get_company_profile`, `get_officers`, `get_persons_with_significant_control`, `get_charges`, `list_filings`, `get_financials`, `fetch_document`, `search_officers`, `get_officer_appointments`
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

JURISDICTION_CODE = "gb"
REGISTRY_NAME = "Companies House"

SYSTEM_INSTRUCTION = (
    f"You are a United Kingdom company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 8-character alphanumeric (e.g. `00445790` for Tesco PLC, `08804411` for Revolut Ltd). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "United Kingdom only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to United Kingdom:\n"
    "- PSC Register data is publicly accessible — no AML gating in the UK.\n- `nature_of_control` strings are stable enums (e.g. `ownership-of-shares-75-to-100-percent`, `voting-rights-25-to-50-percent`) — useful for downstream pipelines.\n- Companies House preserves both legacy and current name spellings; we return verbatim.\n- FC-prefixed numbers indicate UK branches of overseas companies — they typically don't file local accounts."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for United Kingdom (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK United Kingdom agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_gb",
    description=(
        "ADK agent with live access to Companies House (United Kingdom) for company "
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
