"""ADK agent specialised for Canada (Northwest Territories) — live access to Corporate Registries Online System (CROS-RSEL) — NWT Department of Justice.

This is the **CA-NT** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Canada (Northwest Territories) (CA-NT).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Corporate Registries Online System (CROS-RSEL) — NWT Department of Justice
ID format: NT corporate registry number
Sample entity: An NT-incorporated company
Available tools (1): `search_companies`
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

JURISDICTION_CODE = "ca-nt"
REGISTRY_NAME = "CROS-RSEL — Corporate Registries Online (NT)"

SYSTEM_INSTRUCTION = (
    f"You are a Canada (Northwest Territories) company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: NT corporate registry number. "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Canada (Northwest Territories) only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Canada (Northwest Territories):\n"
    "- Smallest jurisdiction in our coverage — search-only; full profiles and filings require manual submission to NT Department of Justice.\n- Common for resource-extraction (mining) and Indigenous corporations operating in the NT.\n- Federal Canadian (CBCA) and other provincial corps that operate in NT must register separately as extra-provincial."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Canada (Northwest Territories) (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Canada (Northwest Territories) agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_ca_nt",
    description=(
        "ADK agent with live access to CROS-RSEL — Corporate Registries Online (NT) (Canada (Northwest Territories)) for company "
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
