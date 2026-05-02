#!/usr/bin/env python3
"""tryon-tier-compare.py — compare flash / flash-3.1 / pro Gemini image tiers.

Generates a try-on image with each model tier on the same input, measures
latency, and saves output URIs side by side so you can judge visual quality.

Usage:
    python scripts/tryon-tier-compare.py \\
        --user-photo gs://my-bucket/user.jpg \\
        --product-id jacket-001 \\
        --description "denim jacket"

    # Just a subset of tiers:
    python scripts/tryon-tier-compare.py --user-photo ... --product-id ... \\
        --tiers flash,pro
"""

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "samples" / "retail-virtual-tryon"))


def main():
    parser = argparse.ArgumentParser(description="Compare Gemini image model tiers for try-on")
    parser.add_argument("--user-photo", required=True, help="GCS URI of user photo (gs://...)")
    parser.add_argument("--product-id", required=True, help="Product ID (must exist in output bucket)")
    parser.add_argument("--description", default="", help="Product description for the prompt")
    parser.add_argument("--project-id", default=os.environ.get("GOOGLE_CLOUD_PROJECT", ""))
    parser.add_argument("--output-bucket", default="")
    parser.add_argument("--upload-bucket", default="")
    parser.add_argument("--safety-level", default="block_most",
                        choices=["block_most", "block_some", "block_few"])
    parser.add_argument("--tiers", default="vto,flash,pro",
                        help="Comma-separated model labels to compare (vto / flash / flash-3.1 / pro)")
    args = parser.parse_args()

    if not args.project_id:
        parser.error("--project-id required (or set GOOGLE_CLOUD_PROJECT)")

    output_bucket = args.output_bucket or f"{args.project_id}-tryon-output"
    upload_bucket = args.upload_bucket or f"{args.project_id}-tryon-uploads"
    tiers = [t.strip() for t in args.tiers.split(",") if t.strip()]

    from app.tryon_processor import generate_tryon

    print(f"User photo:     {args.user_photo}")
    print(f"Product:        {args.product_id} ({args.description or 'no description'})")
    print(f"Safety:         {args.safety_level} (Gemini path only — VTO has its own filter)")
    print(f"Models tested:  {', '.join(tiers)}")
    print()

    results = []
    for tier in tiers:
        print(f"===== Tier: {tier} =====")
        t0 = time.time()
        try:
            result = generate_tryon(
                product_id=args.product_id,
                user_photo_uri=args.user_photo,
                project_id=args.project_id,
                output_bucket=output_bucket,
                upload_bucket=upload_bucket,
                model_label_or_id=tier,
                safety_level=args.safety_level,
                product_description=args.description,
                num_variations=1,
            )
            elapsed = time.time() - t0
            print(f"  Latency:    {elapsed:.1f}s")
            print(f"  Model used: {result['model_used']}")
            print(f"  Safety:     {result['safety_level']}")
            print(f"  Output:     {result['output_uri']}")
            results.append({"tier": tier, "latency_s": elapsed, **result})
        except Exception as e:
            elapsed = time.time() - t0
            print(f"  FAILED ({elapsed:.1f}s): {e}")
            results.append({"tier": tier, "latency_s": elapsed, "error": str(e)})
        print()

    print("===== Summary =====")
    print(f"{'Tier':<12} {'Latency':<10} {'Output URI'}")
    print(f"{'----':<12} {'-------':<10} {'----------'}")
    for r in results:
        latency = f"{r['latency_s']:.1f}s"
        uri = r.get("output_uri", r.get("error", "—"))[:80]
        print(f"{r['tier']:<12} {latency:<10} {uri}")

    print()
    print("Open each output URI in the GCP Console or download with:")
    print("  gsutil cp <gs-uri> .")
    print()
    print("Quality criteria to judge:")
    print("  ✓ Face preserved (same person, same skin tone)")
    print("  ✓ Product fits naturally (no obvious distortion)")
    print("  ✓ Background unchanged")
    print("  ✗ Artifacts (extra fingers, warped features)")


if __name__ == "__main__":
    main()
