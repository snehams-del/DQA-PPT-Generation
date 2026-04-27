"""ADK agent specialised for Canada (Federal) — live access to Corporations Canada — Innovation, Science and Economic Development Canada (ISED).

This is the **CA** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Canada (Federal) (CA).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Corporations Canada — Innovation, Science and Economic Development Canada (ISED)
ID format: 7-digit federal CBCA number (e.g. `1234567`)
Sample entity: A federal CBCA-incorporated company
Available tools (5): `search_companies`, `get_company_profile`, `list_filings`, `get_officers`, `get_persons_with_significant_control`
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

JURISDICTION_CODE = "ca"
REGISTRY_NAME = "Corporations Canada (CBCA)"

SYSTEM_INSTRUCTION = (
    f"You are a Canada (Federal) company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 7-digit federal CBCA number (e.g. `1234567`). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Canada (Federal) only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Canada (Federal):\n"
    "- Canada has a **federal** register (CBCA) plus 13 separate provincial/territorial registers. This skill is **federal only** — for BC use the BC skill, for NT use the NT skill.\n- CBCA's Individuals with Significant Control (ISC) Register is **publicly searchable** since Jan 2024 — `get_persons_with_significant_control` is supported.\n- Federal and provincial entities are separate; a company may be incorporated federally OR provincially but not both for the same name.\n- ISED's Corporations Canada open dataset is in JSON."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Canada (Federal) (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Canada (Federal) agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_ca",
    description=(
        "ADK agent with live access to Corporations Canada (CBCA) (Canada (Federal)) for company "
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
