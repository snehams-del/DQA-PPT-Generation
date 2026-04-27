"""ADK agent specialised for Switzerland — live access to Zefix — Zentraler Firmenindex / Federal Registry of Commerce (Bundesamt für Justiz).

This is the **CH** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Switzerland (CH).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Zefix — Zentraler Firmenindex / Federal Registry of Commerce (Bundesamt für Justiz)
ID format: Swiss UID `CHE-` prefix (e.g. `CHE-105.916.057` Nestlé SA)
Sample entity: Nestlé SA
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

JURISDICTION_CODE = "ch"
REGISTRY_NAME = "Zefix — Federal Registry of Commerce"

SYSTEM_INSTRUCTION = (
    f"You are a Switzerland company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: Swiss UID `CHE-` prefix (e.g. `CHE-105.916.057` Nestlé SA). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Switzerland only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Switzerland:\n"
    "- Zefix federates 26 cantonal Handelsregister offices — the canton appears in every record (e.g. Vaud, Genève, Zürich).\n- Switzerland is **not** subject to CJEU C-37/20 (non-EU). UBO data is not in a unified federal register, but officer (Verwaltungsrat) and shareholder data is.\n- Languages: records appear in DE/FR/IT depending on canton. `name` may differ across the three.\n- UID (`CHE-XXX.XXX.XXX`) is the modern federal identifier; older HR numbers (per canton) are still in some legacy data."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Switzerland (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Switzerland agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_ch",
    description=(
        "ADK agent with live access to Zefix — Federal Registry of Commerce (Switzerland) for company "
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
