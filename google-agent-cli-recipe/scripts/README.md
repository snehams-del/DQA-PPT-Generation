# Test & Quality Scripts

Runnable scripts that turn the testing guides into one-line commands.

| Script | Purpose | Cost | Time | GCP needed |
|--------|---------|------|------|------------|
| [smoke-test.sh](smoke-test.sh) | Offline structural sanity check (syntax, JSON, files) | $0 | ~30s | No |
| [quality-check.sh](quality-check.sh) | Pass rates for all skills + verbose baselines saved | ~$0.04 | ~2 min | Yes |
| [quality-prompts.py](quality-prompts.py) | Real-world prompts stress-test for one skill | ~$0.05 | ~3 min | Yes |
| [quality-ab-compare.sh](quality-ab-compare.sh) | A/B compare a SKILL.md change | ~$0.10 | ~3 min | Yes |
| [tryon-tier-compare.py](tryon-tier-compare.py) | Side-by-side flash / flash-3.1 / pro tiers | ~$0.30 | ~2 min | Yes |
| [quality-log.sh](quality-log.sh) | Append pass rates to a CSV for tracking drift | ~$0.04 | ~2 min | Yes |

---

## Quick start

```bash
# One-time: make scripts executable
chmod +x scripts/*.sh scripts/*.py

# Set your GCP project (only for scripts that need it)
export GOOGLE_CLOUD_PROJECT=your-project-id
gcloud auth application-default login
```

---

## Common workflows

### "Did I break anything?" — every commit

```bash
./scripts/smoke-test.sh
```

Zero cost, ~30s. Fails loudly if any file is malformed.

### "How are all 4 skills doing?" — weekly check

```bash
./scripts/quality-check.sh
./scripts/quality-log.sh           # snapshot to CSV
./scripts/quality-log.sh --plot    # see trend
```

### "Investigate a failing skill"

```bash
./scripts/quality-check.sh retail-virtual-tryon       # save baseline
./scripts/quality-prompts.py retail-virtual-tryon     # subjective check
cat evals/baselines/retail-virtual-tryon.txt          # read failures
```

### "Did my SKILL.md edit help?"

```bash
./scripts/quality-ab-compare.sh retail-virtual-tryon
# opens your $EDITOR; saves before/after; prompts to keep or revert
```

### "Compare image model tiers for try-on"

```bash
./scripts/tryon-tier-compare.py \
    --user-photo gs://my-bucket/me.jpg \
    --product-id jacket-001 \
    --description "denim jacket"
```

Generates one image per tier (flash / flash-3.1 / pro), prints latencies, and gives you GCS URIs to compare visually.

---

## What good output looks like

**smoke-test.sh:**
```
Summary: 23 passed, 0 failed
```

**quality-check.sh:**
```
Skill                                    Rate     Verdict
retail-product-search                    87.3%    good
retail-virtual-tryon                     91.7%    excellent
retail-product-recommendation            83.1%    good
retail-content-generation                79.5%    borderline
```

**quality-log.sh --plot:**
```
retail-virtual-tryon:
  2026-04-25  85.0%  ##########################################
  2026-04-28  88.5%  ############################################
  2026-04-30  91.7%  ##############################################
```

---

## Where scripts write output

```
evals/baselines/<skill>.txt       # quality-check.sh per-skill verbose log
evals/history/<skill>/round_*.json  # improve.py per-round optimization history
evals/quality-log.csv             # quality-log.sh CSV history
```

All of these are gitignored except `quality-log.csv` — feel free to commit that one to track quality over time in the repo.
