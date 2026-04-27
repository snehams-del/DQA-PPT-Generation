"""ADK agent specialised for Italy — live access to Registro delle imprese — Camere di Commercio / InfoCamere S.c.p.A., surfaced via EU Business Registers Interconnection System (BRIS) e-Justice gateway.

This is the **IT** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Italy (IT).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Registro delle imprese — Camere di Commercio / InfoCamere S.c.p.A., surfaced via EU Business Registers Interconnection System (BRIS) e-Justice gateway
ID format: Italian Codice Fiscale or REA number (REA: `MI-1234567` Milan or `RM-1234567` Rome)
Sample entity: Ferrari N.V.
Available tools (2): `search_companies`, `get_company_profile`
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

JURISDICTION_CODE = "it"
REGISTRY_NAME = "Registro delle imprese (InfoCamere via EU BRIS)"

SYSTEM_INSTRUCTION = (
    f"You are a Italy company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: Italian Codice Fiscale or REA number (REA: `MI-1234567` Milan or `RM-1234567` Rome). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Italy only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Italy:\n"
    "- Surfaced through EU BRIS — same gateway used by NL, MT, PT, GR, etc. Italy is a passthrough; full filing detail requires a paid InfoCamere/Camere di Commercio query.\n- **Post CJEU C-37/20** — Italy's Registro dei Titolari Effettivi is access-restricted to AML-obliged entities. `get_persons_with_significant_control` returns 501 with `alternative_url`.\n- REA numbers are court-prefixed (province code + sequence).\n- For full Italian financial statements (deposito di bilanci), the official channel is InfoCamere paid services."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Italy (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Italy agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_it",
    description=(
        "ADK agent with live access to Registro delle imprese (InfoCamere via EU BRIS) (Italy) for company "
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
