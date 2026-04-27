"""ADK agent specialised for Netherlands — live access to Kamer van Koophandel (KVK) — Handelsregister, Open Dataset APIs.

This is the **NL** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Netherlands (NL).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Kamer van Koophandel (KVK) — Handelsregister, Open Dataset APIs
ID format: 8-digit KVK number (e.g. `33002587` for ASML Holding NV)
Sample entity: ASML Holding NV
Available tools (3): `get_company_profile`, `list_filings`, `get_financials`
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

JURISDICTION_CODE = "nl"
REGISTRY_NAME = "KVK Handelsregister"

SYSTEM_INSTRUCTION = (
    f"You are a Netherlands company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 8-digit KVK number (e.g. `33002587` for ASML Holding NV). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Netherlands only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Netherlands:\n"
    "- **Post CJEU C-37/20** — the KVK UBO-register is access-restricted to AML-obliged entities. `get_persons_with_significant_control` returns 501 with `alternative_url`.\n- Officer data is not in the KVK Open Dataset; for directors of Dutch entities the official paid channel is KVK Handelsregister Inzage.\n- Financial statements are filed at KVK as iXBRL (jaarrekeningen). `get_financials` returns the latest deposited annual accounts.\n- Dutch holding companies (BV/NV) are common in cross-border structures — use this as a hop in UBO chains."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Netherlands (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Netherlands agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_nl",
    description=(
        "ADK agent with live access to KVK Handelsregister (Netherlands) for company "
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
