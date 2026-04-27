"""ADK agent specialised for Finland — live access to Patentti- ja rekisterihallitus (PRH) — avoindata YTJ API.

This is the **FI** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Finland (FI).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Patentti- ja rekisterihallitus (PRH) — avoindata YTJ API
ID format: Finnish Y-tunnus (8-digit, hyphenated: `0112038-9` Nokia Oyj)
Sample entity: Nokia Oyj
Available tools (8): `search_companies`, `get_company_profile`, `list_filings`, `get_financials`, `get_officers`, `get_shareholders`, `get_document_metadata`, `fetch_document`
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

JURISDICTION_CODE = "fi"
REGISTRY_NAME = "PRH — Patentti- ja rekisterihallitus"

SYSTEM_INSTRUCTION = (
    f"You are a Finland company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: Finnish Y-tunnus (8-digit, hyphenated: `0112038-9` Nokia Oyj). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Finland only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Finland:\n"
    "- Finland's PRH UBO register (Tosiasiallinen edunsaaja) is publicly queryable. Full UBO support on the roadmap.\n- `Oy` = private limited; `Oyj` = public limited. Branches show as separate Y-tunnukset.\n- Filings include annual reports (tilinpäätös) in iXBRL — `fetch_document` returns raw bytes.\n- Company language can be FI / SV / EN — name fields may include all three."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Finland (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Finland agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_fi",
    description=(
        "ADK agent with live access to PRH — Patentti- ja rekisterihallitus (Finland) for company "
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
