"""ADK agent specialised for France — live access to Recherche d'entreprises (INSEE Sirene + Registre National des Entreprises (RNE) + Répertoire National des Associations (RNA)).

This is the **FR** single-jurisdiction variant of the OpenRegistry
agent family. It pre-binds the MCP toolset to the OpenRegistry hosted server
and the agent's system prompt narrows Gemini's focus to France (FR).
For multi-jurisdiction / cross-border ownership-chain walks, see the sibling
`openregistry-cross-border-kyc` sample.

Native registry: Recherche d'entreprises (INSEE Sirene + Registre National des Entreprises (RNE) + Répertoire National des Associations (RNA))
ID format: 9-digit SIREN (e.g. `552120222` for L'Oréal SA) — extends to 14-digit SIRET for establishments
Sample entity: L'Oréal SA
Available tools (3): `search_companies`, `get_company_profile`, `get_officers`
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

JURISDICTION_CODE = "fr"
REGISTRY_NAME = "INSEE Sirene + RNE"

SYSTEM_INSTRUCTION = (
    f"You are a France company-data assistant with live access to "
    f"{REGISTRY_NAME} via the OpenRegistry MCP server. Whenever you call a "
    f"tool, pass jurisdiction='{JURISDICTION_CODE}' so the query targets "
    f"the right register. ID format for this jurisdiction: 9-digit SIREN (e.g. `552120222` for L'Oréal SA) — extends to 14-digit SIRET for establishments. "
    "Quote the registry's own field names verbatim — do not rename, "
    "translate, or summarise raw upstream values. If the user asks for a "
    "company in a different country, clarify that this agent specialises in "
    "France only and recommend the cross-border sibling agent." + (
    "\n\nQuirks specific to France:\n"
    "- SIREN (9-digit) identifies the legal entity; SIRET (14-digit) adds 5-digit establishment NIC suffix.\n- RNE (since 2023) consolidates the older RCS/RM/RAA registers — single source of truth for corporate filings.\n- Officers (`dirigeants`) are surfaced via INSEE; not all SIRENs have them (associations, sole-trader auto-entrepreneurs).\n- Financial statements are filed at INPI but typically not surfaced via this open-data API; the BODACC (Bulletin Officiel des Annonces Civiles et Commerciales) is the publication channel."
)
)

connection_headers = {"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"} if OPENREGISTRY_TOKEN else None

logger.info("--- 🌍 Loading OpenRegistry MCP toolset for France (%s)... ---", JURISDICTION_CODE)
logger.info("--- 🤖 Creating ADK France agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_fr",
    description=(
        "ADK agent with live access to INSEE Sirene + RNE (France) for company "
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
