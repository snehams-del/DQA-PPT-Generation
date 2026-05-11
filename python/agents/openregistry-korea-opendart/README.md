# South Korea — OPENDART (전자공시) ADK Agent

A Gemini-powered ADK agent with live access to **금융감독원 전자공시시스템 OPENDART (Financial Supervisory Service — Electronic Disclosure System)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **KR** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Korean company · OpenDART · DART · 전자공시 · 금융감독원.

Example queries:

> *"Pull Samsung Electronics' latest quarterly disclosure with full financials"*
>
> *"List all Hyundai Motor (005380) major shareholders disclosed in the last annual filing"*
>
> *"Find LG Energy Solution's audit report from OpenDART"*

## Native ID format

DART corp_code (8-digit) or stock_code (6-digit, e.g. `005930` for Samsung Electronics). Sample entity: **Samsung Electronics Co., Ltd. (삼성전자)**.

## Quirks of this jurisdiction

- OPENDART is the public-disclosure system for **listed and large unlisted Korean firms** — not all Korean companies appear; private SMEs are not in scope.
- `get_financials` returns IFRS-formatted statements (KIFRS). `fetch_document` returns the original Korean-language XBRL / iXBRL filing.
- Officers (임원) and major shareholders (주주) are filed quarterly/annually in mandatory disclosure forms.
- Stock codes (6-digit) and corp codes (8-digit) are distinct identifiers; use `get_company_profile` to map between them.

## Run it

```bash
cd python/agents/openregistry-korea-opendart
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

금융감독원 전자공시시스템 OPENDART (Financial Supervisory Service — Electronic Disclosure System): <https://opendart.fss.or.kr/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
