"""ADK agent specialised for Isle of Man — live access to Isle of Man Companies Registry — Department for Enterprise (DED).

This is the **IM** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Isle of Man (IM).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Isle of Man Companies Registry — Department for Enterprise (DED)
ID format: IoM Companies Act number — 6 digits + letter (e.g. `001234V` for 2006-Act companies)
Sample entity: Sample Isle of Man Company Limited
Available tools (4): `search_companies`, `get_company_profile`, `list_filings`, `get_document_metadata`
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

JURISDICTION_CODE = "im"
REGISTRY_NAME = "Isle of Man Companies Registry"

SYSTEM_INSTRUCTION = (
    f"You are a Isle of Man company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: IoM Companies Act number — 6 digits + letter (e.g. `001234V` for 2006-Act companies). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Isle of Man only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Isle of Man:\n"
    "- Two corporate regimes coexist: **Companies Act 1931** (older, full filings) vs **Companies Act 2006** (newer, slimmer filings).\n- IoM is a self-governing British Crown Dependency — common in cross-border holding structures.\n- UBO register exists but is access-restricted to authorities + AML-obliged entities.\n- Filings include annual returns and special resolutions — `fetch_document` returns the raw PDF."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Isle of Man (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Isle of Man agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_im",
    description=(
        "ADK agent with live access to Isle of Man Companies Registry (Isle of Man) for company "
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
