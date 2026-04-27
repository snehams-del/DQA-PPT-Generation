# Cayman Islands — CIMA ADK Agent

A Gemini-powered ADK agent with live access to **Cayman Islands Monetary Authority (CIMA) — Regulated Entities Register** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **KY** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Cayman company · Cayman Islands fund · CIMA · KY fund · Cayman Limited Partnership.

Example queries:

> *"Look up a CIMA-regulated Cayman mutual fund (paid tier)"*
>
> *"Confirm a Cayman SPC's regulatory status"*
>
> *"Find a Cayman LP by manager name"*

## Native ID format

CIMA licence number (e.g. `123456` for a regulated mutual fund). Sample entity: **A Cayman regulated mutual fund**.

## Quirks of this jurisdiction

- **Paid-tier only** — CIMA / Cayman Companies Registry data requires Pro / Max / Enterprise. Anonymous + Free tiers receive `402 Payment Required`.
- Coverage is **regulated entities** (mutual funds, banks, insurers, TCSPs) via CIMA — not all Cayman incorporations.
- Cayman BOTA register (Beneficial Ownership Transparency Act, in force 2024) is access-restricted to *legitimate-interest* requesters — surfaced via `alternative_url`.
- Common entity types: Exempted Company, Exempted LP, Segregated Portfolio Company (SPC).

## Run it

```bash
cd python/agents/openregistry-cayman-cima
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Cayman Islands Monetary Authority (CIMA) — Regulated Entities Register: <https://www.cima.ky/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
