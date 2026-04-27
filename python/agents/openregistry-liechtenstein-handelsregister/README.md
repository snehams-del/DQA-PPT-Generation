# Liechtenstein — Liechtenstein HR ADK Agent

A Gemini-powered ADK agent with live access to **Handelsregister des Fürstentums Liechtenstein — Amt für Justiz (AJU), Vaduz** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **LI** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Liechtenstein company · Liechtenstein HR · Handelsregister Liechtenstein · FL company · Anstalt.

Example queries:

> *"Find LGT Bank AG in the Liechtenstein Handelsregister"*
>
> *"Look up a Liechtenstein Stiftung by name"*
>
> *"List the latest filings for an Anstalt by FL number"*

## Native ID format

FL-prefix Handelsregister number (e.g. `FL-0001.090.135-8` LGT Bank AG). Sample entity: **LGT Bank AG**.

## Quirks of this jurisdiction

- Liechtenstein has unique entity types: `Anstalt` (establishment), `Stiftung` (foundation), `Treuunternehmen` (trust enterprise) — common in tax-haven structures.
- Liechtenstein UBO data (Tatsächliche Empfänger) is access-restricted to AML-obliged entities.
- Backend is **JSF ViewState** — slow, stateful queries; OpenRegistry runs a dedicated Playwright worker for LI to avoid blocking other traffic.
- Frequently appears in cross-border ownership chains for high-net-worth structures.

## Run it

```bash
cd python/agents/openregistry-liechtenstein-handelsregister
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Handelsregister des Fürstentums Liechtenstein — Amt für Justiz (AJU), Vaduz: <https://www.oera.li/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
