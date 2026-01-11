#!/usr/bin/env bash
# Simple packaging script for Project DIAL handoff
# Produces a tarball with the selected artifacts listed in HANDOFF_ARTIFACTS_CHECKLIST.md
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT/dist"
mkdir -p "$OUT_DIR"
PACKAGE_NAME="project-dial-handoff-$(date +%Y%m%d).tar.gz"
# Files/dirs to include (adjust as needed)
INCLUDE=(
  "PROJECT_DIAL_DECISION_PACKAGE.md"
  "PROJECT_DIAL_SPRINT1_ROADMAP.md"
  "HANDOFF_ARTIFACTS_CHECKLIST.md"
  ".vscode/HEPHAESTUS_BOOTSTRAP.code-snippets"
  "HEPHAESTUS_BOOTSTRAP_GUIDE.md"
)
# Add optional dirs if present
for d in contracts artifacts deployments oracle dapp tests security tokenomics demo ops; do
  if [ -e "$ROOT/$d" ]; then
    INCLUDE+=("$d")
  fi
done

# Create temp dir
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT
mkdir -p "$TMPDIR/package"
for p in "${INCLUDE[@]}"; do
  if [ -e "$ROOT/$p" ]; then
    cp -a "$ROOT/$p" "$TMPDIR/package/"
  else
    echo "Warning: $p not found, skipping"
  fi
done

tar -czf "$OUT_DIR/$PACKAGE_NAME" -C "$TMPDIR" package
echo "Created $OUT_DIR/$PACKAGE_NAME"
