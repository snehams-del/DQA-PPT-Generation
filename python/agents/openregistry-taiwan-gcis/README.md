# Taiwan — GCIS (商工登記) ADK Agent

A Gemini-powered ADK agent with live access to **經濟部商工登記公示資料 (Ministry of Economic Affairs, Department of Commerce) — GCIS open data** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **TW** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Taiwan company · GCIS · 商工登記 · 統一編號 · 統編.

Example queries:

> *"Find TSMC's full board (董事會) from GCIS"*
>
> *"Search GCIS for all Taiwanese 公司 with '半導體' in the name"*
>
> *"Confirm Foxconn (Hon Hai)'s registered address"*

## Native ID format

8-digit Taiwanese 統一編號 / Unified Business Number (e.g. `22099131` TSMC). Sample entity: **Taiwan Semiconductor Manufacturing Co Ltd (台積電)**.

## Quirks of this jurisdiction

- Taiwanese 統一編號 (8-digit BAN) is the universal identifier — same number across business, tax, customs registers.
- Officer data covers 負責人 (responsible person), 董事長 (chair), 董事 (directors).
- Names are returned in Traditional Chinese; English names exist for listed firms but not all SMEs.
- Listed companies disclose more (TWSE / TPEx); private companies have minimal data.

## Run it

```bash
cd python/agents/openregistry-taiwan-gcis
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

經濟部商工登記公示資料 (Ministry of Economic Affairs, Department of Commerce) — GCIS open data: <https://findbiz.nat.gov.tw/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
