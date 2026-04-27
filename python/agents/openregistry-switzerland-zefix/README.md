# Switzerland — Zefix ADK Agent

A Gemini-powered ADK agent with live access to **Zefix — Zentraler Firmenindex / Federal Registry of Commerce (Bundesamt für Justiz)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **CH** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Swiss company · Zefix · Schweizer Firma · Handelsregister Schweiz · AG.

Example queries:

> *"Find Nestlé SA on Zefix and pull the Verwaltungsrat (board)"*
>
> *"Confirm Roche Holding AG's UID and canton"*
>
> *"List shareholders of UBS AG (CHE-101.329.561)"*

## Native ID format

Swiss UID `CHE-` prefix (e.g. `CHE-105.916.057` Nestlé SA). Sample entity: **Nestlé SA**.

## Quirks of this jurisdiction

- Zefix federates 26 cantonal Handelsregister offices — the canton appears in every record (e.g. Vaud, Genève, Zürich).
- Switzerland is **not** subject to CJEU C-37/20 (non-EU). UBO data is not in a unified federal register, but officer (Verwaltungsrat) and shareholder data is.
- Languages: records appear in DE/FR/IT depending on canton. `name` may differ across the three.
- UID (`CHE-XXX.XXX.XXX`) is the modern federal identifier; older HR numbers (per canton) are still in some legacy data.

## Run it

```bash
cd python/agents/openregistry-switzerland-zefix
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Zefix — Zentraler Firmenindex / Federal Registry of Commerce (Bundesamt für Justiz): <https://www.zefix.ch/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
