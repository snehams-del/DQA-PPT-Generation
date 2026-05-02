# Skill Registry

Index of all skills in this repository. Each entry maps a skill name to its SKILL.md, sample code, and evalset.

## Retail Skills

| Skill | Version | SKILL.md | Sample | Evalset | Depends on |
|-------|---------|----------|--------|---------|-----------|
| `retail-product-search` | 1.0 | [SKILL.md](retail-product-search/SKILL.md) | [sample](../samples/retail-product-search/) | [evalset](../evals/sets/retail-product-search.evalset.json) | — |
| `retail-virtual-tryon` | 1.0 | [SKILL.md](retail-virtual-tryon/SKILL.md) | [sample](../samples/retail-virtual-tryon/) | [evalset](../evals/sets/retail-virtual-tryon.evalset.json) | retail-product-search |
| `retail-product-recommendation` | 1.0 | [SKILL.md](retail-product-recommendation/SKILL.md) | [sample](../samples/retail-product-recommendation/) | [evalset](../evals/sets/retail-product-recommendation.evalset.json) | retail-product-search |
| `retail-content-generation` | 1.0 | [SKILL.md](retail-content-generation/SKILL.md) | [sample](../samples/retail-content-generation/) | [evalset](../evals/sets/retail-content-generation.evalset.json) | retail-product-search |

## Dependency Graph

```
retail-product-search (base)
    ├── retail-virtual-tryon
    ├── retail-product-recommendation
    └── retail-content-generation
```

## Installing a Skill

```bash
# From inside the cloned repo
node packages/install-vertical-skill/bin/install.js retail-virtual-tryon
node packages/install-vertical-skill/bin/install.js retail-virtual-tryon --target claude
```

The agent reads the SKILL.md and drives setup conversationally — that's what skills are for.

## Adding a New Skill

1. Create `skills/{your-skill}/SKILL.md` — follow the root `../SKILL.md` guide
2. Create `samples/{your-skill}/` — scripts, assets, tests
3. Create `evals/sets/{your-skill}.evalset.json` — at least 5 eval cases
4. Add a row to this table
5. Open a PR — CI will run `./vs eval {your-skill}` automatically
