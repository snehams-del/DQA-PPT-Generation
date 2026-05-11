# Iceland — Fyrirtækjaskrá ADK Agent

A Gemini-powered ADK agent with live access to **Fyrirtækjaskrá — Skatturinn (Icelandic Revenue and Customs)** via the [OpenRegistry](https://openregistry.sophymarine.com) MCP server.

This is the **IS** single-jurisdiction variant. For multi-jurisdiction / cross-border ownership-chain walks, see the sibling [`openregistry-cross-border-kyc`](../openregistry-cross-border-kyc) sample.

## What it does

Trigger phrases: Icelandic company · Fyrirtækjaskrá · Skatturinn · kennitala · hf.

Example queries:

> *"Pull Marel hf.'s full UBO list with `get_persons_with_significant_control`"*
>
> *"List the directors of Landsbankinn hf."*
>
> *"Find an Icelandic ehf by company name"*

## Native ID format

10-digit Icelandic kennitala (e.g. `5710002400` Landsvirkjun). Sample entity: **Marel hf.**.

## Quirks of this jurisdiction

- Iceland has a **public UBO register** — `get_persons_with_significant_control` is fully supported here (rare in our dataset).
- `hf.` = public limited; `ehf.` = private limited; `slhf.` = Samvinnufélag (cooperative).
- Kennitala is a 10-digit ID assigned to both individuals and companies — the format is the same; context distinguishes.
- Icelandic company names use Icelandic characters (þ, ð, æ); `search_companies` handles ASCII-folded queries.

## Run it

```bash
cd python/agents/openregistry-iceland-fyrirtaekjaskra
cp .env.example .env
# Set GOOGLE_API_KEY in .env
pip install -e .
adk run .
```

## Government source

Fyrirtækjaskrá — Skatturinn (Icelandic Revenue and Customs): <https://www.skatturinn.is/fyrirtaekjaskra/>.

## License

Apache 2.0.

OpenRegistry is a platform by [Sophymarine](https://sophymarine.com).
