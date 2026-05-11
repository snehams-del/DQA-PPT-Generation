# Norway — Brreg ADK Agent

A Gemini-powered ADK agent with live access to **Brønnøysund Register Centre (Enhetsregisteret + Foretaksregisteret)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **NO** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Norwegian company · Brreg · Brønnøysundregistrene · Enhetsregisteret · organisasjonsnummer.

Example queries:

> *"Find Equinor ASA's full styre + daglig leder"*
>
> *"List Telenor ASA's major shareholders"*
>
> *"Confirm the operating status of DNB Bank ASA"*

## Native ID format

9-digit Norwegian organisasjonsnummer (e.g. `923609016` Equinor ASA). Sample entity: **Equinor ASA**.

## Quirks of this jurisdiction

- Norway has a **public UBO register** (Reelle Rettighetshavere) — accessible via Brreg. UBO support is on the roadmap.
- `AS` = limited (private), `ASA` = public limited (Allmennaksjeselskap).
- Filings include annual accounts (årsregnskap) deposited at Regnskapsregisteret — separate from the company-status register.
- Officer data covers styre (board) members, daglig leder (CEO), revisor (auditor).

## Run it

```bash
cd python/agents/openregistry-norway-brreg
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Brønnøysund Register Centre (Enhetsregisteret + Foretaksregisteret): <https://www.brreg.no/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
