"""ADK agent specialised for Monaco — live access to Répertoire du Commerce et de l'Industrie (RCI) — Direction du Développement Économique (DDE), Gouvernement Princier de Monaco.

This is the **MC** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Monaco (MC).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Répertoire du Commerce et de l'Industrie (RCI) — Direction du Développement Économique (DDE), Gouvernement Princier de Monaco
ID format: RCI number (e.g. `99 S 03847` formatted, sequential)
Sample entity: Société des Bains de Mer SA
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

JURISDICTION_CODE = "mc"
REGISTRY_NAME = "RCI — Répertoire du Commerce et de l'Industrie"

SYSTEM_INSTRUCTION = (
    f"You are a Monaco company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: RCI number (e.g. `99 S 03847` formatted, sequential). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Monaco only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Monaco:\n"
    "- Monaco is a small jurisdiction — every company has a personal touch in the filings.\n- `SAM` (Société Anonyme Monégasque) is the local public-limited type; `SARL` is private.\n- Monaco's UBO register exists but is access-restricted; this skill returns the legal-shareholder data.\n- Tax-haven angle: many Monaco entities are nominee structures; cross-reference with French RNE / Italian InfoCamere for parents."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Monaco (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Monaco agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_mc",
    description=(
        "ADK agent with live access to RCI — Répertoire du Commerce et de l'Industrie (Monaco) for company "
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
