#!/usr/bin/env bash
# quality-check.sh — Level 1 + 2 quality assessment for all 4 skills.
#
# Runs the evalset for each skill, prints pass rates side by side, and saves
# verbose per-assertion output to evals/baselines/<skill>.txt for diagnosis.
#
# Usage:
#   ./scripts/quality-check.sh                    # all 4 skills
#   ./scripts/quality-check.sh retail-virtual-tryon  # just one skill

set -uo pipefail

cd "$(dirname "$0")/.."

bold=$'\033[1m'; green=$'\033[32m'; red=$'\033[31m'; yellow=$'\033[33m'; nc=$'\033[0m'

if [ -z "${GOOGLE_CLOUD_PROJECT:-}" ]; then
    echo "${red}Error: GOOGLE_CLOUD_PROJECT not set${nc}"
    echo "  export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

SKILLS=("$@")
if [ "${#SKILLS[@]}" -eq 0 ]; then
    SKILLS=(retail-product-search retail-virtual-tryon retail-product-recommendation retail-content-generation)
fi

mkdir -p evals/baselines
RESULTS=()

for skill in "${SKILLS[@]}"; do
    if [ ! -d "skills/$skill" ]; then
        echo "${red}Skipping unknown skill: $skill${nc}"
        continue
    fi
    echo ""
    echo "${bold}===== $skill =====${nc}"
    out="evals/baselines/$skill.txt"
    python evals/run.py --skill "$skill" --project-id "$GOOGLE_CLOUD_PROJECT" --verbose > "$out" 2>&1 || true

    rate=$(grep "Overall:" "$out" | tail -1 | grep -oE '[0-9]+\.[0-9]+%' | tail -1)
    rate="${rate:-N/A}"

    # Color the rate
    rate_num="${rate%\%}"
    if (( $(echo "$rate_num >= 90" | bc -l 2>/dev/null || echo 0) )); then
        color="$green"; verdict="excellent"
    elif (( $(echo "$rate_num >= 80" | bc -l 2>/dev/null || echo 0) )); then
        color="$green"; verdict="good"
    elif (( $(echo "$rate_num >= 70" | bc -l 2>/dev/null || echo 0) )); then
        color="$yellow"; verdict="borderline"
    else
        color="$red"; verdict="needs work"
    fi

    printf "  Pass rate: ${color}%s${nc}  (${verdict})\n" "$rate"
    printf "  Saved:     %s\n" "$out"

    fails=$(grep -c '\[FAIL\]' "$out" 2>/dev/null || echo 0)
    halls=$(grep -c "Hallucinated" "$out" 2>/dev/null || echo 0)
    if [ "$fails" -gt 0 ]; then
        echo "  Failures: $fails  (top 3 below)"
        grep '\[FAIL\]' "$out" | head -3 | sed 's/^/    /'
    fi
    if [ "$halls" -gt 0 ]; then
        echo "  ${red}Hallucinations detected: $halls${nc}"
    fi

    RESULTS+=("$skill	$rate	$verdict")
done

echo ""
echo "${bold}===== Summary =====${nc}"
printf "%-40s %-8s %s\n" "Skill" "Rate" "Verdict"
printf "%-40s %-8s %s\n" "----" "----" "-------"
for r in "${RESULTS[@]}"; do
    printf "%-40s %-8s %s\n" $(echo "$r" | tr '\t' ' ')
done

echo ""
echo "Detail:  ${bold}cat evals/baselines/<skill>.txt${nc}"
echo "Re-run one skill: ${bold}./scripts/quality-check.sh <skill-name>${nc}"
