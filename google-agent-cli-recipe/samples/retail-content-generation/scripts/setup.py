#!/usr/bin/env python3
"""Automated project setup for content generation, driven by design-spec.md.

Reads the design-spec.md configuration and runs the appropriate scripts
based on the user's answers.

Usage:
    python scripts/setup.py --config assets/design-spec.md
    python scripts/setup.py --config assets/design-spec.md --dry-run
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load design-spec.md YAML frontmatter."""
    if not Path(config_path).exists():
        return {}
    text = Path(config_path).read_text()
    if text.startswith("---"):
        lines = text.split("\n")
        yaml_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            if in_frontmatter:
                yaml_lines.append(line)
        yaml_text = "\n".join(yaml_lines)
        return yaml.safe_load(yaml_text) or {}
    return yaml.safe_load(text) or {}


def run_step(description: str, cmd: list, dry_run: bool = False) -> bool:
    """Run a pipeline step. Returns True on success."""
    logger.info(f"\n  {description}")
    if dry_run:
        logger.info(f"    [dry-run] {' '.join(cmd)}")
        return True
    logger.info(f"    Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        logger.error(f"    FAILED (exit code {result.returncode})")
        return False
    return True


def setup(config_path: str, dry_run: bool = False):
    """Run the content generation pipeline based on design-spec.md."""
    cfg = load_config(config_path)

    project_id = cfg.get("gcp_project_id", "")
    if not project_id:
        logger.error("gcp_project_id is required in design-spec.md")
        sys.exit(1)

    content_type = cfg.get("content_type", "descriptions")
    brand_tone = cfg.get("brand_tone", "Professional and informative")
    target_languages = cfg.get("target_languages", [])
    ab_variants = cfg.get("ab_variants", 1)
    gemini_model = cfg.get("gemini_model", "gemini-2.5-flash")
    batch_size = cfg.get("batch_size", 50)
    output_format = cfg.get("output_format", "BigQuery table")
    dataset_id = cfg.get("dataset_id", "products_dataset")

    logger.info("=" * 60)
    logger.info("CONTENT GENERATION SETUP (driven by design-spec.md)")
    logger.info("=" * 60)
    logger.info(f"  Project:     {project_id}")
    logger.info(f"  Content:     {content_type}")
    logger.info(f"  Tone:        {brand_tone}")
    logger.info(f"  Languages:   {target_languages if target_languages else ['en (default)']}")
    logger.info(f"  A/B variants: {ab_variants}")
    logger.info(f"  Model:       {gemini_model}")
    logger.info(f"  Batch size:  {batch_size}")

    ok = True

    # Build the generate command
    gen_cmd = [
        "python", "scripts/generate_content.py",
        "--config", config_path,
        "--project-id", project_id,
        "--type", content_type,
        "--variants", str(ab_variants),
        "--batch-size", str(batch_size),
    ]

    if target_languages:
        gen_cmd.extend(["--languages", ",".join(target_languages)])

    # Content type guidance
    if content_type == "all":
        logger.info("\n  Generating all content types: description, seo_title, meta_description, marketing_copy")
        for ctype in ["description", "seo_title", "meta_description", "marketing_copy"]:
            type_cmd = gen_cmd.copy()
            # Replace --type value
            type_idx = type_cmd.index("--type") + 1
            type_cmd[type_idx] = ctype
            ok = run_step(
                f"Generating {ctype}...",
                type_cmd,
                dry_run,
            ) and ok
    else:
        ok = run_step(
            f"Generating {content_type} content...",
            gen_cmd,
            dry_run,
        ) and ok

    # Translation step
    if target_languages and content_type != "translations":
        logger.info(f"\n  Translations requested for: {', '.join(target_languages)}")
        trans_cmd = gen_cmd.copy()
        type_idx = trans_cmd.index("--type") + 1
        trans_cmd[type_idx] = "translations"
        ok = run_step(
            "Generating translations...",
            trans_cmd,
            dry_run,
        ) and ok

    # Export info
    if output_format == "BigQuery table":
        logger.info(f"\n  Content saved to BigQuery dataset: {dataset_id}")
    else:
        logger.info("\n  Content saved to local files.")

    # Export command
    if Path("scripts/export_content.py").exists():
        logger.info("  Export content with:")
        logger.info(f"    python scripts/export_content.py --config {config_path} --project-id {project_id}")

    logger.info("\n" + "=" * 60)
    if ok:
        logger.info("CONTENT GENERATION COMPLETE")
    else:
        logger.info("GENERATION COMPLETED WITH ERRORS")
    logger.info("=" * 60)
    return ok


def main():
    parser = argparse.ArgumentParser(description="Run content generation from design-spec.md")
    parser.add_argument("--config", required=True, help="Path to design-spec.md")
    parser.add_argument("--dry-run", action="store_true", help="Show commands without running")
    args = parser.parse_args()
    ok = setup(args.config, args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
