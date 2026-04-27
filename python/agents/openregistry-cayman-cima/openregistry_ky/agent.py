"""ADK agent specialised for Cayman Islands — live access to Cayman Islands Monetary Authority (CIMA) — Regulated Entities Register.

This is the **KY** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Cayman Islands (KY).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Cayman Islands Monetary Authority (CIMA) — Regulated Entities Register
ID format: CIMA licence number (e.g. `123456` for a regulated mutual fund)
Sample entity: A Cayman regulated mutual fund
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

JURISDICTION_CODE = "ky"
REGISTRY_NAME = "CIMA — Cayman Islands Monetary Authority"

SYSTEM_INSTRUCTION = (
    f"You are a Cayman Islands company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: CIMA licence number (e.g. `123456` for a regulated mutual fund). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Cayman Islands only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Cayman Islands:\n"
    "- **Paid-tier only** — CIMA / Cayman Companies Registry data requires Pro / Max / Enterprise. Anonymous + Free tiers receive `402 Payment Required`.\n- Coverage is **regulated entities** (mutual funds, banks, insurers, TCSPs) via CIMA — not all Cayman incorporations.\n- Cayman BOTA register (Beneficial Ownership Transparency Act, in force 2024) is access-restricted to *legitimate-interest* requesters — surfaced via `alternative_url`.\n- Common entity types: Exempted Company, Exempted LP, Segregated Portfolio Company (SPC)."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Cayman Islands (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Cayman Islands agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_ky",
    description=(
        "ADK agent with live access to CIMA — Cayman Islands Monetary Authority (Cayman Islands) for company "
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
