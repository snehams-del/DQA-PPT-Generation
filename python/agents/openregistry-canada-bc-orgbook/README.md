# Canada (British Columbia) — OrgBook BC ADK Agent

A Gemini-powered ADK agent with live access to **BC Registries (OrgBook BC verifiable-credential ledger, Province of British Columbia)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **CA-BC** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: BC company · British Columbia company · OrgBook BC · Canadian BC · BC Ltd.

Example queries:

> *"Find a BC Limited Company by name on OrgBook"*
>
> *"Confirm the registration status of a BC company"*
>
> *"Look up a verifiable credential issued for a BC entity"*

## Native ID format

BC company number (e.g. `BC1234567` BC-incorporated, `A0099999` extra-provincial). Sample entity: **A BC-incorporated company**.

## Quirks of this jurisdiction

- OrgBook BC is built on **verifiable-credential ledger** technology (Hyperledger Indy) — credentials are cryptographically signed.
- BC has many extra-provincial entities (companies registered elsewhere doing business in BC).
- BC corporate types: `BC Limited Company`, `Cooperative`, `Society`, `Sole Proprietor`.
- Officers + UBO data is paid via BC Online — open dataset is basic status only.

## Run it

```bash
cd python/agents/openregistry-canada-bc-orgbook
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

BC Registries (OrgBook BC verifiable-credential ledger, Province of British Columbia): <https://orgbook.gov.bc.ca/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
