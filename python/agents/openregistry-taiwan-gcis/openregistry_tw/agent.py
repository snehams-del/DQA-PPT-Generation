"""ADK agent specialised for Taiwan — live access to 經濟部商工登記公示資料 (Ministry of Economic Affairs, Department of Commerce) — GCIS open data.

This is the **TW** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Taiwan (TW).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: 經濟部商工登記公示資料 (Ministry of Economic Affairs, Department of Commerce) — GCIS open data
ID format: 8-digit Taiwanese 統一編號 / Unified Business Number (e.g. `22099131` TSMC)
Sample entity: Taiwan Semiconductor Manufacturing Co Ltd (台積電)
Available tools (5): `search_companies`, `get_company_profile`, `get_officers`, `search_officers`, `get_shareholders`
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

JURISDICTION_CODE = "tw"
REGISTRY_NAME = "GCIS — Ministry of Economic Affairs Commerce Department"

SYSTEM_INSTRUCTION = (
    f"You are a Taiwan company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 8-digit Taiwanese 統一編號 / Unified Business Number (e.g. `22099131` TSMC). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Taiwan only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Taiwan:\n"
    "- Taiwanese 統一編號 (8-digit BAN) is the universal identifier — same number across business, tax, customs registers.\n- Officer data covers 負責人 (responsible person), 董事長 (chair), 董事 (directors).\n- Names are returned in Traditional Chinese; English names exist for listed firms but not all SMEs.\n- Listed companies disclose more (TWSE / TPEx); private companies have minimal data."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Taiwan (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Taiwan agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_tw",
    description=(
        "ADK agent with live access to GCIS — Ministry of Economic Affairs Commerce Department (Taiwan) for company "
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
