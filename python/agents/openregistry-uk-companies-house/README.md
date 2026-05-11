# United Kingdom — Companies House ADK Agent

A Gemini-powered ADK agent with live access to **Companies House (UK Department for Business and Trade)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **GB** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: UK company · British limited company · Companies House · Companies House UK · UK Ltd.

Example queries:

> *"Walk Revolut Ltd's PSC chain across borders"*
>
> *"Pull all current directors of Tesco PLC (00445790)"*
>
> *"List the latest 5 filings for AstraZeneca PLC and download the most recent annual report"*

## Native ID format

8-character alphanumeric (e.g. `00445790` for Tesco PLC, `08804411` for Revolut Ltd). Sample entity: **Revolut Ltd**.

## Quirks of this jurisdiction

- PSC Register data is publicly accessible — no AML gating in the UK.
- `nature_of_control` strings are stable enums (e.g. `ownership-of-shares-75-to-100-percent`, `voting-rights-25-to-50-percent`) — useful for downstream pipelines.
- Companies House preserves both legacy and current name spellings; we return verbatim.
- FC-prefixed numbers indicate UK branches of overseas companies — they typically don't file local accounts.

## Run it

```bash
cd python/agents/openregistry-uk-companies-house
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Companies House (UK Department for Business and Trade): <https://find-and-update.company-information.service.gov.uk/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
