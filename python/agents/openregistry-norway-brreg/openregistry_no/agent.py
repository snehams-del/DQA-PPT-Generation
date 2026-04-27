"""ADK agent specialised for Norway — live access to Brønnøysund Register Centre (Enhetsregisteret + Foretaksregisteret).

This is the **NO** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Norway (NO).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Brønnøysund Register Centre (Enhetsregisteret + Foretaksregisteret)
ID format: 9-digit Norwegian organisasjonsnummer (e.g. `923609016` Equinor ASA)
Sample entity: Equinor ASA
Available tools (4): `search_companies`, `get_company_profile`, `get_officers`, `get_shareholders`
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

JURISDICTION_CODE = "no"
REGISTRY_NAME = "Brønnøysundregistrene (Enhetsregisteret)"

SYSTEM_INSTRUCTION = (
    f"You are a Norway company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 9-digit Norwegian organisasjonsnummer (e.g. `923609016` Equinor ASA). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Norway only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Norway:\n"
    "- Norway has a **public UBO register** (Reelle Rettighetshavere) — accessible via Brreg. UBO support is on the roadmap.\n- `AS` = limited (private), `ASA` = public limited (Allmennaksjeselskap).\n- Filings include annual accounts (årsregnskap) deposited at Regnskapsregisteret — separate from the company-status register.\n- Officer data covers styre (board) members, daglig leder (CEO), revisor (auditor)."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Norway (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Norway agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_no",
    description=(
        "ADK agent with live access to Brønnøysundregistrene (Enhetsregisteret) (Norway) for company "
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
