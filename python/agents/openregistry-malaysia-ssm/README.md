# Malaysia — SSM ADK Agent

A Gemini-powered ADK agent with live access to **Suruhanjaya Syarikat Malaysia (SSM) — Companies Commission of Malaysia** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **MY** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Malaysian company · SSM · Suruhanjaya Syarikat Malaysia · Sdn Bhd · Bhd.

Example queries:

> *"Find Maybank Bhd's SSM record and confirm operating status"*
>
> *"Look up Petronas Sdn Bhd"*
>
> *"Confirm the registration status of Genting Bhd"*

## Native ID format

12-digit SSM registration number (e.g. `199301015245`) or older 6-digit company number. Sample entity: **Maybank Bhd (Malayan Banking Berhad)**.

## Quirks of this jurisdiction

- SSM open data is **basic-status only** — full filings, officers, shareholders are paid via SSM e-Info / MBRS.
- `Sdn Bhd` (Sendirian Berhad) = private limited; `Bhd` (Berhad) = public.
- 12-digit SSM number = year (4) + counter (8); pre-2017 entities have 6-digit legacy numbers — both still in use.
- Malaysian UBO register (RBO) is access-controlled to AML-obliged entities; not in this dataset.

## Run it

```bash
cd python/agents/openregistry-malaysia-ssm
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Suruhanjaya Syarikat Malaysia (SSM) — Companies Commission of Malaysia: <https://www.ssm.com.my/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
