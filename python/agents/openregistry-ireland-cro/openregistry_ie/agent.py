"""ADK agent specialised for Ireland — live access to Companies Registration Office (CRO) — An Oifig Chláraithe Cuideachtaí.

This is the **IE** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Ireland (IE).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Companies Registration Office (CRO) — An Oifig Chláraithe Cuideachtaí
ID format: 6-digit CRO number (e.g. `462571` Apple Operations International Limited)
Sample entity: Apple Operations International Limited
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

JURISDICTION_CODE = "ie"
REGISTRY_NAME = "Companies Registration Office (CRO)"

SYSTEM_INSTRUCTION = (
    f"You are a Ireland company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 6-digit CRO number (e.g. `462571` Apple Operations International Limited). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Ireland only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Ireland:\n"
    "- Ireland's RBO (Register of Beneficial Owners) is publicly accessible at https://rbo.gov.ie/ — `get_persons_with_significant_control` is on the roadmap.\n- Irish entities are often holding vehicles in cross-border tax structures (Double Irish, Irish DAC, etc.) — note the company type in profile.\n- Filings are returned as PDF documents; `fetch_document` is on the roadmap for IE.\n- `Designated Activity Company (DAC)` and `Public Limited Company (PLC)` are the most common Irish corporate types."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Ireland (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Ireland agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_ie",
    description=(
        "ADK agent with live access to Companies Registration Office (CRO) (Ireland) for company "
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
