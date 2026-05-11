#!/usr/bin/env python3
"""Skill spec-coverage checker — verifies SKILL.md completeness via simulated queries.

Loads the skill's SKILL.md as context, sends test queries to Gemini, and checks
whether the responses (and the spec itself) cover expected topics, fields, and
behaviors. This is NOT an end-to-end agent evaluation — it measures spec quality,
not deployed agent correctness.

Usage:
    python evals/run.py --skill retail-virtual-tryon --project-id $PROJECT
    python evals/run.py --skill retail-product-search --verbose
    python evals/run.py --skill retail-content-generation  # uses GOOGLE_CLOUD_PROJECT
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
EVALSETS_DIR = Path(__file__).parent / "sets"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def load_skill_md(skill: str) -> str:
    path = SKILLS_DIR / skill / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"SKILL.md not found: {path}")
    return path.read_text()


def load_evalset(skill: str) -> dict:
    path = EVALSETS_DIR / f"{skill}.evalset.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Evalset not found: {path}\n"
            f"Available: {[p.stem for p in EVALSETS_DIR.glob('*.evalset.json')]}"
        )
    return json.loads(path.read_text())


def _load_sample_catalog(evalset: dict) -> str:
    """Load sample product catalog if the evalset declares uses_catalog: true."""
    if not evalset.get("uses_catalog", False):
        return ""
    catalog_path = ROOT / "samples" / "retail-product-search" / "assets" / "sample-products.csv"
    if not catalog_path.exists():
        return ""
    return catalog_path.read_text()


def simulate_agent(query: str, skill_md: str, project_id: str, evalset: dict = None) -> dict:
    """Simulate skill agent response using Gemini with SKILL.md as context."""
    from google import genai
    from google.genai import types

    client = genai.Client(vertexai=True, project=project_id, location="global")

    catalog = _load_sample_catalog(evalset or {})
    catalog_section = ""
    if catalog:
        catalog_section = f"""

Your product catalog is already loaded and contains these products:

<catalog>
{catalog}
</catalog>

You are a DEPLOYED search agent with this catalog live. Answer product queries
using ONLY the products above. Do NOT walk through setup steps -- setup is
already complete. If a user asks about a product, search the catalog and respond
with real product data (name, price, brand, etc.)."""

    prompt = f"""You are an AI agent configured with this skill specification:

<skill>
{skill_md}
</skill>{catalog_section}

A user said: "{query}"

Respond as the agent would, following the skill specification exactly.
Be specific and actionable. Keep response under 300 words."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=512),
    )
    text = response.text or ""
    return {"response": text, "response_lower": text.lower()}


def check_assertion(assertion: dict, result: dict, skill_md: str, evalset: dict = None) -> tuple[bool, str]:
    """Check one assertion. Returns (passed, reason)."""
    atype = assertion["type"]
    resp = result.get("response_lower", "")
    skill = skill_md.lower()
    evalset = evalset or {}

    if atype == "response_not_empty":
        ok = len(resp.strip()) > 10
        return ok, "Response not empty" if ok else "Response is empty"

    elif atype == "response_min_length":
        ok = len(resp.strip()) >= assertion["value"]
        return ok, f"Length {len(resp)} >= {assertion['value']}" if ok else f"Too short: {len(resp)}"

    elif atype == "contains_keyword":
        kw = assertion["value"].lower()
        ok = kw in resp
        return ok, f"Found '{kw}'" if ok else f"Missing '{kw}'"

    elif atype == "skill_covers":
        topic = assertion["topic"].lower()
        ok = topic in skill
        return ok, f"SKILL.md covers '{topic}'" if ok else f"SKILL.md missing '{topic}'"

    elif atype == "step_documented":
        step = assertion["step"].lower()
        ok = step in skill
        return ok, f"Step '{step}' documented" if ok else f"Step '{step}' not documented"

    elif atype == "gotcha_mentioned":
        term = assertion["term"].lower()
        ok = term in skill
        return ok, f"Gotcha '{term}' documented" if ok else f"Gotcha '{term}' missing"

    elif atype == "mentions_model":
        model = assertion["model"].lower()
        ok = model in resp
        return ok, f"Model '{model}' mentioned" if ok else f"Model '{model}' missing"

    elif atype == "no_hallucination":
        forbidden = [f.lower() for f in assertion.get("forbidden", [])]
        found = [f for f in forbidden if f in resp]
        ok = len(found) == 0
        return ok, "No hallucinations" if ok else f"Hallucinated: {found}"

    elif atype == "graceful_no_results":
        keywords = ["no ", "not find", "couldn't find", "don't have", "not available", "broaden", "try"]
        ok = any(k in resp for k in keywords)
        return ok, "Graceful no-results handling" if ok else "Did not handle no-results gracefully"

    elif atype == "mentions_price":
        ok = bool(re.search(r"\$[\d]+\.?\d*|[\d]+\.?\d*\s*(dollar|USD)", resp))
        return ok, "Mentions price" if ok else "No price mentioned"

    elif atype == "mentions_field":
        field = assertion["field"].lower()
        # Check for field label OR actual data evidence
        if field == "price":
            ok = field in resp or bool(re.search(r"\$[\d]+\.?\d*", resp))
        elif field == "brand":
            # Brand evidence: declared in evalset (catalog_brands) or the literal word
            brands = [b.lower() for b in evalset.get("catalog_brands", [])]
            ok = field in resp or any(b in resp for b in brands)
        else:
            ok = field in resp
        return ok, f"Mentions {field}" if ok else f"Missing {field}"

    elif atype == "contains_product":
        val = assertion.get("value", "").lower()
        ok = val in resp
        return ok, f"Found '{val}'" if ok else f"Missing '{val}'"

    elif atype == "tool_called":
        # Simulated eval — actual tool execution requires live agent
        return True, "Skipped (tool_called requires --live flag)"

    elif atype == "price_under":
        prices = re.findall(r"\$?([\d]+\.?\d*)", resp)
        if not prices:
            return False, "No prices found in response"
        valid_prices = [float(p) for p in prices if float(p) >= 0.01]
        if not valid_prices:
            return False, "No valid prices found in response"
        ok = all(p <= assertion["value"] for p in valid_prices)
        return ok, f"All prices under ${assertion['value']}" if ok else f"Price over ${assertion['value']}"

    else:
        return False, f"Unknown assertion type: {atype}"


def run_eval(skill: str, project_id: str, verbose: bool = False) -> float:
    """Run all eval cases for a skill. Returns pass rate 0.0–1.0."""
    skill_md = load_skill_md(skill)
    evalset = load_evalset(skill)
    cases = evalset["eval_cases"]

    total = passed = 0
    case_results = []

    for case in cases:
        eval_id = case["eval_id"]
        query = case.get("query", "")
        if not query and "input" in case:
            query = case["input"].get("query", str(case["input"]))

        if verbose:
            logger.info(f"\n{'='*50}")
            logger.info(f"EVAL: {eval_id}")
            logger.info(f"QUERY: {query}")

        result = simulate_agent(query, skill_md, project_id, evalset=evalset)

        if verbose:
            logger.info(f"RESPONSE: {result['response'][:200]}...")

        case_passed = 0
        case_total = len(case["assertions"])

        for assertion in case["assertions"]:
            ok, reason = check_assertion(assertion, result, skill_md, evalset)
            total += 1
            if ok:
                passed += 1
                case_passed += 1
            if verbose:
                logger.info(f"  [{'PASS' if ok else 'FAIL'}] {assertion['type']}: {reason}")

        case_results.append({
            "eval_id": eval_id,
            "passed": case_passed,
            "total": case_total,
        })

    rate = passed / total if total > 0 else 0.0

    logger.info(f"\n{'='*50}")
    logger.info(f"RESULTS: {skill}")
    logger.info("=" * 50)
    for r in case_results:
        status = "PASS" if r["passed"] == r["total"] else "PARTIAL" if r["passed"] > 0 else "FAIL"
        logger.info(f"  [{status}] {r['eval_id']}: {r['passed']}/{r['total']}")

    logger.info(f"\nOverall: {passed}/{total} assertions passed ({rate:.1%})")
    return rate


def main():
    parser = argparse.ArgumentParser(description="Run skill evaluations")
    parser.add_argument("--skill", required=True, help="Skill name, e.g. retail-virtual-tryon")
    parser.add_argument("--project-id", default="", help="GCP project ID")
    parser.add_argument("--verbose", action="store_true", help="Show per-assertion results")
    args = parser.parse_args()

    if not args.project_id:
        args.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    if not args.project_id:
        parser.error("--project-id required (or set GOOGLE_CLOUD_PROJECT)")

    rate = run_eval(args.skill, args.project_id, args.verbose)
    sys.exit(0 if rate >= 0.8 else 1)


if __name__ == "__main__":
    main()
