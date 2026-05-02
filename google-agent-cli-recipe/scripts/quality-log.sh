#!/usr/bin/env bash
# quality-log.sh — append today's pass rates to evals/quality-log.csv.
#
# Run after any change to track quality drift over time. The CSV is plain
# text and easy to plot or tail.
#
# Usage:
#   ./scripts/quality-log.sh                    # log all 4 skills
#   ./scripts/quality-log.sh --tail             # show recent history
#   ./scripts/quality-log.sh --plot             # ascii bar chart per skill

set -uo pipefail

cd "$(dirname "$0")/.."

LOG="evals/quality-log.csv"
mkdir -p evals

# ── tail mode ────────────────────────────────────────────────────────────────
if [ "${1:-}" = "--tail" ]; then
    if [ ! -f "$LOG" ]; then echo "No log yet at $LOG"; exit 0; fi
    column -t -s, "$LOG" | tail -20
    exit 0
fi

# ── plot mode ────────────────────────────────────────────────────────────────
if [ "${1:-}" = "--plot" ]; then
    if [ ! -f "$LOG" ]; then echo "No log yet at $LOG"; exit 0; fi
    echo "Quality over time (last 10 entries per skill):"
    for skill in retail-product-search retail-virtual-tryon retail-product-recommendation retail-content-generation; do
        echo ""
        echo "$skill:"
        grep ",$skill," "$LOG" | tail -10 | while IFS=, read -r date _ rate; do
            num="${rate%\%}"
            bars=$(printf "%.0f" "$num" 2>/dev/null || echo 0)
            bar=$(printf '#%.0s' $(seq 1 $((bars / 2))) 2>/dev/null || echo "")
            printf "  %s  %5s  %s\n" "$date" "$rate" "$bar"
        done
    done
    exit 0
fi

# ── log mode ─────────────────────────────────────────────────────────────────
if [ -z "${GOOGLE_CLOUD_PROJECT:-}" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT not set"
    exit 1
fi

if [ ! -f "$LOG" ]; then
    echo "date,skill,pass_rate" > "$LOG"
fi

DATE=$(date +%Y-%m-%d)
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "no-git")

echo "Logging quality for $DATE (commit $COMMIT)..."
for skill in retail-product-search retail-virtual-tryon retail-product-recommendation retail-content-generation; do
    rate=$(python evals/run.py --skill "$skill" --project-id "$GOOGLE_CLOUD_PROJECT" 2>&1 \
           | grep "Overall:" | tail -1 | grep -oE '[0-9]+\.[0-9]+%' | tail -1)
    rate="${rate:-N/A}"
    echo "  $skill: $rate"
    echo "$DATE,$skill,$rate" >> "$LOG"
done

echo ""
echo "Appended to: $LOG"
echo "View history: ./scripts/quality-log.sh --tail"
echo "Plot:         ./scripts/quality-log.sh --plot"
