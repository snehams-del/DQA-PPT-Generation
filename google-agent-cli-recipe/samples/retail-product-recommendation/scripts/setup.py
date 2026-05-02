#!/usr/bin/env python3
"""Automated project setup for product recommendation, driven by design-spec.md.

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
    """Run the recommendation setup pipeline based on design-spec.md."""
    cfg = load_config(config_path)

    project_id = cfg.get("gcp_project_id", "")
    if not project_id:
        logger.error("gcp_project_id is required in design-spec.md")
        sys.exit(1)

    rec_type = cfg.get("recommendation_type", "collaborative")
    has_user_events = cfg.get("has_user_events", "Yes")
    rec_placement = cfg.get("rec_placement", "product-page")
    dataset_id = cfg.get("dataset_id", "retail_dataset")
    user_events_table = cfg.get("user_events_table", "user_events")

    logger.info("=" * 60)
    logger.info("RECOMMENDATION SETUP (driven by design-spec.md)")
    logger.info("=" * 60)
    logger.info(f"  Project:          {project_id}")
    logger.info(f"  Rec type:         {rec_type}")
    logger.info(f"  Has user events:  {has_user_events}")
    logger.info(f"  Placement:        {rec_placement}")

    ok = True

    # Content-based doesn't need user events
    if rec_type == "content-based":
        logger.info("\n  Content-based recommendations use existing product embeddings.")
        logger.info("  No user event ingestion needed.")
        if has_user_events == "Yes":
            logger.info("  User events available but not required for content-based.")
    else:
        # Collaborative, hybrid, vertex-ai all need user events
        if has_user_events == "No":
            logger.warning("\n  WARNING: Collaborative/hybrid recommendations require user events.")
            logger.warning("  Please provide user event data (views, clicks, purchases).")
            logger.warning("  Place your events file at assets/sample-user-events.csv")
        else:
            sample_file = None
            for candidate in ["assets/sample-user-events.csv", "data/sample-user-events.csv", "data/user-events.csv"]:
                if Path(candidate).exists():
                    sample_file = candidate
                    break

            if sample_file:
                ok = run_step(
                    "Ingesting user events into BigQuery...",
                    ["python", "scripts/ingest_user_events.py", "--config", config_path,
                     "--project-id", project_id, "--dataset-id", dataset_id,
                     "--table-id", user_events_table, "--local-file", sample_file],
                    dry_run,
                ) and ok
            else:
                logger.info("\n  No user events file found. Skipping ingestion.")
                logger.info("  Place events at assets/sample-user-events.csv and re-run.")

    # Vertex AI Recommendations AI setup
    if rec_type == "vertex-ai":
        logger.info("\n  Vertex AI Recommendations AI selected.")
        logger.info("  Ensure the Retail API is enabled in your GCP project.")
        logger.info("  See: https://cloud.google.com/retail/docs/overview")

    # LLM-driven recommendations
    if rec_type == "llm-driven":
        logger.info("\n  LLM-driven recommendations use Gemini with catalog context.")
        logger.info("  No additional setup needed beyond product search.")

    # Placement info
    logger.info(f"\n  Recommendation placement: {rec_placement}")
    if rec_placement == "all":
        logger.info("  Recommendations will appear on product pages, cart, and homepage.")

    logger.info("\n" + "=" * 60)
    if ok:
        logger.info("RECOMMENDATION SETUP COMPLETE")
    else:
        logger.info("SETUP COMPLETED WITH ERRORS")
    logger.info("=" * 60)
    return ok


def main():
    parser = argparse.ArgumentParser(description="Run recommendation setup from design-spec.md")
    parser.add_argument("--config", required=True, help="Path to design-spec.md")
    parser.add_argument("--dry-run", action="store_true", help="Show commands without running")
    args = parser.parse_args()
    ok = setup(args.config, args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
