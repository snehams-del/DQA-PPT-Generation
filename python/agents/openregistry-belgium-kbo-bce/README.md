# Belgium — KBO/BCE ADK Agent

A Gemini-powered ADK agent with live access to **Crossroads Bank for Enterprises (CBE / KBO / BCE) — FOD Economie** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **BE** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Belgian company · KBO · BCE · Kruispuntbank · Banque-Carrefour des Entreprises.

Example queries:

> *"Find Anheuser-Busch InBev's current bestuurders + all establishments"*
>
> *"Confirm KBC Bank NV's enterprise number and registered office"*
>
> *"List Solvay SA's establishment branches across Belgium"*

## Native ID format

10-digit Belgian enterprise number (e.g. `0403.201.185` formatted, `0403201185` raw — Anheuser-Busch InBev SA/NV). Sample entity: **Anheuser-Busch InBev SA/NV**.

## Quirks of this jurisdiction

- Belgium is bilingual — KBO (Dutch) and BCE (French) are the same register. Company names appear in both languages where applicable.
- **Post CJEU C-37/20** — Belgium's UBO register is access-restricted. `get_persons_with_significant_control` returns 501.
- `list_establishments` returns the company's *vestigingseenheden* / *unités d'établissement* (branches) — useful for disentangling holding-vs-operating entities.
- Officers data covers *bestuurders* / *administrateurs* (directors).

## Run it

```bash
cd python/agents/openregistry-belgium-kbo-bce
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Crossroads Bank for Enterprises (CBE / KBO / BCE) — FOD Economie: <https://kbopub.economie.fgov.be/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
