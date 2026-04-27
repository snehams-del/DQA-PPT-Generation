"""ADK agent specialised for New Zealand — live access to New Zealand Companies Office (Ministry of Business, Innovation & Employment).

This is the **NZ** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to New Zealand (NZ).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: New Zealand Companies Office (Ministry of Business, Innovation & Employment)
ID format: 7-digit NZBN suffix or 13-digit NZBN (e.g. `9429038949149` Fonterra Co-operative Group Limited)
Sample entity: Fonterra Co-operative Group Limited
Available tools (9): `search_companies`, `get_company_profile`, `get_officers`, `get_shareholders`, `list_filings`, `get_officer_appointments`, `search_officers`, `get_document_metadata`, `fetch_document`
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

JURISDICTION_CODE = "nz"
REGISTRY_NAME = "New Zealand Companies Office"

SYSTEM_INSTRUCTION = (
    f"You are a New Zealand company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 7-digit NZBN suffix or 13-digit NZBN (e.g. `9429038949149` Fonterra Co-operative Group Limited). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "New Zealand only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to New Zealand:\n"
    "- NZ has full public officer + shareholder data — among the most transparent registers globally.\n- NZBN (New Zealand Business Number) is the modern identifier; legacy company numbers (6-digit) still appear in older records.\n- Annual return filings include constitution amendments — `fetch_document` returns the raw filing.\n- Cross-border structures often use NZ entities — note the `ultimate-holding-company` field in profile."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for New Zealand (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK New Zealand agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_nz",
    description=(
        "ADK agent with live access to New Zealand Companies Office (New Zealand) for company "
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
