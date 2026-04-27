# Spain — BORME ADK Agent

A Gemini-powered ADK agent with live access to **Boletín Oficial del Registro Mercantil (BORME) — Agencia Estatal Boletín Oficial del Estado (AEBOE)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **ES** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Spanish company · BORME · Registro Mercantil · S.A. · S.L..

Example queries:

> *"Find Inditex SA in BORME and pull its current administradores"*
>
> *"List BORME actos inscritos for Telefónica SA in the last 90 days"*
>
> *"Download the BORME daily batch PDF for 2026-04-15"*

## Native ID format

BORME announcement ID (e.g. `BORME-A-2025-001-08` section A, year 2025, batch 001, entry 08), or full-name search. Sample entity: **Inditex SA**.

## Quirks of this jurisdiction

- BORME is published as **daily change batches** (Boletín daily PDF + structured `actos` data). `list_change_batches` enumerates daily batches; `list_actos_inscritos` returns the registered acts for a date range.
- **Post CJEU C-37/20** — Spain's Registro de Titulares Reales is access-restricted. `get_persons_with_significant_control` returns 501 with `alternative_url`. Use `get_shareholders` (legal owners only).
- `get_officers` mines the `actos inscritos` for current administrators.
- Backed by a 17-year ES BORME full-text index (~9.39M `actos`) hosted server-side for fast historical queries.

## Run it

```bash
cd python/agents/openregistry-spain-borme
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Boletín Oficial del Registro Mercantil (BORME) — Agencia Estatal Boletín Oficial del Estado (AEBOE): <https://www.boe.es/diario_borme/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
