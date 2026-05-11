"""ADK agent specialised for Germany — live access to Gemeinsames Registerportal der Länder — Handelsregister (Amtsgericht Registergerichte der 16 Länder).

This is the **DE** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Germany (DE).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Gemeinsames Registerportal der Länder — Handelsregister (Amtsgericht Registergerichte der 16 Länder)
ID format: Court-prefixed Handelsregister number (e.g. `HRB 123456 B` Berlin, `HRB 12345 München`)
Sample entity: Deutsche Bank AG
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

JURISDICTION_CODE = "de"
REGISTRY_NAME = "Handelsregister"

SYSTEM_INSTRUCTION = (
    f"You are a Germany company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: Court-prefixed Handelsregister number (e.g. `HRB 123456 B` Berlin, `HRB 12345 München`). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Germany only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Germany:\n"
    "- **Post CJEU C-37/20 (Nov 2022)** — the Transparenzregister (Germany's UBO register) became access-restricted to AML-obliged entities. `get_persons_with_significant_control` is *not* available for DE. Use `get_shareholders` for legal-shareholder data, but note shareholders ≠ beneficial owners.\n- Handelsregister filings are mainly iXBRL annual reports (Bundesanzeiger). `fetch_document` returns raw bytes.\n- Court (Amtsgericht) prefixes the HRB number — region matters for disambiguation.\n- Liechtenstein and Austria HRs are separate from this — see those skills."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Germany (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Germany agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_de",
    description=(
        "ADK agent with live access to Handelsregister (Germany) for company "
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
