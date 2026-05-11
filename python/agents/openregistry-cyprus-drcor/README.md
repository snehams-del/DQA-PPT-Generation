# Cyprus — DRCOR Cyprus ADK Agent

A Gemini-powered ADK agent with live access to **Cyprus Department of Registrar of Companies (DRCOR)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **CY** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Cyprus company · DRCOR · Cyprus Registrar · HE prefix · Cyprus Ltd.

Example queries:

> *"Find Bank of Cyprus PCL on DRCOR"*
>
> *"Confirm the legal status of a Cyprus HE company by number"*
>
> *"Search Cyprus Ltd by name"*

## Native ID format

Cyprus CR number with optional letter prefix (e.g. `HE 1234`). Sample entity: **Bank of Cyprus Public Company Ltd**.

## Quirks of this jurisdiction

- Cyprus is a major holding-company jurisdiction (post-Brexit, EU-aligned, English law-influenced).
- Cyprus UBO Register is access-restricted to AML-obliged entities.
- Common prefixes: `HE` (companies), `EE` (partnerships), `TS` (trusts).
- Open data covers basic status only; full filings + officers are paid via DRCOR e-search.

## Run it

```bash
cd python/agents/openregistry-cyprus-drcor
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Cyprus Department of Registrar of Companies (DRCOR): <https://www.companies.gov.cy/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
