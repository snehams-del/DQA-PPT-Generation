# Netherlands — KVK ADK Agent

A Gemini-powered ADK agent with live access to **Kamer van Koophandel (KVK) — Handelsregister, Open Dataset APIs** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **NL** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Dutch company · KVK · Kamer van Koophandel · Handelsregister Nederland · BV.

Example queries:

> *"Pull ASML Holding NV's latest deposited annual accounts in iXBRL format"*
>
> *"Confirm the legal status of Adyen NV (KVK 34259528)"*
>
> *"Get the most recent filings list for ING Groep NV"*

## Native ID format

8-digit KVK number (e.g. `33002587` for ASML Holding NV). Sample entity: **ASML Holding NV**.

## Quirks of this jurisdiction

- **Post CJEU C-37/20** — the KVK UBO-register is access-restricted to AML-obliged entities. `get_persons_with_significant_control` returns 501 with `alternative_url`.
- Officer data is not in the KVK Open Dataset; for directors of Dutch entities the official paid channel is KVK Handelsregister Inzage.
- Financial statements are filed at KVK as iXBRL (jaarrekeningen). `get_financials` returns the latest deposited annual accounts.
- Dutch holding companies (BV/NV) are common in cross-border structures — use this as a hop in UBO chains.

## Run it

```bash
cd python/agents/openregistry-netherlands-kvk
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Kamer van Koophandel (KVK) — Handelsregister, Open Dataset APIs: <https://www.kvk.nl/zoeken/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
