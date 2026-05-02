#!/usr/bin/env python3
"""Self-improving skill optimizer — Karpathy pattern applied to SKILL.md files.

Three-agent loop:
  Executor  — runs evals/run.py, returns pass_rate + failures
  Analyst   — reads failures, diagnoses root cause, proposes mutation type
  Mutator   — applies exactly ONE targeted change to skills/<skill>/SKILL.md

Usage:
    python evals/improve.py --skill retail-virtual-tryon --rounds 5 --project-id $PROJECT
    python evals/improve.py --skill retail-product-search --dry-run --project-id $PROJECT
"""

import argparse
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
HISTORY_DIR = Path(__file__).parent / "history"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)


# ── Executor ──────────────────────────────────────────────────────────────────

def executor(skill: str, project_id: str) -> tuple[float, list]:
    """Run eval suite and return (pass_rate, failure_details)."""
    from evals.run import load_skill_md, load_evalset, simulate_agent, check_assertion

    skill_md = load_skill_md(skill)
    evalset = load_evalset(skill)
    cases = evalset["eval_cases"]

    total = passed = 0
    failures = []

    for case in cases:
        query = case.get("query", "")
        if not query and "input" in case:
            query = case["input"].get("query", str(case["input"]))

        result = simulate_agent(query, skill_md, project_id, skill=skill)

        for assertion in case["assertions"]:
            ok, reason = check_assertion(assertion, result, skill_md)
            total += 1
            if ok:
                passed += 1
            else:
                failures.append({
                    "eval_id": case["eval_id"],
                    "query": query,
                    "assertion": assertion["type"],
                    "reason": reason,
                    "response_snippet": result["response"][:200],
                })

    rate = passed / total if total > 0 else 0.0
    return rate, failures


# ── Analyst ───────────────────────────────────────────────────────────────────

def analyst(current_skill_md: str, failures: list, pass_rate: float, round_num: int, project_id: str) -> str:
    """Diagnose failures and recommend a mutation strategy."""
    if not failures:
        return ""

    client = genai.Client(vertexai=True, project=project_id, location="global")

    failure_text = "\n".join(
        f"- [{f['eval_id']}] {f['assertion']}: {f['reason']} | query: '{f['query']}'"
        for f in failures[:10]
    )

    prompt = f"""You are diagnosing why an AI skill specification is failing its evaluations.

Current pass rate: {pass_rate:.1%} (round {round_num})

SKILL.md (current):
\"\"\"
{current_skill_md[:3000]}
\"\"\"

Failing assertions:
{failure_text}

Analyze the failures and describe in 2-3 sentences:
1. The root cause pattern
2. Exactly ONE specific change to the SKILL.md that would fix the most failures

Be concrete. Specify which section needs changing and what to add/change."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=512),
    )
    return (response.text or "").strip()


# ── Mutator ───────────────────────────────────────────────────────────────────

def mutator(current_skill_md: str, diagnosis: str, project_id: str) -> str:
    """Apply ONE targeted mutation to SKILL.md based on the analyst's diagnosis."""
    client = genai.Client(vertexai=True, project=project_id, location="global")

    prompt = f"""You are improving an AI skill specification (SKILL.md).

Analyst diagnosis:
{diagnosis}

Current SKILL.md:
\"\"\"
{current_skill_md}
\"\"\"

Apply EXACTLY ONE targeted change to fix the diagnosed issue.
Rules:
- Keep all existing content unless explicitly removing something harmful
- Do NOT restructure the whole document
- Do NOT add emojis
- Keep it under 500 lines total

Return ONLY the complete updated SKILL.md content, nothing else."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.4, max_output_tokens=4096),
    )
    return (response.text or "").strip()


# ── History ───────────────────────────────────────────────────────────────────

def save_history(skill: str, round_num: int, skill_md: str, pass_rate: float, failures: list, diagnosis: str = ""):
    """Save one optimization round to evals/history/<skill>/."""
    skill_dir = HISTORY_DIR / skill
    skill_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "round": round_num,
        "timestamp": datetime.now().isoformat(),
        "pass_rate": pass_rate,
        "diagnosis": diagnosis,
        "failures": failures[:10],
        "skill_md_snapshot": skill_md[:2000],
    }

    path = skill_dir / f"round_{round_num:03d}.json"
    path.write_text(json.dumps(record, indent=2))
    logger.info(f"  History saved: {path.relative_to(ROOT)}")


# ── Main loop ─────────────────────────────────────────────────────────────────

def improve(skill: str, project_id: str, max_rounds: int = 5, target_rate: float = 1.0, dry_run: bool = False):
    """Run the Karpathy self-improvement loop on a skill's SKILL.md."""
    skill_path = SKILLS_DIR / skill / "SKILL.md"
    if not skill_path.exists():
        logger.error(f"Skill not found: {skill_path}")
        sys.exit(1)

    original_md = skill_path.read_text()

    # Backup
    backup = skill_path.with_suffix(".md.backup")
    if not backup.exists():
        shutil.copy2(skill_path, backup)
        logger.info(f"Backed up original to {backup.relative_to(ROOT)}")

    logger.info("=" * 60)
    logger.info(f"SELF-IMPROVING: {skill}")
    logger.info(f"Target: {target_rate:.0%} | Max rounds: {max_rounds}")
    logger.info("=" * 60)

    # Baseline
    logger.info("\n[Baseline] Running evals...")
    best_rate, failures = executor(skill, project_id)
    save_history(skill, 0, original_md, best_rate, failures)
    logger.info(f"[Baseline] Pass rate: {best_rate:.1%}")

    if best_rate >= target_rate:
        logger.info("Already at target. Nothing to do.")
        return

    best_md = original_md
    current_md = original_md

    for round_num in range(1, max_rounds + 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"ROUND {round_num}/{max_rounds}  (best: {best_rate:.1%})")
        logger.info("=" * 60)

        # Analyst: diagnose failures
        _, current_failures = executor(skill, project_id)
        if not current_failures:
            logger.info("  No failures to diagnose. Stopping.")
            break

        logger.info("  Analyst: diagnosing failures...")
        diagnosis = analyst(current_md, current_failures, best_rate, round_num, project_id)
        logger.info(f"  Diagnosis: {diagnosis[:200]}...")

        # Mutator: apply change
        logger.info("  Mutator: applying ONE targeted change...")
        new_md = mutator(current_md, diagnosis, project_id)

        if new_md == current_md:
            logger.info("  No change proposed. Skipping round.")
            continue

        if not dry_run:
            skill_path.write_text(new_md)

        # Executor: test the mutation
        logger.info("  Executor: running evals on mutated skill...")
        new_rate, new_failures = executor(skill, project_id)
        save_history(skill, round_num, new_md, new_rate, new_failures, diagnosis)

        if new_rate > best_rate:
            logger.info(f"  IMPROVEMENT: {best_rate:.1%} → {new_rate:.1%}")
            best_rate = new_rate
            best_md = new_md
            current_md = new_md
        else:
            logger.info(f"  No improvement: {new_rate:.1%} <= {best_rate:.1%}. Reverting.")
            if not dry_run:
                skill_path.write_text(best_md)
            current_md = best_md

        if best_rate >= target_rate:
            logger.info(f"\n  Target reached: {best_rate:.1%}")
            break

        time.sleep(1)

    # Final report
    baseline = json.loads((HISTORY_DIR / skill / "round_000.json").read_text())
    logger.info(f"\n{'='*60}")
    logger.info("OPTIMIZATION COMPLETE")
    logger.info(f"Baseline:  {baseline['pass_rate']:.1%}")
    logger.info(f"Final:     {best_rate:.1%}")
    gained = best_rate - baseline["pass_rate"]
    logger.info(f"Gained:    {'+' if gained >= 0 else ''}{gained:.1%}")
    logger.info(f"History:   evals/history/{skill}/")
    if not dry_run and best_rate > baseline["pass_rate"]:
        logger.info(f"Updated:   skills/{skill}/SKILL.md")


def main():
    parser = argparse.ArgumentParser(description="Self-improving skill optimizer")
    parser.add_argument("--skill", required=True, help="Skill name, e.g. retail-virtual-tryon")
    parser.add_argument("--project-id", default="", help="GCP project ID")
    parser.add_argument("--rounds", type=int, default=5, help="Max optimization rounds (default: 5)")
    parser.add_argument("--target", type=float, default=1.0, help="Target pass rate 0–1 (default: 1.0)")
    parser.add_argument("--dry-run", action="store_true", help="Show mutations without writing to SKILL.md")
    args = parser.parse_args()

    if not args.project_id:
        args.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    if not args.project_id:
        parser.error("--project-id required (or set GOOGLE_CLOUD_PROJECT)")

    os.environ["GOOGLE_CLOUD_PROJECT"] = args.project_id
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

    improve(
        skill=args.skill,
        project_id=args.project_id,
        max_rounds=args.rounds,
        target_rate=args.target,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
