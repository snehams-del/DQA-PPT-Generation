# France — RNE / Sirene ADK Agent

A Gemini-powered ADK agent with live access to **Recherche d'entreprises (INSEE Sirene + Registre National des Entreprises (RNE) + Répertoire National des Associations (RNA))** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **FR** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: French company · SIREN · SIRET · Sirene · RNE.

Example queries:

> *"Find L'Oréal SA on Sirene and confirm its SIREN + registered office"*
>
> *"Pull current dirigeants of TotalEnergies SE (SIREN 542051180)"*
>
> *"Search for all French SAS with 'AI' in the name registered in 2025"*

## Native ID format

9-digit SIREN (e.g. `552120222` for L'Oréal SA) — extends to 14-digit SIRET for establishments. Sample entity: **L'Oréal SA**.

## Quirks of this jurisdiction

- SIREN (9-digit) identifies the legal entity; SIRET (14-digit) adds 5-digit establishment NIC suffix.
- RNE (since 2023) consolidates the older RCS/RM/RAA registers — single source of truth for corporate filings.
- Officers (`dirigeants`) are surfaced via INSEE; not all SIRENs have them (associations, sole-trader auto-entrepreneurs).
- Financial statements are filed at INPI but typically not surfaced via this open-data API; the BODACC (Bulletin Officiel des Annonces Civiles et Commerciales) is the publication channel.

## Run it

```bash
cd python/agents/openregistry-france-rne-sirene
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Recherche d'entreprises (INSEE Sirene + Registre National des Entreprises (RNE) + Répertoire National des Associations (RNA)): <https://recherche-entreprises.api.gouv.fr/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
