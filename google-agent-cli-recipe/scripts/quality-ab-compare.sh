#!/usr/bin/env bash
# quality-ab-compare.sh — Level 4: A/B compare two versions of a SKILL.md.
#
# Snapshots the current SKILL.md, lets you edit it (or runs improve.py), then
# diffs the eval results before vs after.
#
# Usage:
#   ./scripts/quality-ab-compare.sh retail-virtual-tryon                  # interactive edit
#   ./scripts/quality-ab-compare.sh retail-virtual-tryon --improve 3      # run optimizer
#   ./scripts/quality-ab-compare.sh retail-virtual-tryon --apply path.md  # apply a draft

set -uo pipefail

cd "$(dirname "$0")/.."

bold=$'\033[1m'; green=$'\033[32m'; red=$'\033[31m'; cyan=$'\033[36m'; nc=$'\033[0m'

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <skill> [--improve <rounds>] [--apply <path-to-new-SKILL.md>]"
    exit 1
fi

SKILL="$1"
shift
MODE="interactive"
ROUNDS=3
DRAFT=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        --improve) MODE="improve"; ROUNDS="$2"; shift 2 ;;
        --apply) MODE="apply"; DRAFT="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

SKILL_PATH="skills/$SKILL/SKILL.md"
if [ ! -f "$SKILL_PATH" ]; then
    echo "${red}Error: $SKILL_PATH not found${nc}"
    exit 1
fi

if [ -z "${GOOGLE_CLOUD_PROJECT:-}" ]; then
    echo "${red}Error: GOOGLE_CLOUD_PROJECT not set${nc}"
    exit 1
fi

BEFORE_TXT=$(mktemp)
AFTER_TXT=$(mktemp)
BEFORE_MD="${SKILL_PATH}.before"

echo "${bold}1. Snapshot + baseline eval${nc}"
cp "$SKILL_PATH" "$BEFORE_MD"
python evals/run.py --skill "$SKILL" --project-id "$GOOGLE_CLOUD_PROJECT" --verbose > "$BEFORE_TXT" 2>&1
BEFORE_RATE=$(grep "Overall:" "$BEFORE_TXT" | tail -1 | grep -oE '[0-9]+\.[0-9]+%' | tail -1)
echo "  Before: ${cyan}$BEFORE_RATE${nc}"

echo ""
echo "${bold}2. Apply change${nc}"
case "$MODE" in
    interactive)
        echo "  Opening $SKILL_PATH in \$EDITOR (${EDITOR:-vi})..."
        "${EDITOR:-vi}" "$SKILL_PATH"
        ;;
    improve)
        echo "  Running ./vs improve $SKILL --rounds $ROUNDS"
        ./vs improve "$SKILL" --rounds "$ROUNDS" --project-id "$GOOGLE_CLOUD_PROJECT"
        ;;
    apply)
        if [ ! -f "$DRAFT" ]; then echo "${red}Draft not found: $DRAFT${nc}"; exit 1; fi
        cp "$DRAFT" "$SKILL_PATH"
        echo "  Applied draft from: $DRAFT"
        ;;
esac

if cmp -s "$BEFORE_MD" "$SKILL_PATH"; then
    echo "  ${red}No change made.${nc} Reverting and exiting."
    mv "$BEFORE_MD" "$SKILL_PATH"
    exit 0
fi

echo ""
echo "${bold}3. Re-eval${nc}"
python evals/run.py --skill "$SKILL" --project-id "$GOOGLE_CLOUD_PROJECT" --verbose > "$AFTER_TXT" 2>&1
AFTER_RATE=$(grep "Overall:" "$AFTER_TXT" | tail -1 | grep -oE '[0-9]+\.[0-9]+%' | tail -1)
echo "  After:  ${cyan}$AFTER_RATE${nc}"

echo ""
echo "${bold}4. Verdict${nc}"
echo "  Before: $BEFORE_RATE"
echo "  After:  $AFTER_RATE"

# Compare per-case results
echo ""
echo "${bold}5. Cases that changed${nc}"
diff <(grep -E "^\s+\[(PASS|FAIL)\]" "$BEFORE_TXT") \
     <(grep -E "^\s+\[(PASS|FAIL)\]" "$AFTER_TXT") || true

echo ""
echo "${bold}6. Hallucination check${nc}"
HALLS_BEFORE=$(grep -c "Hallucinated" "$BEFORE_TXT" 2>/dev/null || echo 0)
HALLS_AFTER=$(grep -c "Hallucinated" "$AFTER_TXT" 2>/dev/null || echo 0)
echo "  Before: $HALLS_BEFORE hallucinations"
echo "  After:  $HALLS_AFTER hallucinations"

echo ""
read -r -p "Keep the new SKILL.md? [y/N] " keep
if [[ "$keep" =~ ^[Yy]$ ]]; then
    rm "$BEFORE_MD"
    echo "${green}Kept.${nc} Backup deleted."
else
    mv "$BEFORE_MD" "$SKILL_PATH"
    echo "${red}Reverted.${nc} Restored from .before"
fi

echo ""
echo "Full output: ${cyan}$BEFORE_TXT${nc} (before) / ${cyan}$AFTER_TXT${nc} (after)"
