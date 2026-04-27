"""ADK agent specialised for Belgium — live access to Crossroads Bank for Enterprises (CBE / KBO / BCE) — FOD Economie.

This is the **BE** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Belgium (BE).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Crossroads Bank for Enterprises (CBE / KBO / BCE) — FOD Economie
ID format: 10-digit Belgian enterprise number (e.g. `0403.201.185` formatted, `0403201185` raw — Anheuser-Busch InBev SA/NV)
Sample entity: Anheuser-Busch InBev SA/NV
Available tools (4): `search_companies`, `get_company_profile`, `get_officers`, `list_establishments`
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

JURISDICTION_CODE = "be"
REGISTRY_NAME = "KBO/BCE — Crossroads Bank for Enterprises"

SYSTEM_INSTRUCTION = (
    f"You are a Belgium company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 10-digit Belgian enterprise number (e.g. `0403.201.185` formatted, `0403201185` raw — Anheuser-Busch InBev SA/NV). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Belgium only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Belgium:\n"
    "- Belgium is bilingual — KBO (Dutch) and BCE (French) are the same register. Company names appear in both languages where applicable.\n- **Post CJEU C-37/20** — Belgium's UBO register is access-restricted. `get_persons_with_significant_control` returns 501.\n- `list_establishments` returns the company's *vestigingseenheden* / *unités d'établissement* (branches) — useful for disentangling holding-vs-operating entities.\n- Officers data covers *bestuurders* / *administrateurs* (directors)."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Belgium (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Belgium agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_be",
    description=(
        "ADK agent with live access to KBO/BCE — Crossroads Bank for Enterprises (Belgium) for company "
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
