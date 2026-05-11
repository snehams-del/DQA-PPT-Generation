# Mexico — PSM Mexico ADK Agent

A Gemini-powered ADK agent with live access to **Sistema Electrónico de Publicaciones de Sociedades Mercantiles (PSM), Secretaría de Economía (SE)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **MX** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Mexican company · PSM · Sistema Electrónico · Secretaría de Economía · S.A. de C.V..

Example queries:

> *"Search PSM for any publication mentioning a Mexican S.A. de C.V."*
>
> *"Download a PSM corporate-acts publication"*
>
> *"List recent PSM filings"*

## Native ID format

PSM publication ID per filing; companies are identified by name + tax ID (RFC). Sample entity: **A Mexican S.A. de C.V.**.

## Quirks of this jurisdiction

- PSM is the **publication channel** (like Spanish BORME), not the company register itself — Mexican companies file at state-level Registros Públicos de Comercio (RPC).
- PSM publishes corporate acts: incorporations, mergers, dissolutions, etc. `fetch_document` returns the raw publication.
- Mexican company types: `S.A. de C.V.` (variable-capital limited), `S.A.P.I.` (investment), `S. de R.L. de C.V.`.
- RFC (Registro Federal de Contribuyentes) is the tax identifier — separate from PSM publication IDs.

## Run it

```bash
cd python/agents/openregistry-mexico-psm
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Sistema Electrónico de Publicaciones de Sociedades Mercantiles (PSM), Secretaría de Economía (SE): <https://psm.economia.gob.mx/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
