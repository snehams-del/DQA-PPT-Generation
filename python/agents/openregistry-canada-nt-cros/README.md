# Canada (Northwest Territories) — CROS-RSEL NT ADK Agent

A Gemini-powered ADK agent with live access to **Corporate Registries Online System (CROS-RSEL) — NWT Department of Justice** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **CA-NT** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: NWT company · Northwest Territories company · CROS · RSEL · NT corporate registry.

Example queries:

> *"Search NT corporate registry for a company name"*
>
> *"Confirm an NT-registered name's existence"*

## Native ID format

NT corporate registry number. Sample entity: **An NT-incorporated company**.

## Quirks of this jurisdiction

- Smallest jurisdiction in our coverage — search-only; full profiles and filings require manual submission to NT Department of Justice.
- Common for resource-extraction (mining) and Indigenous corporations operating in the NT.
- Federal Canadian (CBCA) and other provincial corps that operate in NT must register separately as extra-provincial.

## Run it

```bash
cd python/agents/openregistry-canada-nt-cros
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Corporate Registries Online System (CROS-RSEL) — NWT Department of Justice: <https://www.justice.gov.nt.ca/en/corporate-registries/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
