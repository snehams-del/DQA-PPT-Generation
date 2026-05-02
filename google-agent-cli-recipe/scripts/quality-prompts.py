#!/usr/bin/env python3
"""quality-prompts.py — Level 3: real-world prompt stress-test.

Runs a curated set of realistic prompts through a skill's simulated agent
and prints the responses side by side so you can judge subjectively.

Usage:
    python scripts/quality-prompts.py retail-virtual-tryon
    python scripts/quality-prompts.py retail-product-search
    python scripts/quality-prompts.py retail-virtual-tryon --save out.md
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

PROMPT_SETS = {
    "retail-product-search": [
        "show me products under $50",
        "I want something for my dad's birthday, he likes camping",
        "compare your top 3 keyboards",
        "do you sell cars?",
        "which of these do you have in stock right now?",
        "I'm looking for noise-canceling headphones for travel",
        "what's your cheapest item that ships overnight?",
    ],
    "retail-virtual-tryon": [
        "I have very dark skin tone — will the try-on look natural?",
        "Can my 8-year-old try on clothes?",
        "I uploaded a photo but it failed. What now?",
        "Why does the same product look different each time?",
        "Show me how this swimsuit looks on me",
        "Can I try on jewelry without a face photo?",
        "My photo got rejected for safety — what's wrong?",
        "Which model gives best quality?",
        "How long does try-on take?",
        "Can I try on multiple products at once?",
    ],
    "retail-product-recommendation": [
        "I'm a brand new user, no history yet",
        "Show me what people like me bought",
        "I want diverse recommendations, not all the same brand",
        "Recommend something based on this product page",
        "The recommendations are too repetitive — fix it",
        "Recommend gifts under $100",
        "Why are you recommending this product?",
    ],
    "retail-content-generation": [
        "Generate a product description for kids",
        "Write SEO meta description in Spanish",
        "Give me 3 A/B variants for Black Friday",
        "Match Patagonia's brand voice",
        "Generate content but don't make up specs that aren't given",
        "Translate this description to French and German",
        "Write a marketing email for our holiday sale",
    ],
}


def run(skill: str, project_id: str, save_path: str = "") -> None:
    if skill not in PROMPT_SETS:
        print(f"Unknown skill: {skill}")
        print(f"Available: {list(PROMPT_SETS.keys())}")
        sys.exit(1)

    from evals.run import load_skill_md, simulate_agent

    skill_md = load_skill_md(skill)
    prompts = PROMPT_SETS[skill]

    output_lines = [f"# Quality prompts for {skill}\n"]
    output_lines.append(f"_{len(prompts)} real-world prompts; judge each response subjectively._\n")

    for i, p in enumerate(prompts, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(prompts)}] Q: {p}")
        print("=" * 60)
        try:
            result = simulate_agent(p, skill_md, project_id)
            response = result["response"]
        except Exception as e:
            response = f"[error] {e}"
        print(response)

        output_lines.append(f"\n## {i}. {p}\n")
        output_lines.append("```")
        output_lines.append(response)
        output_lines.append("```\n")

    if save_path:
        Path(save_path).write_text("\n".join(output_lines))
        print(f"\nSaved to: {save_path}")

    print("\n" + "=" * 60)
    print("Judge each response on:")
    print("  ✓ Specific (mentions config/model/file) vs generic")
    print("  ✓ Honest about limitations")
    print("  ✓ Handles edge cases")
    print("  ✗ Hallucinations or contradictions to SKILL.md")


def main():
    parser = argparse.ArgumentParser(description="Stress-test a skill with real-world prompts")
    parser.add_argument("skill", choices=list(PROMPT_SETS.keys()), help="Skill to test")
    parser.add_argument("--project-id", default=os.environ.get("GOOGLE_CLOUD_PROJECT", ""))
    parser.add_argument("--save", default="", help="Save responses to a markdown file")
    args = parser.parse_args()

    if not args.project_id:
        parser.error("--project-id required (or set GOOGLE_CLOUD_PROJECT)")

    run(args.skill, args.project_id, args.save)


if __name__ == "__main__":
    main()
