# Germany — Handelsregister ADK Agent

A Gemini-powered ADK agent with live access to **Gemeinsames Registerportal der Länder — Handelsregister (Amtsgericht Registergerichte der 16 Länder)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **DE** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: German company · Handelsregister · AG · GmbH · KG.

Example queries:

> *"Pull the latest annual report for Deutsche Bank AG and extract the iXBRL financial statements"*
>
> *"List the directors of Volkswagen AG from Handelsregister"*
>
> *"What's the legal shareholder structure of Allianz SE? (Note: not UBO — see notes)"*

## Native ID format

Court-prefixed Handelsregister number (e.g. `HRB 123456 B` Berlin, `HRB 12345 München`). Sample entity: **Deutsche Bank AG**.

## Quirks of this jurisdiction

- **Post CJEU C-37/20 (Nov 2022)** — the Transparenzregister (Germany's UBO register) became access-restricted to AML-obliged entities. `get_persons_with_significant_control` is *not* available for DE. Use `get_shareholders` for legal-shareholder data, but note shareholders ≠ beneficial owners.
- Handelsregister filings are mainly iXBRL annual reports (Bundesanzeiger). `fetch_document` returns raw bytes.
- Court (Amtsgericht) prefixes the HRB number — region matters for disambiguation.
- Liechtenstein and Austria HRs are separate from this — see those skills.

## Run it

```bash
cd python/agents/openregistry-germany-handelsregister
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Gemeinsames Registerportal der Länder — Handelsregister (Amtsgericht Registergerichte der 16 Länder): <https://www.handelsregister.de/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
