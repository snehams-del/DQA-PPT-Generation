# Czechia — ARES ADK Agent

A Gemini-powered ADK agent with live access to **Administrativní registr ekonomických subjektů (ARES) — Czech Ministry of Finance** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **CZ** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Czech company · ARES · IČO · Obchodní rejstřík · a.s..

Example queries:

> *"Find ČEZ a.s. in ARES and pull current statutory body"*
>
> *"Search ARES for all Czech political parties registered after 2020"*
>
> *"Look up the Czech address `Václavské náměstí, Praha 1` and list registered businesses there"*

## Native ID format

8-digit IČO (e.g. `45274649` for ČEZ a.s.). Sample entity: **ČEZ a.s.**.

## Quirks of this jurisdiction

- ARES is the umbrella over multiple Czech registers: Obchodní rejstřík (companies), RŽP (trades), RPSH (political parties), RES (statistical), RUIAN (addresses).
- Czech UBO register (Evidence skutečných majitelů) is publicly accessible — UBO support is on the roadmap.
- **Specialised records**: `search_specialised_records({source:"rpsh"})` for political parties; addresses via `search_addresses`. These are unique to ARES coverage.
- Multiple registers means a single legal entity may appear under different IDs across them — `get_code_description` decodes the registry codes.

## Run it

```bash
cd python/agents/openregistry-czechia-ares
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Administrativní registr ekonomických subjektů (ARES) — Czech Ministry of Finance: <https://ares.gov.cz/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
