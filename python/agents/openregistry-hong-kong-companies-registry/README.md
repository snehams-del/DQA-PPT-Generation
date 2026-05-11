# Hong Kong SAR — HK CR ADK Agent

A Gemini-powered ADK agent with live access to **公司註冊處 / Companies Registry of the Hong Kong Special Administrative Region** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **HK** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Hong Kong company · HK Companies Registry · 公司註冊處 · HK Limited · Hong Kong Ltd.

Example queries:

> *"Look up HSBC Holdings plc's HK branch"*
>
> *"Confirm the legal status of Tencent (HK) Holdings Limited"*
>
> *"Find Alibaba Group's Hong Kong incorporated entity"*

## Native ID format

Hong Kong CR number — 7 digits, sometimes prefixed (e.g. `0066011` HSBC Holdings plc HK branch). Sample entity: **HSBC Holdings plc (HK branch)**.

## Quirks of this jurisdiction

- Hong Kong's open data covers basic company status only; full filings (Annual Return NAR1, officer changes) are paid via CR Cyber Search Centre.
- Hong Kong's Significant Controllers Register (SCR) is **not publicly accessible** — only viewable on-site by AML-obliged entities.
- Hong Kong is a major holding-company jurisdiction in Asia — note `Hong Kong Ltd` vs. `Foreign Company` (registered under Part 16 of CO).
- Two language registries — Chinese (Traditional) and English; both names appear.

## Run it

```bash
cd python/agents/openregistry-hong-kong-companies-registry
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

公司註冊處 / Companies Registry of the Hong Kong Special Administrative Region: <https://www.cr.gov.hk/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
