# Monaco — RCI Monaco ADK Agent

A Gemini-powered ADK agent with live access to **Répertoire du Commerce et de l'Industrie (RCI) — Direction du Développement Économique (DDE), Gouvernement Princier de Monaco** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **MC** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Monaco company · RCI Monaco · Répertoire du Commerce · SAM · SARL Monaco.

Example queries:

> *"Find Société des Bains de Mer's directors"*
>
> *"List recent filings for any Monaco SAM with 'Yacht' in the name"*
>
> *"Confirm the registered office of a Monaco SARL by RCI number"*

## Native ID format

RCI number (e.g. `99 S 03847` formatted, sequential). Sample entity: **Société des Bains de Mer SA**.

## Quirks of this jurisdiction

- Monaco is a small jurisdiction — every company has a personal touch in the filings.
- `SAM` (Société Anonyme Monégasque) is the local public-limited type; `SARL` is private.
- Monaco's UBO register exists but is access-restricted; this skill returns the legal-shareholder data.
- Tax-haven angle: many Monaco entities are nominee structures; cross-reference with French RNE / Italian InfoCamere for parents.

## Run it

```bash
cd python/agents/openregistry-monaco-rci
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Répertoire du Commerce et de l'Industrie (RCI) — Direction du Développement Économique (DDE), Gouvernement Princier de Monaco: <https://service-public-entreprises.gouv.mc/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
