# Retail Agent Skills

Production-ready AI agent skills for retail on Google Cloud. Install a skill, open your AI agent, and it walks you through the rest.

**One foundation, three revenue levers** — semantic product search at the base, with virtual try-on, recommendations, and content generation layered on top.

This repo serves two audiences:

- **[Use a skill](#use-a-skill)** — you're a developer building a retail agent and you want a skill to guide your AI agent (Claude Code, Gemini CLI, Codex, …).
- **[Hack on the skills](#hack-on-the-skills)** — you've cloned this repo and want to edit, evaluate, or contribute a skill.

---

## Skills

| Skill | Description | Layered on |
|-------|-------------|------------|
| [retail-product-search](skills/retail-product-search/SKILL.md) | Semantic product search with Vector Search, RAG, optional voice | base |
| [retail-virtual-tryon](skills/retail-virtual-tryon/SKILL.md) | Virtual try-on with dedicated VTO model or Gemini image tiers | product-search |
| [retail-product-recommendation](skills/retail-product-recommendation/SKILL.md) | "You might also like" via collaborative / content-based / LLM | product-search |
| [retail-content-generation](skills/retail-content-generation/SKILL.md) | Product descriptions, SEO, marketing copy via Gemini | product-search |

See [skills/REGISTRY.md](skills/REGISTRY.md) for the full index.

---

## Use a skill

You're building a retail agent. Pick a skill, install it into your AI coding agent, and let the agent drive the rest.

### Prerequisites

- Node 18+ (for the installer)
- Python 3.10+ (for the sample code the agent will run)
- Google Cloud project with Vertex AI + BigQuery APIs enabled
- `gcloud auth application-default login`
- [agents-cli](https://github.com/google/agents-cli) — `pip install google-agents-cli && agents-cli setup`
- An AI coding agent: [Gemini CLI](https://github.com/google/gemini-cli), [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Codex, etc.

### 1. Install a skill into your agent

Pick `--target` based on your AI coding agent:

```bash
# Default: --target gemini (Gemini CLI, etc.)
npx --package github:google/vertical-skills install-vertical-skill retail-product-search

# Claude Code
npx --package github:google/vertical-skills install-vertical-skill retail-product-search --target claude

# Both at once (cross-agent demo)
npx --package github:google/vertical-skills install-vertical-skill retail-product-search --target both
```

| Your agent | Use this | Why |
|---|---|---|
| Gemini CLI | default (or `--target gemini`) | Gemini reads `.agents/skills/` |
| Claude Code | `--target claude` | Claude Code reads `.claude/skills/` |
| Codex / Cursor / Aider / Jules / Devin / … | default — they read AGENTS.md only | These agents have no skills mechanism; AGENTS.md is sufficient |

The installer drops:
- **`SKILL.md`** → the chosen target dir (`.agents/skills/` or `.claude/skills/`, or both)
- **`AGENTS.md`** at project root — routes the question flow to the retail skill regardless of which other skills (e.g. `google-agents-cli-*`) are also active. The Q-MODE first-response block is **inlined** so agents that don't load skill files (Codex, Cursor, Aider, Jules, Devin) still follow the right behavior verbatim. This is the load-bearing piece.
- Slim sample tree → `./<skill-name>/`
- Shared helpers → `./_shared/`

> Once published, the shorter form `npx install-vertical-skill <skill>` will work directly. Until then, point at the source repo with `--package github:google/vertical-skills` (or use `--source <org>/<repo>[@branch]` to install from your own fork).

### 1b. Skill collisions

`agents-cli` ships ~7 of its own skills (`google-agents-cli-scaffold`, `google-agents-cli-workflow`, etc.) that handle generic agent mechanics. They share descriptions with the retail skill and would otherwise compete for the conversation flow.

The `AGENTS.md` written by the installer **routes around this** — it tells the AI agent that the retail skill drives Q&A while the agents-cli skills handle mechanics underneath. Most modern agents read `AGENTS.md` from the project root before / above skill matching, so the routing wins.

If you still see bulk-question lists instead of the Q-MODE / `[default: ...]` flow:
1. Verify `AGENTS.md` exists at your project root and contains a `vertical-skills:routing-start` marker.
2. Ensure your AI agent reads `AGENTS.md` (Claude Code, Gemini CLI, Codex, Cursor, Aider — all do today).
3. As a hard fix, the installer prints `mv` commands to rename conflicting global skills out of the way. Run them, then retry.

### 2. Open your agent and talk to it

```bash
gemini       # or: claude, codex, …
```

Then describe what you want — for example:
> *"I want to build a product search agent for my e-commerce site."*

The agent finds the SKILL.md automatically and walks you through setup conversationally — asks about your GCP project, runs `agents-cli scaffold` to bootstrap the project, copies sample code, configures the design-spec, ingests data. You answer questions; it does the work.

**Skills are recipes, not scripts.** The SKILL.md is the entry point — it tells your AI agent what to build and how.

---

## Hack on the skills

You've cloned this repo and want to edit a SKILL.md, run quality checks, or contribute a new skill. The `vs` CLI is the contributor entrypoint.

### Prerequisites

- Everything from [Use a skill](#use-a-skill), plus:
- This repo cloned locally
- Python deps for the eval framework (`pip install -e samples/retail-product-search` or per-sample as needed)

### Common workflows

```bash
./vs list                                                # show all skills with descriptions
./vs eval retail-virtual-tryon --project-id $PROJECT     # run spec-coverage check, get score
./vs eval retail-virtual-tryon --verbose                 # per-assertion PASS/FAIL output
./vs improve retail-virtual-tryon --dry-run              # propose mutations without writing
./vs improve retail-virtual-tryon --rounds 5             # interactive: confirm each mutation
```

`vs eval` measures SKILL.md spec completeness (does the spec cover expected topics, fields, and behaviors?), not deployed agent correctness. It sends simulated queries to Gemini with the SKILL.md as context and checks assertions against the responses.

### Testing your changes end-to-end against a real AI agent

Once `vs eval` passes, install your branch into an empty dir and drive the conversation manually to make sure the SKILL.md actually behaves as intended:

```bash
mkdir /tmp/skill-test && cd /tmp/skill-test
node /path/to/repo/packages/install-vertical-skill/bin/install.js \
    retail-product-search --local /path/to/repo --target gemini
# The installer warns about conflicting global skills -- follow the mv commands if any
gemini
# → drive through the developer-style conversation; observe the agent's first
#   message matches the expected Q-MODE format
```

The first agent message is the load-bearing test -- if it doesn't match the expected Q-MODE pattern, your SKILL.md edits aren't being honored (or a conflicting global skill is winning).

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Quick paths:

- **Share a gotcha** → markdown file in [contrib/learnings/](contrib/learnings/)
- **Improve a skill** → edit `SKILL.md`, run `./vs eval` before/after, open PR with score delta
- **Create a new skill** → see the [SKILL.md](skills/SKILL.md) skill-creator guide

CI runs `./vs eval` on any PR that touches `skills/`. Spec-coverage score must stay >= 80%.

### Experimental: self-improvement loop

`./vs improve` runs a Karpathy-style three-agent loop (Analyst → Mutator → Executor) that mutates `skills/<skill>/SKILL.md` to maximize the spec-coverage score. History saved to `evals/history/`.

> ⚠️ **Caveat:** the score is partially self-referential — `gotcha_mentioned`/`step_documented`/`skill_covers` check whether topics appear in SKILL.md itself. Treat the score as a regression signal, not an absolute quality measure. Always review diffs before merging optimizer-generated edits. Default behavior asks for confirmation per round; pass `--yes` only in CI.

### Repository layout

```
skills/        SKILL.md files — agent knowledge (the entry point)
samples/       Runnable code per skill — scripts, assets, tests
evals/         Shared eval framework (run.py, improve.py, sets/)
contrib/       Community gotchas, demo kit, contribution guide
catalog/       Static HTML catalog (no build step, GitHub Pages-ready)
packages/      npx installer source
scripts/       Test, quality, and helper scripts (smoke-test, conflict-check, ...)
vs             Contributor CLI (list / eval / improve)
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
