"""ADK agent specialised for Poland — live access to Krajowy Rejestr Sądowy (KRS) — National Court Register, Polish Ministry of Justice.

This is the **PL** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Poland (PL).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Krajowy Rejestr Sądowy (KRS) — National Court Register, Polish Ministry of Justice
ID format: 10-digit KRS number (e.g. `0000033057` for PKO Bank Polski SA)
Sample entity: PKO Bank Polski SA
Available tools (7): `search_companies`, `get_company_profile`, `list_filings`, `get_officers`, `get_shareholders`, `get_document_metadata`, `fetch_document`
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

JURISDICTION_CODE = "pl"
REGISTRY_NAME = "KRS — Krajowy Rejestr Sądowy"

SYSTEM_INSTRUCTION = (
    f"You are a Poland company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 10-digit KRS number (e.g. `0000033057` for PKO Bank Polski SA). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Poland only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Poland:\n"
    "- KRS distinguishes between sections — *Rejestr Przedsiębiorców* (companies) vs *Rejestr Stowarzyszeń* (associations) vs *Rejestr Dłużników* (debtors register).\n- Polish UBO data is publicly queryable via Centralny Rejestr Beneficjentów Rzeczywistych (CRBR) — exposed via `get_persons_with_significant_control` is on the roadmap; today use `get_shareholders` for legal owners.\n- Branches of foreign companies (`oddział zagraniczny`) appear in KRS but typically don't file local Polish accounts.\n- Filings are NIP/REGON-stamped; `fetch_document` returns the raw KRS document image."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Poland (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Poland agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_pl",
    description=(
        "ADK agent with live access to KRS — Krajowy Rejestr Sądowy (Poland) for company "
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
