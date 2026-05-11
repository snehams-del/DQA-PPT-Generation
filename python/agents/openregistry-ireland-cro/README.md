# Ireland — CRO ADK Agent

A Gemini-powered ADK agent with live access to **Companies Registration Office (CRO) — An Oifig Chláraithe Cuideachtaí** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **IE** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Irish company · CRO Ireland · Companies Registration Office Ireland · Irish DAC · Irish PLC.

Example queries:

> *"Find Apple Operations International Limited's CRO record"*
>
> *"List the latest annual return filings for Google Ireland Limited"*
>
> *"Confirm the company status of Stripe Payments Europe Limited"*

## Native ID format

6-digit CRO number (e.g. `462571` Apple Operations International Limited). Sample entity: **Apple Operations International Limited**.

## Quirks of this jurisdiction

- Ireland's RBO (Register of Beneficial Owners) is publicly accessible at https://rbo.gov.ie/ — `get_persons_with_significant_control` is on the roadmap.
- Irish entities are often holding vehicles in cross-border tax structures (Double Irish, Irish DAC, etc.) — note the company type in profile.
- Filings are returned as PDF documents; `fetch_document` is on the roadmap for IE.
- `Designated Activity Company (DAC)` and `Public Limited Company (PLC)` are the most common Irish corporate types.

## Run it

```bash
cd python/agents/openregistry-ireland-cro
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Companies Registration Office (CRO) — An Oifig Chláraithe Cuideachtaí: <https://core.cro.ie/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
