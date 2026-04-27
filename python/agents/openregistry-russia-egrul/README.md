# Russia — ЕГРЮЛ (FNS) ADK Agent

A Gemini-powered ADK agent with live access to **ЕГРЮЛ / ЕГРИП — Федеральная налоговая служба (ФНС России) + ГИР БО** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **RU** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Russian company · ЕГРЮЛ · ЕГРИП · ОГРН · ИНН.

Example queries:

> *"Pull Sberbank Rossii's full officer + shareholder list"*
>
> *"Find a Russian OOO by ОГРН"*
>
> *"Get latest filings + financial statements for a Russian PAO from ГИР БО"*

## Native ID format

10-digit ОГРН (legal entity) or 13-digit ОГРНИП (sole trader). Sample entity: **Сбербанк России (Sberbank Rossii)**.

## Quirks of this jurisdiction

- Russia's FNS provides the most comprehensive open dataset of any major country — full officers, shareholders, financial filings (ГИР БО) are public.
- **Sanctions context**: many Russian entities are subject to OFAC / EU / UK sanctions. Cross-reference any UBO walk with the relevant sanctions list before action.
- OOO (ООО) = LLC; PAO (ПАО) = public stock company; AO/ZAO (АО/ЗАО) = closed JSC.
- Some data fields are surfaced under 115-FZ art. 6.1 restrictions for sanctioned individuals — those records may show 'данные защищены'.

## Run it

```bash
cd python/agents/openregistry-russia-egrul
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

ЕГРЮЛ / ЕГРИП — Федеральная налоговая служба (ФНС России) + ГИР БО: <https://egrul.nalog.ru/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
