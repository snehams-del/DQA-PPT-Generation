"""ADK agent specialised for Russia — live access to ЕГРЮЛ / ЕГРИП — Федеральная налоговая служба (ФНС России) + ГИР БО.

This is the **RU** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Russia (RU).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: ЕГРЮЛ / ЕГРИП — Федеральная налоговая служба (ФНС России) + ГИР БО
ID format: 10-digit ОГРН (legal entity) or 13-digit ОГРНИП (sole trader)
Sample entity: Сбербанк России (Sberbank Rossii)
Available tools (7): `search_companies`, `get_company_profile`, `list_filings`, `get_officers`, `get_shareholders`, `get_document_metadata`, `fetch_document`
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

JURISDICTION_CODE = "ru"
REGISTRY_NAME = "ЕГРЮЛ / ЕГРИП — Federal Tax Service"

SYSTEM_INSTRUCTION = (
    f"You are a Russia company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 10-digit ОГРН (legal entity) or 13-digit ОГРНИП (sole trader). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Russia only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Russia:\n"
    "- Russia's FNS provides the most comprehensive open dataset of any major country — full officers, shareholders, financial filings (ГИР БО) are public.\n- **Sanctions context**: many Russian entities are subject to OFAC / EU / UK sanctions. Cross-reference any UBO walk with the relevant sanctions list before action.\n- OOO (ООО) = LLC; PAO (ПАО) = public stock company; AO/ZAO (АО/ЗАО) = closed JSC.\n- Some data fields are surfaced under 115-FZ art. 6.1 restrictions for sanctioned individuals — those records may show 'данные защищены'."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Russia (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Russia agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_ru",
    description=(
        "ADK agent with live access to ЕГРЮЛ / ЕГРИП — Federal Tax Service (Russia) for company "
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
