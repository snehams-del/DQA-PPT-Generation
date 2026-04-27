# New Zealand — NZ Companies Office ADK Agent

A Gemini-powered ADK agent with live access to **New Zealand Companies Office (Ministry of Business, Innovation & Employment)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **NZ** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: New Zealand company · NZ Companies Office · NZBN · Limited · Kiwi company.

Example queries:

> *"Pull Fonterra Co-operative Group Limited's full director list + shareholders"*
>
> *"List Xero Limited's recent filings"*
>
> *"Search NZ Companies Office for any director named 'Andrew Smith'"*

## Native ID format

7-digit NZBN suffix or 13-digit NZBN (e.g. `9429038949149` Fonterra Co-operative Group Limited). Sample entity: **Fonterra Co-operative Group Limited**.

## Quirks of this jurisdiction

- NZ has full public officer + shareholder data — among the most transparent registers globally.
- NZBN (New Zealand Business Number) is the modern identifier; legacy company numbers (6-digit) still appear in older records.
- Annual return filings include constitution amendments — `fetch_document` returns the raw filing.
- Cross-border structures often use NZ entities — note the `ultimate-holding-company` field in profile.

## Run it

```bash
cd python/agents/openregistry-new-zealand-companies-office
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

New Zealand Companies Office (Ministry of Business, Innovation & Employment): <https://companies-register.companiesoffice.govt.nz/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
