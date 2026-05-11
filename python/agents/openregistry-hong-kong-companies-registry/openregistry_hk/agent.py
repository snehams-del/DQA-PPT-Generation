"""ADK agent specialised for Hong Kong SAR — live access to 公司註冊處 / Companies Registry of the Hong Kong Special Administrative Region.

This is the **HK** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Hong Kong SAR (HK).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: 公司註冊處 / Companies Registry of the Hong Kong Special Administrative Region
ID format: Hong Kong CR number — 7 digits, sometimes prefixed (e.g. `0066011` HSBC Holdings plc HK branch)
Sample entity: HSBC Holdings plc (HK branch)
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

JURISDICTION_CODE = "hk"
REGISTRY_NAME = "Hong Kong Companies Registry (公司註冊處)"

SYSTEM_INSTRUCTION = (
    f"You are a Hong Kong SAR company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: Hong Kong CR number — 7 digits, sometimes prefixed (e.g. `0066011` HSBC Holdings plc HK branch). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Hong Kong SAR only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Hong Kong SAR:\n"
    "- Hong Kong's open data covers basic company status only; full filings (Annual Return NAR1, officer changes) are paid via CR Cyber Search Centre.\n- Hong Kong's Significant Controllers Register (SCR) is **not publicly accessible** — only viewable on-site by AML-obliged entities.\n- Hong Kong is a major holding-company jurisdiction in Asia — note `Hong Kong Ltd` vs. `Foreign Company` (registered under Part 16 of CO).\n- Two language registries — Chinese (Traditional) and English; both names appear."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Hong Kong SAR (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Hong Kong SAR agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_hk",
    description=(
        "ADK agent with live access to Hong Kong Companies Registry (公司註冊處) (Hong Kong SAR) for company "
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
