# Finland — PRH (YTJ) ADK Agent

A Gemini-powered ADK agent with live access to **Patentti- ja rekisterihallitus (PRH) — avoindata YTJ API** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **FI** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Finnish company · PRH · YTJ · Y-tunnus · Patentti- ja rekisterihallitus.

Example queries:

> *"Pull Nokia Oyj's latest annual report from PRH and parse the iXBRL"*
>
> *"List directors of Kone Oyj"*
>
> *"Search for all Finnish Oy with 'sauna' in the name"*

## Native ID format

Finnish Y-tunnus (8-digit, hyphenated: `0112038-9` Nokia Oyj). Sample entity: **Nokia Oyj**.

## Quirks of this jurisdiction

- Finland's PRH UBO register (Tosiasiallinen edunsaaja) is publicly queryable. Full UBO support on the roadmap.
- `Oy` = private limited; `Oyj` = public limited. Branches show as separate Y-tunnukset.
- Filings include annual reports (tilinpäätös) in iXBRL — `fetch_document` returns raw bytes.
- Company language can be FI / SV / EN — name fields may include all three.

## Run it

```bash
cd python/agents/openregistry-finland-prh
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Patentti- ja rekisterihallitus (PRH) — avoindata YTJ API: <https://www.prh.fi/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
