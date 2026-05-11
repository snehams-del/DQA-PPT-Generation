"""ADK agent specialised for Iceland — live access to Fyrirtækjaskrá — Skatturinn (Icelandic Revenue and Customs).

This is the **IS** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to Iceland (IS).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Fyrirtækjaskrá — Skatturinn (Icelandic Revenue and Customs)
ID format: 10-digit Icelandic kennitala (e.g. `5710002400` Landsvirkjun)
Sample entity: Marel hf.
Available tools (8): `search_companies`, `get_company_profile`, `list_filings`, `get_officers`, `get_persons_with_significant_control`, `get_shareholders`, `get_document_metadata`, `fetch_document`
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

JURISDICTION_CODE = "is"
REGISTRY_NAME = "Fyrirtækjaskrá — Skatturinn"

SYSTEM_INSTRUCTION = (
    f"You are a Iceland company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 10-digit Icelandic kennitala (e.g. `5710002400` Landsvirkjun). "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "Iceland only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to Iceland:\n"
    "- Iceland has a **public UBO register** — `get_persons_with_significant_control` is fully supported here (rare in our dataset).\n- `hf.` = public limited; `ehf.` = private limited; `slhf.` = Samvinnufélag (cooperative).\n- Kennitala is a 10-digit ID assigned to both individuals and companies — the format is the same; context distinguishes.\n- Icelandic company names use Icelandic characters (þ, ð, æ); `search_companies` handles ASCII-folded queries."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for Iceland (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK Iceland agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_is",
    description=(
        "ADK agent with live access to Fyrirtækjaskrá — Skatturinn (Iceland) for company "
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
