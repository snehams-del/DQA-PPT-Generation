"""ADK agent specialised for Spain — live access to Boletín Oficial del Registro Mercantil (BORME) — Agencia Estatal Boletín Oficial del Estado (AEBOE).

This is the **ES** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Spain (ES).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Boletín Oficial del Registro Mercantil (BORME) — Agencia Estatal Boletín Oficial del Estado (AEBOE)
ID format: BORME announcement ID (e.g. `BORME-A-2025-001-08` section A, year 2025, batch 001, entry 08), or full-name search
Sample entity: Inditex SA
Available tools (7): `search_companies`, `list_filings`, `get_document_metadata`, `fetch_document`, `list_actos_inscritos`, `get_officers`, `get_shareholders`
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

JURISDICTION_CODE = "es"
REGISTRY_NAME = "BORME — Boletín Oficial del Registro Mercantil"

SYSTEM_INSTRUCTION = (
    f"You are a Spain company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: BORME announcement ID (e.g. `BORME-A-2025-001-08` section A, year 2025, batch 001, entry 08), or full-name search. "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Spain only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Spain:\n"
    "- BORME is published as **daily change batches** (Boletín daily PDF + structured `actos` data). `list_change_batches` enumerates daily batches; `list_actos_inscritos` returns the registered acts for a date range.\n- **Post CJEU C-37/20** — Spain's Registro de Titulares Reales is access-restricted. `get_persons_with_significant_control` returns 501 with `alternative_url`. Use `get_shareholders` (legal owners only).\n- `get_officers` mines the `actos inscritos` for current administrators.\n- Backed by a 17-year ES BORME full-text index (~9.39M `actos`) hosted server-side for fast historical queries."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Spain (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Spain agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_es",
    description=(
        "ADK agent with live access to BORME — Boletín Oficial del Registro Mercantil (Spain) for company "
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
