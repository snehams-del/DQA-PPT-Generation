# Retail Agent Skills

Production-ready AI agent skills for retail on Google Cloud. Install a skill, open your AI agent, and it walks you through the rest.

**One foundation, three revenue levers** — semantic product search at the base, with virtual try-on, recommendations, and content generation layered on top.

---

## Quick Start

### 1. Install a skill

From inside the cloned repo:

```bash
node packages/install-vertical-skill/bin/install.js retail-product-search                 # default: gemini
node packages/install-vertical-skill/bin/install.js retail-virtual-tryon --target claude
node packages/install-vertical-skill/bin/install.js retail-content-generation --target gemini
```

This drops the skill's `SKILL.md` into your agent's skill directory (`.gemini/skills/` or `.claude/skills/`) and the runnable sample into `./<skill-name>/`.

### 2. Open your agent

```bash
gemini                # if you installed with --target gemini (default)
claude                # if you installed with --target claude
```

### 3. The agent takes over

The agent finds the SKILL.md automatically and walks you through setup conversationally — asks about your GCP project, runs `agents-cli init`, copies sample code, configures the design-spec, ingests data. You answer questions; it does the work.

**Skills are recipes, not scripts.** The SKILL.md is the entry point — it tells the agent what to build and how.

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

## Evaluation & Self-Improvement (contributors)

If you've cloned this repo and want to test or improve a skill:

```bash
./vs eval retail-virtual-tryon --project-id $PROJECT     # run evalset, get pass rate
./vs improve retail-virtual-tryon --rounds 5             # Analyst → Mutator → Executor loop
./vs improve retail-virtual-tryon --dry-run              # show proposed mutations only
```

The optimizer targets `skills/<skill>/SKILL.md` directly. Each round: run evals → diagnose failures → propose ONE targeted change → test → keep if it improves, revert otherwise. History at `evals/history/`.

---

## Repository Layout

```
skills/        SKILL.md files — agent knowledge (the entry point)
samples/       Runnable code per skill — scripts, assets, tests
evals/         Shared eval framework (run.py, improve.py, sets/)
contrib/       Community gotchas, demo kit, contribution guide
catalog/       Static HTML catalog (no build step, GitHub Pages-ready)
packages/      npx installer source
```

---

## Prerequisites

- Python 3.10+
- Node 18+ (for the skill installer)
- Google Cloud project with Vertex AI + BigQuery APIs enabled
- `gcloud auth application-default login`
- [Gemini CLI](https://github.com/google/gemini-cli) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Quick paths:

- **Share a gotcha** → markdown file in [contrib/learnings/](contrib/learnings/)
- **Improve a skill** → edit `SKILL.md`, run `./vs eval` before/after, open PR with score delta
- **Create a new skill** → see the root [SKILL.md](SKILL.md) skill-creator guide

CI runs `./vs eval` on any PR that touches `skills/`. Pass rate must stay ≥ 80%.

---

## License

Apache 2.0 — see [LICENSE](LICENSE) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
