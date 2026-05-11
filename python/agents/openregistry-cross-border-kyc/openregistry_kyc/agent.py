"""ADK agent that gives Gemini live access to 27 national company registries.

OpenRegistry is a free, hosted Streamable-HTTP MCP server that proxies UK
Companies House, Germany Handelsregister, France Sirene + RNE, Italy
InfoCamere via EU BRIS, Spain BORME, Korea OPENDART, plus 21 more — every
tool call is a real-time query against the upstream government API and the
response is returned unmodified.

Anonymous tier requires no signup or API key, so this sample runs out of the
box with only the standard Gemini / Vertex credentials.
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

SYSTEM_INSTRUCTION = (
    "You are a cross-border KYC / due-diligence assistant with live access to "
    "27 national company registries via the OpenRegistry MCP server. "
    "When the user asks about a company, identify the relevant jurisdiction "
    "(ISO 3166-1 alpha-2, e.g. 'gb' for the UK, 'de' for Germany, 'fr' for "
    "France) and use the OpenRegistry tools to look it up directly. Quote the "
    "registry's own field names verbatim (for example, do not normalise the "
    "UK PSC Register's 'nature_of_control' values). When walking corporate "
    "ownership chains across borders, recurse jurisdiction by jurisdiction "
    "until you reach an individual or hit an AML-gated register. If the tool "
    "returns HTTP 501 with an `alternative_url`, surface the alternative "
    "channel to the user — that signals a CJEU C-37/20-restricted register "
    "(DE / ES / IT / NL / LU / AT / MT / PT) which only AML-obliged entities "
    "can query. Always cite the registry and the company identifier you "
    "looked up, so the user can verify against the government source."
)

logger.info("--- 🌍 Loading OpenRegistry MCP toolset (%s)... ---", OPENREGISTRY_MCP_URL)
logger.info("--- 🤖 Creating ADK OpenRegistry KYC agent... ---")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="openregistry_kyc",
    description=(
        "Cross-border KYC / due-diligence agent backed by live data from 27 "
        "national company registries (UK Companies House, Germany "
        "Handelsregister, France Sirene+RNE, Italy InfoCamere via EU BRIS, "
        "Spain BORME, Korea OPENDART, etc.) over the OpenRegistry MCP server."
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=OPENREGISTRY_MCP_URL,
            )
        )
    ],
)
