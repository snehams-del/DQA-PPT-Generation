"""ADK agent specialised for Australia — live access to Australian Business Register (ABR) — ABN Lookup, Australian Taxation Office.

This is the **AU** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Australia (AU).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Australian Business Register (ABR) — ABN Lookup, Australian Taxation Office
ID format: 11-digit ABN or 9-digit ACN (e.g. ABN `33 123 456 789`, ACN `004 028 077` for BHP Group Limited)
Sample entity: BHP Group Limited
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

JURISDICTION_CODE = "au"
REGISTRY_NAME = "Australian Business Register (ABR — ABN Lookup)"

SYSTEM_INSTRUCTION = (
    f"You are a Australia company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 11-digit ABN or 9-digit ACN (e.g. ABN `33 123 456 789`, ACN `004 028 077` for BHP Group Limited). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Australia only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Australia:\n"
    "- ABR (ABN Lookup) is the open public dataset; full ASIC company data (officers, shareholders, registered addresses) is paid-only via ASIC's commercial channels.\n- ABN ≠ ACN. ABN is for tax/business; ACN is for incorporated companies (subset of ABNs).\n- GST registration date is in the ABR record — useful indicator of operational status.\n- Indigenous corporations (CATSI) and partnerships also have ABNs — filter by `entity_type` in profile."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Australia (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Australia agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_au",
    description=(
        "ADK agent with live access to Australian Business Register (ABR — ABN Lookup) (Australia) for company "
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
