"""ADK agent specialised for South Korea — live access to 금융감독원 전자공시시스템 OPENDART (Financial Supervisory Service — Electronic Disclosure System).

This is the **KR** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to South Korea (KR).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: 금융감독원 전자공시시스템 OPENDART (Financial Supervisory Service — Electronic Disclosure System)
ID format: DART corp_code (8-digit) or stock_code (6-digit, e.g. `005930` for Samsung Electronics)
Sample entity: Samsung Electronics Co., Ltd. (삼성전자)
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

JURISDICTION_CODE = "kr"
REGISTRY_NAME = "OPENDART — 금융감독원 전자공시시스템"

SYSTEM_INSTRUCTION = (
    f"You are a South Korea company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: DART corp_code (8-digit) or stock_code (6-digit, e.g. `005930` for Samsung Electronics). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "South Korea only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to South Korea:\n"
    "- OPENDART is the public-disclosure system for **listed and large unlisted Korean firms** — not all Korean companies appear; private SMEs are not in scope.\n- `get_financials` returns IFRS-formatted statements (KIFRS). `fetch_document` returns the original Korean-language XBRL / iXBRL filing.\n- Officers (임원) and major shareholders (주주) are filed quarterly/annually in mandatory disclosure forms.\n- Stock codes (6-digit) and corp codes (8-digit) are distinct identifiers; use `get_company_profile` to map between them."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for South Korea (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK South Korea agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_kr",
    description=(
        "ADK agent with live access to OPENDART — 금융감독원 전자공시시스템 (South Korea) for company "
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
