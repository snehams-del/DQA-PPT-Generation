# Italy — Registro Imprese (BRIS) ADK Agent

A Gemini-powered ADK agent with live access to **Registro delle imprese — Camere di Commercio / InfoCamere S.c.p.A., surfaced via EU Business Registers Interconnection System (BRIS) e-Justice gateway** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **IT** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Italian company · Registro Imprese · InfoCamere · BRIS · EU Business Register.

Example queries:

> *"Find Ferrari N.V. on the Italian Registro Imprese via BRIS"*
>
> *"Confirm the legal status of Pirelli & C. S.p.A."*
>
> *"What's the registered address of Generali Assicurazioni S.p.A.?"*

## Native ID format

Italian Codice Fiscale or REA number (REA: `MI-1234567` Milan or `RM-1234567` Rome). Sample entity: **Ferrari N.V.**.

## Quirks of this jurisdiction

- Surfaced through EU BRIS — same gateway used by NL, MT, PT, GR, etc. Italy is a passthrough; full filing detail requires a paid InfoCamere/Camere di Commercio query.
- **Post CJEU C-37/20** — Italy's Registro dei Titolari Effettivi is access-restricted to AML-obliged entities. `get_persons_with_significant_control` returns 501 with `alternative_url`.
- REA numbers are court-prefixed (province code + sequence).
- For full Italian financial statements (deposito di bilanci), the official channel is InfoCamere paid services.

## Run it

```bash
cd python/agents/openregistry-italy-infocamere-bris
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Registro delle imprese — Camere di Commercio / InfoCamere S.c.p.A., surfaced via EU Business Registers Interconnection System (BRIS) e-Justice gateway: <https://e-justice.europa.eu/489/EN/business_registers__search_for_a_company_in_the_eu>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
