# Isle of Man — IoM CR ADK Agent

A Gemini-powered ADK agent with live access to **Isle of Man Companies Registry — Department for Enterprise (DED)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **IM** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Isle of Man company · IoM CR · Manx company · IoM Limited · IoM 2006 Act.

Example queries:

> *"List the latest filings for an Isle of Man 2006 Act company"*
>
> *"Find an IoM Limited by company number"*
>
> *"Confirm a Manx company's registered agent"*

## Native ID format

IoM Companies Act number — 6 digits + letter (e.g. `001234V` for 2006-Act companies). Sample entity: **Sample Isle of Man Company Limited**.

## Quirks of this jurisdiction

- Two corporate regimes coexist: **Companies Act 1931** (older, full filings) vs **Companies Act 2006** (newer, slimmer filings).
- IoM is a self-governing British Crown Dependency — common in cross-border holding structures.
- UBO register exists but is access-restricted to authorities + AML-obliged entities.
- Filings include annual returns and special resolutions — `fetch_document` returns the raw PDF.

## Run it

```bash
cd python/agents/openregistry-isle-of-man-companies-registry
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Isle of Man Companies Registry — Department for Enterprise (DED): <https://services.gov.im/ded/services/companiesregistry/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
