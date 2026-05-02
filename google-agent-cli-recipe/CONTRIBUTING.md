# Contributing to Vertical Agent Skills

Thanks for helping improve these skills. There are three ways to contribute, each with its own path:

---

## 1. Submit a Learning / Gotcha


**Template:**
```markdown
---
skill: retail-virtual-tryon
symptom: One sentence describing the problem the user hits
root_cause: Why it happens
fix: What to do
affected_skills:
  - retail-virtual-tryon
---

Longer explanation here (optional). Keep it concise.
```

**Rules:**
- File name: `{skill}-{short-description}.md` (e.g. `virtual-tryon-safety-filter.md`)
- No code required — open a PR or a GitHub Discussion and a maintainer will add it
- Gotchas in `contrib/learnings/` are candidates for the Analyst agent in `evals/improve.py`

---

## 2. Improve a Skill (SKILL.md)

Skills improve by running the eval loop. To propose a manual improvement:

1. Fork the repo
2. Edit `skills/{skill-name}/SKILL.md`
3. Run the eval before and after: `./vs eval {skill-name} --project-id $PROJECT`
4. Include both scores in your PR description: `Before: 72% → After: 89%`
5. Open a PR with the label `skill-improvement`

**Or let the optimizer do it:**
```bash
./vs improve retail-virtual-tryon --rounds 3 --project-id $PROJECT
```
Then review `evals/history/retail-virtual-tryon/` and open a PR with the best result.

---

## 3. Create a New Skill

New skills should follow the same structure as the existing ones.

**Checklist:**
- [ ] `skills/{your-skill}/SKILL.md` — under 500 lines, interview-driven steps
- [ ] `samples/{your-skill}/scripts/setup.py` — setup automation
- [ ] `samples/{your-skill}/assets/design-spec.md` — config template
- [ ] `samples/{your-skill}/tests/unit/` — at minimum test that setup.py runs
- [ ] `evals/sets/{your-skill}.evalset.json` — at least 5 eval cases
- [ ] Entry in `skills/SKILL.md` (parent index) under dependencies

**Read first:** the root `SKILL.md` in this repo (the skill-creator guide).

---

## For Non-Technical Contributors

No code? No problem.

- **GitHub Discussions** → "Share a Learning" — use the template, no PR needed
- Maintainers will convert your discussion into a `contrib/learnings/` file

---

## Eval Score Bar

PRs that change a `skills/*/SKILL.md` should not lower the eval score. The CI check runs `./vs eval {skill}` on changed skill files.

Target: **≥ 0.80 pass rate** to merge.
