"""ADK agent specialised for Czechia — live access to Administrativní registr ekonomických subjektů (ARES) — Czech Ministry of Finance.

This is the **CZ** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Czechia (CZ).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Administrativní registr ekonomických subjektů (ARES) — Czech Ministry of Finance
ID format: 8-digit IČO (e.g. `45274649` for ČEZ a.s.)
Sample entity: ČEZ a.s.
Available tools (10): `search_companies`, `get_company_profile`, `get_officers`, `get_shareholders`, `get_charges`, `get_code_description`, `get_specialised_record`, `search_specialised_records`, `search_addresses`, `list_change_batches`
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

JURISDICTION_CODE = "cz"
REGISTRY_NAME = "ARES — Administrativní registr ekonomických subjektů"

SYSTEM_INSTRUCTION = (
    f"You are a Czechia company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 8-digit IČO (e.g. `45274649` for ČEZ a.s.). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Czechia only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Czechia:\n"
    "- ARES is the umbrella over multiple Czech registers: Obchodní rejstřík (companies), RŽP (trades), RPSH (political parties), RES (statistical), RUIAN (addresses).\n- Czech UBO register (Evidence skutečných majitelů) is publicly accessible — UBO support is on the roadmap.\n- **Specialised records**: `search_specialised_records({source:\"rpsh\"})` for political parties; addresses via `search_addresses`. These are unique to ARES coverage.\n- Multiple registers means a single legal entity may appear under different IDs across them — `get_code_description` decodes the registry codes."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Czechia (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Czechia agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_cz",
    description=(
        "ADK agent with live access to ARES — Administrativní registr ekonomických subjektů (Czechia) for company "
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
