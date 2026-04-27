# Poland — KRS ADK Agent

A Gemini-powered ADK agent with live access to **Krajowy Rejestr Sądowy (KRS) — National Court Register, Polish Ministry of Justice** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **PL** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Polish company · KRS · Krajowy Rejestr Sądowy · Polish sp. z o.o. · Polish SA.

Example queries:

> *"Find PKO Bank Polski SA in KRS and pull current directors"*
>
> *"List the latest filings for KGHM Polska Miedź SA (0000023302)"*
>
> *"Search for all Polish sp. z o.o. with 'AI' in the name registered after 2024"*

## Native ID format

10-digit KRS number (e.g. `0000033057` for PKO Bank Polski SA). Sample entity: **PKO Bank Polski SA**.

## Quirks of this jurisdiction

- KRS distinguishes between sections — *Rejestr Przedsiębiorców* (companies) vs *Rejestr Stowarzyszeń* (associations) vs *Rejestr Dłużników* (debtors register).
- Polish UBO data is publicly queryable via Centralny Rejestr Beneficjentów Rzeczywistych (CRBR) — exposed via `get_persons_with_significant_control` is on the roadmap; today use `get_shareholders` for legal owners.
- Branches of foreign companies (`oddział zagraniczny`) appear in KRS but typically don't file local Polish accounts.
- Filings are NIP/REGON-stamped; `fetch_document` returns the raw KRS document image.

## Run it

```bash
cd python/agents/openregistry-poland-krs
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Krajowy Rejestr Sądowy (KRS) — National Court Register, Polish Ministry of Justice: <https://wyszukiwarka-krs.ms.gov.pl/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
