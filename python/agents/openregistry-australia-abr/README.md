# Australia — ABR / ASIC ADK Agent

A Gemini-powered ADK agent with live access to **Australian Business Register (ABR) — ABN Lookup, Australian Taxation Office** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **AU** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Australian company · ABN · ACN · ABR · ABN Lookup.

Example queries:

> *"Find BHP Group Limited's ABN and confirm GST/operating status"*
>
> *"Look up Commonwealth Bank of Australia by ABN"*
>
> *"Search for all Pty Ltd with 'Coal' in the name in NSW"*

## Native ID format

11-digit ABN or 9-digit ACN (e.g. ABN `33 123 456 789`, ACN `004 028 077` for BHP Group Limited). Sample entity: **BHP Group Limited**.

## Quirks of this jurisdiction

- ABR (ABN Lookup) is the open public dataset; full ASIC company data (officers, shareholders, registered addresses) is paid-only via ASIC's commercial channels.
- ABN ≠ ACN. ABN is for tax/business; ACN is for incorporated companies (subset of ABNs).
- GST registration date is in the ABR record — useful indicator of operational status.
- Indigenous corporations (CATSI) and partnerships also have ABNs — filter by `entity_type` in profile.

## Run it

```bash
cd python/agents/openregistry-australia-abr
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Australian Business Register (ABR) — ABN Lookup, Australian Taxation Office: <https://abr.business.gov.au/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
