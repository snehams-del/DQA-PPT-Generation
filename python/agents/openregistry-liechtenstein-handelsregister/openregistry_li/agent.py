"""ADK agent specialised for Liechtenstein — live access to Handelsregister des Fürstentums Liechtenstein — Amt für Justiz (AJU), Vaduz.

This is the **LI** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Liechtenstein (LI).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Handelsregister des Fürstentums Liechtenstein — Amt für Justiz (AJU), Vaduz
ID format: FL-prefix Handelsregister number (e.g. `FL-0001.090.135-8` LGT Bank AG)
Sample entity: LGT Bank AG
Available tools (3): `search_companies`, `get_company_profile`, `list_filings`
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

JURISDICTION_CODE = "li"
REGISTRY_NAME = "Liechtenstein Handelsregister (Amt für Justiz)"

SYSTEM_INSTRUCTION = (
    f"You are a Liechtenstein company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: FL-prefix Handelsregister number (e.g. `FL-0001.090.135-8` LGT Bank AG). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Liechtenstein only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Liechtenstein:\n"
    "- Liechtenstein has unique entity types: `Anstalt` (establishment), `Stiftung` (foundation), `Treuunternehmen` (trust enterprise) — common in tax-haven structures.\n- Liechtenstein UBO data (Tatsächliche Empfänger) is access-restricted to AML-obliged entities.\n- Backend is **JSF ViewState** — slow, stateful queries; OpenRegistry runs a dedicated Playwright worker for LI to avoid blocking other traffic.\n- Frequently appears in cross-border ownership chains for high-net-worth structures."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Liechtenstein (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Liechtenstein agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_li",
    description=(
        "ADK agent with live access to Liechtenstein Handelsregister (Amt für Justiz) (Liechtenstein) for company "
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
