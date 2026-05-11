"""ADK agent specialised for Mexico — live access to Sistema Electrónico de Publicaciones de Sociedades Mercantiles (PSM), Secretaría de Economía (SE).

This is the **MX** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Mexico (MX).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Sistema Electrónico de Publicaciones de Sociedades Mercantiles (PSM), Secretaría de Economía (SE)
ID format: PSM publication ID per filing; companies are identified by name + tax ID (RFC)
Sample entity: A Mexican S.A. de C.V.
Available tools (4): `search_companies`, `list_filings`, `get_document_metadata`, `fetch_document`
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

JURISDICTION_CODE = "mx"
REGISTRY_NAME = "PSM — Sistema Electrónico de Publicaciones de Sociedades Mercantiles"

SYSTEM_INSTRUCTION = (
    f"You are a Mexico company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: PSM publication ID per filing; companies are identified by name + tax ID (RFC). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Mexico only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Mexico:\n"
    "- PSM is the **publication channel** (like Spanish BORME), not the company register itself — Mexican companies file at state-level Registros Públicos de Comercio (RPC).\n- PSM publishes corporate acts: incorporations, mergers, dissolutions, etc. `fetch_document` returns the raw publication.\n- Mexican company types: `S.A. de C.V.` (variable-capital limited), `S.A.P.I.` (investment), `S. de R.L. de C.V.`.\n- RFC (Registro Federal de Contribuyentes) is the tax identifier — separate from PSM publication IDs."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Mexico (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Mexico agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_mx",
    description=(
        "ADK agent with live access to PSM — Sistema Electrónico de Publicaciones de Sociedades Mercantiles (Mexico) for company "
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
