# 🌍 OpenRegistry Cross-Border KYC Agent (ADK + MCP)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-ADK-4285F4.svg)](https://github.com/google/adk-python)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A Gemini-powered ADK agent with **live access to 27 national company registries** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server — UK Companies House, Germany Handelsregister, France Sirene + RNE, Italy InfoCamere via EU BRIS, Spain BORME, Korea OPENDART, plus 21 more. Every tool call is a real-time query against the upstream government API; responses come back **unmodified**, with every field name, status string, and raw filing byte preserved verbatim.

## What it does

Out of the box the agent answers questions like:

- *"Walk Tesco PLC's PSC chain — who actually owns it?"*
- *"Find Inditex SA on Spanish BORME and pull the most recent administradores filings."*
- *"Pull Samsung Electronics' latest annual disclosure from Korean OpenDART."*
- *"Search Polish KRS for sp. z o.o. with 'AI' in the name registered after 2024."*
- *"For an EU/UK Ltd, walk corporate ownership across jurisdictions until you reach an individual or an AML-gated register."*

When the answer crosses a CJEU C-37/20–restricted UBO register (DE, ES, IT, NL, LU, AT, MT, PT), the agent surfaces the upstream `alternative_url` so the user knows which AML-obliged-entity channel to use next, instead of silently failing or substituting commercial-aggregator data.

## Why MCP (and not a custom tool function)?

OpenRegistry's API surface is large — about 30 tools across the 27 registries — and updates as new countries come online. Wiring it as a Streamable-HTTP MCP server means the agent **discovers tools at runtime** via the MCP `tools/list` call, so this sample stays small (~70 lines) and you don't have to update it when the registry grows.

```python
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

tools = [
    MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://openregistry.sophymarine.com/mcp",
        )
    )
]
```

That's the entire integration. The `MCPToolset` instance behaves like any other ADK tool — pass it to your `LlmAgent(tools=[...])` and Gemini sees ~30 first-class tools at function-calling time.

## Run it

### 1. Prerequisites

- Python 3.10+
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- (Optional) Vertex AI project — only needed if you want to deploy to Agent Engine; not needed for local runs

### 2. Install + configure

```bash
cd python/agents/openregistry-cross-border-kyc
cp .env.example .env
# edit .env, set GOOGLE_API_KEY=...
pip install -e .
```

### 3. Run interactively

From the `python/agents/openregistry-cross-border-kyc/` directory:

```bash
adk run .
```

Or with the ADK web UI:

```bash
adk web
```

Then ask:

> Find Tesco PLC on Companies House (jurisdiction gb) and quote its current directors with the exact upstream field names.

You should see Gemini call OpenRegistry's `search_companies` and `get_officers` tools live, then summarise.

## OpenRegistry tier and rate limits

The default MCP URL (`https://openregistry.sophymarine.com/mcp`) is the **anonymous tier** — no signup, no API key, no client-side OAuth dance. Limits:

| Tier | Cost | Rate limit | Cross-border fan-out |
| --- | --- | --- | --- |
| Anonymous | Free | 20 req/min/IP | 3 countries / 60s |
| Pro | $9/mo | 180 req/min/user | 10 countries / 60s |
| Max | $29/mo | 900 req/min/user | 30 countries / 60s |
| Enterprise | Contact | 3000 req/min/user | unlimited |

For batch onboarding flows, complete the OAuth 2.1 flow at [openregistry.sophymarine.com/account](https://openregistry.sophymarine.com/account) and pass the resulting bearer token via `StreamableHTTPConnectionParams(headers={"Authorization": f"Bearer {OPENREGISTRY_TOKEN}"})`.

## Statutorily restricted registers (good to know)

After [CJEU ruling C-37/20](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A62020CJ0037) (November 2022), beneficial-ownership registers in **DE / ES / IT / NL / LU / AT / MT / PT** became access-restricted to AML-obliged entities. OpenRegistry doesn't proxy these — it returns HTTP 501 with an `alternative_url` pointing at the statutory portal. The agent's system prompt teaches it to surface this signal verbatim instead of silently failing.

## Resources

- OpenRegistry docs: <https://openregistry.sophymarine.com/docs/integrations/google-adk>
- 40 Claude Agent Skills (drop-in workflows) at the OpenRegistry GitHub repo: <https://github.com/sophymarine/openregistry/tree/main/skills>
- Live capability matrix per jurisdiction: call `list_jurisdictions` from the running agent.

## License

Apache 2.0 — same as the rest of `google/adk-samples`.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com); the agent itself is contributed under Apache 2.0 with copyright assigned to Google for the purpose of inclusion in this samples repository.
