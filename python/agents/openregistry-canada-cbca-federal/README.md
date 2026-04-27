# Canada (Federal) — Corporations Canada ADK Agent

A Gemini-powered ADK agent with live access to **Corporations Canada — Innovation, Science and Economic Development Canada (ISED)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **CA** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Canadian company · CBCA · Corporations Canada · Canadian Inc. · Canadian Ltd..

Example queries:

> *"Find a federally-incorporated Canadian company"*
>
> *"Pull the ISC (UBO) list of a federal CBCA company"*
>
> *"List officers of a federally-registered Canadian Inc."*

## Native ID format

7-digit federal CBCA number (e.g. `1234567`). Sample entity: **A federal CBCA-incorporated company**.

## Quirks of this jurisdiction

- Canada has a **federal** register (CBCA) plus 13 separate provincial/territorial registers. This skill is **federal only** — for BC use the BC skill, for NT use the NT skill.
- CBCA's Individuals with Significant Control (ISC) Register is **publicly searchable** since Jan 2024 — `get_persons_with_significant_control` is supported.
- Federal and provincial entities are separate; a company may be incorporated federally OR provincially but not both for the same name.
- ISED's Corporations Canada open dataset is in JSON.

## Run it

```bash
cd python/agents/openregistry-canada-cbca-federal
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Corporations Canada — Innovation, Science and Economic Development Canada (ISED): <https://www.ic.gc.ca/app/scr/cc/CorporationsCanada/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
