"""ADK agent specialised for Malaysia — live access to Suruhanjaya Syarikat Malaysia (SSM) — Companies Commission of Malaysia.

This is the **MY** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Malaysia (MY).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Suruhanjaya Syarikat Malaysia (SSM) — Companies Commission of Malaysia
ID format: 12-digit SSM registration number (e.g. `199301015245`) or older 6-digit company number
Sample entity: Maybank Bhd (Malayan Banking Berhad)
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

JURISDICTION_CODE = "my"
REGISTRY_NAME = "SSM — Suruhanjaya Syarikat Malaysia"

SYSTEM_INSTRUCTION = (
    f"You are a Malaysia company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 12-digit SSM registration number (e.g. `199301015245`) or older 6-digit company number. "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Malaysia only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Malaysia:\n"
    "- SSM open data is **basic-status only** — full filings, officers, shareholders are paid via SSM e-Info / MBRS.\n- `Sdn Bhd` (Sendirian Berhad) = private limited; `Bhd` (Berhad) = public.\n- 12-digit SSM number = year (4) + counter (8); pre-2017 entities have 6-digit legacy numbers — both still in use.\n- Malaysian UBO register (RBO) is access-controlled to AML-obliged entities; not in this dataset."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Malaysia (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Malaysia agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_my",
    description=(
        "ADK agent with live access to SSM — Suruhanjaya Syarikat Malaysia (Malaysia) for company "
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
